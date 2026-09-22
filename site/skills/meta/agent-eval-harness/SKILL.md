---
name: agent-eval-harness
description: >
  Quantify "is the AI agent behaving correctly" into a 0-100 score with a
  verifiable rubric, so you stop relying on gut feel when you ship an agent.
  Use when the user asks to 评估 agent / 给 agent 打分 / eval 用例 / LLM 行为验证
  / 防幻觉怎么测 / 回归 agent 行为 / "怎么证明 agent 没退化". Do NOT use for
  writing the agent itself (use skill-author / webapp-e2e-harness) or for pure
  unit tests of code (use tdd-guide / api-test-suite-builder).
license: Apache-2.0
compatibility: 纯 Python 离线脚本（只写文件，不发网络请求）；模式 B 的 LLM-as-judge 只产出可复制的评审 prompt，真正调模型由用户自己接（凭证走 env）
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: programming
  pattern: script
  tier: standard
  verified-date: "2026-09-20"
---

# Agent Eval Harness（Agent 行为量化评分）

把"AI agent 到底对不对"从**玄学**变成**可回归、可门禁**的数字：5 个可自动判定
的维度（结构 / 接地 / 无幻觉 / 自洽 / 安全）加权成 0-100 分，每个用例给出
`pass / fail / warn` 判定 + 失败维度明细。

核心判断：**agent 最大成本不是"写得出来"，是"改了 prompt 之后悄悄退化了没人发现"**。
一个能跑、能复用、能对 CI 出退码的评分器，比一次性的"看着挺好"值钱得多。
本技能把评分标准写死成脚本，让"行为对不对"可重复验证——正是 skill 该干的
**固定步骤**活，而不是让模型自由发挥。

> 红线：脚本**离线**（只写文件，不发网络请求）；默认 dry-run，`--write` 才落盘；
> 凭证只走 env（模式 B 才涉及，且只产出 prompt 文本，不替用户调模型）。

## 输入清单

| 输入 | 必填 | 说明 |
|---|---|---|
| 用例文件（JSONL） | 是 | 每行 `{"prompt","response","expects":{...}}`，见下 |
| `--index` | 否 | 评第几行（0-based），默认 0 |
| `--mode` | 否 | `offline`（默认）/ `judge`（LLM-as-judge prompt） |
| `--weights-json` | 否 | 覆盖维度权重（JSON object） |
| `--forbidden-json` | 否 | 追加禁用串（JSON array） |

`expects` 字段（均可选，缺省走宽松判分）：

| 字段 | 作用 | 命中后 |
|---|---|---|
| `must_contain_table` | 要求含 markdown 表格 | format 加分 |
| `must_contain_code` | 要求含代码块 ``` | format 加分 |
| `min_length` | 输出最小字符数 | format 加分 |
| `must_include` | 必须包含的关键词列表 | 漏掉→grounding 风险 |
| `evidence` | 防幻觉：response 应命中的证据串 | grounding 维度 |
| `forbidden` | 危险/禁用串（如 `rm -rf /`） | no_hallu/safety 扣分 |
| `conflict_pairs` | 互斥值对 `[["a","b"]]`，同现即矛盾 | consistency 归零 |

## 前置自检

1. 用例是不是 JSONL、每行合法 JSON？（`python3 -c "import json,sys;[json.loads(l) for l in open('c.jsonl') if l.strip()]"` 不报错即可）
2. 想验防幻觉就填 `evidence`；想让"危险操作"扣分就填 `forbidden`。不填=宽松模式。
3. 模式 B 不需要本地 LLM，只生成 prompt 文本；真要调模型由用户接。

## 工作流

```bash
# 1. 干跑：离线规则评分第 0 个用例（打印 JSON 到 stdout）
python3 scripts/eval_harness.py --input assets/sample-cases.jsonl --index 0   # 随包样例（离线规则评分）；你的用例换成 cases.jsonl

# 2. 真出报告（可挂 CI 门禁）
# python3 scripts/eval_harness.py --input cases.jsonl --index 3 \
#   --weights-json config/weights.json --out reports/case3.json --write

# 3. LLM-as-judge：生成可复制的评审 prompt（不替用户调模型）
# python3 scripts/eval_harness.py --input assets/sample-cases.jsonl --index 0   # 随包样例（离线规则评分）；你的用例换成 cases.jsonl --mode judge --out judge.md
```

`expects` 怎么填、各维度判分逻辑、CI 门禁接法：
见 [references/eval-rubric.md](references/eval-rubric.md)。

## 交付标准

- 每个用例输出 `score(0-100)` + `verdict(pass/fail/warn)` + `failed_dimensions`
- `evidence` 填了则 grounding 维度**必须**参与判分（防幻觉真正生效）
- `forbidden` 命中则 no_hallu/safety 扣分，`failed_dimensions` 非空
- 模式 B 产出的 prompt 里搜不到明文凭证（全走 env 占位）
- 脚本离线：dry-run 不调任何模型、不发任何网络请求

## 失败处置表

| 现象 | 根因 | 处置 |
|---|---|---|
| 全 `pass` 但你觉得 agent 在瞎编 | `evidence` 没填（宽松模式） | 填 `evidence`，让 grounding 真正咬住 |
| `consistency` 莫名归零 | `conflict_pairs` 两值同时出现在 response 里 | 核对 response，确认是否真矛盾；改用例 |
| 危险操作没扣分 | `forbidden` 串和实际措辞对不上 | 把实际危险串加进 `--forbidden-json` 或用例 `forbidden` |
| 评分数字漂移（同用例两次不同） | 脚本本身确定性，漂移来自**用例或权重**变了 | 固定 `--weights-json`，版本化用例文件 |
| 想接 LLM 判分却报错 401/404 | 凭证/endpoint 没设 | 模式 B 不替调模型；用户按 `judge.md` 里伪代码设 env |

## 参考

- 判分逻辑 / 维度语义 / CI 门禁：[references/eval-rubric.md](references/eval-rubric.md)
- 权重示例：`config/weights.example.json`

## 链路位置

- 上游：`webapp-e2e-harness`（e2e 跑出的 response 作为被评对象）/ 任意 agent 产出
- 下游：`ci-cd-pipeline-builder`（把 `verdict=fail` 接进 CI 做行为回归门禁）
- 平行：`skill-tester`（测单个 skill 能不能跑通；本技能测 agent 行为"对不对"，粒度不同）
