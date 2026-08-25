---
name: "env-secrets-manager"
description: "Manage environment-variable hygiene and secrets safety across local development and production. Practical auditing, drift awareness, rotation readiness. Use when auditing .env files for committed secrets, planning a credential rotation, debugging missing-env-var production incidents, or hardening a new project against secrets leakage."
license: Apache-2.0
metadata:
  version: "1.0"
  category: "security"
  verified-date: "2026-08-26"
---

# Env & Secrets Manager

**Tier:** POWERFUL
**Category:** Engineering
**Domain:** Security / DevOps / Configuration Management

---

## Overview

Manage environment-variable hygiene and secrets safety across local development and production workflows. This skill focuses on practical auditing, drift awareness, and rotation readiness.

## Core Capabilities

- `.env` and `.env.example` lifecycle guidance
- Secret leak detection for repository working trees
- Severity-based findings for likely credentials
- Operational pointers for rotation and containment
- Integration-ready outputs for CI checks

---

## When to Use

- Before pushing commits that touched env/config files
- During security audits and incident triage
- When onboarding contributors who need safe env conventions
- When validating that no obvious secrets are hardcoded

---

## Quick Start

```bash
# Scan a repository for likely secret leaks
python3 scripts/env_auditor.py /path/to/repo

# JSON output for CI pipelines
python3 scripts/env_auditor.py /path/to/repo --json
```

---

## Recommended Workflow

1. Run `scripts/env_auditor.py` on the repository root.
2. Prioritize `critical` and `high` findings first.
3. Rotate real credentials and remove exposed values.
4. Update `.env.example` and `.gitignore` as needed.
5. Add or tighten pre-commit/CI secret scanning gates.

---

## Reference Docs

- `references/validation-detection-rotation.md`
- `references/secret-patterns.md`

---

## Common Pitfalls

- Committing real values in `.env.example`
- Rotating one system but missing downstream consumers
- Logging secrets during debugging or incident response
- Treating suspected leaks as low urgency without validation

## Best Practices

1. Use a secret manager as the production source of truth.
2. Keep dev env files local and gitignored.
3. Enforce detection in CI before merge.
4. Re-test application paths immediately after credential rotation.

---

## Rotation Readiness (detection only)

Deep rotation execution — provider automation, dynamic secrets, emergency
checklists — belongs to **secrets-vault-manager**. This skill covers the
readiness half:

- Record creation/expiry metadata next to every credential.
- Set alerts at 30, 14, and 7 days before expiry.
- Run `scripts/env_auditor.py` to flag secrets with no recorded rotation
  date/comment (`# ROTATED: <date>`).
- Maintain a consumer inventory per secret so rotation blast radius is known
  before you need it.

> **Cross-reference:** for production vault infrastructure, cloud secret store
> selection (Vault / AWS Secrets Manager / Azure Key Vault / GCP Secret
> Manager), rotation execution workflows, audit-log backends, and disaster
> recovery, see `secrets-vault-manager`.

---

## CI/CD Secret Injection (pointers)

- Prefer **OIDC federation / short-lived tokens** over long-lived access keys.
- Never echo or print secret values in pipeline output; rely on platform
  masking but don't test it.
- Do not expose secrets to pipelines triggered by untrusted forks.
- Pipeline architecture patterns → `ci-cd-pipeline-builder`; vault-backed
  injection → `secrets-vault-manager`.

---

## Pre-Commit Secret Detection

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

### False Positive Management

- Maintain `.gitleaksignore` or `.secrets.baseline` in version control so the whole team shares exclusions.
- Review false positive lists during security audits — patterns may mask real leaks over time.
- Prefer tightening regex patterns over broadly ignoring files.

---

## Audit Logging (pointer)

Who accessed which secret and when is vault territory — cloud-native audit
trails (CloudTrail / Activity Log / Cloud Audit Logs / Vault audit backend),
bulk-read alerting, and SIEM feeds are covered in `secrets-vault-manager`.
Local equivalent: keep `.env` values out of shell history and CI logs.

---

## Cross-References

This skill covers env hygiene and secret detection. For deeper coverage of related domains, see:

| Skill | Relationship |
|-------|-------------|
| **Secrets Vault Manager** (`secrets-vault-manager`) | Production vault infrastructure, rotation execution, audit logging, HA/DR |
| **CI/CD Pipeline Builder** (`ci-cd-pipeline-builder`) | Pipeline architecture, secret injection patterns |
