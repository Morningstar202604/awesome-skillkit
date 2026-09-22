---
name: incident-commander
description: "Comprehensive incident response framework from detection through resolution and post-incident review. Battle-tested SRE/DevOps practices: severity classification, timeline reconstruction, structured post-incident analysis. Use when declaring an incident, coordinating multi-team response during an outage, leading a post-mortem, or setting up on-call practices for a new service. 当用户要求 处理线上故障 / 事故指挥 / 应急响应 时使用。 Do NOT use for performing the remediation actions it assigns."
license: Apache-2.0
compatibility: Pure prompt-based; may read project structure via Bash.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: incident
  pattern: single-task
  tier: powerful
  verified-date: "2026-09-09"
---

# Incident Commander

线上可用性/可靠性事故的指挥与复盘框架：定级、时间线重建、结构化事后复盘（PIR）。本技能负责编排与决策，**不替你执行它分派的修复动作**。

> 区分：本技能处理可用性事故（宕机、降级、失败发布）。安全事件（勒索、入侵、数据外泄、IOC 取证）→ 路由到 `incident-response`。两者都用 SEV1–SEV4，但本技能按业务影响（用户/营收/SLA）定级。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 事故描述 / 症状 | 必需 | 自由文本或 JSON（影响用户比例、业务影响等级） |
| 时间线事件源 | 条件必需 | 生成时间线时：`--input` 事件 JSON |
| 事故数据文件 | 条件必需 | 生成 PIR 时：`--incident` 数据 JSON + `--timeline` markdown |
| 输出路径 | 可选 | `--output` 文件名；不传则 stdout |
| RCA 方法 | 可选 | `--rca-method`：`5whys`/`fishbone`/`timeline`（默认见脚本） |

缺失输入时一次性问齐：「请提供：①事故描述（影响用户比例 + 业务影响 high/medium/low）②是否需要重建时间线（需事件 JSON）③是否需要生成 PIR（需事故数据 + 时间线）④输出文件名。其余按默认执行。」

## 前置自检

```bash
# 自检：python3 scripts/incident_classifier.py --help / timeline_reconstructor.py / pir_generator.py 均预期退出码 0
```

## 工作流

### 步骤 1：定级（SEV）

```bash
python3 scripts/incident_classifier.py --input assets/simple_incident.json --format text   # 随包样例事件；你的真实输入换成 incident.json
# 管道用法：echo '{"description": "…", "affected_users": "80%", "business_impact": "high"}' | python3 scripts/incident_classifier.py
```

预期：脚本输出 SEV 等级与建议响应团队/初始动作。
若失败：输入缺 `affected_users`/`business_impact` → 补全字段或改用自由文本 + `--format text`；JSON 解析错 → 核对字段名。

严重度速查（完整版见 `references/incident_severity_matrix.md`）：

| 等级 | 定义 | 指挥就位 | 对外通报 |
|------|------|---------|---------|
| SEV1 | 全量用户/关键业务不可用、数据丢失 | ≤5 min | ≤15 min |
| SEV2 | >25% 用户明显降级 | ≤30 min | ≤30 min |
| SEV3 | 局部、有临时绕过 | ≤2 h（工作时段） | 里程碑时 |
| SEV4 | 外观/文档/监控缺口 | 1–2 工作日 | 无需 |

### 步骤 2：重建时间线

```bash
python3 scripts/timeline_reconstructor.py --input assets/sample_timeline_events.json --output timeline.md
python3 scripts/timeline_reconstructor.py --input assets/simple_timeline_events.json --detect-phases --gap-analysis
```

预期：输出按时间排序的事件叙述，含阶段划分与空白分析；`--output` 时写入文件。
若失败：事件源 JSON 格式错 → 参照 `assets/sample_timeline_events.json` 校验 schema。

### 步骤 3：生成 PIR（复盘）

```bash
python3 scripts/pir_generator.py --incident assets/sample_incident_pir_data.json --timeline assets/sample_timeline.md --output pir.md   # 随包样例（timeline.md 由上文 reconstructor 对样例事件生成）
python3 scripts/pir_generator.py --incident assets/sample_incident_pir_data.json --rca-method fishbone --action-items
```

预期：结构化 PIR，含 RCA（按所选方法）与可追踪的后续行动项。
若失败：缺 `--timeline` → 先跑步骤 2；`--rca-method` 非法 → 用 `5whys`/`fishbone`/`timeline` 之一。

## 沟通节奏

按干系人与严重度确定通报频率（完整矩阵见 `references/sla-management-guide.md`）：

| 干系人 | SEV1 | SEV2 | SEV3 |
|--------|------|------|------|
| 工程负责人 | 实时 | 30 min | 4 h |
| 高管 | 15 min | 1 h | 当日 |
| 客户 | 15 min | 1 h | 可选 |

初始通报模板结构（完整模板见 `references/communication_templates.md`）：

```text
Subject: [SEV{severity}] {Service Name} - {Brief Description}
Incident Details: Start Time / Severity / Impact / Current Status
Affected Services / Symptoms / Initial Assessment
Incident Commander / Technical Lead / SMEs
Next Update / Status Page / War Room
```

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| `--format` | `text`/`json` | 分类器输出形态 |
| `--input` | JSON 路径 | 时间线事件源 |
| `--output` | 文件路径 | 时间线/PIR 写出 |
| `--detect-phases` / `--gap-analysis` | flag | 时间线阶段与空白分析 |
| `--incident` | JSON 路径 | PIR 的事故数据 |
| `--timeline` | md 路径 | PIR 的时间线输入 |
| `--rca-method` | `5whys`/`fishbone`/`timeline` | RCA 框架 |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------------|------|------|
| 分类器 JSON 解析失败 | 字段缺失/格式错 | 补全 `affected_users`/`business_impact` 或改 `--format text` |
| 时间线 `--input` 格式错 | schema 不符 | 对照 `assets/sample_timeline_events.json` |
| PIR 缺 `--timeline` | 未先建时间线 | 先跑步骤 2 |
| `--rca-method` 非法 | 拼写错 | 用三选一合法值 |

## 交付标准

成功定义：产出 SEV 定级 + 时间线 md + PIR md（含 RCA 与 action items），且 action items 有负责人与截止日期。
产物命名：`timeline.md`、`pir.md`（或用户指定名）。
保存位置：事故跟踪系统/版本库；PIR 广泛共享。
验证完整性：PIR 中每条 action item 可追踪；时间线覆盖检测→缓解→恢复全段；定级与 `incident_severity_matrix.md` 一致。

## 安全红线

- **本技能只编排不修复**：绝不执行它分派的缓解/回滚命令。实际修复（回滚、扩缩容、改配置）由值班工程师在 war room 执行，并经用户确认。
- 优先用 feature-flag 禁用而非代码回滚；数据库仅在非破坏性迁移时回滚（前向迁移优先）。
- 复盘坚持 blameless（无指责）文化：聚焦系统失效而非个人失误。

## 参考

- `references/incident-response-framework.md` —— 完整响应流程与指挥角色
- `references/incident_severity_matrix.md` —— SEV1–SEV4 定义与响应要求
- `references/communication_templates.md` —— 初始/高管/客户通报模板
- `references/rca_frameworks_guide.md` —— 5 Whys / Fishbone / Timeline RCA 用法
- `references/sla-management-guide.md` —— SLA 与通报节奏矩阵
- `references/reference-information.md` —— 外部工具/术语速查
- `assets/incident_report_template.md` / `assets/runbook_template.md` —— 报告与 runbook 填空模板
