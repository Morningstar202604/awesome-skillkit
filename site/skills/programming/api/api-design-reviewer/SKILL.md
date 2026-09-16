---
name: api-design-reviewer
description: "Comprehensive REST API design review with automated linting, breaking-change detection, and design scorecards. Catches inconsistent conventions, missing versioning, and design smells before APIs ship. Use when reviewing a PR that adds or changes API endpoints, auditing an existing API for v2 migration, or establishing API standards for a team. 当用户要求 审查 API 设计 / REST 接口设计评审 / 找出反模式 时使用。 Do NOT use for implementing API endpoints or generating client SDKs."
license: Apache-2.0
compatibility: Requires network access. No API keys required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: api
  pattern: code-reviewer
  tier: powerful
  verified-date: "2026-09-09"
---

# API Design Reviewer

用三件工具审查 REST API 设计——对 OpenAPI spec 做规范 lint、检测版本间破坏性变更、给整体设计质量打分——然后附上工具输出汇报发现。

## 输入清单

| 输入 | 必需 | 说明 |
|---|---|---|
| OpenAPI/Swagger spec（JSON） | 是 | 当前版规范文件路径，如 `openapi.json`；无 spec 时可用 `--sample` 内置样例 |
| 旧版 spec | 仅破坏性变更检测时 | 与新版对比的旧规范文件路径 |
| 最低通过等级 | 否 | `api_scorecard.py --min-grade A\|B\|C\|D\|F`，默认无门槛 |
| 输出格式 | 否 | `--format text\|json`，CI 场景用 json |

输入缺失时一次性问齐："请提供：① 待审查的 OpenAPI/Swagger JSON 文件路径；② 若要做破坏性变更检测，旧版 spec 路径；③ 最低通过等级（不填默认 B）。"

## 前置自检

逐条执行，任一失败 → 按修复处置后 STOP：

```bash
# 1. Python 3 可用
python3 --version
# 预期：Python 3.8+。

# 2. 三个工具脚本存在
ls scripts/api_linter.py scripts/breaking_change_detector.py scripts/api_scorecard.py
# 预期：三个文件名（在技能目录内执行）。失败→cd 到技能目录后重试；仍缺→STOP 回报。

# 3. spec 文件可读且为合法 JSON
python3 -c "import json,sys; json.load(open('<spec>'))" && echo OK
# 预期：OK。失败→向用户确认正确的 spec 路径/格式，STOP。
```

## 工作流

命令在技能目录（`skills/programming/api/api-design-reviewer/`）内执行。无现成 spec 时，先跑 `python3 scripts/api_linter.py --sample` 熟悉输出结构。

### 步骤 1：Lint 规范

```bash
python3 scripts/api_linter.py openapi.json --format json --output lint.json
```

- **动作**：检查资源命名（资源 kebab-case、字段 camelCase）、HTTP 方法用法、URL 结构、状态码合规、错误响应结构一致性、文档覆盖度。
- **预期**：生成 `lint.json`；无致命项时退出码 0。
- **若失败**：JSON 内含 violation 明细 → 逐条整理为发现清单（含文件/路径定位），进入步骤 3 一并报告。

### 步骤 2：破坏性变更检测

```bash
python3 scripts/breaking_change_detector.py openapi-v1.json openapi-v2.json --format json --exit-on-breaking --output breaking.json
```

- **动作**：对比两版 spec，检出端点删除、响应结构变化、字段删除/改名、类型变更、新增必填字段、状态码变更，并给出影响严重度。
- **预期**：退出码 0（无破坏性变更）；或破坏项已全部被版本号提升（version bump）覆盖。
- **若失败**：`--exit-on-breaking` 使其检出破坏项时以非零退出 → 把每项破坏性变更列入报告，标记"需 version bump 或回退"。

### 步骤 3：设计评分

```bash
python3 scripts/api_scorecard.py openapi.json --format json --min-grade B --output scorecard.json
```

- **动作**：五维评分——Consistency 30%、Documentation 20%、Security 20%、Usability 15%、Performance 15%，输出 0-100 分与 A-F 等级、改进建议。
- **预期**：等级 ≥ `--min-grade`（上例 B），退出码 0。
- **若失败**：等级低于门槛 → 输出报告但裁决为 "not approved"，附 scorecard 中的改进项。

### 步骤 4：汇总裁决

- **动作**：向用户报告 lint 发现 + 破坏性变更 + 等级。禁止仅凭文字评审签收——必须附三个工具的输出。
- **预期**：lint 无 violation（或已全部接受）、`--exit-on-breaking` 通过（或破坏项已 version bump）、等级 ≥ 约定门槛，三项齐备裁决 "approved"。
- **若失败**：用户修复 spec 后，从步骤 1 重跑全流程。

## 参数速查表

| 参数 | 取值 | 说明 |
|---|---|---|
| `--format` | text / json | 输出格式；CI 用 json |
| `--output` | 文件路径 | 写入文件（三脚本均无 `-o` 短选项，必须用全称） |
| `--exit-on-breaking` | 布尔 | breaking_change_detector 检出破坏项时非零退出，作 CI 门禁 |
| `--min-grade` | A / B / C / D / F | api_scorecard 低于该等级非零退出，作 CI 门禁 |
| `--sample` | 布尔 | api_linter 用内置样例 spec，无需输入文件 |
| `--raw-endpoints` | 布尔 | api_linter 接受原始端点清单 JSON 而非完整 spec |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|---|---|---|
| `unrecognized arguments: -o` | 用了不存在的短选项 | 改用 `--output` |
| `json.decoder.JSONDecodeError` | spec 非 JSON（可能是 YAML） | 请用户提供 JSON 格式 spec 或先转换，STOP |
| 退出码非 0 且无输出文件 | 检出门禁失败项（`--exit-on-breaking`/`--min-grade`） | 读 stdout/JSON 报告，属正常门禁行为，按发现项处置 |
| `FileNotFoundError` | 不在技能目录执行 | `cd` 到技能目录，或改用脚本绝对路径 |
| breaking 项无法修复 | 上游接口约束 | 报告给用户决策：version bump 或接受并书面记录 |

## 交付标准

- 成功定义：三工具全部运行完毕，报告含 lint 发现清单、破坏性变更清单、等级分数；裁决词只能是 "approved" 或 "not approved"（附依据）。
- 产物命名：`lint.json`、`breaking.json`、`scorecard.json`（或用户指定名）。
- 保存位置：默认当前目录，或用户指定的输出目录。
- 完整性验证：三个文件均可被 `json.load` 解析且非空；报告引用了各文件的 `overall_score`/等级原文。

## 参考

- `references/rest_design_rules.md` — REST 命名、方法、状态码、分页、错误格式的完整规则集；解读 lint violation 或回答"应该怎么改"时读。
- `references/api_antipatterns.md` — 常见反模式及修复方案；lint 大量命中或用户要求"找出反模式"时读。

## CI 集成

```yaml
- name: "api-linting"
  run: python scripts/api_linter.py openapi.json --output lint.json

- name: "breaking-change-detection"
  run: python scripts/breaking_change_detector.py openapi-v1.json openapi-v2.json --exit-on-breaking

- name: "api-scorecard"
  run: python scripts/api_scorecard.py openapi.json --min-grade B
```
