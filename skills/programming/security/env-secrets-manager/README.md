# Env & Secrets Manager

Environment-variable hygiene and secrets-safety auditing for local dev and CI.

## Quick Start

```bash
# Scan a repository working tree for likely secret leaks (redacted output)
python3 scripts/env_auditor.py /path/to/repo

# JSON output for CI pipelines
python3 scripts/env_auditor.py /path/to/repo --json
```

Exit codes: `0` clean · `1` critical/high findings (use as a CI gate) ·
`2` usage error.

## What It Detects

| Severity | Signals |
|----------|---------|
| critical | OpenAI-style keys, GitHub tokens, AWS access key IDs, PEM private-key blocks |
| high | Slack tokens, hardcoded assignments to sensitive keys, `.env` not gitignored |
| medium | plaintext JWTs, real-looking values committed in `.env.example` |
| low | `.env ↔ .env.example` drift, credentials with no recorded rotation date |

All excerpts are **redacted** (`ghp_...(36 chars)`) so the auditor never leaks
secrets into logs. Placeholder/template values (`your_api_key_here`,
`${VAR}`, `process.env.X`) are ignored to keep false positives down.

## Recommended Workflow

1. Run `scripts/env_auditor.py` on the repo root.
2. Fix `critical` and `high` first; rotate real credentials.
3. Update `.env.example` and `.gitignore`.
4. Add a pre-commit/CI gate: `python3 scripts/env_auditor.py . || exit 1`.

## Scope

This skill owns **env hygiene and detection**. Vault/cloud-secret-store
infrastructure, rotation execution, and audit logging live in
`secrets-vault-manager`.

## Sample Data

- `assets/sample_env_leak.env` — fixture with fake-but-detectable credentials
- `expected_outputs/sample_audit_report.json` — golden auditor output for the fixture
- `tests/test_env_auditor.py` — unit tests (`python3 tests/test_env_auditor.py`)
