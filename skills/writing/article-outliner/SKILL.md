---
name: article-outliner
description: "Create article outlines: structure, section hierarchy, key points, and reading flow. Supports blog posts, technical articles, news, listicles, and opinion pieces. Also audits an existing draft's structure with reverse outlining, and de-duplicates listicle entries (MECE check). Use when the topic is defined but structure is needed before drafting. 当用户要求 搭文章大纲 / 列提纲 / 规划结构 / 帮我理一下文章框架 / 检查文章结构有没有问题 时使用。 Do NOT use for writing full prose (outline only — use article-drafter for that), nor for line-level editing of a finished draft (use content-editor)."
license: Apache-2.0
compatibility: "Pure prompt-based structuring. Optional scripts/outliner.py is a deterministic skeleton generator (Python 3.8+, stdlib only) — it emits template headings and field scaffolding, NOT content; the real outlining work happens in prompt mode. No API keys required."
metadata:
  version: "2.0"
  author: awesome-skillkit
  category: writing
  pattern: dual-mode
  tier: standard
  verified-date: "2026-09-22"
---

# Article Outliner（动笔前把结构钉死）

本技能产**结构合同**：每节的论点、要点、字数预算与节间关系。不产正文。

大纲是全文唯一"改动成本最低"的东西——在大纲上删一节是 10 秒的事，在成稿上删一节是 2 小时的事。本技能全部设计围绕这一点。

## 适用决策表

| 你的处境 | 本技能的位置 | 去向 |
|----------|--------------|------|
| 主题有了，结构没定 | ✅ write 模式：出大纲 | 本技能 |
| 初稿已有，怀疑结构有问题 | ✅ audit 模式：反向大纲体检 | 本技能，工作流 B |
| listicle 条目疑似重叠/凑数 | ✅ 用 MECE 三查 | 本技能，暗知识 3 + 验证步骤 |
| 结构定了，要写正文 | ❌ 越界 | article-drafter |
| 正文有了，要删词/去 AI 腔 | ❌ 越界 | content-editor |
| 标题抽不出疑问词（主题没收敛） | ⚠️ 先收敛：补疑问词再开工 | references/outline-templates.md §1 判定法 |
| 只想要个标题/钩子，不要结构 | ✅ 轻量模式：只交付 title/hook，跳过 section 设计 | 本技能 |

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| `topic` | 是 | 文章主题，如 `FastAPI 性能优化` |
| `type` | 否 | `technical` / `blog` / `news` / `listicle` / `opinion` / `tutorial`，默认 `technical` |
| `target_length` | 否 | `short(800)` / `medium(2000)` / `long(5000)`，默认 `medium` |
| `audience` | 否 | `beginner` / `intermediate` / `expert`，默认 `intermediate` |
| `key_points` | 否 | 要点列表，如 `["async","caching","DB indexing"]` |
| `platforms` | 否 | 目标平台，如 `["csdn","juejin","wechat"]` |

**先提取，再判定缺失**：用户的信息经常以自然语言/散文给出，而不是字段格式——「我列了 7 条：写类型注解、用 lint、……，帮我搭大纲」已经把 `topic` 与 `key_points` 都给了。**先把散文里的信息抽成字段，只有抽取后仍不存在的内容才算缺失**；把已在手的信息判成「缺失」并要求用户重发 = 交付事故（`key_points` 本就「可空」，任何情况下都不是阻塞项）。

仅在抽取后 `topic` 仍缺失时才一次性问齐：「请提供：① 主题 topic；② 文章类型 type（technical/blog/news/listicle/opinion/tutorial）；③ 目标长度 target_length；④ 目标受众 audience；⑤ 关键要点 key_points（可空）。其余默认：type=technical、target_length=medium、audience=intermediate。」

## 前置自检

1. **主题收敛检查**：把标题里的疑问词抽出来——「怎么/如何」→ tutorial、「该不该/真的吗」→ opinion、「哪些/几个」→ listicle、「为什么失败/如何恢复」→ blog（复盘）、「vs/对比」→ technical（评测）。抽不出疑问词 = 主题还没收敛，先补疑问词再开工。
2. 校验脚本可用性（可选，确定性骨架）：
   ```bash
   python3 scripts/outliner.py --topic "FastAPI 性能优化" --type technical --output outline.json
   ```
   预期：退出码 `0`，生成 `outline.json`，含 `sections[]` 与每节 `word_count_target`。
