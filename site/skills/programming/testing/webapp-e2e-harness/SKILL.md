---
name: webapp-e2e-harness
description: >
  Scaffold a runnable Playwright end-to-end test suite for a local web app,
  with the discipline that keeps tests from rotting: semantic-first selectors,
  login-state reuse via storage_state, and anti-scrape/anti-429 etiquette. Use
  when the user asks to e2e 测试 / 端到端测试 / Playwright 测试 / webapp 自动化
  / 选择器漂移怎么修 / 登录态复用. Do NOT use for unit tests (use tdd-guide)
  or for pure API testing (use api-test-suite-builder).
license: Apache-2.0
compatibility: 产出 Python 测试脚手架；跑测试需用户 `pip install pytest playwright` + `playwright install chromium`（脚本本身离线，不下载二进制）
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: programming
  pattern: script
  tier: standard
  verified-date: "2026-09-20"
---

# Webapp E2E Harness（Playwright 端到端测试脚手架）

生成一套**能跑的 Playwright e2e 测试**（Python 版，无需 node），并内置"让测试
不腐烂"的三套纪律：语义优先选择器、登录态复用、反爬礼仪。改造自
anthropics/skills `webapp-testing` + skill-forge 的 Playwright 思路，裁剪为
离线脚手架 + 处置指南。

核心判断：**e2e 测试最大的成本不是写，是维护**。选择器漂移、登录态每条用例
重登、被反爬 429——这三样决定测试能不能活过第二次重构。本技能把处置办法
直接写进脚手架，而不只是给个空壳。

> 红线：脚本**离线**（只写文件，不发网络请求）；真正跑测试由用户执行
> `run_e2e.sh`；默认 dry-run，`--write` 才落盘；凭证只走 env。

## 输入清单

| 输入 | 必填 | 说明 |
|---|---|---|
| 目标 base URL | 否 | 默认 `http://127.0.0.1:8000`，可用 `E2E_BASE_URL` 覆盖 |
| 输出目录 | 否 | 默认 `e2e/` |

## 前置自检

1. 被测应用是否已本地起好？（脚本不替你起服务；起好再跑）
2. 是否装了 `pytest` + `playwright`？没装 → `run_e2e.sh` 第一步会装，但
   浏览器二进制要 `python3 -m playwright install chromium`。
3. 有登录态吗？有就准备 `auth.json`（codegen 首登产出）。

## 工作流

```bash
# 1. 干跑：看会生成哪些文件
python3 scripts/e2e_scaffold.py --url http://127.0.0.1:8000 --out e2e

# 2. 真生成
python3 scripts/e2e_scaffold.py --url http://127.0.0.1:8000 --out examples/e2e --write   # 真实生成写 examples/e2e/；CI 场景可用临时目录

# 3. 一键跑（装依赖 + 装浏览器 + pytest）
E2E_BASE_URL=http://127.0.0.1:8000 bash e2e/run_e2e.sh
```

生成后，把 `test_<slug>.py` 里的 `# TODO: assert` 换成**语义断言**
（`get_by_role` / `get_by_label`），再按 [references/e2e-playbook.md](references/e2e-playbook.md)
补齐登录态与反爬段。

## 交付标准

- 选择器**零 css 类名 / 零 xpath**，全走 role/label/testid
- 登录态用 `storage_state` 复用，不每条用例重登
- 凭证全部从 env 读，测试代码里搜不到明文账号
- `bash run_e2e.sh` 绿（至少冒烟 title 断言过）

## 失败处置表

| 现象 | 根因 | 处置 |
|---|---|---|
| `playwright install` 失败 | 浏览器没下载 | 手跑 `python3 -m playwright install chromium` |
| 用例飘忽（flaky） | 用了 css 选择器 | 改 `get_by_role`，见 playbook |
| 登录反复 | 没用 storage_state | 首登 codegen 出 auth.json，`new_context(storage_state=...)` |
| 429/被拦 | 硬刚反爬 | 降并发 + 退避；验证码**不自动化**（合规） |
| 基类断言全绿但页面没变 | 断言太弱（只断 title 非空） | 换成真实业务断言 |

## 参考

- 选择器漂移 / 登录态 / 反爬完整处置：[references/e2e-playbook.md](references/e2e-playbook.md)

## 链路位置

- 上游：`webapp-flow-tester`（手工流程探查）
- 下游：`ci-cd-pipeline-builder`（把 e2e 挂进 CI 门禁）
