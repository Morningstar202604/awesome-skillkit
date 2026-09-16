---
name: tech-debt-tracker
description: "Scan codebases for technical debt, score severity, track trends, and generate prioritized remediation plans. Use when users mention tech debt, code quality, refactoring priority, debt scoring, cleanup sprints, or code health assessment. Also use for legacy code modernization planning and maintenance cost estimation. 当用户要求 梳理技术债 / 债项分级 / 还债计划 时使用。 Do NOT use for performing the refactors it tracks."
license: Apache-2.0
compatibility: Pure prompt-based; may read project structure via Bash.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: code-quality
  pattern: single-task
  tier: powerful
  verified-date: "2026-09-09"
---

# 技术债追踪器

扫描代码库中的技术债信号，用 cost-of-delay 框架给待办排序，并基于带日期的快照追踪趋势。本技能只追踪和规划还债工作——不执行重构。

流水线：`debt_scanner.py` → `debt_prioritizer.py` → `debt_dashboard.py`。扫描器的 JSON 输出直接喂给排序器；带日期的清单快照喂给看板。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 代码库目录 | 必需 | 传给扫描器的路径；必须存在且可读 |
| 排序框架 | 可选 | `cost_of_delay`（默认）、`wsjf` 或 `rice` |
| `--team-size` | 可选 | 冲刺分配用的人数（prioritizer 默认：5） |
| `--sprint-capacity` | 可选 | 冲刺容量（小时）（prioritizer 默认：80） |
| 快照历史 | 可选 | 带日期的清单 JSON（`debt_YYYY-MM-DD.json`），趋势追踪用 |

输入缺失时一次性问齐："请提供：① 要扫描的代码库目录 ② 框架选择（cost_of_delay/wsjf/rice，默认 cost_of_delay）③ 冲刺分配用的人数与容量 ④ 如有历史快照文件一并给出，做趋势分析。其余按默认处理。"

## 前置自检

逐条探测，任一失败 → 给出修复方法并 STOP：

```bash
python3 --version   # 预期 3.8+；失败：安装 python3
python3 scripts/debt_scanner.py --help >/dev/null 2>&1       # 预期退出码 0；失败：脚本缺失 → 检查技能目录
python3 scripts/debt_prioritizer.py --help >/dev/null 2>&1
python3 scripts/debt_dashboard.py --help >/dev/null 2>&1
test -d <codebase-directory>   # 预期退出码 0；失败：路径不对 → 向用户要正确目录
```

## 工作流

### 步骤 1：扫描代码库

```bash
python3 scripts/debt_scanner.py /path/to/codebase --format json --output debt_inventory.json
```

预期：生成 `debt_inventory.json`，含 `scan_metadata`、`summary`、`debt_items[]`、`file_statistics` 与 `recommendations`。把 `summary` 计数报给用户。演练：把扫描器指向 `assets/sample_codebase`。若失败：`debt_items[]` 为空 → 目录里可能没有可扫描的源码文件；确认路径里是代码，不只是文档/配置。

### 步骤 2：给待办排序

```bash
python3 scripts/debt_prioritizer.py debt_inventory.json --framework wsjf --team-size 6 --sprint-capacity 20 --format json --output debt_priorities.json
```

预期：`debt_priorities.json` 含 `prioritized_backlog`（自上而下执行）、`sprint_allocation`（直接贴进冲刺计划）与 `insights`。若失败：清单 JSON 非法 → 重跑步骤 1；框架名未知 → 从 `cost_of_delay`、`wsjf`、`rice` 中选一。

### 步骤 3：追踪时间趋势

保留带日期的快照（`debt_YYYY-MM-DD.json`），然后：

```bash
python3 scripts/debt_dashboard.py --input-dir snapshots/ --period monthly --format both --output debt_dashboard
```

或显式传文件：

```bash
python3 scripts/debt_dashboard.py assets/historical_debt_2024-01-15.json assets/historical_debt_2024-02-01.json --period monthly
```

预期：看板输出趋势方向和一份可直接汇报的摘要。用它验证清理冲刺是否真的降了债。若失败：`--input-dir` 里没有清单文件 → 改为位置参数显式传文件；快照命名不一致 → 文件名必须含可解析的日期。

### 步骤 4：验证闭环

还债冲刺结束后：重跑步骤 1 生成新快照，把它纳入步骤 3 重跑，断言目标类别的计数确实下降。看板没动的清理等于返工，不算还债。

## 债务严重度评分

| 因子 | 权重 | 说明 |
|------|------|------|
| Impact | 30% | 影响多少用户/服务？ |
| Risk | 25% | 有安全、数据丢失或合规风险吗？ |
| Effort | 20% | 修复工作量多大？（反向计分） |
| Frequency | 15% | 多久引发一次问题？ |
| Age | 10% | 这笔债存在多久了？ |

框架指南（WSJF、RICE、分类体系）在下方 references 里——用户质疑某个评分或追问特定框架的依据时读。

## 失败处置表

| 症状 / 报错 | 原因 | 修复 |
|-------------|------|------|
| 扫描器输出 `debt_items[]` 为空 | 目录里没有可扫描的源码文件 | 确认路径含代码；向用户要正确目录 |
| 排序器拒绝清单文件 | 清单 JSON 损坏或被截断 | 重跑步骤 1，检查 `scan_metadata` 里的扫描错误 |
| 看板不输出趋势 | 只有一份快照 | 至少收集两份带日期快照，或先生成一份日后对比 |
| `--output` 文件没生成 | `--format both` 写的是带后缀的文件（如 `.json`/`.txt`） | 在输出基名旁边找两种扩展名 |
| 用户觉得评分不对 | 默认权重不匹配团队情况 | 用扫描器 `--config` JSON 调整，或在报告里人工覆盖优先级 |

## 交付标准

- 成功定义：清单（计数 + 逐项债务）、按优先级排序且含冲刺分配的待办，以及——若有历史——趋势摘要。
- 产物命名：`debt_inventory.json`、`debt_priorities.json`、`debt_dashboard.json` / `debt_dashboard.txt`，快照 `debt_YYYY-MM-DD.json`。
- 保存位置：工作目录根；构建历史时用 `snapshots/` 目录。
- 完整性核验：清单 `summary` 总数与 `len(debt_items)` 一致；待办每一条都能回溯到清单条目 ID；趋势输出覆盖所有传入的快照文件。

## 安全红线

- 对目标代码库只读：扫描器绝不修改被扫描的文件。不要借本技能"顺手"修债项。
- 快照文件是审计历史——绝不覆盖已有的带日期快照；要存就建新的。
- 范围：只做分析与规划。执行重构、依赖升级或清理属于其他技能，且需用户明确确认。

## 参考

- `references/debt-frameworks.md` — 选择或解释评分框架时读
- `references/debt-classification-taxonomy.md` — 用户对某条债项的分类有异议时读
- `references/prioritization-framework.md` — 产出或捍卫待办顺序时读
- `references/stakeholder-communication-templates.md` — 写高管摘要或冲刺计划沟通稿时读
