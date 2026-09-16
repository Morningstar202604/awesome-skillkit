---
name: webapp-flow-tester
description: Drive end-to-end flow tests against a locally running web application with Playwright — discover interactive elements from the rendered page first, then navigate, interact, assert, and screenshot, with console-error collection and a server-lifecycle wrapper so crashing tests never leave orphan processes. Use when the user asks to 网页测试 / e2e 测试 / 自动化测试 / 跑一遍下单流程 / 验证页面功能 / web app testing / e2e test / playwright test / test user flow / verify page works. Do NOT use for production traffic, load/stress testing, or testing sites you are not authorized to automate.
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

# Webapp Flow Tester（Web 应用流程自动化测试）

对本地起着的 Web 应用做端到端流程验证：像真实用户一样点一遍关键路径，留下截图与 console 错误清单作为证据。铁律只有一条——**先看页面里真有什么，再写选择器**，盲猜 selector 是流程测试失败的头号原因。

## 输入清单

| 输入 | 必需 | 说明 |
|---|---|---|
| 启动命令 | 是* | 把应用跑起来的命令，如 `npm run dev`；应用已在运行则不需要 |
| 端口 | 是* | 应用监听的端口，如 3000；用于就绪探测 |
| 待验证流程 | 是 | 用自然语言描述的步骤，如"打开首页 → 登录 → 加入购物车 → 结账" |
| 验证标准 | 是 | 每步怎样算成功：出现某文案、URL 跳转、元素可见、请求返回 |

\* 应用已经在跑时可不提供；否则两者缺一不可。

缺必填项时，只问一次：

> 请提供：1) 应用的启动命令和端口（若已在运行请直接给地址）；2) 要验证的完整流程步骤；3) 每一步成功的判断标准是什么？

## 前置自检

每步给出预期与失败处置，全部通过才进入工作流：

```bash
python3 -c "import playwright; print('ok')"          # 预期 ok
python3 -m playwright --version                       # 预期打印版本号
python3 -m playwright install chromium --dry-run 2>/dev/null || \
  echo "browser may be missing"                       # 提示性检查
```

- **若失败：** 无 playwright 模块 → 指引用户执行 `pip install playwright && python3 -m playwright install chromium`，安装属于环境变更，先征得同意再动手。
- **若失败：** chromium 装了但启动报错（常见于缺系统依赖）→ 建议执行 `python3 -m playwright install-deps chromium`（需 sudo 权限，交由用户执行）。
- 应用可启动性：若应用未在运行，先用启动命令手动起一次，curl 探测端口返回 200 再继续；起不来的应用不进入测试，把启动报错原样反馈给用户。

## 工作流

### 步骤 1：元素发现——先侦察，后行动

- **动作：** 对目标页面先跑一段 dump 脚本，把当前可交互元素（role + 可见文本 + name/placeholder）打印出来，据实选择器写测试：

```python
# dump_elements.py — 侦察页面可交互元素，禁止跳过此步盲写 selector
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

- **预期：** 每类元素都有输出；据此挑出"文本唯一 / aria-label 唯一"的元素作为定位依据，优先 `get_by_role(role, name=...)`，其次 `get_by_placeholder`，最后才是 CSS 选择器。
- **若失败：** 页面空白或元素数全为 0 → 八成是 SPA 未渲染完：把 `wait_until` 改为 `networkidle` 再加 `page.wait_for_timeout(1000)` 重试；仍为空则说明 URL 不对或应用起错端口，回报用户而不是硬写选择器。

### 步骤 2：写流程测试脚本

- **动作：** 按此模板组织脚本：goto → 交互 → 断言 → 截图，四段齐全；console 错误全程收集，任何失败自动截图：

```python
# flow_test.py 模板 — 按业务流程填空，每步都留证据
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
            raise AssertionError(f"步骤 {name} 失败: {exc}") from exc
        finally:
            shots.append(name)

    step("open_home", lambda: page.goto(BASE, wait_until="networkidle"))
    step("login", lambda: (
        page.get_by_placeholder("用户名").fill("demo"),
        page.get_by_placeholder("密码").fill("secret"),
        page.get_by_role("button", name="登录").click(),
        page.wait_for_url("**/dashboard"),
    ))
    step("assert_dashboard", lambda: (
        page.get_by_role("heading", name="工作台").wait_for(state="visible", timeout=5000),
        assert "欢迎" in page.content(),
    ))

    print(f"steps: {shots}")
    print(f"console errors: {console_errors or 'none'}")
    assert not console_errors, "存在 console 错误，见截图与清单"
