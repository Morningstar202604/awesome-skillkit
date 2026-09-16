---
name: feature-flags-architect
description: >-
  Audit, plan, and govern feature flags across their full lifecycle (classify → ship → ramp → retire). Use when the user asks to 配置功能开关 / 灰度发布 / 开关治理 / feature flag / 上线开关 / add a flag / ship behind a flag / rollout plan / kill switch / stale flags / flag debt / LaunchDarkly / GrowthBook / Statsig / Unleash / Flipt. Ships stdlib-only Python tools (flag_debt_scanner, rollout_planner, kill_switch_audit) plus 4 references on taxonomy, provider trade-offs, rollout strategies, and lifecycle. Do NOT use for writing the flag SDK calls inside application code.
license: Apache-2.0
compatibility: Reads project structure via Bash and git. Requires Python 3.8+ (stdlib only) to run the bundled scripts.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: ai-engineering
  verified-date: "2026-09-09"
---

# Feature Flags Architect

End-to-end discipline for feature flags: classify them, ship them, ramp them, and retire them. Most teams treat flags as throwaway `if`-statements; this skill treats them as a controlled lifecycle with measurable debt.

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 目标仓库路径 | 否 | `--repo`，默认当前目录 `.`；用于代码扫描与 git 引入时间判定 |
| 开关文档路径 | 否 | kill-switch 审计用 `--flag-doc`，如 docs/feature-flags.md；缺省则仅做代码侧扫描 |
| 人口老龄化参数 | 否 | flag_debt_scanner 的 `--max-age-days`（默认 90）、`--min-uses` |
| rollout 参数 | 否 | rollout_planner 的 `--population --target-percent --duration-days --strategy` |
| 输出格式 | 否 | `--format text\|json`，CI 用 `json` |

缺失时一次性问齐：
「请提供：①目标仓库路径（默认 `.`）②开关文档路径（kill-switch 审计需要，如 docs/feature-flags.md，无则跳过）③人口规模/目标比例/周期（rollout 用）④债务半衰期 `--max-age-days`（默认 90）。其余我用默认值；确认后开始。」

## 前置自检

- Python 3.8+ 可用：`python3 --version` → 输出版本号（如 `Python 3.11.0`）。若 `command not found` 或版本 <3.8 → 提示安装后 **STOP**。
- 三个脚本在盘：`test -f scripts/flag_debt_scanner.py && test -f scripts/rollout_planner.py && test -f scripts/kill_switch_audit.py` → 均存在；任一缺失 → **STOP** 并报告具体文件名。
- git 可用（用于定位 flag 引入时间）：在 `--repo` 内执行 `git rev-parse --is-inside-work-tree` → 输出 `true`。若非 git 仓库，债务扫描的"引入时间"判据降级为文件 mtime，需向用户说明该降级。

## 核心原则：flag 是生命周期，不是 `if`

```text
request → design → ship → ramp → cleanup → archive
```

跳过 cleanup 的 flag 会变成债务：死分支、过期默认值、未经测试的代码路径、不可控的爆炸半径。本技能的 3 个脚本强制推行该生命周期。

## 工作流

### 步骤 1：审计 flag 债务

```bash
python scripts/flag_debt_scanner.py --repo . --max-age-days 90 --format text
python scripts/flag_debt_scanner.py --repo . --max-age-days 60 --format json > debt.json
```

动作：扫描代码库，找出老于 `--max-age-days` 且使用频次低的 flag。
预期：输出 flag 名、age(天)、文件引用、建议动作；退出码 `0`；JSON 模式写入 `debt.json`。
若失败：`FileNotFoundError` → 检查 `--repo` 路径是否正确；`git` 报错 → 见前置自检降级说明。

### 步骤 2：设计渐进式 rollout

```bash
python scripts/rollout_planner.py --population 100000 --target-percent 100 --duration-days 14 --strategy ring
python scripts/rollout_planner.py --population 50000 --target-percent 25 --duration-days 7 --strategy linear
python scripts/rollout_planner.py --population 1000000 --target-percent 100 --duration-days 30 --strategy log
```

动作：由人口规模、目标比例、周期、策略生成分阶段发布排期。
预期：输出含日期、比例、预期用户数、中止判据、每阶段验证步骤的 markdown 表格。
若失败：`--strategy` 非法值 → 脚本报错并列出 `ring|linear|log|cohort`；参数缺失 → 报 `required argument`。

