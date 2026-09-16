---
name: paper-topic-selector
description: "Identify research gaps and select paper topics. Scans recent literature trends, finds underexplored areas, evaluates novelty/feasibility/impact. Outputs a ranked list of viable research directions. Use at the start of a research project. 当用户要求 选论文选题 / 找研究空白 / 投稿选刊 / 评估选题可行性 / research gap / 选题打分 时使用。 Do NOT use for writing the paper itself."
license: Apache-2.0
compatibility: Gap analysis is prompt-based (may call web-search for trend scanning). Heuristic scoring via scripts/topic_selector.py, stdlib only. No API keys required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-09"
---

# Paper Topic Selector

Find viable research directions by identifying gaps, then rank and gate them.

> 诚实声明：两条评估轨道，勿混淆——① 工作流中的 Novelty/Feasibility/Impact 评分由模型按下方评分表**分析判断**；② `scripts/topic_selector.py` 的评分是**关键词启发式**（命中 `novel/unexplored` 等词就加分），只适合快速粗筛，不得当真实查新结论引用。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 研究领域 | 是 | `--topic "LLM agent coordination"`（脚本用）或自然语言给出 broad area（工作流用） |
| 子方向 | 否 | 缩小扫描范围，如 "multi-agent coordination" |
| 资源约束 | 否 | JSON，如 `--constraints '{"time":"3mo","gpu":"1xA100"}'`（时间/算力/目标会议） |
| 已知论文 | 否 | 已读过的相关论文清单，避免重复推荐 |
| 输出路径 | 否 | `--output topics.json`，缺省打印到 stdout |

缺失时一次性问齐：「请提供：① broad area（和可选 sub_area）② 约束（时间/算力/目标 venue）③ 已知论文清单 ④ 是否用启发式脚本粗筛 `topic_selector.py` ⑤ 是否落盘 `--output`。」

## 前置自检
```bash
python3 --version                                 # 预期 >= 3.8（仅用脚本时需要），否则报错并 STOP
test -f scripts/topic_selector.py && echo OK      # 预期打印 OK，否则脚本缺失 STOP
```
纯工作流模式无脚本依赖；若联网扫描趋势，网络不可达 → 转用本地已知文献作 gap 分析并在产出中注明「未联网核实」。

## 工作流

### 步骤 1：（可选）启发式粗筛
```bash
python3 scripts/topic_selector.py --topic "LLM agent coordination" --constraints '{"time":"3mo","gpu":"1xA100"}'
python3 scripts/topic_selector.py --topic "zero-shot coordination" --output topics.json
```
预期：输出 JSON 含 `topic`、`scores{novelty,feasibility,impact}`、`recommendation: "go"|"risky"`（`feasibility >= 0.7` 为 go）、`next: "Run lit-review to verify gap exists"`。
若失败：`--constraints` 非法 JSON → 脚本返回 rc=2 与 `status: "error"`，校验 JSON 后重试。

### 步骤 2：扫描文献并识别 gap

1. Scan recent papers in area (last 6 months)
2. Identify what's been done
3. Find what's NOT done (gap)

预期：每个候选 gap 能指出「谁做了什么 / 缺什么」；产出格式见下例（`ranked_topics[]` + `rejected[]`）。
若失败：领域太宽找不到边界 → 先收窄 sub_area 再扫描；联网失败 → 标注「未联网核实」后基于已知文献继续。

### 步骤 3：按评分表排序并对照约束

| Factor | Weight | What to Check |
|--------|--------|---------------|
| Novelty | 40% | Is the specific angle unexplored? (not just the general area) |
| Feasibility | 30% | Can it be done in the time/resource budget? |
| Impact | 20% | Would reviewers care? Is there a clear evaluation? |
| Buildability | 10% | Can results build on top of existing code? |

预期：每个 topic 有 4 项打分与理由；`feasibility` 与用户约束（时间/算力）一致；被否掉的进 `rejected[]` 并写明 reason。
若失败：打分无依据 → 必须引用具体论文/事实支撑，否则降级进 `rejected`。

### 步骤 4：产出 ranked list

预期：输出 `{"ranked_topics": [...], "rejected": [...]}`，每项含 `rank`/`topic`/`novelty`/`feasibility`/`impact`/`gap`，推荐项附 `baseline` 与 `contribution_angle`（参考格式如下，字段可按实际增删）。
若失败：清单为空 → 放宽 area 或改用 lit-review 先做系统调研。

```json
{
  "ranked_topics": [
    {
      "rank": 1,
      "topic": "Conflict resolution in LLM agent teams without shared memory",
      "novelty": 0.85,
      "feasibility": 0.7,
      "impact": 0.8,
      "gap": "Existing work assumes shared context; zero-shot coordination unexplored",
      "baseline": "AgentBench, CAMEL",
      "contribution_angle": "Propose protocol-based coordination + evaluate with 5 benchmarks"
    }
  ],
  "rejected": [
    {"topic": "...", "reason": "Already covered by PaperX (2025)"}
  ]
}
```

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| `--topic` | 字符串 | 研究方向（脚本必填） |
| `--constraints` | JSON 字符串 | 资源约束，键如 `time`/`gpu`；`A100/H100/8` 会提升可行性分 |
| `--output` | 路径 | 结果 JSON 输出路径，缺省打印 stdout |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------------|------|------|
| rc=2，`status: "error"` | `--constraints` 非法 JSON | `python3 -c "import json;json.loads(open('<f>').read())"` 先自检 |
| `recommendation: "risky"` | 启发式判定复杂度过高/资源不足 | 视为粗筛信号，回步骤 3 用评分表人工复核 |
| gap 全被 rejected | 领域已饱和 | 换 sub_area 或读 `references/gap-finding.md` 换找法 |
| 分数与直觉严重不符 | 启发式只看关键词 | 以步骤 3 评分表结论为准，脚本分仅参考 |

## 交付标准

成功定义：产出 ranked list，每项四因子有分有据；被否项有 reason。
产物命名：`topics.json`（若指定 `--output`）或直接输出文本。
保存位置：调用方当前目录或 `--output` 指定路径。
验证方法：`python3 -c "import json;d=json.load(open('<output>'));assert d['ranked_topics']"` 通过（脚本产物）；工作流产出的分数必须能在正文找到依据句。

## 参考

- [references/gap-finding.md](references/gap-finding.md) — **步骤 2 前读**：系统化找 gap 的方法（分类维度、检索式写法）
- [references/venue-matching.md](references/venue-matching.md) — **步骤 3 对照 target_venue 时读**：各 venue 偏好与匹配度判断

## 链路位置

上游无前置；产出交 lit-review 验证 gap 是否真实存在，确定选题后进实验规划（experiment-runner）。