3. **`--type` 只接受 6 个枚举值**。传其它值 → argparse 直接报错并退出（rc=2），**不会自动回退到 `technical`**；需要用默认值就别传该参数。
4. 纯提示词模式可跳过第 2 步，直接进入工作流 A。

## 暗知识（决定大纲好不好用的东西）

### 1. 每一节都要回答上一节留下的问题

Minto 金字塔原理的问答链：相邻两节之间必须能填进一句「读完上一节，读者自然会问什么」——若下一节答不上来，它就不属于这篇文章（要么补过渡，要么移出去）。

**机械自检**：遮住所有标题，只读相邻两节的要点列表，看能否看出"为什么下一节要存在"。看不出 = 逻辑断层。

### 2. 「结论先行 vs 悬念铺垫」由读者处境决定，不是风格偏好

搜索进来的读者（有时间压力、随时退出）→ 结论先行；被推荐流吸引来的读者（已决定读完）→ 悬念铺垫。**混合方式是默认最优**：给方向结论，留细节悬念。完整判定表与混合句式见 `references/flow-guide.md` §2。

### 3. MECE 只对盘点型大纲成立

MECE（互斥、穷尽）是"列表/盘点"的检查工具：条目之间同维度、不重叠、覆盖主要类别。**叙事型与观点型强行套 MECE 会把论证拆散**——Minto 本人在原书里就声明该框架不适用于开放式探讨，且 MECE 在实践中很难完全达成。所以：listicle 必查，technical/opinion 不查。

### 4. 标题里出现「与 / 和 / 及」，通常是两节被压成了一节

一节的合格判据是「能一句话说清它的中心工作」。`性能优化与部署实践` 说不清 → 拆成两节，或在标题里二选一。

### 5. title 与 hook 服务的是两拨人

| 字段 | 服务对象 | 优化目标 | 常见错误 |
|------|----------|----------|----------|
| `title` | 还没点进来的人（搜索/信息流） | 被选中：具体对象 + 可验证信息 | 写成内部代号或「XX 入门」 |
| `hook` | 已经点进来的人 | 留下：制造信息缺口/张力 | 重复标题，或泛问「你遇到过X痛点吗」 |

把两者当一个字段写，会得到又长又平的标题。

### 6. 字数预算是防挤压装置，不是配额

`word_count_target` 的作用是防止某一节膨胀、吃掉其他节的空间（尤其技术文里的"背景"节）。实际写作时字数是结果。若某节预算达到别节的 3 倍，先问「它凭什么」——答不上就是结构失衡。

### 7. 已有初稿时用「反向大纲」体检结构

从初稿反向提取"每节实际在说什么"（不是标题声称说什么），与标题/开头承诺对照。三种高发问题：一节在干两件事、某节删掉后文章仍成立（= 无关展开）、结尾结论与开头承诺不是同一件事。这套检查在学术写作教学里叫 reverse outlining，是结构体检的通行手法。

### 8. CTA 因平台而异，而脚本只产一个 `conclusion` 字段

CSDN/掘金的互动是点赞收藏、公众号是"在看/转发"、知乎是"赞同"、B 站是"一键三连"。**多平台投递时要按平台各写一版 conclusion**——脚本的单一字段是骨架，不是成品（见诚实声明）。

## 红线（硬性禁令）

1. **不虚构数据与来源**：大纲里出现「性能提升 10 倍」「90% 的开发者」这类数字，必须有可指向的出处；没有就改成定性表述，或标注「待补数据」。
2. **listicle 不注水凑数**：7 条的标题就写 7 条，凑数的条目会稀释整篇可信度——宁可改标题为 5 条。
3. **不把用户素材原样退回**：`key_points` 是原料，必须加工成可写作的主张（带判据/动作/量化目标）；直接罗列等于没做大纲。
4. **不越界写正文**：本技能交结构；写成段落就侵权了 article-drafter 的职责，且会让用户失去对结构的审核点。
5. **不承诺写作质量**：结构合格 ≠ 文章好看。交付时必须说明质量仍取决于正文写作与素材质量。

## 诚实声明（脚本模式的实际行为）

`scripts/outliner.py` 是**确定性骨架生成器**，不是"AI 大纲"。以下为 2026-09-22 实跑核实的行为：