### 步骤 3：审计 kill switch 文档

```bash
python scripts/kill_switch_audit.py --repo . --flag-doc docs/feature-flags.md
python scripts/kill_switch_audit.py --repo . --flag-doc runbooks/flags.md --format json
```

动作：将代码中发现的 flag 与文档交叉核对，确认每个都有书面 kill switch 路径。
预期：报告缺失文档的 flag（FAIL）或缺失字段的 flag（WARN）；退出码 `0` 表示审计跑通（不代表全 PASS）。
若失败：`--flag-doc` 文件不存在 → `FileNotFoundError`，先创建文档再跑；作为 pre-merge 门禁使用。

### 步骤 4：选型 provider

见 `references/provider_comparison.md` 决策树。判定规则：
- <50 flag 且无定向 → DIY（配置文件或环境变量）
- 需要分析 + 实验 → Statsig 或 GrowthBook
- 合规/SOC2 审计日志 → LaunchDarkly
- 必须自托管（数据驻留/空气隔离）→ Unleash 或 Flipt

### 步骤 5：清理债务（季度）

```bash
python scripts/flag_debt_scanner.py --repo . --max-age-days 90 > debt.md
```

对每个命中项：确认已达 100% 或已 kill → 找引入它的 issue/PR 并取得 owner 同意 → 删死分支、移除 flag 配置 → 重跑 kill_switch_audit.py 应少一个 flag。最后在 CHANGELOG 写「Removed N stale flags」。

## 4 种 flag 类型（分类法）

不同 flag 类型有不同生命周期与归属。错分会产生债务。

| Type | Purpose | Typical lifespan | Owner | Cleanup trigger |
|---|---|---|---|---|
| **Release** | 在生产环境隐藏未完成功能 | days–weeks | Eng | 达到 100% rollout |
| **Experiment** | A/B 测试变体 | weeks | Product/Marketing | 测试结束，选定胜者 |
| **Operational** | 熔断器、性能开关、kill switch | months–years | Eng/SRE | 被自动扩缩/功能退役替代 |
| **Permission** | 按用户/账户/套餐的权益 | years (permanent) | Product | 套餐/角色移除 |

只有 Release 与 Experiment 应进入债务扫描观察名单；Operational 与 Permission 设计为长期存在。详见 `references/flag_taxonomy.md` 决策树。

## 3 个 Python 工具

三者均为 stdlib-only，可用 `--help` 查看完整参数。

### `flag_debt_scanner.py`

找出老于 `--max-age-days` 且低使用的 flag，建议清理候选。
**检测启发式：**
1. 在 `--repo` 中按常见 flag 调用模式匹配代码引用：
   - `flag("...")`, `isFlagEnabled("...")`, `featureFlag("...")`, `getFlag("...")`
   - `client.variation("...", ...)`, `unleash.isEnabled("...")`, `growthbook.feature("...")`
2. 对每个唯一 flag 标识，找最早引入它的 commit（`git log --diff-filter=A -S <name>`）。
3. 若引入时间 > `--max-age-days` 且使用处 ≤ `--min-uses` → 标记为 DEBT。

输出 flag 名、age(天)、文件引用、建议动作。JSON 模式对 CI 友好。

### `rollout_planner.py`

由人口规模、目标比例、周期、策略生成分阶段发布排期。
**策略：**
- `ring`：1% → 5% → 25% → 50% → 100%，均匀间隔。高风险发布默认。
- `linear`：每天恒定速率。中风险默认。
- `log`：前期快、尾部慢。有把握的低风险默认。
- `cohort`：按命名队列（internal → beta → free → paid → all）。

输出含日期、比例、预期用户数、中止判据、每阶段验证步骤的 markdown 表格。

### `kill_switch_audit.py`

将代码发现的 flag 与文档交叉核对，确认每个都有书面 kill switch 路径。
**检查项：**
1. 每个代码发现的 flag 在 `--flag-doc` 中有条目
2. 每个条目声明：owner、type、kill-switch trigger、monitoring dashboard
3. 报告缺文档的 flag（FAIL）或缺字段的 flag（WARN）

作为任何新 flag 上线前的 pre-merge 门禁。

## Provider 选型（5 + DIY）

