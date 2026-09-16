---
name: env-secrets-manager
description: "Manage environment-variable hygiene and secrets safety across local development and production. Triggers on "audit .env", "secrets scan", "check for leaked keys", "rotate credentials", "env file hygiene", "committed secrets", "detect-secrets or gitleaks setup", "missing env var incident". Practical auditing, drift awareness, rotation readiness. Use when auditing .env files for committed secrets, planning a credential rotation, debugging missing-env-var production incidents, or hardening a new project against secrets leakage. 当用户要求 管理环境变量 / 密钥审计 / 检查 .env 泄露 / 轮换准备 时使用。 Do NOT use for reading or printing secret values (hygiene checks only); production vault infrastructure and rotation execution live in secrets-vault-manager."
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

Manage environment-variable hygiene and secrets safety across local development and production workflows. This skill focuses on practical auditing, drift awareness, and rotation readiness.

## Core capabilities

- `.env` and `.env.example` lifecycle guidance
- Secret leak detection for repository working trees (`scripts/env_auditor.py`)
- Severity-based findings for likely credentials
- Operational pointers for rotation and containment
- Integration-ready outputs for CI checks

## When to use

- Before pushing commits that touched env/config files
- During security audits and incident triage
- When onboarding contributors who need safe env conventions
- When validating that no obvious secrets are hardcoded

## When NOT to use

- Reading or printing secret values — hygiene checks only; findings are redacted
- Production vault infrastructure, rotation execution, audit-log backends, HA/DR → `secrets-vault-manager`

## Input checklist

Collect once before scanning. If inputs are missing, ask the user once with: "要审计密钥泄露，请一次性提供：仓库根目录路径、是否需要 CI 用的 JSON 输出、是否已有 .secrets.baseline / .gitleaksignore。"

| Input | Required | Description |
|---|---|---|
| Repo / project root | Yes | path to scan → positional arg of `env_auditor.py` |
| Output format | No | text (default) or `--json` for CI pipelines |
| Scan size cap | No | `--max-filesize <KB>`; large generated files slow the scan |
| Existing baseline/ignore files | For false-positive triage | `.secrets.baseline` (detect-secrets) and/or `.gitleaksignore` (gitleaks), kept in version control |

## Pre-flight checks

```bash
python3 --version        # Expected: Python ≥ 3.8. The auditor is stdlib-only.
ls scripts/env_auditor.py
                         # Expected: file listed.
test -d <repo-root> && echo ok
                         # Expected: ok — the target repo exists.
```

- Python missing/outdated → install Python ≥ 3.8, then STOP.
- Script missing → wrong directory; `cd` to this skill's directory and re-check, then STOP.
- Target repo missing → confirm the path with the user before scanning; do not scan the wrong tree.

## Quick start

```bash
# Scan a repository for likely secret leaks (output is redacted)
python3 scripts/env_auditor.py /path/to/repo

# JSON output for CI pipelines
python3 scripts/env_auditor.py /path/to/repo --json
```

## Workflow

### Step 1: Scan the working tree

- **Action:** `python3 scripts/env_auditor.py <repo-root>` (add `--json` for CI).
- **Expected:** a `=== ENV AUDITOR ===` header, a `Findings: N (critical=x, high=y, ...)` summary line, and per-finding lines with `file:line` and a **redacted** excerpt (e.g. `sk-F...(30 chars)`); exit 0 even with findings.
- **If it fails:** `usage: env_auditor.py ...` → the repo path positional arg is missing; empty findings with 0 total → confirm you scanned the intended root, not a subdirectory.

### Step 2: Triage by severity

- **Action:** work `critical` → `high` → `medium`/`low`; for each finding decide: real credential, test fixture, or false positive.
- **Expected:** every finding labeled real / test-fixture / false-positive.
- **If it fails:** can't tell if a value is real → treat as real until proven otherwise; never print the value to decide (the auditor's redacted excerpt is enough to locate it).

### Step 3: Rotate real credentials and remove exposed values

- **Action:** rotate at the provider first, then remove the value from the working tree and history; update `.env.example` with empty placeholders and confirm `.gitignore` covers `.env`.
- **Expected:** provider-side old credential revoked; working tree contains only placeholders.
- **If it fails:** value already in git history → deleting the file is not enough; the credential must be rotated regardless, and history rewriting is a separate explicit decision with the user.

### Step 4: Record rotation metadata

- **Action:** annotate each credential with `# ROTATED: <date>` and expiry metadata; keep a consumer inventory per secret (which services read it).
- **Expected:** every secret has a rotation date comment and a known consumer list.
- **If it fails:** a secret has unknown consumers → do not rotate blind; inventory consumers first or the rotation breaks them.

### Step 5: Add CI/pre-commit gates

- **Action:** wire gitleaks or detect-secrets into pre-commit and CI (configs below); re-run `env_auditor.py` and `gitleaks detect` / `detect-secrets scan` until clean.
- **Expected:** gate blocks a planted test secret; clean run on the current tree.
- **If it fails:** gate passes with a known-real secret present → pattern set too narrow; add a rule rather than ignoring the file.

