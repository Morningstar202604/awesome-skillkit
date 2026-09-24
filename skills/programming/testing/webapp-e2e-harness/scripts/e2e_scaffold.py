#!/usr/bin/env python3
"""
e2e_scaffold.py -- generate a runnable Playwright e2e test scaffold (Python version,
no node required). Produces:
  <out>/conftest.py           browser-lifecycle fixture (headless by default; switchable via env)
  <out>/test_<slug>.py        one smoke case (visit the URL + assert title)
  <out>/run_e2e.sh            one-command run (pip install deps, then pytest)
  <out>/README.md             a handling guide for selector drift / login state / anti-bot (plain text)

Guardrails:
- dry-run by default; --write actually writes to disk
- makes no network requests (the script only writes files; running the tests is done by the user via run_e2e.sh)
- the browser binary requires the user to run `playwright install`; the script does not download it
"""
import argparse
import json
import os
import re
import sys

CONFTXT = '''"""Playwright e2e fixtures. Headless by default; set E2E_HEADFUL=1 for debug."""
import os
import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def browser_ctx():
    with sync_playwright() as p:
        headless = os.environ.get("E2E_HEADFUL") != "1"
        b = p.chromium.launch(headless=headless)
        ctx = b.new_context()
        yield ctx
        ctx.close()
        b.close()

@pytest.fixture
def page(browser_ctx):
    yield browser_ctx.new_page()
'''

TEST_TPL = '''"""Smoke test for {url_name}."""
import os

BASE_URL = os.environ.get("E2E_BASE_URL", "{base}")

def test_smoke_title(page):
    page.goto(BASE_URL)
    # TODO: assert on a STABLE selector (role/label > testid > css).
    # Prefer: page.get_by_role("heading", name="...")
    # Drift-safe fallback: page.wait_for_selector('[data-testid="..."]')
    assert page.title()  # placeholder; replace with a real assertion
'''

RUN_SH = """#!/usr/bin/env bash
set -euo pipefail
# 1. deps
python3 -m pip install --quiet pytest playwright
# 2. browser (first run only; skip if present)
if [ ! -d "$HOME/.cache/ms-playwright" ] || [ "${E2E_INSTALL_BROWSER:-0}" = "1" ]; then
  python3 -m playwright install chromium
fi
# 3. run
export E2E_BASE_URL="${E2E_BASE_URL:-http://127.0.0.1:8000}"
python3 -m pytest -q __OUT_REL__ -p no:cacheprovider
"""

README_TPL = """# webapp-e2e-harness: run & handling

## Run
E2E_BASE_URL=http://127.0.0.1:8000 bash run_e2e.sh
Debug headful: E2E_HEADFUL=1 E2E_INSTALL_BROWSER=1 bash run_e2e.sh

## How to fix selector drift
1. Always prefer `get_by_role` / `get_by_label` / `get_by_placeholder` (semantic selectors).
2. Next best: `[data-testid]` (stable, does not change with copy).
3. Avoid `css class names` (break on refactor) and `xpath` (fragile).
4. After copy changes, run `playwright codegen` to re-record selectors.

## Login state
- Use storage_state: `ctx = browser.new_context(storage_state='auth.json')`
- Produce auth.json once via `codegen`; reuse it afterward so each case does not log in again.
- Credentials never go in test code: read them from env (e.g. E2E_USER / E2E_PASS).

## Anti-bot / CAPTCHA
- Make the `user_agent` and viewport more realistic; lower concurrency.
- CAPTCHA scenarios are **not** automated by default (bypassing them is a compliance risk); use manual login + storage_state reuse.
- On 429 rate limiting: back off with `page.wait_for_timeout`; do not force it.
"""


def slugify(url: str) -> str:
    m = re.search(r"//([^/]+)", url)
    host = m.group(1) if m else "app"
    s = re.sub(r"[^a-z0-9]+", "_", host.lower()).strip("_")
    return s or "app"


def main() -> int:
    ap = argparse.ArgumentParser(description="Scaffold a Playwright e2e suite (offline)")
    ap.add_argument("--url", default="http://127.0.0.1:8000", help="target base URL")
    ap.add_argument("--out", default="e2e", help="output dir")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--write", action="store_true", help="actually write; default dry-run")
    args = ap.parse_args()

    url_name = slugify(args.url)
    out_rel = os.path.relpath(args.out)
    files = {
        "conftest.py": CONFTXT,
        f"test_{url_name}.py": TEST_TPL.format(url_name=url_name, base=args.url),
        "run_e2e.sh": RUN_SH.replace("__OUT_REL__", out_rel),
        "README.md": README_TPL,
    }
    if args.write:
        # out can be either a directory or a suffixed file path: when it is a file path, write the
        # scaffold files into a same-named directory and drop a summary JSON at out's exact path
        # (a machine-readable artifact consumed by CI).
        if os.path.splitext(args.out)[1]:
            target_dir = os.path.splitext(args.out)[0]
            os.makedirs(target_dir, exist_ok=True)
            real_out = target_dir
        else:
            os.makedirs(args.out, exist_ok=True)
            real_out = args.out
    else:
        real_out = args.out
    existing = [os.path.join(args.out, f) for f in files if os.path.exists(os.path.join(args.out, f))]

    print(f"e2e scaffold for {args.url} (slug={url_name}) -> {args.out}/")
    for f in files:
        print(f"  {os.path.join(args.out, f)}{'  (exists)' if os.path.join(args.out, f) in existing else ''}")

    if existing and not args.force:
        print(f"\n[DRY-RUN] {len(existing)} exist. Use --write --force to overwrite.")
        if not args.write:
            return 0
    if args.write:
        for f, content in files.items():
            with open(os.path.join(real_out, f), "w", encoding="utf-8") as fh:
                fh.write(content)
        os.chmod(os.path.join(real_out, "run_e2e.sh"), 0o755)
        # when out is a file path (.json etc.), drop the summary JSON at the exact path; directory usage is unaffected
        if real_out != args.out:
            summary = {
                "scaffold": "webapp-e2e-harness",
                "url": args.url,
                "files_written": sorted(files.keys()),
                "dir": real_out,
            }
            with open(args.out, "w", encoding="utf-8") as fh:
                json.dump(summary, fh, ensure_ascii=False, indent=1)
            print(f"  summary -> {args.out}")
        print(f"\n[WRITE] generated {len(files)} files. Run: bash {real_out}/run_e2e.sh")
    else:
        print(f"\n[DRY-RUN] nothing written. Re-run with --write (and --force to overwrite).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
