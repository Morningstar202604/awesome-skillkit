#!/usr/bin/env python3
"""
e2e_scaffold.py — 生成一套可运行的 Playwright e2e 测试脚手架（Python 版，
无需 node）。产出：
  <out>/conftest.py           浏览器生命周期 fixture（默认 headless，可 env 切）
  <out>/test_<slug>.py       一个冒烟用例（访问 URL + 断言 title）
  <out>/run_e2e.sh           一键运行（先 pip 装依赖再 pytest）
  <out>/README.md            选择器漂移/登录态/反爬 的处置指南（纯文本）

红线：
- 默认 dry-run；--write 才落盘
- 不发任何网络请求（脚本只写文件；真正跑测试由用户执行 run_e2e.sh）
- 浏览器二进制需用户 `playwright install`，脚本不负责下载
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

README_TPL = """# webapp-e2e-harness 运行与处置

## 跑
E2E_BASE_URL=http://127.0.0.1:8000 bash run_e2e.sh
调试有头：E2E_HEADFUL=1 E2E_INSTALL_BROWSER=1 bash run_e2e.sh

## 选择器漂移怎么修
1. 永远优先 `get_by_role` / `get_by_label` / `get_by_placeholder`（语义选择器）。
2. 次选 `[data-testid]`（稳定、不随文案变）。
3. 避免 `css 类名`（重构即崩）与 `xpath`（脆弱）。
4. 文案改动后跑 `playwright codegen` 重新录选择器。

## 登录态
- 用 storage_state：`ctx = browser.new_context(storage_state='auth.json')`
- 首登走 `codegen` 产出 auth.json；后续复用，避免每条用例都登录。
- 凭证绝不进测试代码：从 env（如 E2E_USER / E2E_PASS）读。

## 反爬/验证码
- 提高 `user_agent` 与视口真实性；降并发。
- 验证码场景默认**不做**自动化（绕过有合规风险）；用人工登录 + storage_state 复用。
- 429 限流：`page.wait_for_timeout` 退避，别硬刚。
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
        # out 既可以是目录也可以是带后缀的文件路径：文件路径时把脚手架文件写到同名目录、
        # 并在 out 精确路径落一份摘要 JSON（机器可读产物；CI 消费这个文件）。
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
        # out 是文件路径（.json 等）时，在精确路径落摘要 JSON——目录用法不受影响
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