## Failure handling

| Symptom / exit code | Cause | Fix |
|---|---|---|
| `usage: env_auditor.py [-h] [--json] ...` | repo path positional arg missing | pass the repo root as the first argument |
| 0 findings on a tree you know leaks | scanned wrong root, or file exceeds size cap | re-run from the correct root; raise `--max-filesize` |
| Finding in `tests/` or fixtures | intentional test credentials | verify they are truly fake; keep out of production configs and document in the baseline |
| `.env.example` contains real-looking values | example file was filled with live config | treat as a leak: rotate, replace with empty placeholders |
| Rotated credential breaks a downstream service | unknown consumer | restore from overlap window (if provider allows), complete the consumer inventory, re-rotate |
| Secret echoed into CI logs while debugging | log statement prints env | redact/remove the log line; rotate the printed value |
| gitleaks flood of false positives | default rules too broad for the stack | tighten regex or add `.gitleaksignore` fingerprints — never ignore whole files by default |

## Pre-commit secret detection

Catching secrets before they reach version control is the most cost-effective defense. Two leading tools cover this space.

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
- Baseline scanning: `gitleaks detect --source . --report-path gitleaks-report.json`
- Manage false positives in `.gitleaksignore` (one fingerprint per line).

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

- Supports **custom plugins** for organization-specific patterns.
- Audit workflow: `detect-secrets audit .secrets.baseline` interactively marks true/false positives.

### False positive management

- Maintain `.gitleaksignore` or `.secrets.baseline` in version control so the whole team shares exclusions.
- Review false positive lists during security audits — patterns may mask real leaks over time.
- Prefer tightening regex patterns over broadly ignoring files.

## Rotation readiness (detection only)

Deep rotation execution — provider automation, dynamic secrets, emergency checklists — belongs to **secrets-vault-manager**. This skill covers the readiness half:

- Record creation/expiry metadata next to every credential.
- Set alerts at 30, 14, and 7 days before expiry.
- Run `scripts/env_auditor.py` to flag secrets with no recorded rotation date/comment (`# ROTATED: <date>`).
- Maintain a consumer inventory per secret so rotation blast radius is known before you need it.

> **Cross-reference:** for production vault infrastructure, cloud secret store selection (Vault / AWS Secrets Manager / Azure Key Vault / GCP Secret Manager), rotation execution workflows, audit-log backends, and disaster recovery, see `secrets-vault-manager`.

## CI/CD secret injection (pointers)

- Prefer **OIDC federation / short-lived tokens** over long-lived access keys.
- Never echo or print secret values in pipeline output; rely on platform masking but don't test it.
- Do not expose secrets to pipelines triggered by untrusted forks.
- Pipeline architecture patterns → `ci-cd-pipeline-builder`; vault-backed injection → `secrets-vault-manager`.

## Audit logging (pointer)

Who accessed which secret and when is vault territory — cloud-native audit trails (CloudTrail / Activity Log / Cloud Audit Logs / Vault audit backend), bulk-read alerting, and SIEM feeds are covered in `secrets-vault-manager`. Local equivalent: keep `.env` values out of shell history and CI logs.

## Common pitfalls

- Committing real values in `.env.example`
- Rotating one system but missing downstream consumers
- Logging secrets during debugging or incident response
- Treating suspected leaks as low urgency without validation

## Best practices

1. Use a secret manager as the production source of truth.
2. Keep dev env files local and gitignored.
3. Enforce detection in CI before merge.
4. Re-test application paths immediately after credential rotation.

## References

Read the reference only when the corresponding situation applies:

- `references/secret-patterns.md` — read when triaging what a finding matched (which credential shapes the auditor detects) or writing custom detection rules.
- `references/validation-detection-rotation.md` — read when validating whether a finding is a live credential or when planning the rotation-readiness inventory.

## Asset templates

- `assets/sample_env_leak.env` — sample file containing fake-but-realistic credential shapes; usable to verify the auditor detects your patterns before trusting a clean run.

## Cross-references

| Skill | Relationship |
|-------|-------------|
| **Secrets Vault Manager** (`secrets-vault-manager`) | Production vault infrastructure, rotation execution, audit logging, HA/DR |
| **CI/CD Pipeline Builder** (`ci-cd-pipeline-builder`) | Pipeline architecture, secret injection patterns |

## Deliverables and success criteria

A run of this skill is done when:

- Audit report saved as `env_audit_<repo>_<date>.json` (via `--json`) next to the repo or in the security workspace; raw findings never pasted unredacted into tickets.
- Every finding closed as: rotated + removed, false-positive baselined, or test-fixture documented.
- `.env.example` contains only placeholders; `.gitignore` covers `.env`; rotation metadata (`# ROTATED: <date>`) present for every credential.
- Verification of completeness: `python3 scripts/env_auditor.py <repo-root>` reports 0 critical/high on the current tree; the pre-commit/CI gate blocks a planted test secret.
- Ongoing: rotation alerts fire at 30/14/7 days before expiry; consumer inventory current per secret.
