---
name: paper-topic-selector
description: "学术论文选题缺口识别与可行性打分工具。当用户提出一个模糊研究方向、疑问\"这个题行不行\"\"缺什么创新\"\"值不值得做\"\"能发什么刊\"时使用。适配 academic-topic-strategist，负责把模糊想法收敛成可落地的研究问题，输出缺口矩阵、创新点论证与五维可行性评分，并给出砍题/换题建议。也用于 选论文选题 / 找研究空白 / research gap / 投稿选刊 / 评估选题可行性 / 选题打分。不用于撰写论文正文本身。"
license: Apache-2.0
compatibility: Gap analysis is prompt-based (may call web-search for trend scanning). Heuristic scoring via scripts/topic_selector.py, stdlib only. No API keys required.
metadata:
  version: "2.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-21"
---

# Paper Topic Selector（选题缺口识别与可行性打分 SOTA）

识别研究空白 → 多候选按四因子排序 → 输出 `ranked_topics[]` 与带原因的 `rejected[]`。

> **诚实声明**：两条轨道勿混淆——① 工作流中的 Novelty/Feasibility/Impact 判断由模型按下方评分表**分析**；
> ② `scripts/topic_selector.py` 的 novelty 默认是**关键词启发式**（`novelty_source: "heuristic-keyword"`，
> `novelty_verified: false`），**不得当查新结论引用**。只有传入 `--lit-review-json` 且 gap 命中时，
> 才升级为 `novelty_source: "lit-review"` + `novelty_verified: true`。

本 skill 供「选题策略师」（academic-topic-strategist）使用，把一句模糊的研究冲动，拆成"有没有人做过、缺口在哪、我能不能做、做出来值不值"四张底牌。严禁一上来就夸"这个方向很有前景"，必须用证据压。

## 这是什么

选题不是拍脑袋定题目，而是三步收敛：
1. **现状扫描**：该细分问题上已有哪些代表性工作、共识是什么、卡在哪。
2. **缺口定位**：缺口是"没人做 / 有人做但结论打架 / 有人做但数据/方法/场景旧"三类，必须明确属于哪一类。
3. **可行性评分**：在缺口真实存在的前提下，评估"我手里的资源能不能把它做下来、做出来有没有人认"。

## 何时使用

- 用户说"我想做 X，但不知道从哪下手"。
- 用户带着一个题目来问"这个有没有创新点"。
- 团队 W2 快速选题阶段、W1 的 Phase 1。
- 已经做了一半发现题目立不住，需要回炉重估。
- 选论文选题 / 找 research gap / 投稿选刊 / 评估选题可行性 / 选题打分。
- 不用于撰写论文正文（选题定稿后交给写作链路）。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 研究方向 | 是 | `--topic "..."`（**可重复，多候选对比**）或 `--candidates FILE`（JSON：list 或 `{constraints, candidates}`） |
| 资源约束 | 否 | `--constraints '{"time":"3mo","gpu":"1xA100"}'`；`time` 支持 `3mo`/`6 months`/`1y`/`8w`（纯数字视作月），`gpu` 形如 `8xA100` |
| 查新证据 | 否 | `--lit-review-json lit_review.json`：用其 `summary.gaps_identified` 校验 novelty |
| 返回条数 | 否 | `--top-n 5`（默认 5） |
| 输出路径 | 否 | `--output topics.json`，缺省打印到 stdout |

缺失时一次性问齐：「请提供：① 候选方向（一个或多个）② 约束（时间/算力/目标 venue）③ 是否已有 lit-review 结果可校验查新 ④ 是否落盘 `--output`。」

## 前置自检
```bash
python3 --version                                 # 预期 >= 3.8，否则报错并 STOP
test -f scripts/topic_selector.py && echo OK      # 预期打印 OK，否则脚本缺失 STOP
```
纯工作流模式无脚本依赖；若联网扫描趋势，网络不可达 → 用本地已知文献做 gap 分析并在产出中注明「未联网核实」。

## 工作流

