---
name: ship-gate
description: "Pre-production audit that scans a codebase for security, database, deployment, code quality, AI/LLM, dependency, frontend, and observability issues. Intercepts deploy commands and blocks until critical items pass. 当用户要求 上线前检查 / 发布门禁 / 发布前把关 时使用。 Also triggers on / 上线检查 / 发布前审计 / 部署门禁 / pre-deploy audit / release checklist. Do NOT use for fixing the failures it reports (this skill only gates and reports)."
license: Apache-2.0
compatibility: Pure prompt-based; runs Python stdlib scanner via Bash. No API keys required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: cicd
  pattern: single-task
  tier: powerful
  verified-date: "2026-09-09"
---

# Ship Gate

上线前审计：对代码库做 8 大类别扫描，逐项给出 PASS/FAIL/MANUAL 结论。自动化检查由内置扫描器执行；无法自动验证的项转为人工确认清单。本技能只审计和报告——不负责修复。

## 拦截行为

当用户说 "push to production"、"deploy"、"ship it"、"go live" 或类似部署意图的话时，不要直接执行部署。改为：

1. 询问："跑过上线门禁了吗？需要我现在扫描一遍？"
2. 用户同意 → 执行下方工作流。
3. 用户称已跑过 → 询问时间。超过 24 小时，或此后代码有改动 → 建议重跑。

## 输入清单

| 输入 | 必需 | 说明 |
|---|---|---|
| 项目根目录 | 否 | 缺省当前目录 |
| 扫描类别 | 否 | 8 类之一（SEC/DB/CODE/DEP/AI/DEPLOY/FE/OBS），缺省全跑 |
| 输出格式 | 否 | 人读（默认，带色）或 `--json` |
| 交互确认 | 否 | 默认交互式询问人工确认项；CI 场景加 `--no-interactive` |

输入缺失时一次性问齐："请提供：① 项目根目录（不填默认当前目录）；② 是全量扫描还是只扫某类别。"

## 前置自检

```bash
# 1. Python 3 可用
python3 --version
# 预期：Python 3.8+。失败→安装后重试，STOP。

# 2. 扫描器存在
ls scripts/ship_gate_scanner.py
# 预期：文件名（在技能目录内执行）。失败→cd 到技能目录；仍缺→STOP 回报。

# 3. 目标项目目录存在
ls <项目根目录> > /dev/null && echo OK
# 预期：OK。失败→向用户确认路径，STOP。

# 4. 检查规则与模式库在位
ls references/checks.md references/patterns.md
# 预期：两个文件名。缺失→STOP 回报仓库不完整。
```

## 工作流

### 步骤 1：全量扫描

```bash
python3 scripts/ship_gate_scanner.py examples/sample-frontend --json --no-interactive --category FE   # 随包达标样例（FE 类全 ADVISORY 通过 → CLEAR_TO_SHIP rc=0）；完整审计对真实项目去掉 --category，未达标时退出码非 0 属 CI 门禁语义
```

- **动作**：扫描器自动检测技术栈（框架、数据库、部署目标、鉴权、AI/LLM SDK——检测规则实现在 scanner 内，与 `references/checks.md` 中带栈标签的检查项联动），并按 SEC → DB → CODE → DEP → AI → DEPLOY → FE → OBS 顺序执行全部自动化检查。
- **预期**：生成 JSON 报告，含每类检查的 PASS/FAIL/SKIP 与文件定位；退出码 0/1/2（含义见失败处置表）。
- **若失败**：扫描器报错退出 → 读错误信息；目标目录无法访问 → 向用户确认路径后 STOP。

### 步骤 2：人工确认项

- **动作**：自动化无法覆盖的检查（备份恢复已演练、回滚方案存在、staging 测试通过、监控告警接通等）逐条列出，向用户逐项确认 yes/no/unknown。
- **预期**：每项获得明确答复并记录；unknown 一律按未通过计。
- **若失败**：用户拒绝答复 → 该项记 MANUAL/未确认，进入裁决。

### 步骤 3：裁决

- **动作**：把结果按严重度分级并给出裁决：
  - **CRITICAL**（必须修复）：secrets 暴露、路由无鉴权、无 HTTPS、SQL 注入向量、Supabase 表无 RLS
  - **HIGH**（应该修复）：无 error boundary、无 rate limiting、生产代码 console.log、无分页
  - **ADVISORY**（建议项）：无 OG 标签、无自定义 404、无 analytics、无 SBOM
- **裁决规则**：存在任一 CRITICAL 未解决 → `DO NOT SHIP`；仅剩 HIGH → `SHIP WITH CAUTION`（需用户书面知悉风险）；零 CRITICAL 且人工确认项通过 → `CLEAR TO SHIP`。
- **预期**：输出如下格式的报告（含真实文件定位与行号）：

