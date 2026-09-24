---
name: api-design-reviewer
description: "Comprehensive REST API design review with automated linting, breaking-change detection, and design scorecards. Catches inconsistent conventions, missing versioning, and design smells before APIs ship. Use when reviewing an API design, doing a REST endpoint design review, finding anti-patterns, reviewing a PR that adds or changes API endpoints, auditing an existing API for v2 migration, or establishing API standards for a team. Do NOT use for implementing API endpoints or generating client SDKs."
license: Apache-2.0
compatibility: Requires network access. No API keys required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: api
  pattern: code-reviewer
  tier: powerful
  verified-date: "2026-09-09"
---

# API Design Reviewer

Reviews REST API design with three tools — convention linting of the OpenAPI spec, breaking-change detection across versions, and an overall design-quality scorecard — then reports the findings together with the tools' output.

## Input Checklist

| Input | Required | Description |
|---|---|---|
| OpenAPI/Swagger spec (JSON) | Yes | Path to the current spec file, e.g. `openapi.json`; if there's no spec, use the built-in sample with `--sample` |
| Previous-version spec | Only for breaking-change detection | Path to the older spec to compare against the new one |
| Minimum passing grade | No | `api_scorecard.py --min-grade A\|B\|C\|D\|F`; defaults to no threshold |
| Output format | No | `--format text\|json`; use json for CI |

When inputs are missing, ask for all at once: "Please provide: (1) the path to the OpenAPI/Swagger JSON file to review; (2) if you want breaking-change detection, the path to the previous-version spec; (3) the minimum passing grade (defaults to B if left blank)."

## Pre-flight Checks

Run each in turn; on any failure → apply the fix, then STOP:

```bash
# 1. Python 3 is available
python3 --version
# Expected: Python 3.8+.

# 2. The three tool scripts exist
ls scripts/api_linter.py scripts/breaking_change_detector.py scripts/api_scorecard.py
# Expected: the three filenames (run inside the skill directory). On failure → cd to the skill directory and retry; if still missing → STOP and report.

# 3. The spec file is readable and valid JSON
python3 -c "import json,sys; json.load(open('<spec>'))" && echo OK
# Expected: OK. On failure → confirm the correct spec path/format with the user, STOP.
```

## Workflow

Run commands inside the skill directory (`skills/programming/api/api-design-reviewer/`). If there's no ready-made spec, use the bundled sample `examples/spec.json` (same source as the built-in `--sample`).

### Step 0: Try the built-in sample (optional)

```bash
python3 scripts/api_linter.py --sample   # when there's no spec, first use the built-in sample to get familiar with the output structure
```

### Step 1: Lint the spec

```bash
python3 scripts/api_linter.py examples/spec.json --format json --output lint.json   # swap in openapi.json for your real spec
```

- **Action**: Check resource naming (resources kebab-case, fields camelCase), HTTP-method usage, URL structure, status-code compliance, consistency of error-response structure, and documentation coverage.
- **Expected**: Produce `lint.json`; exit code 0 when there are no fatal items.
- **On failure**: The JSON contains per-violation details → organize each into a findings list (with file/path location) and report it together in step 3.

### Step 2: Breaking-change detection

```bash
python3 scripts/breaking_change_detector.py openapi-v1.json openapi-v2.json --format json --exit-on-breaking --output breaking.json
```

- **Action**: Compare the two spec versions; detect endpoint removal, response-structure changes, field deletion/renaming, type changes, newly required fields, and status-code changes, and give an impact severity.
- **Expected**: Exit code 0 (no breaking changes); or the breaking items are all covered by a version bump.
- **On failure**: `--exit-on-breaking` makes it exit non-zero when a breaking item is detected → list each breaking change in the report, marked "needs a version bump or rollback".

### Step 3: Design scoring

```bash
python3 scripts/api_scorecard.py examples/spec.json --format json --output scorecard.json   # add --min-grade B for gate mode (non-zero exit when below the threshold; the report is still output in full)
```

- **Action**: Five-dimensional scoring — Consistency 30%, Documentation 20%, Security 20%, Usability 15%, Performance 15%; output a 0-100 score and an A-F grade, plus improvement suggestions.
- **Expected**: Grade ≥ `--min-grade` (B in the example), exit code 0.
- **On failure**: Grade below the threshold → output the report but rule "not approved", with the improvement items from the scorecard attached.

### Step 4: Summarize the verdict

- **Action**: Report lint findings + breaking changes + grade to the user. Never sign off on a text-only review — the output of the three tools must accompany it.
- **Expected**: No lint violations (or all accepted), `--exit-on-breaking` passes (or breaking items version-bumped), grade ≥ the agreed threshold; with all three, rule "approved".
- **On failure**: After the user fixes the spec, rerun the whole flow from step 1.

## Parameter Quick Reference

| Parameter | Values | Description |
|---|---|---|
| `--format` | text / json | Output format; use json for CI |
| `--output` | file path | Write to a file (none of the three scripts has a `-o` short option; the full name must be used) |
| `--exit-on-breaking` | boolean | breaking_change_detector exits non-zero on a breaking item; use as a CI gate |
| `--min-grade` | A / B / C / D / F | api_scorecard exits non-zero below this grade; use as a CI gate |
| `--sample` | boolean | api_linter uses a built-in sample spec; no input file needed |
| `--raw-endpoints` | boolean | api_linter accepts a raw endpoint-list JSON instead of a full spec |

## Failure Handling Table

| Symptom / error code | Cause | Fix |
|---|---|---|
| `unrecognized arguments: -o` | A non-existent short option was used | Switch to `--output` |
| `json.decoder.JSONDecodeError` | The spec isn't JSON (maybe it's YAML) | Ask the user for a JSON-format spec or convert it first, STOP |
| Non-zero exit with no output file | A gate failure was detected (`--exit-on-breaking`/`--min-grade`) | Read the stdout/JSON report; this is normal gate behavior; handle per the findings |
| `FileNotFoundError` | Not running in the skill directory | `cd` to the skill directory, or use the script's absolute path |
| A breaking item can't be fixed | Upstream interface constraints | Report to the user for a decision: version bump, or accept and document it in writing |

## Delivery Criteria

- Definition of success: all three tools run to completion; the report includes the lint findings list, the breaking-changes list, and the grade/score; the verdict can only be "approved" or "not approved" (with the basis attached).
- Artifact naming: `lint.json`, `breaking.json`, `scorecard.json` (or names the user specifies).
- Save location: default current directory, or the output directory the user specifies.
- Completeness verification: all three files parse with `json.load` and are non-empty; the report cites each file's `overall_score`/grade verbatim.

## References

- `references/rest_design_rules.md` — the full rule set for REST naming, methods, status codes, pagination, and error formats; read when interpreting lint violations or answering "how should this be fixed".
- `references/api_antipatterns.md` — common anti-patterns and fixes; read when lint hits many or the user asks to "find anti-patterns".

## CI Integration

```yaml
- name: "api-linting"
  run: python scripts/api_linter.py openapi.json --output lint.json

- name: "breaking-change-detection"
  run: python scripts/breaking_change_detector.py openapi-v1.json openapi-v2.json --exit-on-breaking

- name: "api-scorecard"
  run: python scripts/api_scorecard.py openapi.json --min-grade B
```
