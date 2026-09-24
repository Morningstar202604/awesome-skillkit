---
name: api-test-suite-builder
description: "Generate API tests and integration test suites by scanning route definitions across frameworks (Next.js App Router, Express, FastAPI, Django REST). Covers auth, input validation, error codes, pagination, file upload, and rate limiting. Use when the user asks to generate API tests, generate interface tests, write integration tests, build contract tests, test REST endpoints, or create integration test suites. Do NOT use for running the generated suites inside CI (it only generates them)."
license: Apache-2.0
compatibility: Pure prompt-based; may read project structure via Bash.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: api
  pattern: pipeline-builder
  tier: powerful
  verified-date: "2026-09-09"
---

# API Test Suite Builder

Scans API route definitions across frameworks (Next.js App Router, Express, FastAPI, Django REST) and generates a runnable test suite — Vitest+Supertest (Node) or Pytest+httpx (Python) — covering auth, input validation, error codes, pagination, file upload, and rate limiting.

## Input Checklist

| Input | Required | Description |
|---|---|---|
| Project root | Yes | Path to the repo containing the API route definitions |
| Framework | Yes | next-app-router / express / fastapi / django-rest (if unsure, step 1's probe commands decide it) |
| Test stack | Yes | vitest+supertest (Node) or pytest+httpx (Python) |
| Output location | No | The directory for test files; defaults to project convention (`tests/` or `__tests__/`) |
| Generation scope | No | All routes or a specified route group; defaults to all |

When inputs are missing, ask for all at once: "Please provide: (1) the project root; (2) the test stack (Vitest+Supertest or Pytest+httpx); (3) whether to generate only some routes. If the framework is unclear, I'll decide it with probe commands first."

## Pre-flight Checks

Run each in turn; on any failure → apply the fix, then STOP:

```bash
# 1. The project directory exists
ls <project-root> > /dev/null && echo OK
# Expected: OK. On failure → confirm the path with the user, STOP.

# 2. Probe for framework signals (at least one hits)
ls <project-root>/package.json <project-root>/requirements.txt <project-root>/pyproject.toml 2>/dev/null
# Expected: at least one file listed. If all are missing → confirm this is an API project, STOP.

# 3. The test runner is available
node --version || python3 --version
# Expected: prints a version. On failure → test-file generation is unaffected, but note to the user that local verification isn't possible.
```

## Workflow

### Step 1: Probe routes

Run the probe command for the corresponding framework (in the project root):

**Next.js App Router**
```bash
find ./app/api -name "route.ts" -o -name "route.js" | sort
grep -rn "export async function\|export function" app/api/**/route.ts | \
  grep -oE "(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)" | sort -u
find ./app/api -name "route.ts" | while read f; do
  route=$(echo $f | sed 's|./app||' | sed 's|/route.ts||')
  methods=$(grep -oE "export (async )?function (GET|POST|PUT|PATCH|DELETE)" "$f" | \
    grep -oE "(GET|POST|PUT|PATCH|DELETE)")
  echo "$methods $route"
done
```

**Express**
```bash
find ./src -name "*.ts" -o -name "*.js" | xargs grep -l "router\.\(get\|post\|put\|delete\|patch\)" 2>/dev/null
grep -rn "router\.\(get\|post\|put\|delete\|patch\)\|app\.\(get\|post\|put\|delete\|patch\)" \
  src/ --include="*.ts" | grep -oE "(get|post|put|delete|patch)\(['\"][^'\"]*['\"]"
grep -rn "router\.\|app\." src/ --include="*.ts" | \
  grep -oE "\.(get|post|put|delete|patch)\(['\"][^'\"]+['\"]" | \
  sed "s/\.\(.*\)('\(.*\)'/\U\1 \2/"
```

**FastAPI**
```bash
grep -rn "@app\.\|@router\." . --include="*.py" | \
  grep -E "@(app|router)\.(get|post|put|delete|patch)"
grep -rn "@\(app\|router\)\.\(get\|post\|put\|delete\|patch\)" . --include="*.py" | \
  grep -oE "@(app|router)\.(get|post|put|delete|patch)\(['\"][^'\"]*['\"]"
```

**Django REST Framework**
```bash
grep -rn "path\|re_path\|url(" . --include="*.py" | grep "urlpatterns" -A 50 | \
  grep -E "path\(['\"]" | grep -oE "['\"][^'\"]+['\"]" | head -40
grep -rn "router\.register\|DefaultRouter\|SimpleRouter" . --include="*.py"
```

- **Expected**: Output a route→HTTP-method mapping with at least one route.
- **On failure**: Output is empty → try the next framework's probe command; if all are empty → the project has no API routes; report and STOP.

### Step 2: Read route handlers

- **Action**: Read each route file and record: the request-body schema, auth requirements (middleware/decorator), return type and status code, and business rules (ownership/role checks).
- **Expected**: Each route has a record of the four items above; unknown items are flagged explicitly rather than assumed.
- **On failure**: A route file's handler logic can't be located → confirm the route's contract with the user before generating; don't write assertions from guesswork.

### Step 3: Generate tests by matrix

Generate an auth matrix for each authenticated endpoint, and an input-validation matrix for each POST/PUT/PATCH with a request body:

**Auth test matrix** (expected status codes):

| Test case | Expected status |
|-----------|-----------------|
| Missing Authorization header | 401 |
| Invalid token format | 401 |
| Valid token but wrong user role | 403 |
| Expired JWT token | 401 |
| Valid token and correct role | 2xx |
| Token for a deleted user | 401 |

**Input-validation matrix** (expected status codes):

| Test case | Expected status |
|-----------|-----------------|
| Empty body `{}` | 400 or 422 |
| Missing a required field (only one at a time) | 400 or 422 |
| Wrong type (string where an int is expected) | 400 or 422 |
| Boundary: min-1 | 400 or 422 |
| Boundary: min | 2xx |
| Boundary: max | 2xx |
| Boundary: max+1 | 400 or 422 |
| SQL injection in a string field | 400 or 200 (sanitized) |
| XSS payload in a string field | 400 or 200 (sanitized) |
| Required field passed as null | 400 or 422 |

Generation rules:
1. Descriptive test names: `"returns 401 when token is expired"`, not `"auth test 3"`
2. Build data with factories/fixtures; never hardcode IDs
3. Assert on the response structure, not just the status code
4. One describe block per endpoint
5. Sensitive fields (password/secret) must not appear in the response

- **Expected**: Each route group produces one test file; the matrix entries inside correspond one-to-one with the tables above.
- **On failure**: A matrix item can't be applied (e.g. the route has no auth) → delete that row and note the reason in a comment at the top of the file; don't leave an empty test.

### Step 4: Verify the artifacts

- **Action**: Run `node --test` / `npx vitest list` or `python3 -m pytest --collect-only <generated file>` to verify the syntax parses.
- **Expected**: The collect/test-list output includes all generated test names, with no syntax errors.
- **On failure**: A syntax error → fix the generated file and rerun collection; if it still fails → report that the generator output is faulty.

## Failure Handling Table

| Symptom / error code | Cause | Fix |
|---|---|---|
| Probe command output is empty | Wrong framework guess or no routes | Try all four framework probes in turn; if all are empty, STOP and report |
| pytest collect reports a SyntaxError | The generated file has a syntax error | Fix it and rerun `--collect-only` |
| Route contract is unclear | Handler logic is scattered / middleware is implicit | Confirm the contract with the user; guessing assertions is forbidden |
| Tests pollute each other | Shared state wasn't cleaned up | Clean up in afterEach/afterAll; run rate-limit tests last and separately |

## Delivery Criteria

- Definition of success: every scanned route has a corresponding test block; the auth/input-validation matrices land per the tables; step 4's collect passes.
- Artifact naming: one file per route group, e.g. `tests/test_<route-group>_api.py` or `__tests__/<route-group>.test.ts`.
- Save location: the project's test directory (`tests/` / `__tests__/`), or wherever the user specifies.
- Completeness verification: `--collect-only` (pytest) or `vitest list` (vitest) lists all test names, matching the generation list in count.

## References

- `references/example-test-files.md` — complete example test files for Vitest+Supertest and Pytest+httpx; read through it once before generating in step 3, and generate in its style.
