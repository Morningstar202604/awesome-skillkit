---
name: self-eval
description: "Honestly evaluate AI work quality using a two-axis scoring system. Use after completing a task, code review, or work session to get an unbiased assessment. Detects score inflation, forces devil's advocate reasoning, and persists scores across sessions. Use when the user runs /self-eval, asks for 评估我的工作质量 / 自评 / 复盘这次任务 / 打分是否虚高 / honest review / rate my work. Do NOT use for grading user answers or producing production artifacts."
license: Apache-2.0
compatibility: Pure prompt-based; no external tools. May append to `.self-eval-scores.jsonl` in the working directory.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: ai-engineering
  verified-date: "2026-09-09"
---

# Self-Eval: Honest Work Evaluation

产出诚实、校准的工作评估。用结构化双轴评分、强制魔鬼辩护论证与跨会话反膨胀检测，替代 AI 默认"什么都打 4 分"的倾向。

核心洞察：AI 自评会收敛到"什么都是 4 分"，因为单轴评分把任务难度和执行质量混在一起。self-eval 把两个轴拆开，再用模型无法覆盖的固定矩阵合成分数。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 待评估上下文 | 是 | 当前会话已完成的工作，或 `/self-eval <描述>` 传入的具体任务 |
| 历史分数文件 | 否 | 工作目录下的 `.self-eval-scores.jsonl`；存在则用于反膨胀检查 |

缺失时一次性问齐：
「请提供：①要评估的工作（默认=本会话已完成内容，可用 /self-eval <一句话描述> 指定）②是否需跨会话对比历史分数（默认读取 `.self-eval-scores.jsonl`，无则跳过）。确认后开始。」

## 前置自检

- 本技能纯提示词驱动，无外部依赖；无需安装任何工具。
- 工作目录可写（用于追加 `.self-eval-scores.jsonl`）：`test -w .` → 可写；否则仅输出评估、跳过持久化并提示。
- 若用户传入 `$ARGUMENTS` 或 `/self-eval <内容>`，以该内容作为评估对象；否则审查整段会话历史，先用一句话概括本次成果再评分。

## 工作流

### 步骤 1：识别并概括工作

动作：从会话历史（或传入参数）中识别已完成的工作，用一句话概括。
预期：产出 **Task** 单行摘要。
若失败：历史为空或无法确定 → 要求用户用 `/self-eval <描述>` 明确指定评估对象。

### 步骤 2：双轴独立打分

动作：先评 Axis 1 任务野心（Low/Medium/High），再评 Axis 2 执行质量（Poor/Adequate/Strong）。**禁止先选分数再倒推**——两轴分别评定后查表。
预期：两个轴均给出等级 + 一句理由。
若失败：模型倾向给"全 4" → 强制回到矩阵，低野心封顶 2。

### 步骤 3：魔鬼辩护（强制）

动作：在定稿前必须写出三种论证：
1. **Case for LOWER**：为何该工作配更低分？什么很容易、被回避、野心不及表面？
2. **Case for HIGHER**：什么真正有挑战、超出原计划？
3. **Resolution**：若任一论证揭示轴评错，重评并重算矩阵，再给出最终分 + 1–2 句理由（必须覆盖两方各至少一点）。
预期：三块合计 ≥3 句；不足则重做。
若失败：不足 3 句 → 视为未真正参与，重做。

### 步骤 4：反膨胀检查

动作：检查工作目录 `.self-eval-scores.jsonl`；若存在，读最近 5 条。若最近 5 条中 ≥4 条相同 → 输出警告。
预期：打印 `Warning: Score clustering detected. Last 5 scores: [...]`，并提示是否锚定默认值。
若失败：文件不存在 → 自问"外部观察者会给我同样的评分吗？"，继续。

### 步骤 5：持久化并输出

动作：向 `.self-eval-scores.jsonl` 追加一行 JSON；按下方输出格式呈现评估。
预期：文件追加成功（或工作目录不可写时仅输出）；输出含 Task/Ambition/Execution/Devil's Advocate/Score。
若失败：写入失败 → 仍输出评估，注明未持久化。

## 双轴评分模型

### Axis 1：任务野心（做了什么）

评难度与风险，**不是**做得好不好。