### 步骤 1：多候选粗筛打分
```bash
python3 scripts/topic_selector.py --topic "LLM agent coordination" --constraints '{"time":"3mo","gpu":"1xA100"}'
python3 scripts/topic_selector.py --topic "A" --topic "B" --topic "C" --constraints '{"time":"6mo","gpu":"8xA100"}'
python3 scripts/topic_selector.py --candidates candidates.json --lit-review-json lit_review.json --output topics.json
```
预期：输出 JSON 含 `ranked_topics[]`（每项 `rank`/`topic`/`scores{novelty,feasibility,impact,buildability}`/`total`/`weights`/`recommendation`/`reason`/`novelty_source`/`novelty_verified`/`workload_weeks`/`deadline_weeks`/`gpu_count`/`next`）、`rejected[]`（含 `reason`）、`n_candidates`、`novelty_source`、`weights`、`honesty_note`。
若失败：rc=2 → `--constraints` 非法 JSON 或未给任何候选；rc=1 → `--candidates`/`--lit-review-json` 路径不存在。

### 步骤 2：扫描文献并识别 gap

1. 扫描该领域近期论文（近 6 个月）
2. 梳理已有哪些工作
3. 找出没人做的部分（gap）——把结果喂给 lit-review 的 `--s2`，或反过来把 lit-review 的 `gaps_identified` 传给本脚本

预期：每个候选 gap 能指出「谁做了什么 / 缺什么」；产出格式见下例。
若失败：领域太宽找不到边界 → 先收窄 sub_area 再扫描；联网失败 → 标注「未联网核实」后基于已知文献继续。

### 步骤 3：核对四因子权重与约束

| 因子 | 权重 | 检查内容 |
|------|--------|---------------|
| Novelty | 40% | 具体切入角是否没人做过？（不是泛领域本身） |
| Feasibility | 30% | `1 - workload_weeks / deadline_weeks`；工作量含复杂度词、from-scratch 惩罚、少卡折扣 |
| Impact | 20% | 审稿人会在意吗？有清晰评测方案吗？ |
| Buildability | 10% | 能在现有代码上构建吗？（fine-tune/adapter/LoRA 加分，from scratch 减分） |

预期：`total` 恰为四因子加权和（脚本会回填 `weights` 以便复核）；`recommendation` ∈ `go`/`risky`/`reject`；被否项写明 `reason`。
若失败：打分无依据 → 必须引用具体论文/事实支撑，否则降级进 `rejected`。

### 步骤 4：产出 ranked list

预期：输出 `{"ranked_topics": [...], "rejected": [...]}`，推荐项附 `next`（默认指向 lit-review 查证）。
若失败：清单为空 → 放宽 area 或改用 lit-review 先做系统调研。

```json
{
  "ranked_topics": [
    {
      "rank": 1,
      "topic": "Conflict resolution in LLM agent teams without shared memory",
      "scores": {"novelty": 0.75, "feasibility": 0.72, "impact": 0.65, "buildability": 0.8},
      "total": 0.729,
      "recommendation": "go",
      "novelty_source": "heuristic-keyword",
      "novelty_verified": false,
      "next": "Verify the gap with lit-review (Semantic Scholar) before committing"
    }
  ],
  "rejected": [{"topic": "...", "reason": "feasibility 0.2 (workload 33.0w vs 4.3w)", "total": 0.38}]
}
```

## 核心步骤：五维评估与缺口矩阵方法论

1. **复述并锁定边界**：用一句话向用户确认研究对象、自变量/因变量、场景、目标人群；边界不清先问，不假设。
2. **三方检索**：近 3 年顶会顶刊（Google Scholar / Web of Science / arXiv）、综述类文章、该方向最新博士论文各取 5-10 篇，记录作者、年份、方法、结论、局限。
3. **填缺口矩阵**：行=已有工作，列=研究问题/变量/数据/方法/结论，标出"已覆盖/部分覆盖/空白/有争议"。
4. **提炼候选缺口**：至少列出 3 个候选缺口，每个写清"前人没做 X 的原因是什么"（是做不到、没人想到、还是做了但不好）。
5. **五维打分**（每维 1-5 分）：
   - 新颖性：与最近一篇最接近工作的差异是否一眼可辨。
   - 可行性：数据/代码/算力/时间是否在用户现有条件内。
   - 可证伪：能否设计出"做不出来就推翻"的实验，而非自说自话。
   - 价值：解决的问题对领域/政策/行业是否真实存在。
   - 可发表性：目标档次期刊近 2 年是否发过同类工作。
6. **出结论**：总分 ≥20 推荐做；15-19 给改造建议（缩范围/换数据/换方法）；<15 直接劝退并给 2 个替代方向。

