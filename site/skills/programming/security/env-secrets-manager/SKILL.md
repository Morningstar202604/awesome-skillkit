---
name: env-secrets-manager
description: >-
  Manage environment-variable hygiene and secrets safety across local development and production. Triggers on "audit .env", "secrets scan", "check for leaked keys", "rotate credentials", "env file hygiene", "committed secrets", "detect-secrets or gitleaks setup", "missing env var incident". Practical auditing, drift awareness, rotation readiness. Use when auditing .env files for committed secrets, planning a credential rotation, debugging missing-env-var production incidents, hardening a new project against secrets leakage, managing environment variables, auditing secrets, checking .env leaks, or preparing for rotation. Do NOT use for reading or printing secret values (hygiene checks only); production vault infrastructure and rotation execution live in secrets-vault-manager.
license: Apache-2.0
compatibility: Pure prompt-based; may read project structure via Bash.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: security
  pattern: workflow
  tier: expert
  verified-date: "2026-09-09"
---

# Env & Secrets Manager

Manages environment-variable hygiene and secret safety across local development and production flows. This skill focuses on hands-on auditing, drift awareness, and rotation readiness.

## Core Capabilities

- Lifecycle guidance for `.env` and `.env.example`
- Secret-leak detection across the repo working tree (`scripts/env_auditor.py`)
- Severity-tiered reporting of suspected credentials
- Practical guidance for rotation and stop-the-bleeding
- Ready-to-consume output for CI checks

## When to Use

- Before pushing commits that touch env/config files
- During security audits and incident triage
- Onboarding new contributors to safe env conventions
- Verifying no obvious secrets are hard-coded

## When Not to Use

- Reading or printing secret values — only hygiene checks; every finding is redacted
- Production vault infrastructure, rotation execution, audit-log backends, HA/DR → `secrets-vault-manager`

## Input Checklist

Collect everything before scanning. When inputs are missing, ask the user once with this line: "To audit for secret leaks, please provide all at once: the repo-root path, whether you need CI-friendly JSON output, and whether you already have a .secrets.baseline / .gitleaksignore."

| Input | Required | Description |
|---|---|---|
| Repo / project root | Yes | Scan path → the positional argument to `env_auditor.py` |
| Output format | No | text (default) or `--json` for CI pipelines |
| Scan size cap | No | `--max-filesize <KB>`; large generated files slow the scan |
| Existing baseline/ignore file | For false-positive triage | `.secrets.baseline` (detect-secrets) and/or `.gitleaksignore` (gitleaks), committed to version control |

## Pre-flight Checks

```bash
python3 --version        # Expected: Python ≥ 3.8. The audit script depends only on the standard library.
ls scripts/env_auditor.py
                         # Expected: the file is listed.
test -d <repo-root> && echo ok
                         # Expected: ok — the target repo exists.
```

- Python missing or too old → install Python ≥ 3.8, then stop.
- Script missing → wrong directory; `cd` to this skill's directory and re-check, then stop.
- Target repo does not exist → confirm the path with the user before scanning; do not scan the wrong tree.

## Quick Start

```bash
# Scan the repo for suspected secret leaks (output is redacted)
python3 scripts/env_auditor.py assets/sample-repo   # bundled sample repo (placeholder keys + correct .gitignore); swap in your real project root

# JSON output for CI pipelines
python3 scripts/env_auditor.py assets/sample-repo --json
```

## Workflow

### Step 1: Scan the working tree

- **Action:** `python3 scripts/env_auditor.py <repo-root>` (add `--json` for CI).
- **Expected:** a `=== ENV AUDITOR ===` header, a `Findings: N (critical=x, high=y, ...)` summary line, and each finding with `file:line` and a **redacted** excerpt (e.g. `sk-F...(30 chars)`); exit code 0 even with findings.
- **On failure:** output shows `usage: env_auditor.py ...` → the missing repo-path positional argument; 0 findings → confirm you scanned the target root, not a subdirectory.

### Step 2: Triage by severity

- **Action:** handle in order `critical` → `high` → `medium`/`low`; for each finding decide whether it is a real credential, a test fixture, or a false positive.
- **Expected:** each finding labeled real / test-fixture / false-positive.
- **On failure:** if you can't tell whether a value is real → treat it as real until proven otherwise; never print the value to decide (the auditor's redacted excerpt is enough to locate it).

### Step 3: Rotate real credentials and purge the exposed value

- **Action:** rotate on the provider side first, then remove the value from the working tree and history; update `.env.example` to an empty placeholder and confirm `.gitignore` covers `.env`.
- **Expected:** the old credential is revoked on the provider side; the working tree holds only placeholders.
- **On failure:** the value is already in git history → deleting the file is not enough; the credential must be rotated regardless, and rewriting history is a separate decision to confirm explicitly with the user.

### Step 4: Record rotation metadata

- **Action:** annotate each credential with `# ROTATED: <date>` and expiry metadata; maintain a consumer list for each key (which services read it).
- **Expected:** each key has a rotation-date comment and a list of known consumers.
- **On failure:** a key's consumers are unknown → do not rotate blindly; inventory consumers first, or the rotation will break them.

### Step 5: Add CI/pre-commit gates

- **Action:** wire gitleaks or detect-secrets into pre-commit and CI (config below); rerun `env_auditor.py` and `gitleaks detect` / `detect-secrets scan` until clean.
- **Expected:** the gate can catch a planted test secret; the current working tree scans clean.
- **On failure:** a gate passes despite known real keys → the rule set is too narrow; add rules rather than ignoring files.

## Failure Handling Table

