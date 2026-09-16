---
name: memory-manager
description: "Use when managing the lifecycle of an agent's memory store: resolve conflicts between new candidates and existing entries, execute ADD/UPDATE/DELETE/NOOP operations, and run forgetting policies (TTL, recency decay, topic compaction). Triggers on 记忆管理, 记忆去重, 冲突消解, memory lifecycle, memory deduplication, ADD UPDATE DELETE NOOP, TTL 过期, 记忆压缩, memory consolidation. NOT for extracting new candidates or retrieving memories — use memory-extractor or memory-retriever."
license: Apache-2.0
compatibility: Pure prompt-based; no scripts, no environment probing.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: memory
  pattern: workflow
  tier: powerful
  verified-date: "2026-09-16"
---

# Memory Manager

记忆库会腐烂：新旧条目冲突、事实过期失效、同主题重复膨胀。本技能管记忆的全生命周期——每个新候选进来先过冲突消解决策表，落库只用 ADD/UPDATE/DELETE/NOOP 四个原子操作，再按 TTL、衰减、压缩三把扫帚定期清库。所有操作留审计日志：记忆可以被改写，但不可以被悄悄改写。

## 输入清单

开工前一次性收集。缺输入时用这句话向用户问一次："要管理记忆库，请一次性提供：现有记忆库导出（JSON）、待落库的新候选（memory-extractor 的 candidates.json）、本次模式（增量合并 / 全库清扫 / 响应用户删除请求）。"

| 输入 | 必需 | 说明 |
|---|---|---|
| 现有记忆库导出 | 是 | JSON 条目数组，须含 id、content、confidence、updated_at、hit_count |
| 新候选 | 增量合并时必需 | memory-extractor 产出的 candidates.json；全库清扫时不需要 |
| 本次模式 | 是 | merge（增量合并）/ sweep(全库清扫) / purge（响应用户显式删除） |
| 用户删除指令 | purge 模式必需 | 明确指认删除对象（按 id 或按 user_id 全删） |

## 前置自检

本技能为纯 prompt 技能，无需探测运行环境，只检查输入完备性：

- 现有库导出是否为合法 JSON 且条目带 id？无 id 的库 → 先要求按 memory-architect 的 schema 补 id，不要现场编造 id。
- merge 模式下候选是否带 evidence_quote？缺证据的候选 → 退回 memory-extractor 重抽，本技能不收无证据条目。
- purge 模式下删除指令是否明确到 id 或 user_id？"把那些没用的删了"不算明确指令 → 问清后再执行（红线 2 不允许猜）。

## 红线

1. DELETE 必须留审计日志：每次删除在 operations 日志中记录 op、target_id、before 全文、reason，日志随库一起持久化。
2. 用户显式要求删除 → 立即删且不可恢复（GDPR 式删除权）：不做"软删除留备份"的自作主张；按 user_id 请求删除时删除该用户全部条目。
3. 冲突不改写历史：条目内容更新必须保留演进注记 changed_from，禁止无痕覆盖旧值。
4. 不静默修改 confidence 与 ttl 之外的机器字段：id、created_at、user_id 永不改动。
5. 审计日志与库同级持久化：只输出"改了什么"而不产出可存档日志文件的操作不算完成。

## 工作流

### 步骤 1：读入库与候选

- **动作：** 载入现有库与候选，建立两张索引：按 id 的主索引、按内容关键词的比对索引（同主题候选集中比对）。
- **预期：** 统计快照：库内条数、候选条数、按 type 分布。
- **失败时：** 库文件损坏或截断 → 停止，要求重新导出；禁止"跳过坏行继续"——静默丢数据不可接受。

### 步骤 2：冲突消解

- **动作：** 逐个候选对照决策表裁决：

| 情形 | 判定 | 处置 |
|---|---|---|
| 语义等价且无新信息 | NOOP | 丢弃候选，reason 记 duplicate |
| 语义等价且信息更新（状态变了） | UPDATE | 新值胜出，旧值写进 changed_from 注记 |
| 同主题但时间线矛盾（"在上海工作" vs "已回北京"） | UPDATE + disputed 标记 | 按时间戳新者为准，条目标 `disputed: true` 供检索端降权 |
| 新主题 | ADD | 直接入库，继承候选的 confidence |
| 与现有条目互补（同一事实的两面） | ADD（拆细后） | 两条并存，互相在 tags 中引用 |
| 部分重叠（既非等价也非互补） | UPDATE（归并） | 取信息量大的表述为主体，重叠部分去重，独有信息并入；难以归并时拆细后按互补处理 |

- **预期：** 每个候选获得唯一裁决，无悬空项。演进注记格式统一为 `[changed_from: 旧值原文]`，disputed 另加 `[disputed: true]`，两个标记都可被 memory-retriever 机器识别。
- **失败时：** 新旧条目无法判定孰新（时间戳缺失）→ 保守取 NOOP 并在日志记 ambiguous，宁漏勿错。

### 步骤 3：执行四操作

- **动作：** 把裁决转成原子操作并生成操作日志，每条 `{op, target_id, before, after, reason}`；UPDATE 参照 letta core memory 的自编辑模式——对整块重写而非在末尾追加，避免"用户在上海工作 → 用户现在在北京 → 用户在上海工作"式追加膨胀。
- **预期：** operations 数组顺序执行后库状态一致；每条 UPDATE 的 after 里 changed_from 链可回溯。
- **失败时：** 某操作的目标 id 在库中不存在 → 该操作作废并记日志，不中断其余操作。

### 步骤 4：遗忘与压缩

