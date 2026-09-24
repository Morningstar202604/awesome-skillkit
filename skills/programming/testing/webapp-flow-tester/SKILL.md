---
name: webapp-flow-tester
description: "Drive end-to-end flow tests against a locally running web application with Playwright — discover interactive elements from the rendered page first, then navigate, interact, assert, and screenshot, with console-error collection and a server-lifecycle wrapper so crashing tests never leave orphan processes. Use when the user asks for web testing, e2e testing, automated testing, to walk through an order/checkout flow, to verify page functionality, web app testing, e2e test, playwright test, test user flow, or verify page works. Do NOT use for production traffic, load/stress testing, or testing sites you are not authorized to automate."
license: Apache-2.0
compatibility: Requires Python 3.8+ with playwright (pip install playwright && playwright install chromium); scripts/with_server.py is stdlib-only.
metadata:
  author: awesome-skillkit
  version: "1.0"
  category: test-driven-development
  pattern: single-task
  tier: standard
  verified-date: "2026-09-16"
---

# Webapp Flow Tester (Web App Flow Automation Testing)

Validates end-to-end flows against a locally running web app: walk through the critical paths like a real user, leaving screenshots and a console-error list as evidence. There's only one iron rule — **first look at what's actually on the page, then write selectors**; guessing selectors blindly is the number one cause of flow-test failures.

## Input Checklist

| Input | Required | Description |
|---|---|---|
| Start command | Yes* | The command that starts the app, e.g. `npm run dev`; not needed if the app is already running |
| Port | Yes* | The port the app listens on, e.g. 3000; used for readiness probing |
| Flow to verify | Yes | Steps described in natural language, e.g. "open the home page → log in → add to cart → check out" |
| Success criteria | Yes | What counts as success at each step: some text appears, a URL change, an element visible, a request returning |

\* Not required if the app is already running; otherwise both are mandatory.

When a required item is missing, ask only once:

> Please provide: (1) the app's start command and port (or just the address if it's already running); (2) the complete flow steps to verify; (3) the success criterion for each step?

## Pre-flight Checks

Give the expected result and failure handling for each step; only enter the workflow once all pass:

```bash
python3 -c "import playwright; print('ok')"          # expected ok
python3 -m playwright --version                       # expected to print the version
python3 -m playwright install chromium --dry-run 2>/dev/null || \
  echo "browser may be missing"                       # informational check
```

- **On failure:** no playwright module → guide the user to run `pip install playwright && python3 -m playwright install chromium`; installation is an environment change, so get consent before doing it.
- **On failure:** chromium is installed but errors on launch (often missing system deps) → suggest running `python3 -m playwright install-deps chromium` (needs sudo, left to the user).
- App startability: if the app isn't running, start it manually once with the start command first, and continue only once curling the port returns 200; an app that won't start doesn't enter testing — report the startup error verbatim to the user.

## Workflow

### Step 1: Element discovery — recon first, then act

- **Action:** first run a dump script against the target page that prints the currently interactive elements (role + visible text + name/placeholder), and write tests from the selectors based on what's actually there:

```python
# dump_elements.py — recon the page's interactive elements; never skip this step and write selectors blind
from playwright.sync_api import sync_playwright
import sys

url = sys.argv[1]
with sync_playwright() as p:
    page = p.chromium.launch(headless=True).new_page()
    page.goto(url, wait_until="networkidle")
    for sel in ("button", "a", "input", "textarea", "select", "[role='button']"):
        for el in page.locator(sel).all():
            role = el.evaluate("e => e.getAttribute('role') || e.tagName.toLowerCase()")
            text = (el.inner_text() or "").strip()[:40]
            name = el.evaluate(
                "e => e.getAttribute('name') || e.getAttribute('placeholder')"
                " || e.getAttribute('aria-label') || ''")
            print(f"{role:10s} | text={text!r:44s} | name={name!r}")
```

- **Expected:** every element type produces output; based on it, pick elements with "unique text / unique aria-label" as the locator, preferring `get_by_role(role, name=...)`, then `get_by_placeholder`, and CSS selectors only as a last resort.
- **On failure:** blank page or zero elements across the board → most likely the SPA hasn't finished rendering; change `wait_until` to `networkidle` and add `page.wait_for_timeout(1000)` before retrying; if still empty, the URL is wrong or the app started on the wrong port — report it to the user rather than hard-coding selectors.

### Step 2: Write the flow-test script

- **Action:** organize the script by this template: goto → interact → assert → screenshot, all four present; collect console errors throughout, and auto-screenshot on any failure:

