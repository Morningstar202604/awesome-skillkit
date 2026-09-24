---
name: webapp-e2e-harness
description: >-
  Scaffold a runnable Playwright end-to-end test suite for a local web app,
  with the discipline that keeps tests from rotting: semantic-first selectors,
  login-state reuse via storage_state, and anti-scrape/anti-429 etiquette. Use
  when the user asks for e2e testing, end-to-end testing, Playwright tests,
  webapp automation, how to fix selector drift, or login-state reuse. Do NOT
  use for unit tests (use tdd-guide) or for pure API testing (use
  api-test-suite-builder).
license: Apache-2.0
compatibility: Produces a Python test scaffold; running tests requires the user's `pip install pytest playwright` + `playwright install chromium` (the script itself is offline and does not download binaries).
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: programming
  pattern: script
  tier: standard
  verified-date: "2026-09-20"
---

# Webapp E2E Harness (Playwright End-to-End Test Scaffold)

Generates a **runnable Playwright e2e test suite** (Python edition, no node required), with three built-in disciplines that keep tests from rotting: semantic-first selectors, login-state reuse, and anti-scrape etiquette. Adapted from anthropics/skills `webapp-testing` plus skill-forge's Playwright thinking, trimmed to an offline scaffold + handling guide.

The core judgment: **the biggest cost of e2e tests isn't writing them, it's maintaining them**. Selector drift, re-login on every case, and getting 429'd by anti-scraping — these three decide whether tests survive a second refactor. This skill writes the handling into the scaffold itself, not just an empty shell.

> Red line: the script is **offline** (it only writes files, makes no network requests); actually running the tests is done by the user via `run_e2e.sh`; it dry-runs by default and only writes files with `--write`; credentials go only through env.

## Input Checklist

| Input | Required | Description |
|---|---|---|
| Target base URL | No | Defaults to `http://127.0.0.1:8000`, overridable via `E2E_BASE_URL` |
| Output directory | No | Defaults to `e2e/` |

## Pre-flight Checks

1. Is the app under test already running locally? (The script doesn't start the service for you; start it first.)
2. Is `pytest` + `playwright` installed? If not, `run_e2e.sh`'s first step installs them, but the browser binary needs `python3 -m playwright install chromium`.
3. Is there a login state? If so, prepare `auth.json` (produced by the first codegen login).

## Workflow

```bash
# 1. Dry run: see which files would be generated
python3 scripts/e2e_scaffold.py --url http://127.0.0.1:8000 --out e2e

# 2. Actually generate
python3 scripts/e2e_scaffold.py --url http://127.0.0.1:8000 --out examples/e2e --write   # real generation writes examples/e2e/; in CI use a temp directory

# 3. Run in one step (install deps + install browser + pytest)
E2E_BASE_URL=http://127.0.0.1:8000 bash e2e/run_e2e.sh
```

After generation, replace the `# TODO: assert` in `test_<slug>.py` with **semantic assertions** (`get_by_role` / `get_by_label`), then fill in the login-state and anti-scrape sections per [references/e2e-playbook.md](references/e2e-playbook.md).

## Delivery Criteria

- Selectors use **zero CSS class names / zero XPath**, all via role/label/testid
- Login state is reused via `storage_state`, not re-logged-in on every case
- Credentials are all read from env; no plaintext account is searchable in the test code
- `bash run_e2e.sh` is green (at least the smoke title assertion passes)

## Failure Handling Table

| Symptom | Root cause | Fix |
|---|---|---|
| `playwright install` failed | The browser wasn't downloaded | Run `python3 -m playwright install chromium` manually |
| Flaky cases | Used CSS selectors | Switch to `get_by_role`; see the playbook |
| Repeated logins | Didn't use storage_state | First-login codegen produces auth.json; use `new_context(storage_state=...)` |
| 429 / blocked | Fighting anti-scraping head-on | Lower concurrency + backoff; **don't automate** CAPTCHAs (compliance) |
| Base assertions all green but the page didn't change | Assertions too weak (only asserted a non-empty title) | Switch to real business assertions |

## References

- Full handling of selector drift / login state / anti-scraping: [references/e2e-playbook.md](references/e2e-playbook.md)

## Pipeline Position

- Upstream: `webapp-flow-tester` (manual flow exploration)
- Downstream: `ci-cd-pipeline-builder` (hang the e2e tests into the CI gate)