- **动作：** 三把扫帚依次执行——
  1. TTL 扫帚：`ttl` 字段早于今天的条目直接 DELETE（记审计日志）。
  2. 衰减扫帚：超过 90 天（经验值，可调）未被检索命中且 confidence < 0.7 的条目，confidence 乘 0.8（经验值，可调）；跌破 0.4 的条目 DELETE。hit_count 缺失的库按 updated_at 距今天数代替。
  3. 压缩扫帚：同主题（同 user_id + 同 type + 同 tags）条目超过 10 条（经验值，可调）时，摘要合并为一条主题摘要，原条目 DELETE、摘要条 source 记 `compacted`。
- **预期：** 每把扫帚产出清理清单；库条数下降或维持稳定，不出现只增不减。三把扫帚的执行节奏：TTL 与衰减随每次 merge 顺带执行；压缩只在全库清扫（sweep）时执行——压缩代价高且影响检索习惯，不宜每次增量都跑。
- **失败时：** 压缩摘要丢失关键细节（如具体数字）→ 该主题不压缩，宁膨胀勿失真，在日志记 skip_compaction。

### 步骤 5：输出操作日志与新库

- **动作：** 产出 operations.json 与更新后的完整库 JSON，附统计：四操作各多少条、清扫删除多少条、库条数前后对比。
- **预期：** operations.json 可直接归档为审计记录；新库条目全部符合 memory-architect schema。
- **失败时：** 统计对不上（操作数 ≠ 库差值）→ 逐步骤重放操作找差异，修完再交付。

operations.json 结构：

```json
{
  "date": "2026-09-16",
  "mode": "merge",
  "operations": [
    {"op": "UPDATE", "target_id": "mem_001", "before": "用户在上海工作", "after": "用户已回北京工作 [changed_from: 用户在上海工作] [disputed: false]", "reason": "candidate newer by 90 days"}
  ],
  "sweep": {"ttl_deleted": 3, "decayed": 12, "compacted_topics": 2},
  "stats": {"before": 210, "after": 198}
}
```

## 参数速查表

| 参数 | 默认值 | 说明 |
|---|---|---|
| 衰减触发线 | 90 天未命中 且 confidence < 0.7 | 经验值，可调 |
| 衰减系数 | confidence × 0.8 / 次 | 经验值，可调；每次全库清扫执行一轮 |
| 删除阈值 | confidence < 0.4 | 经验值，可调 |
| 压缩触发线 | 同主题 > 10 条 | 经验值，可调 |
| disputed 标记 | 时间线矛盾时置 true | 检索端（memory-retriever）据此降权 |
| NOOP 占比健康线 | > 60% 提示抽取端过噪 | 经验值，可调；持续超线应回头调 memory-extractor |
| sweep 建议频率 | 每周或每千次写入一次 | 经验值，可调；全库清扫（三把扫帚全跑）在此触发 |
| 审计日志保留期 | 与库同生命周期 | 日志随库持久化，不单独过期；purge 操作日志永久保留 |

## 失败处置表

| 现象 | 原因 | 处置 |
|---|---|---|
| 库条数只增不减 | 只 ADD 不清扫 | 补跑步骤 4 三把扫帚；长期方案是把 sweep 设为定期任务 |
| 同一事实反复 UPDATE | 抽取端粒度过粗或事实本身摇摆 | 查 changed_from 链长度；> 3 次的条目标 unstable 供检索端降权 |
| DELETE 后用户找条目 | 用户不记得曾要求删除 | 出示审计日志中的 reason 与指令原文；库不回滚（红线 2） |
| 压缩后检索变差 | 摘要丢了高价值细节 | 回滚该主题压缩（有审计日志可重建），提高压缩触发线 |
| 候选与库字段对不上 | schema 版本漂移 | 以 memory-architect 冻结版为准映射字段，映射表写进日志 |
| purge 请求指认模糊 | 用户未给 id | 用检索预览列出候选删除条目请用户确认，确认前不删 |
| sweep 误删用户仍需要的条目 | TTL 设得过短或衰减过快 | 从审计日志取 before 全文手工恢复该条目；下调对应参数并在库的元信息中记录调整 |
| merge 后库出现两条近似条目 | 比对索引按关键词漏配 | 把漏配对补进日志，跑一遍步骤 2 专项重比；长期方案是候选改带 embedding 时双路比对 |
| 用户要求"顺便把库优化一下" | 超出本次模式范围 | 明确本次只做声明过的模式；全库优化走 sweep 模式另开一次任务 |
| 候选 user_id 与库内任一归属都不符 | 新用户或标注错误 | 与用户确认：新用户则直接 ADD，标注错误则退回 memory-extractor 改归属 |

## 交付标准

- operations.json 为合法 JSON，每条操作含 op、target_id、before、after、reason 五字段，全部 DELETE 有审计记录。
- 新库为合法 JSON，全部条目符合上游 schema，changed_from 链完整可回溯。
- 三把扫帚各产出清理清单，库条数统计前后一致。
- purge 模式下目标条目零残留，且审计日志记录了用户指令原文。
- 附统计段：四操作分布、清扫量、条数变化。
- 审计日志已随库持久化（与库文件同目录或同一导出包），可独立重放。

## 参考

- `references/sources-and-methodology.md` —— 需要说明 ADD/UPDATE/DELETE/NOOP 决策表、core memory 自编辑重写模式的出处（mem0 / letta）、如何署名时读；评审核对方法论时也读。

## 链路位置

- 上游：`memory-extractor`（candidates.json 的唯一合法来源）与 `memory-architect`（schema 与遗忘策略的制定者）。
- 下游：`memory-retriever`（消费本技能维护出的干净库；disputed 与 unstable 标记供其降权）。
- 本技能是 memory-systems 链路的"库管员"：上游产得再好，没有本技能的裁决与清扫，库照样烂掉。