| Provider | Best for | Pricing model | Lock-in risk | OSS option |
|---|---|---|---|---|
| **LaunchDarkly** | Enterprise, complex targeting, audit/compliance | Per-MAU, expensive | High | No |
| **GrowthBook** | Mid-market, A/B testing focused, OSS-friendly | Per-MAU + OSS | Low | Yes (self-host) |
| **Statsig** | Growth/product teams, advanced experimentation | Free tier + per-MAU | Medium | No |
| **Unleash** | OSS-first, self-hosted, dev-friendly | OSS + Enterprise | Low | Yes |
| **Flipt** | Lightweight, k8s-native, simple needs | OSS-only | None | Yes |
| **DIY** | <100 flags, no targeting, full control | None | None | N/A |

详见 `references/provider_comparison.md`。

## 参数速查表

| 脚本 | 参数 | 取值 | 说明 |
|------|------|------|------|
| flag_debt_scanner.py | `--repo` | 路径 | 待扫描仓库，默认 `.` |
| | `--max-age-days` | 整数 | 超过该天数的 flag 视为债务候选，默认 90 |
| | `--min-uses` | 整数 | 使用处 ≤ 该值才标记，默认由脚本定 |
| | `--format` | `text\|json` | 输出格式，CI 用 `json` |
| rollout_planner.py | `--population` | 整数 | 总用户/请求规模 |
| | `--target-percent` | 0–100 | 目标覆盖率 |
| | `--duration-days` | 整数 | 发布周期天数 |
| | `--strategy` | `ring\|linear\|log\|cohort` | 发布曲线 |
| kill_switch_audit.py | `--repo` | 路径 | 代码侧扫描根 |
| | `--flag-doc` | 路径 | 开关文档（如 docs/feature-flags.md） |
| | `--format` | `text\|json` | 输出格式 |

## 失败处置表

| 现象/错误 | 原因 | 处置 |
|-----------|------|------|
| `python3: command not found` 或版本 <3.8 | Python 未装/过旧 | 安装 Python 3.8+ 后重跑 |
| `FileNotFoundError: <脚本>` | 脚本缺失 | 确认 `scripts/` 完整，缺失则 STOP 报告 |
| `git rev-parse` 报错 | 非 git 仓库 | 债务扫描降级为文件 mtime，提示用户 |
| `<flag-doc> not found` | 文档路径错 | 先创建/修正 `--flag-doc` 路径 |
| kill_switch_audit 报 FAIL | 有 flag 无 kill switch 文档 | 补文档条目（owner/type/trigger/dashboard）后重跑 |
| debt.json 为空 | 无超期 flag | 正常，无需清理 |

## 交付标准

成功定义：新 flag 100% 通过 `kill_switch_audit.py`；`flag_debt_scanner.py --max-age-days 90` 全仓返回 ≤5 个过期 flag；每个 flag 有书面 owner、type、kill switch；Release flag 自 100% 起平均 60 天内退役。
产物命名/位置：债务报告 `debt.md` 或 `debt.json`（用户指定路径）；rollout 排期直接输出到对话或用户指定文件。
完整性验证：重跑对应脚本退出码为 `0` 且 FAIL 数为 0。

## 参考

- `references/flag_taxonomy.md` —— 分类/选型时读：4 类 flag 决策树、归属、生命周期
- `references/provider_comparison.md` —— 选型 provider 时读：5 家 + DIY 取舍
- `references/rollout_strategies.md` —— 设计 ramp 时读：ring/linear/log/cohort/geo、中止判据、监控
- `references/flag_lifecycle.md` —— 设计 lifecycle/清理时读：request → design → ship → ramp → cleanup → archive

## Slash command

`/flag-cleanup` — 在当前仓库跑完整清理流程：扫描债务、生成移除计划、审计 kill switch。

## Asset 模板

- `assets/flag_request_template.md` — 新 flag 申请填报表（name、owner、type、kill switch、rollout plan）

## 反模式

- **`if (FLAG_FOO)` 出现在 50 处且无期限** — 应是 Permission flag + 运行时配置，而非 Release flag
- **flag 无 owner** — 原作者离职后无人清理
- **未记录 kill switch** — 功能出错时无人知如何禁用
- **A/B 测试跑了 6 个月** — 选定胜者，无限期运行即债务
- **用 flag 做外观微调** — 应通过部署而非 flag 发布