> 评分口径说明：脚本四因子（步骤 3，可复核的量化粗筛）与人工五维（本节，含可证伪性与可发表性判断）并行——脚本分排序候选，人工五维做终审；两者结论冲突时以人工五维复核为准，并在产出中写明分歧原因。

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| `--topic` | 字符串 | 候选方向，**可重复** |
| `--candidates` | 路径(JSON) | list 或 `{constraints, candidates}`；与 `--topic` 可叠加 |
| `--constraints` | JSON 字符串 | `time`（`3mo`/`6 months`/`1y`/`8w`）、`gpu`（`8xA100`） |
| `--lit-review-json` | 路径(JSON) | 读 `summary.gaps_identified` 校验 novelty |
| `--top-n` | 整数 | `ranked_topics` 返回条数，默认 5 |
| `--output` | 路径 | 结果 JSON 输出路径 |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------------|------|------|
| rc=2，`status: "error"` | `--constraints` 非法 JSON，或未给任何候选 | 先 `python3 -c "import json;json.loads(...)"` 自检；补 `--topic`/`--candidates` |
| rc=1，`Not found` | `--candidates` 或 `--lit-review-json` 路径不存在 | 核对路径 |
| 全部进 `rejected` | 领域已饱和或约束过紧（工期太短） | 换 sub_area、放宽 `time`，或读 `references/gap-finding.md` 换找法 |
| `novelty_verified: false` 但你已读过文献 | 未传 `--lit-review-json` | 把 lit-review 输出 JSON 传进来，才对得起「已查新」的说法 |
| 分数与直觉严重不符 | novelty 是关键词启发式、feasibility 是工作量估算 | 以步骤 3 的模型判断为准；把 `workload_weeks` 与 `deadline_weeks` 摆出来人工复核 |

## 交付标准

成功定义：产出 ranked list，每项四因子有分有据、`total` = 加权和；被否项有 `reason`。
产物命名：`topics.json`（若指定 `--output`）或直接输出文本。
保存位置：调用方当前目录或 `--output` 指定路径。
验证方法：`python3 -c "import json;d=json.load(open('<output>'));assert d['ranked_topics'] or d['rejected'];assert d['weights']"` 通过；工作流产出的分数必须能在正文找到依据句。
诚实口径：`novelty_verified` 为 false 时，MUST NOT 在正文写「据我们所知无人研究」这类断言。

## 清单

- [ ] 一句话问题已与用户确认，边界无歧义。
- [ ] 已有 15+ 篇近 3 年代表性文献，缺口矩阵填满。
- [ ] 至少 3 个候选缺口，每个都写了"前人为什么没做"。
- [ ] 五维打分每维都有依据，不是凭感觉给分。
- [ ] 最终结论明确：做 / 改造后做 / 劝退，并附理由。
- [ ] 指出最大的 2 个翻车点（数据拿不到 / 方法跑不动 / 创新点被别人抢先）。
- [ ] `novelty_verified` 口径与正文表述一致，没有把启发式分当查新结论。

## 易错点

- **把"热门"当"缺口"**：所有人都在做的方向，恰恰最难出新东西；热门里找细分场景、反例、失效条件才是缺口。
- **缺口写成"前人研究较少"**：这不是缺口，是没查文献。缺口必须具体到"前人在 Y 场景下用了 Z 方法，但没考虑 W 这个约束"。
- **可行性只看兴趣不看资源**：用户是本科生、一学期时间，就别推荐需要百万级算力和三年追踪数据的题。
- **创新点自我感动**："结合了 A 和 B"不是创新，除非能说清为什么 A+B 会产生单独用 A、单独用 B 都得不到的结论。
- **题目过大**："人工智能在医疗中的应用"是领域不是题目；题目要能缩到一页 PPT 讲清实验设计。
- **把脚本当裁判**：四因子分是启发式粗筛，`novelty_verified: false` 时禁止写"无人研究"式断言。

## 参考

- [references/gap-finding.md](references/gap-finding.md) — **步骤 2 前读**：系统化找 gap 的方法（分类维度、检索式写法）
- [references/venue-matching.md](references/venue-matching.md) — **步骤 3 对照 target_venue 时读**：各 venue 偏好与匹配度判断
- 脚本内部：`WEIGHTS`（四因子权重）、`_workload_weeks`/`_deadline_weeks`（可行性模型）、`_novelty`（novelty 来源与校验）、`rank`（排序与落选）。

## 链路位置

上游无前置；产出交 lit-review 验证 gap 是否真实存在（并把其输出回灌 `--lit-review-json` 提升 novelty 可信度），确定选题后进实验规划（experiment-runner）。
