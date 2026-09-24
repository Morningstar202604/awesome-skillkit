---
name: ship-gate
description: "Pre-production audit that scans a codebase for security, database, deployment, code quality, AI/LLM, dependency, frontend, and observability issues. Intercepts deploy commands and blocks until critical items pass. Use when doing a pre-launch check, a release gate, pre-release review, a launch check, a pre-release audit, or a deployment gate. Also triggers on / pre-deploy audit / release checklist. Do NOT use for fixing the failures it reports (this skill only gates and reports)."
license: Apache-2.0
compatibility: Pure prompt-based; runs Python stdlib scanner via Bash. No API keys required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: cicd
  pattern: single-task
  tier: powerful
  verified-date: "2026-09-09"
---

# Ship Gate

A pre-production audit: scan the codebase across 8 categories, giving a PASS/FAIL/MANUAL verdict per item. Automated checks run via a built-in scanner; items that can't be verified automatically become a manual-confirmation checklist. This skill only audits and reports — it doesn't fix.

## Interception Behavior

When the user says "push to production", "deploy", "ship it", "go live", or similar deployment intent, don't deploy directly. Instead:

1. Ask: "Have you run the ship gate? Want me to scan it now?"
2. If the user agrees → run the workflow below.
3. If the user says it's already been run → ask when. If it was over 24 hours ago, or the code changed since then → recommend rerunning.

## Input Checklist

| Input | Required | Description |
|---|---|---|
| Project root | No | Defaults to the current directory |
| Scan category | No | One of the 8 (SEC/DB/CODE/DEP/AI/DEPLOY/FE/OBS); defaults to all |
| Output format | No | Human-readable (default, colored) or `--json` |
| Interactive confirmation | No | Defaults to interactively asking about manual items; add `--no-interactive` for CI |

When inputs are missing, ask for all at once: "Please provide: (1) project root (blank = current directory); (2) a full scan or just one category."

## Pre-flight Checks

```bash
# 1. Python 3 is available
python3 --version
# Expected: Python 3.8+. On failure: install and retry, STOP.

# 2. The scanner exists
ls scripts/ship_gate_scanner.py
# Expected: the filename (run inside the skill directory). On failure: cd to the skill directory; still missing → STOP and report.

# 3. The target project directory exists
ls <project root> > /dev/null && echo OK
# Expected: OK. On failure: confirm the path with the user, STOP.

# 4. The checks and patterns library are in place
ls references/checks.md references/patterns.md
# Expected: both filenames. Missing → STOP and report an incomplete repo.
```

## Workflow

### Step 1: Full scan

```bash
python3 scripts/ship_gate_scanner.py examples/sample-frontend --json --no-interactive --category FE   # bundled compliant sample (all FE items pass as ADVISORY → CLEAR_TO_SHIP rc=0); for a full audit on a real project drop --category; a non-zero exit on non-compliance is the CI gate semantics
```

- **Action**: the scanner auto-detects the tech stack (framework, database, deployment target, auth, AI/LLM SDK — detection rules live in the scanner and link to the stack-tagged checks in `references/checks.md`), then runs all automated checks in order SEC → DB → CODE → DEP → AI → DEPLOY → FE → OBS.
- **Expected**: produce a JSON report with PASS/FAIL/SKIP per category check and file locations; exit code 0/1/2 (see the failure table for meanings).
- **On failure**: the scanner errors out → read the error message; the target directory is inaccessible → confirm the path with the user, then STOP.

### Step 2: Manual-confirmation items

- **Action**: list the checks automation can't cover (backup restore rehearsed, rollback plan exists, staging tests passed, monitoring/alerts wired, etc.) one by one, and ask the user yes/no/unknown for each.
- **Expected**: each item gets an explicit answer and is recorded; unknown always counts as not-passing.
- **On failure**: the user refuses to answer → mark that item MANUAL/unconfirmed and move to adjudication.

### Step 3: Adjudication

- **Action**: grade the results by severity and give a verdict:
  - **CRITICAL** (must fix): secret exposure, routes without auth, no HTTPS, SQL-injection vectors, Supabase tables without RLS
  - **HIGH** (should fix): no error boundary, no rate limiting, console.log in production code, no pagination
  - **ADVISORY** (suggested): no OG tags, no custom 404, no analytics, no SBOM