```

- **预期：** 脚本退出码 0，工作目录下每一步一张 `_ok.png`，stdout 打出步骤清单与 `console errors: none`。
- **若失败：** 某步断言失败 → 该步截图为 `_FAIL.png`，先看截图再回步骤 1 重新侦察，禁止不改依据直接换第三种 selector 碰运气。

### 步骤 3：用 with_server 包装服务生命周期

- **动作：** 应用不在运行时，永远通过包装器跑测试，保证测试崩溃也不留孤儿进程：

```bash
python3 scripts/with_server.py \
  --cmd "npm run dev" --port 3000 \
  --ready-path /health \
  -- python3 flow_test.py
```

- **机制：** 后台拉起服务 → socket 轮询端口就绪（给了 `--ready-path` 则还要求该路径 GET 200，默认超时 60s，可 `--timeout` 调整）→ 执行 `--` 之后的测试命令并透传退出码 → 无论测试成败，finally 中对服务进程树先 SIGTERM、宽限 5 秒后 SIGKILL。
- **预期：** stderr 出现 `server is ready` 与 `test exit code: 0`；测试段落后 `server process tree terminated`；`ss -ltn | grep 3000` 无残留监听。
- **若失败：** `server exited early with code N` → 是应用自身起不来，包装器会把服务输出尾部打到 stderr，据此排应用启动问题，不是测试脚本问题。

### 步骤 4：汇总证据并交付

- **动作：** 汇齐四样交付物：测试脚本、运行日志（含退出码）、逐步截图、console 错误清单（无错误也要显式写 none）。
- **预期：** 用户不看截图也能从日志复现结论；console 错误清单里标注每条发生时所在的步骤编号。
- **若失败：** 某些错误来自页面第三方脚本（统计、字体）→ 在清单中单独归为"非被测代码错误"，不要混入业务结论。

## 交付标准

| 项 | 要求 |
|---|---|
| 测试脚本 | 四段式齐全；选择器全部来自元素发现结果，脚本内注释标明依据 |
| 运行日志 | 完整 stderr/stdout + 最终退出码；用 with_server 时含 ready/terminated 两行 |
| 截图 | 每步一张；失败步骤有 `_FAIL.png` 且在报告中置顶说明 |
| console 清单 | 逐条列出或显式写 none；第三方脚本错误单独归类 |
| 边界声明 | 只测了哪些路径、未覆盖哪些（支付回调等真实第三方交互需注明未模拟） |

## 失败处置表

| 症状 | 处置 |
|---|---|
| playwright 未安装 | 给出安装命令，征得同意后代跑；无法安装则降级为 curl 级接口冒烟并声明非 UI 级验证 |
| 端口 60s 内未就绪 | 分层排查：进程活着吗 → 端口对吗 → ready-path 对吗；把每一层证据给用户，不盲目加大 timeout |
| 元素定位不稳定（偶发超时） | 改用 `get_by_role` + `wait_for` 显式等待；仍抖动则检查是否有动画/懒加载，加固定状态等待 |
| 测试把数据写坏了 | 只对用户提供或确认过的测试账号执行写操作；下单、删除类流程先问测试数据从哪来 |
| 页面需要登录态 | 问用户拿测试凭据或 cookie；绝不猜测凭据，绝不测试生产环境地址 |
| 步骤间强耦合难排查 | 拆成独立脚本逐段跑，定位到最短失败用例后再合回主脚本 |

## 参考

- scripts/with_server.py —— 服务生命周期包装器（`--help` 查看全部参数），本技能实测记录见交付日志要求。
- references/sources-and-methodology.md —— 方法论来源与许可说明。
