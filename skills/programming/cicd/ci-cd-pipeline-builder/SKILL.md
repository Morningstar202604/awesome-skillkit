---
name: ci-cd-pipeline-builder
description: "Generate pragmatic CI/CD pipelines from detected project stack signals — fast baseline generation, repeatable checks, environment-aware deployment stages. Use when setting up CI for a new project, building a CI/CD pipeline, configuring automated build and deployment, refactoring existing pipelines, or standardizing deployment workflows across multiple repos. Do NOT use for debugging an existing pipeline on a live runner."
license: Apache-2.0
compatibility: Pure prompt-based; runs Python stdlib scripts via Bash. No API keys required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: cicd
  pattern: pipeline-builder
  tier: powerful
  verified-date: "2026-09-09"
---

# CI/CD Pipeline Builder

Generates pragmatic CI/CD pipelines from detected project-stack signals (not guesswork): first probe the tech stack, then emit a GitHub Actions or GitLab CI baseline YAML with caching and matrix strategies, validated before merge.

## Input Checklist

| Input | Required | Description |
|---|---|---|
| Repo path | Yes | Project root to generate the pipeline for, e.g. `.` |
| CI platform | Yes | github / gitlab (sets `--platform`; the scripts support only these two) |
| Output path | No | GitHub defaults to writing `ci.yml` under `.github/workflows/`; GitLab defaults to `.gitlab-ci.yml` |
| Stack-detection report | No | If you already have `detected-stack.json`, pass it via `--input` to skip re-detection |

When inputs are missing, ask for all at once: "Please provide: (1) repo path; (2) target platform (GitHub Actions or GitLab CI); (3) whether you have an already-generated detection report to reuse."

## Pre-flight Checks

Run line by line; on any failure → fix per the remediation and STOP:

```bash
# 1. Python 3 is available
python3 --version
# Expected: Python 3.8+.

# 2. Both tool scripts exist
ls scripts/stack_detector.py scripts/pipeline_generator.py
# Expected: both filenames (run inside the skill directory). On failure: cd to the skill directory; still missing → STOP and report.

# 3. The target repo exists and contains stack signals
ls <repo path>/package.json <repo path>/requirements.txt <repo path>/pyproject.toml <repo path>/go.mod <repo path>/Cargo.toml 2>/dev/null
# Expected: at least one file. All empty → confirm the project type, otherwise detection finds nothing, STOP.
```

## Workflow

### Step 1: Detect the tech stack

```bash
python3 scripts/stack_detector.py --repo . --format text
python3 scripts/stack_detector.py --repo . --format json > detected-stack.json
```

- **Action**: probe the language/runtime/toolchain from repo files (lockfiles, manifests, configs); `--input` or stdin can feed a precomputed signals JSON for offline analysis.
- **Expected**: text mode prints a readable stack summary; json mode produces `detected-stack.json`.
- **On failure**: the output is empty → the repo has no known signal files; confirm the project type with the user, then STOP.

### Step 2: Generate the pipeline

```bash
# Generate from a detection report (recommended; two-step so it's reviewable)
python3 scripts/pipeline_generator.py \
  --input detected-stack.json \
  --platform github \
  --output .github/workflows/ci.yml \
  --format text

# Or generate end-to-end from the repo directly
python3 scripts/pipeline_generator.py --repo . --platform gitlab --output .gitlab-ci.yml
```

- **Action**: per the detection result, emit YAML with `lint`/`test`/`build` stages and caching/matrix strategies; without `--output`, print to stdout.
- **Expected**: valid YAML is generated at the target path, containing the detected build/test commands.
- **On failure**: it reports `--platform` missing → that parameter is required (choose github/gitlab); the YAML is empty → the detection report has no signals; rerun Step 1.

### Step 3: Validate before merge

1. Confirm the commands referenced in the YAML (`test`/`lint`/`build`) actually exist in the project's build definitions (package.json scripts, Makefile targets).
2. Reproduce the pipeline commands locally as far as possible (e.g. `npx act` or run the scripts one by one).
3. Confirm the required secrets/env vars are listed in YAML comments or docs.
4. Confirm the deploy job triggers only from protected branches/environments.

- **Expected**: all four checks pass; any referenced command that doesn't exist is a FAIL.
- **On failure**: the command doesn't exist → regenerate with the project's real commands (rerun Step 2); don't hand-write placeholder commands.

### Step 4: Add deployment stages safely

- **Action**: evolve in order: CI-only first (lint/test/build) → add a staging deployment (explicit environment) → add a production deployment (manual-approval gate); keep rollout/rollback commands explicit and auditable. See `references/deployment-gates.md` for deployment details and gate patterns.
- **Expected**: after each evolution the YAML still passes the four checks in Step 3.
- **On failure**: the user asks to go straight to production deploy with no gate → explain the risk (automatic release without human approval); insist on keeping a manual gate or get written confirmation.

## Parameter Cheat Sheet

| Parameter | Values | Description |
|---|---|---|
| `--repo` | directory path | The repo to scan |
| `--input` | JSON file | Precomputed stack-detection report (offline analysis) |
| `--format` | text / json | Output format |
| `--platform` | github / gitlab | Required; target CI platform |
| `--output` | file path | Where the YAML is written; defaults to stdout |

## Platform Decision Quick Reference

| Factor | GitHub Actions | GitLab CI | Jenkins |
|--------|---------------|-----------|---------|
| **Setup** | YAML in .github/workflows | YAML in .gitlab-ci.yml | Groovy/Jenkinsfile |
| **Runners** | GitHub-hosted, self-hosted | Shared / group / project-level | Self-hosted |
| **Secrets** | Repo/environment variables | CI/CD Variables | Credentials plugin |
| **Caching** | actions/cache | cache key/tag | Workspace cleanup |
| **Matrix** | strategy.matrix | parallel:matrix | Matrix Authorization |

## Failure Handling Table

| Symptom / error code | Cause | Fix |
|---|---|---|
| `error: the following arguments are required: --platform` | No platform specified at generation | Add `--platform github\|gitlab` |
| Detection output empty | The repo has no known signal files | Confirm the project type with the user; still empty after confirming → STOP |
| The YAML references non-existent commands | Detection signals don't match the actual scripts | Regenerate with the project's real commands |
| The output path's directory doesn't exist | `.github/workflows/` not created | `mkdir -p` and rerun, or confirm the path with the user |

## Delivery Criteria

- Definition of success: both `detected-stack.json` (if two-step) and the target-platform YAML are generated, and all four Step 3 checks pass.
- Artifact naming: GitHub → write `ci.yml` under `.github/workflows/`; GitLab → `.gitlab-ci.yml`; the detection report `detected-stack.json`.
- Save location: the corresponding path inside the target repo (confirm with the user before writing).
- Completeness verification: the YAML parses without error via `python3 -c "import yaml,sys; yaml.safe_load(open(sys.argv[1]))" <file>` (or `npx js-yaml <file>`).

## References

- `references/pipeline-design-notes.md` — detection heuristics, generation strategy, platform trade-offs, pre-merge validation checklist, extension guidance; read when interpreting detection results or customizing the pipeline.
- `references/github-actions-templates.md` — GitHub Actions templates; read when you need advanced config after generating the GitHub YAML.
- `references/gitlab-ci-templates.md` — GitLab CI templates; read when you need advanced config after generating the GitLab YAML.
- `references/deployment-gates.md` — deployment gates and rollback patterns; read when executing Step 4.