1. **章节标题来自固定模板表**：`technical` → `问题背景 / 原因分析 / 解决方案 / 对比测试 / 总结`。这些标题**与主题无关**，是骨架槽位，必须按 `references/outline-templates.md` 的对应模板重写。
2. **`title` / `hook` / `conclusion` 是占位文本**：分别是 `{topic}：从入门到精通`、`你遇到过{topic}相关的痛点吗？`、字面字符串 `总结要点 + CTA`。三者都必须重写（暗知识 5、8）。
3. **`points` 由 `--points` 搬运**：每条要点进一节；要点条数超过章节数时轮转分配（不丢点）；未提供要点的节 `points` 为空数组。
4. **`word_count_target` 按节均分**（余数前移到前几节），不考虑内容权重；各节之和恒等于 `total_words_target`。
5. **`reading_time_min` = `total_words_target // 250`**（250 词/分是英文阅读速度的通行惯例口径）。中文阅读速度通常更快，因此该字段对中文内容**偏保守**（高估阅读时间）。
6. **`--type` 非法值 → argparse 报错退出 rc=2**，无自动回退。
7. 脚本只产 `level: 2` 单层结构，不产三级标题；不校验 `type` 与内容是否匹配。

> 实测记录与完整字段清单见 `references/sources-and-methodology.md`。

## 工作流 A：write 模式（从零搭大纲）

### 步骤 1：收敛主题、读者与载体
按前置自检 1 定 `type`；定 `audience` 与 `platforms`（决定结论先行与否、CTA 形态）。
预期：`type` / `audience` / `platforms` 三者明确。若失败：`audience` 不明 → 用 `intermediate` 并在交付时标注。

### 步骤 2：选模板骨架
读 `references/outline-templates.md` §1 速查，选 A 技术教程 / B 观点评论 / C 清单盘点 / D 案例复盘 / E 评测对比之一，取该模板的"部分 × 作用 × 字数占比 × 必含要素"表。
预期：选定一套模板及其字数占比。若失败：疑问词抽不出 → 回前置自检 1。

### 步骤 3：把每节写成断言 + 要点
每个 h2 改写成一句**断言**（不是「什么是 X」「概述」）；每节 2–5 条要点，要点必须具体可执行（含动作/判据/量化目标）。
预期：每节一条断言 + 2–5 条要点。若失败：某节写不出断言 → 它可能是两节，按暗知识 4 拆分。

### 步骤 4：标节间关系
对每一对相邻节标注关系类型（递进/转折/并列/因果/举例/问题-解决），产出 `link_to_prev` 字段；标不出的相邻对 = 逻辑断层。
预期：无"标不出"的相邻对。完整关系表与检验问句见 `references/flow-guide.md` §3。

### 步骤 5：分字数预算
按模板占比分配各节 `word_count_target`，替代脚本的均分结果（脚本均分是无信息默认值）。
预期：各节之和 = `total_words_target`；主体部分（论证/步骤/条目）≥ 55%、背景铺垫 ≤ 15%（两者为 `references/outline-templates.md` 的经验值，非平台规则）。

### 步骤 6：写 title / hook / conclusion
按暗知识 5 的分工写 title 与 hook；conclusion 按平台给具体 CTA（暗知识 8）。
预期：title 含具体对象与可验证信息；hook 在 2 句内制造信息缺口；conclusion 有具体动作。

### 步骤 7：跑内置验证
按下方「内置验证步骤」逐条打勾；脚本模式下再按诚实声明的 1–4 条核对占位字段是否已重写。

## 工作流 B：audit 模式（反向大纲体检）

1. **反向提取**：通读初稿，凝练出每节"实际在说什么"（不是标题声称说什么），列表呈现。
2. **三查**：① 哪些节在干两件事（→ 拆分建议）；② 哪些节删掉后文章仍成立（→ 无关展开，建议删）；③ 标题、开头承诺、结尾结论三处是否指向同一件事（→ 结论漂移，改结尾不改开头）。
3. **输出诊断表**：`节 ↦ 实际主张 ↦ 问题类型 ↦ 处置`。逻辑断层类型与修复优先级见 `references/flow-guide.md` §5。
4. **不重写正文**：只给结构处置建议；行级改写交给 content-editor。

## 结构模式表