```text
SHIP GATE REPORT
================
Stack: Next.js + Supabase + Vercel
Scan time: 12s

CRITICAL (3 items, must fix)
  FAIL  [SEC-01] API key found in src/lib/api.ts:14
  FAIL  [DB-07] RLS not enabled on "profiles" table

HIGH (2 items, should fix)
  FAIL  [DEP-04] 3 critical npm audit vulnerabilities
  MANUAL [DEPLOY-06] Staging test not confirmed

ADVISORY (1 item, recommended)
  FAIL  [FE-01] Missing OG meta tags

VERDICT: DO NOT SHIP (2 critical issues)
Fix critical items and re-run.
```

- **若失败**：裁决为 DO NOT SHIP → 报告后 STOP；本技能不修复，交用户或其他技能处理修复后重新扫描。

### 步骤 4：复扫与放行

- **动作**：修复完成后重跑步骤 1（全量，不做增量），核对上轮 CRITICAL 项全部转为 PASS。
- **预期**：退出码 0，报告 `VERDICT: CLEAR TO SHIP`。
- **若失败**：仍有 CRITICAL → 回到步骤 3 裁决，绝不放行。

## 八大类别

| 前缀 | 类别 | 说明 |
|--------|----------|------|
| SEC | 安全 | 密钥泄漏、鉴权缺失、注入向量、CSRF、HTTPS |
| DB | 数据库 | RLS、备份、迁移安全、连接安全 |
| DEPLOY | 部署 | 回滚方案、staging 验证、环境配置 |
| CODE | 代码质量 | console.log、空 catch、错误边界 |
| AI | AI/LLM 安全 | API key 管理、prompt 注入面、输出过滤 |
| DEP | 依赖 | npm audit 严重漏洞、SBOM |
| FE | 前端质量 | OG 标签、404 页、错误页面 |
| OBS | 可观测性 | 错误监控、日志、告警 |

各项检查的完整定义见 `references/checks.md`，扫描模式（grep 规则）见 `references/patterns.md`。

## 适用范围

本技能只审计，不修复。发现问题后，带着文件定位与修复建议报告出来；修复由用户或其他技能（systematic-debugging、backend-patterns、shadcn-stack）负责。

本技能不做：

- 搭建 CI/CD 流水线
- 开通基础设施
- 配置监控工具
- 部署后运行（本技能只在部署前使用）

## 参数速查表

| 参数 | 取值 | 说明 |
|---|---|---|
| `path` | 目录（位置参数） | 项目根目录，缺省当前目录 |
| `--json` | 布尔 | JSON 输出，供程序消费 |
| `--no-color` | 布尔 | 关闭 ANSI 颜色 |
| `--no-interactive` | 布尔 | 跳过人工确认交互（CI 必加） |
| `--category` | SEC/DB/CODE/DEP/AI/DEPLOY/FE/OBS | 只跑单类 |
| `--verbose` | 布尔 | 额外显示 PASS 项 |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|---|---|---|
| 退出码 1 | 发现 critical 问题 | 裁决 DO NOT SHIP，逐条报告，STOP |
| 退出码 2 | 仅 high 级问题 | 裁决 SHIP WITH CAUTION，列风险交用户书面确认 |
| 退出码 0 | 无 critical 问题 | 可进入 CLEAR TO SHIP 流程，仍需核对人工确认项 |
| 扫描器崩溃/traceback | 目标目录结构异常或权限不足 | 读 traceback 定位；权限问题换目录重试 |
| 人工确认项全是 unknown | 用户未配合 | 一律按未通过计，裁决不放宽 |

## 交付标准

- 成功定义：输出含真实栈检测结果、8 类 PASS/FAIL/SKIP 统计、分级明细（文件+行号）、明确 VERDICT 三选一。
- 产物命名：对话内报告 `SHIP GATE REPORT`；留档 `ship-gate-report-<YYYYMMDD>.json`（`--json` 输出）。
- 保存位置：对话内交付；留档放用户指定目录。
- 完整性验证：报告中每条 FAIL 都有 `[类别-编号]` + 文件定位；VERDICT 与 CRITICAL/HIGH 计数一致。

## 参考

- `references/checks.md` — 全部检查项定义（含适用栈标签）；解读某条 FAIL 或核对人工确认项范围时读。
- `references/patterns.md` — 扫描模式库；需要向用户解释某项是如何检出的时读。

## 相关技能

- **karpathy-coder**：karpathy-check 通过后再跑 ship-gate——先保简洁，再上生产
- **adversarial-reviewer**：对 ship-gate 判为 critical 的问题做深度安全审查
- **security-pen-testing**：针对 SEC 类发现的渗透测试方法论
- **code-reviewer**：通用代码质量审查，与 ship-gate 的自动检查互补