- **Verdict rule**: any unresolved CRITICAL → `DO NOT SHIP`; only HIGHs remain → `SHIP WITH CAUTION` (requires the user's written acknowledgment of the risk); zero CRITICAL and manual items pass → `CLEAR TO SHIP`.
- **Expected**: output a report like this (with real file locations and line numbers):

```text
SHIP GATE REPORT
================
Stack: Next.js + Supabase + Vercel
Scan time: 12s

CRITICAL (3 items, must fix)
  FAIL  [SEC-01] API key found in src/lib/api.ts:14
  FAIL  [DB-07] RLS not enabled on "profiles" table

HIGH (2 items, should fix)
  FAIL  [DEP-04] 3 critical npm audit vulnerabilities
  MANUAL [DEPLOY-06] Staging test not confirmed

ADVISORY (1 item, recommended)
  FAIL  [FE-01] Missing OG meta tags

VERDICT: DO NOT SHIP (2 critical issues)
Fix critical items and re-run.
```

- **On failure**: the verdict is DO NOT SHIP → report, then STOP; this skill doesn't fix; hand off to the user or another skill to fix and rescan.

### Step 4: Rescan and release

- **Action**: after fixes, rerun Step 1 (full scan, not incremental), and confirm last round's CRITICAL items all turned PASS.
- **Expected**: exit code 0, report `VERDICT: CLEAR TO SHIP`.
- **On failure**: CRITICALs remain → return to Step 3 for adjudication; never release.

## The Eight Categories

| Prefix | Category | Description |
|--------|----------|------|
| SEC | Security | Secret leakage, missing auth, injection vectors, CSRF, HTTPS |
| DB | Database | RLS, backups, migration safety, connection security |
| DEPLOY | Deployment | Rollback plan, staging validation, environment config |
| CODE | Code quality | console.log, empty catch, error boundaries |
| AI | AI/LLM security | API key management, prompt-injection surface, output filtering |
| DEP | Dependencies | npm audit critical vulnerabilities, SBOM |
| FE | Frontend quality | OG tags, 404 page, error pages |
| OBS | Observability | Error monitoring, logging, alerting |

See `references/checks.md` for the full definition of every check, and `references/patterns.md` for the scan patterns (grep rules).

## Scope

This skill only audits; it doesn't fix. When it finds problems, it reports them with file locations and fix suggestions; fixing is done by the user or other skills (systematic-debugging, backend-patterns, shadcn-stack).

This skill does NOT:

- Set up CI/CD pipelines
- Provision infrastructure
- Configure monitoring tools
- Run things after deployment (this skill is used only before deployment)

## Parameter Cheat Sheet

| Parameter | Values | Description |
|---|---|---|
| `path` | directory (positional) | Project root; defaults to the current directory |
| `--json` | boolean | JSON output for programmatic consumption |
| `--no-color` | boolean | Disable ANSI colors |
| `--no-interactive` | boolean | Skip the manual-confirmation interaction (required in CI) |
| `--category` | SEC/DB/CODE/DEP/AI/DEPLOY/FE/OBS | Run a single category only |
| `--verbose` | boolean | Also show PASS items |

## Failure Handling Table

| Symptom / error code | Cause | Fix |
|---|---|---|
| Exit code 1 | Critical problems found | Adjudicate DO NOT SHIP, report each item, STOP |
| Exit code 2 | Only high-level problems | Adjudicate SHIP WITH CAUTION, list risks for the user's written confirmation |
| Exit code 0 | No critical problems | May enter the CLEAR TO SHIP flow; still check the manual-confirmation items |
| Scanner crash/traceback | Abnormal target-dir structure or insufficient permissions | Read the traceback to locate it; for permission issues retry in another directory |
| All manual items unknown | The user didn't cooperate | Count them all as not-passing; don't relax the verdict |

## Delivery Criteria

- Definition of success: output includes real stack detection, 8-category PASS/FAIL/SKIP stats, graded details (file + line number), and an explicit three-way VERDICT.
- Artifact naming: in-conversation report `SHIP GATE REPORT`; archival `ship-gate-report-<YYYYMMDD>.json` (`--json` output).
- Save location: delivered in-conversation; archives go to a user-specified directory.
- Completeness verification: every FAIL in the report has a `[CATEGORY-NUMBER]` + file location; the VERDICT matches the CRITICAL/HIGH counts.

## References

- `references/checks.md` — definitions of all checks (with applicable stack tags); read when interpreting a FAIL or checking the scope of manual items.
- `references/patterns.md` — the scan-pattern library; read when you need to explain to the user how an item was detected.

## Related Skills

- **karpathy-coder**: run ship-gate after the karpathy-check passes — keep it simple first, then go to production
- **adversarial-reviewer**: deep security review of the issues ship-gate judges critical
- **security-pen-testing**: penetration-testing methodology for SEC findings
- **code-reviewer**: general code-quality review, complementary to ship-gate's automated checks