| 模式 | 何时用 | 章节 | 关键风险 |
|------|--------|------|----------|
| Problem → Solution | 技术文章、故障复盘 | 3-5 | 背景节膨胀吃掉正文预算 |
| Listicle | 技巧、资源盘点 | N 项 + 开头 + 结尾 | 条目不同维度/凑数（必查 MECE） |
| Tutorial | 操作指南 | 步骤 1-N + 前置条件 + 结果 | 步骤粒度不一（一行命令 vs 一整章） |
| News | 公告、更新 | 是什么 → 为什么 → 怎么做 → 影响 | 埋没最重要的信息（倒金字塔失效） |
| Opinion | 评论、观点文 | 论点 → 论据 → 反方 → 结论 | 稻草人反方；结论漂移 |

## 内置验证步骤（交付前逐条打勾）

- [ ] **问答链测试**：遮住标题只读相邻节要点，"为什么下一节要存在"答得出
- [ ] **断言测试**：每个 h2 都能改写成一句断言
- [ ] **MECE 三查**（仅 listicle）：同维度、无重叠、有穷尽说明
- [ ] **一致性测试**：title / hook / conclusion 指向同一件事
- [ ] **字数测试**：各节 `word_count_target` 之和 = `total_words_target`
- [ ] **占位清除**（脚本模式）：模板标题与 title/hook/conclusion 占位文本已全部重写

完整判据（含主体占比、反方占比要求）见 `references/outline-templates.md` §7 与 `references/flow-guide.md` §6。

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|-------------|------|------|
| `需要 --topic 或 --json-input` | 缺主题 | 补 `--topic` 或在 `--json-input` 提供 topic 字段 |
| argparse `invalid choice`（rc=2） | `--type` 取值非法 | 改用 6 个枚举值之一；脚本不会自动回退 |
| 某节 points 为空 | 未提供 `--points` 或要点少于节数 | 按工作流 A 步骤 3 手写要点，不要留空节 |
| 标题含「与/和/及」 | 两节压成一节 | 按暗知识 4 拆分或二选一 |
| 相邻节标不出 `link_to_prev` | 逻辑断层 | 按 flow-guide §3 补过渡或调整顺序 |
| listicle 条目可互换而不影响理解 | 真并列（可接受）；若不能互换 | 不能互换 = 有隐含依赖，改标递进 |
| 结尾结论 ≠ 开头承诺 | 结论漂移 | 改结尾回扣（不要改开头，flow-guide §5） |
| 用户要"专业感"但要点全是空话 | 素材不足以支撑结构 | 如实说明：大纲无法弥补素材缺口，先补素材 |

## 交付标准

- 产出 `outline` 对象：`title` / `hook` / `sections[]`（每节含 `id` / `heading` / `level` / `points` / `word_count_target`）/ `conclusion` / `total_words_target` / `reading_time_min`。
- `sections` 长度 ∈ [3,7]（listicle 允许 7+2）；每节 `points` 2–5 条。
- 各节 `word_count_target` 之和 = `total_words_target`。
- 表格形式的交付须同时给 `link_to_prev` 标注列。
- 脚本模式下额外核对：模板标题与占位文本已重写（诚实声明 1–2）。
- audit 模式下产出结构诊断表，不改正文。

## 参考

- `references/outline-templates.md` —— 5 套中文大纲模板（选型速查 / 字数占比 / 必含要素 / 合格判据 §7）。工作流 A 步骤 2 与交付前必读。
- `references/flow-guide.md` —— 逻辑流设计（结论先行 vs 悬念、节间关系标注、过渡句库、逻辑断层修复、流检查表 §6）。工作流 A 步骤 4 与工作流 B 必读。
- `references/sources-and-methodology.md` —— 暗知识来源、采信纪律与脚本实测记录。

## 附录：CLI 契约（参数速查表）

| 参数 | 取值 | 说明 |
|------|------|------|
| `--topic` | 字符串 | 文章主题，与 `--json-input` 二选一 |
| `--type` | technical/blog/news/listicle/opinion/tutorial | 默认 `technical`；非法值直接报错 |
| `--length` | short/medium/long | 默认 `medium` |
| `--audience` | beginner/intermediate/expert | 默认 `intermediate` |
| `--points` | 多值 | 关键要点列表 |
| `--platforms` | 多值 | 目标平台 |
| `--json-input` | 文件路径 | 完整 JSON 输入（含 topic） |
| `--output` | 文件路径 | 写出大纲 JSON；缺省打印到 stdout |
