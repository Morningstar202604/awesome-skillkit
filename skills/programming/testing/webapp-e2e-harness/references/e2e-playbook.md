# E2E Playbook

## Selector priority (highest to lowest)
1. `get_by_role("button", name="Submit")` — semantic, most robust under refactoring
2. `get_by_label("Email")` / `get_by_placeholder("...")` — first choice for forms
3. `[data-testid="pay-btn"]` — anchor when the visible text changes (must be pre-planted in the business code)
4. css `text=...` only as a last resort; **forbid** pure class or pure xpath

## Reusing the logged-in session
```python
# first login (codegen produces auth.json)
ctx = browser.new_context(storage_state="auth.json")
# pass this ctx to all subsequent cases to avoid re-logging in per test
```
- Credentials go via env: `os.environ["E2E_USER"]`; never hard-code in test files.

## Anti-bot / 429 / CAPTCHA
- Lower concurrency, add backoff with `page.wait_for_timeout(backoff)`.
- Emulate a realistic user_agent / viewport.
- **Do not automate CAPTCHA** (bypassing it is a compliance risk): log in manually once → reuse storage_state.

## How to run
```bash
E2E_BASE_URL=http://127.0.0.1:8000 E2E_HEADFUL=1 bash run_e2e.sh
```
- `E2E_HEADFUL=1` to watch the browser for debugging; `E2E_INSTALL_BROWSER=1` to force a browser reinstall.