```python
# flow_test.py template — fill in per the business flow; leave evidence at every step
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:3000"
shots, console_errors = [], []

with sync_playwright() as p:
    page = p.chromium.launch(headless=True).new_page()
    page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: console_errors.append(str(e)))

    def step(name, fn):
        try:
            fn()
            page.screenshot(path=f"{len(shots):02d}_{name}_ok.png")
        except Exception as exc:
            page.screenshot(path=f"{len(shots):02d}_{name}_FAIL.png")
            raise AssertionError(f"step {name} failed: {exc}") from exc
        finally:
            shots.append(name)

    step("open_home", lambda: page.goto(BASE, wait_until="networkidle"))
    step("login", lambda: (
        page.get_by_placeholder("Username").fill("demo"),
        page.get_by_placeholder("Password").fill("secret"),
        page.get_by_role("button", name="Sign in").click(),
        page.wait_for_url("**/dashboard"),
    ))
    step("assert_dashboard", lambda: (
        page.get_by_role("heading", name="Dashboard").wait_for(state="visible", timeout=5000),
        assert "Welcome" in page.content(),
    ))

    print(f"steps: {shots}")
    print(f"console errors: {console_errors or 'none'}")
    assert not console_errors, "console errors present; see screenshots and list"
```

- **Expected:** the script exits 0, each step leaves an `_ok.png` in the working directory, and stdout prints the step list plus `console errors: none`.
- **On failure:** a step's assertion fails → that step's screenshot is `_FAIL.png`; look at the screenshot first, then return to Step 1 to re-recon; it's forbidden to blindly swap in a third selector based on nothing.

### Step 3: Wrap the server lifecycle with with_server

- **Action:** when the app isn't running, always run tests through the wrapper so a crashing test never leaves an orphan process:

```bash
python3 scripts/with_server.py \
  --cmd "npm run dev" --port 3000 \
  --ready-path /health \
  -- python3 flow_test.py
```

- **Mechanism:** start the service in the background → socket-poll the port until ready (if `--ready-path` is given, also require that path to GET 200; default timeout 60s, adjustable via `--timeout`) → run the test command after `--` and pass through its exit code → regardless of test outcome, SIGTERM the service process tree in `finally`, grace period 5s, then SIGKILL.
- **Expected:** stderr shows `server is ready` and `test exit code: 0`; after the test section, `server process tree terminated`; `ss -ltn | grep 3000` shows no leftover listener.
- **On failure:** `server exited early with code N` → the app itself won't start; the wrapper prints the tail of the service output to stderr, so diagnose the app startup from that, not the test script.

### Step 4: Aggregate evidence and deliver

- **Action:** gather the four deliverables: test script, run log (with exit code), step-by-step screenshots, console-error list (write none explicitly if there are no errors).
- **Expected:** the user can reproduce the conclusion from the logs without looking at screenshots; the console-error list marks which step number each error occurred in.
- **On failure:** some errors come from third-party page scripts (analytics, fonts) → categorize them separately in the list as "errors not in code under test"; don't mix them into the business conclusion.

## Delivery Criteria

| Item | Requirement |
|---|---|
| Test script | All four sections present; selectors all come from the element-discovery results, with the basis annotated in comments |
| Run log | Complete stderr/stdout + final exit code; when using with_server, includes the ready/terminated lines |
| Screenshots | One per step; failed steps have `_FAIL.png` and are highlighted at the top of the report |
| Console list | List each error or write none explicitly; categorize third-party script errors separately |
| Boundary statement | Which paths were tested, which weren't (real third-party interactions such as payment callbacks must be noted as not simulated) |

## Failure Handling Table

| Symptom | Fix |
|---|---|
| playwright not installed | Give the install command, run it after consent; if it can't be installed, degrade to curl-level endpoint smoke tests and declare it non-UI verification |
| Port not ready within 60s | Troubleshoot in layers: is the process alive → is the port right → is the ready-path right; give the user evidence at each layer; don't blindly increase the timeout |
| Unstable element location (occasional timeouts) | Switch to `get_by_role` + explicit `wait_for`; still flaky → check for animations/lazy-loading and add fixed-state waits |
| The test corrupted data | Only perform write operations against test accounts the user provided or approved; for order/deletion flows, first ask where the test data comes from |
| The page needs a login state | Ask the user for test credentials or cookies; never guess credentials, never test production addresses |
| Strong coupling between steps makes it hard to debug | Split into independent scripts run segment by segment; once the shortest failing case is located, merge back into the main script |

## References

- scripts/with_server.py — the server-lifecycle wrapper (`--help` for all parameters); see the delivery-log requirement for this skill's measured record.
- references/sources-and-methodology.md — methodology sources and license notes.