| Symptom / exit code | Cause | Fix |
|---|---|---|
| `usage: env_auditor.py [-h] [--json] ...` | Missing repo-path positional argument | Pass the repo root as the first argument |
| Reports 0 findings despite a known leak | Scanned the wrong root, or files exceed the size cap | Rerun from the correct root; raise `--max-filesize` |
| Findings in `tests/` or fixtures | Intentional test credentials | Verify they are indeed fake; ensure they don't reach production config and record them in the baseline |
| `.env.example` contains values that look real | The example file was filled with real config | Treat as a leak: rotate, replace with an empty placeholder |
| Downstream services break after rotation | Unknown consumers | Use the provider's overlap window to recover (if supported), complete the consumer list, and rotate again |
| A secret printed into CI logs during debugging | A log statement printed the env | Redact/remove that log line; rotate the printed value |
| Flood of gitleaks false positives | Default rules are too broad for this stack | Tighten the regex or add `.gitleaksignore` fingerprints — never ignore whole files by default |

## Pre-commit Secret Detection

Catching secrets before they enter version control is the highest-leverage defense. Two mainstream tools cover this space.

### gitleaks

```toml
# .gitleaks.toml — minimal configuration
[extend]
useDefault = true

[[rules]]
id = "custom-internal-token"
description = "Internal service token pattern"
regex = '''INTERNAL_TOKEN_[A-Za-z0-9]{32}'''
secretGroup = 0
```

- Install: `brew install gitleaks` or download from GitHub releases.
- Pre-commit hook: `gitleaks git --pre-commit --staged`
- Baseline scan: `gitleaks detect --source . --report-path gitleaks-report.json`
- False positives are managed in `.gitleaksignore` (one fingerprint per line).

### detect-secrets

```bash
# Generate baseline
detect-secrets scan --all-files > .secrets.baseline

# Pre-commit hook (via pre-commit framework)
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.5.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
```

- Supports writing **custom plugins** for organization-specific patterns.
- Audit flow: `detect-secrets audit .secrets.baseline`, interactively marking true/false positives.

### False-positive management

- Commit `.gitleaksignore` or `.secrets.baseline` to version control so the whole team shares the exclusions.
- Re-review the false-positive list during security audits — exclusion patterns can mask real leaks over time.
- Prefer tightening the regex over broadly ignoring files.

## Rotation Readiness (Detection Side Only)

Deep rotation execution — provider automation, dynamic secrets, emergency runbooks — belongs to **secrets-vault-manager**. This skill covers the readiness side:

- Record creation/expiry metadata next to each credential.
- Set reminders at 30, 14, and 7 days before expiry.
- Run `scripts/env_auditor.py` and flag keys lacking a rotation-date comment (`# ROTATED: <date>`).
- Maintain a consumer list for each key so the rotation blast radius is known before it's needed.

> **Cross-reference:** for production vault infrastructure, cloud secret-store selection (Vault / AWS Secrets Manager / Azure Key Vault / GCP Secret Manager), rotation execution flows, audit-log backends, and disaster recovery, see `secrets-vault-manager`.

## CI/CD Secret Injection (Key Points)

- Prefer **OIDC federation / short-lived tokens** over long-lived access keys.
- Never echo or print secret values in pipeline output; rely on platform masking, but don't go test it.
- Don't expose secrets to pipelines triggered by untrusted forks.
- Pipeline architecture patterns → `ci-cd-pipeline-builder`; vault-backed injection → `secrets-vault-manager`.

## Audit Logging (Key Points)

Who accessed which secret and when is vault territory — cloud-native audit trails (CloudTrail / Activity Log / Cloud Audit Logs / Vault audit backend), bulk-read alerting, and SIEM integration are covered by `secrets-vault-manager`. The local equivalent requirement: `.env` values must not end up in shell history or CI logs.

## Common Pitfalls

- Committing real values in `.env.example`
- Rotating one system but missing downstream consumers
- Logging secrets during debugging or incident response
- Treating a suspected leak as low priority without verification

## Best Practices

1. Use a secret manager as the single source of truth in production.
2. Keep dev env files local and gitignored.
3. Enforce detection in CI before merge.
4. Re-test the application path immediately after credential rotation.

## References

Read only when the corresponding situation arises:

- `references/secret-patterns.md` — when triaging what a finding matched (which credential shapes the auditor detects) or writing custom detection rules.
- `references/validation-detection-rotation.md` — when deciding whether a finding is an active credential or planning a rotation-readiness checklist.

## Asset Templates

- `assets/sample_env_leak.env` — a sample file with "fake-but-realistic" credential shapes; before trusting a clean result, use it to verify the auditor hits your patterns.

## Cross-References

| Skill | Relationship |
|-------|-------------|
| **Secrets Vault Manager** (`secrets-vault-manager`) | Production vault infrastructure, rotation execution, audit logs, HA/DR |
| **CI/CD Pipeline Builder** (`ci-cd-pipeline-builder`) | Pipeline architecture, secret injection patterns |

## Delivery Criteria

This skill counts as done only when:

- The audit report is saved beside the repo (or in a secure workspace) as `env_audit_<repo>_<date>.json` (via `--json`); raw findings are never pasted into tickets unredacted.
- Every finding is closed out as one of: rotated+removed, false positive added to baseline, or test fixture documented.
- `.env.example` contains only placeholders; `.gitignore` covers `.env`; every credential has rotation metadata (`# ROTATED: <date>`).
- Completeness verification: `python3 scripts/env_auditor.py <repo-root>` reports 0 critical/high on the current working tree; the pre-commit/CI gate can catch a planted test secret.
- Ongoing requirement: rotation reminders at 30/14/7 days before expiry actually fire; each key's consumer list stays current.