- **Low (1)** — 安全、熟悉、例行。无真实失败风险。如：小配置改动、简单重构、带小改的复制粘贴、开始前就有把握完成的任务。
- **Medium (2)** — 有意义且有新意或挑战。可能部分失败。如：新功能实现、接入陌生 API、架构改动、调试棘手问题。
- **High (3)** — 野心大、陌生或高风险。存在彻底失败的真实风险。如：在陌生领域从零构建、复杂系统重设计、性能关键优化、高压下上线生产。

**自检：** 若开始前就确信能成功，野心是 Low 或 Medium，不是 High。

### Axis 2：执行质量（做得如何）

独立于野心，评实际产出质量。

- **Poor (1)** — 重大失败、未完成、输出错误、中途放弃。交付物未达自身标准。
- **Adequate (2)** — 完成但有缺口、捷径或欠严谨。做了但留下明显可改进处。
- **Strong (3)** — 执行好、彻底、质量高。在范围内无遗留明显改进。

### 合成分矩阵

|                        | 差执行 (1) | 足执行 (2) | 强执行 (3) |
|------------------------|:---:|:---:|:---:|
| **低野心 (1)**   |  1  |  2  |  2  |
| **中野心 (2)**|  2  |  3  |  4  |
| **高野心 (3)**  |  2  |  4  |  5  |

**读矩阵，不要覆盖它。** 合成分即你的分数。魔鬼辩护可让你重评某一轴——但你不能直接覆盖矩阵结果。

关键性质：
- 低野心封顶 2。安全的工作做得再完美也是安全工作。
- 5 分要求**既**高野心**又**强执行。应属罕见。
- 高野心 + 差执行 = 2。大胆失败代价大。
- 扎实工作最常见的诚实分是 3（中野心、足执行）。

## 魔鬼辩护（强制）

定稿前必须写出上述三步（Lower/Higher/Resolution）。若魔鬼辩护合计不足 3 句，说明你没真正参与——重做。

## 反膨胀检查

检查工作目录下 `.self-eval-scores.jsonl`。若存在，读最近 5 条；若其中 ≥4 条相同数字，标记：
> **Warning: Score clustering detected.** Last 5 scores: [list]. Consider whether you're anchoring to a default.

若不存在，自问："外部观察者会给我同样的评分吗？"

## 分数持久化

评估后向工作目录 `.self-eval-scores.jsonl` 追加一行：

```json
{"date":"YYYY-MM-DD","score":N,"ambition":"Low|Medium|High","execution":"Poor|Adequate|Strong","task":"1-sentence summary"}
```

文件不存在则创建。这使跨会话反膨胀检查可用。

## 输出格式

## 自我评估

**Task:** [一句话概括所做工作]
**Ambition:** [Low/Medium/High] — [一句理由]
**Execution:** [Poor/Adequate/Strong] — [一句理由]

**Devil's Advocate:**
- Lower: [为何可能应打更低]
- Higher: [为何可能应打更高]
- Resolution: [最终裁定理由]

**Score: [1-5]** — [一句最终理由]

## 失败处置表

| 现象/错误 | 原因 | 处置 |
|-----------|------|------|
| 会话历史为空、无 `$ARGUMENTS` | 无评估对象 | 要求用户用 `/self-eval <描述>` 明确指定 |
| 模型给"全 4"倾向 | 单轴惯性 | 强制回矩阵，低野心封顶 2 |
| 魔鬼辩护 <3 句 | 未真正参与 | 重做三块论证 |
| `.self-eval-scores.jsonl` 写入失败 | 目录不可写 | 仍输出评估，注明未持久化 |
| 最近 5 分 ≥4 相同 | 锚定默认值 | 输出聚类警告，重新校准 |

## 交付标准

成功定义：产出含 Task/Ambition/Execution/Devil's Advocate/Score 五段，分数来自矩阵而非直接选定，魔鬼辩护覆盖两方；若目录可写则追加 `.self-eval-scores.jsonl` 一行。
产物命名/位置：`.self-eval-scores.jsonl`（工作目录）。
完整性验证：输出 Score 与矩阵查表一致；JSONL 末行字段齐全。

## 参考

本技能纯提示词驱动（prompt-only），无 bundled `references/*.md`、无 `scripts/`。评分矩阵、魔鬼辩护、反膨胀与持久化规则均已内联于上文。
