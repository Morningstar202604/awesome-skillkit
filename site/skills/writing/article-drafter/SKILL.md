---
name: article-drafter
description: "Generate article first draft from an approved outline. Fills in each section with prose based on key points, audience level, and style. Use after the outline is approved, before editing/SEO. 当用户要求 写文章初稿 / 起草正文 / 帮我写这篇 / 把大纲扩写成文章 时使用。 Also triggers on / 正文起草 / 写初稿 / 扩写大纲 / draft article / write first draft. Do NOT use for publishing the finished draft to platforms, or for building the outline itself (use article-outliner)."
license: Apache-2.0
compatibility: Pure prompt-based drafting; LLM generates prose. Optional helper scripts/drafter.py requires Python 3.8+ (stdlib only). No API keys required.
metadata:
  version: "2.0"
  author: awesome-skillkit
  category: writing
  pattern: single-task
  tier: standard
  verified-date: "2026-09-21"
---

# Article Drafter（从大纲生成文章初稿）

根据已批准的大纲，按受众层级与文风把每个章节的关键点扩写成可读正文，产出待评审初稿。

## 适用决策表

| 情况 | 用不用本技能 | 原因 |
|------|------------|------|
| 大纲已批准，要写正文 | ✅ 本技能主场 | 每节按 points 扩写 |
| 大纲还没定 | ❌ 先走 article-outliner | 大纲未定时起草=在流沙上盖楼 |
| 初稿已写完要润色 | ❌ 走 content-editor | 起草与编辑是两件事，混做两件都做不好（见暗知识 1） |
| 要发布到平台 | ❌ 先编辑再走发布类技能 | 未编辑的初稿不该直接见读者 |
| 只缺一个 hook 或结论 | ✅ `--section` 单节模式 | 不必重跑全篇 |

## 诚实声明（先读）

- `scripts/drafter.py` 是**骨架生成器**：产出的 `draft` 字段是占位提示语（标注 `status:"draft_placeholder"`），不是成品正文。**正文由 agent 在步骤 2 逐节生成**。下方"真实脚本输出"与"agent 填充后"两个示例分开给，不冒充。
- 脚本不校验 `audience` 枚举值（传 `初级到中级工程师` 也照收）；枚举归一到 beginner/intermediate/expert 是 agent 层的职责（步骤 0）。
- `word_count ±20%` 是 agent 自检目标，脚本不做字数门禁。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| `outline` | 是 | 大纲对象：含 `title`、`sections[]`（每节 `heading`/`points`/`word_count_target`），可选 `hook`/`conclusion` |
| `audience` | 否 | `beginner` / `intermediate` / `expert`，默认 `intermediate`，决定术语密度 |
| `tone` | 否 | 文风，如 `technical` / `casual` / `news` |
| `research_notes` | 否 | 原始素材，用于补充事实与数据 |

缺失时一次性问齐：「请提供：① 大纲（标题 + 各章节要点 + 每节字数目标）；② 目标受众（beginner/intermediate/expert）；③ 文风 tone；其余我采用默认值：audience=intermediate、tone=technical、research_notes=空。」

## 前置自检

1. 确认 `outline` 存在且非空：
   ```bash
   python3 scripts/drafter.py --outline outline.json --output /tmp/draft_check.json
   ```
   预期：退出码 `0`；**outline 模式**下 `sections` 数组长度 ≥ 大纲章节数。
   若失败：`[ERROR] 大纲文件不存在` → 路径错误，请用户确认 `outline.json` 位置后 STOP。
2. `--topic` 模式（无大纲）产出的是空骨架（`sections: []`），这是设计行为——只用来占位存标题，不作为起草依据。
3. 确认 `audience` 取值：不在 `beginner|intermediate|expert` 内时，agent 自行归一（如"初级到中级工程师"→ intermediate），并向用户复述映射结果。脚本层不做校验。
4. 若不用脚本（纯提示词模式），跳过第 1 步，直接进入工作流步骤 2。

## 工作流

### 步骤 1：生成大纲骨架（确定性，可选）

运行脚本把大纲结构化为初稿占位骨架，正文由 agent 在步骤 2 填充：
```bash
python3 scripts/drafter.py --outline outline.json --audience intermediate --output draft.json
```
预期：`draft.json` 含 `title`/`hook`/`sections[]`/`status:"draft"`/`needs_review:true`，每节 `draft` 为占位提示语。
若失败：参数缺失报 `Need --outline, --topic, or --section` → 补 `--outline` 后重跑。

### 步骤 2：逐节填充正文（agent 生成，按起草纪律）

对 `sections[]` 每一项，**先读完该节全部要点、想清楚"这节要让读者明白什么"，再动笔**（暗知识 3），然后：

- 读取 `points`，展开为 2–4 段；每个 point 至少落到一个**具体**的名词/数字/场景，不许停留在"很重要/不可或缺"式的抽象句；
- 匹配 `audience` 术语密度（见「受众风格规则」）；
- 命中 `word_count_target` ±20%；
- **不回头改写已完成的节**——初稿阶段只向前推进，修改留给 content-editor（暗知识 1/2）。

预期：每节 `draft` 字段非空，字数落在目标区间。
若失败：某节无 `points` → 用 `heading` 作为唯一要点生成，并标记该节 `needs_review`。

### 步骤 3：写开头 hook 与结论 CTA

- hook 用**具体场景或反直觉事实**开场，不用"在当今快速发展的时代"式抽象概括（暗知识 3 的直接推论）；
- 用 `outline.hook`（若存在）作开头 2 句抓注意力；缺失则自写一句场景化开场；
- 写 `conclusion` + 行动号召（关注/收藏/评论，按平台口径）。
预期：`hook` 与 `conclusion` 非空。

### 步骤 4：产出完整初稿

整合为完整初稿，输出 JSON 或 Markdown。
预期：产物含全部章节、总字数、状态 `draft`、待评审标记；交给 content-editor 而不是直接发布。

## 起草暗知识（有来源，写初稿前读一遍）

写作方法论是"人很主观的东西"，本节全部来自公开出版物与原始文本，不自行发明：

1. **初稿的任务是"存在"，不是"好"**。Anne Lamott《Bird by Bird》的 "shitty first drafts" 一章：所有好作者都写糟糕的初稿，初稿是"下头稿"（down draft——只管倒出来）， perfectionism 是初稿的头号杀手。推论：**起草与修改必须物理分离**，边写边改的人实际是在用编辑的焦虑阻止起草。
2. **改稿的预期是做减法**。Stephen King《On Writing》：第二稿 = 第一稿 − 10%；写作时关门（只给自己写），修改时开门（考虑读者）。推论：起草时字数略超目标（按同一定律留出约 10% 余量）是健康的，给删减留余地；写满目标字数才停下，往往意味着注水。
3. **意义先于措辞**。George Orwell《Politics and the English Language》（1946）："先用画面和感觉把意思想到最清楚，然后再挑选——而不是接受——词句。" 预制短语（dying metaphors）是思想被接管的表现：英文的 "in my opinion it is not an unjustifiable assumption that"，中文的对应物是"赋能 / 抓手 / 闭环 / 引爆 / 深度解析"。**识别能力注记**：Orwell 的"禁被动语态"针对英文文风，中文受事主语句（"被"字句）常更自然，此条不机械移植中文——移植的是"让意义选词"的原则，不是逐条规则。
4. **砍冗词**。Strunk & White《The Elements of Style》"Omit needless words" + Orwell 规则 (iii)"能删的词一律删"：中文初稿里"只是 / 几乎 / 显然 / 基本上 / 可以说"多为赘词，删掉通常不损义。
5. **filter words 拉开读者距离**（Jane Friedman 的编辑清单）："我注意到 / 她感到 / 似乎"这类过滤词让读者隔着一层毛玻璃看场景；"她感到一阵寒意"不如"门缝里灌进来的风压灭了蜡烛"。同时句长要有变化——连续同长度的句子是机器腔的节奏特征。
6. **研究占起草时间的大头**。Robert Caro 的工作方式：动笔前研究早已完成，写作是把已经想清楚的东西倒出来。推论：`research_notes` 为空时，先问用户要素材，再动笔——无米之炊的初稿只能靠编造，而编造是初稿最贵的错误。

**来源**：Anne Lamott *Bird by Bird* (1994)；Stephen King *On Writing* (2000)；George Orwell "Politics and the English Language" (1946, Horizon)；William Strunk Jr. & E.B. White *The Elements of Style*；Jane Friedman 的 self-editing 清单；Robert Caro *Working* (2019)。逐条采信前经过多源交叉核对；单一来源且无法交叉验证的说法未收录。

## 红线（初稿阶段的"不做"）

1. **不在起草中做润色循环**——改写交给 content-editor；本技能产出物永远带 `needs_review:true`。
2. **不用预制短语开场**——hook 禁用"在当今…的时代 / 随着…的发展 / 众所周知"。
3. **不注水凑字数**——要点撑不起 `word_count_target` 时，如实缩短并标记 `needs_review`，而不是重复表达凑数。
4. **无来源不编数据**——`research_notes` 里没有的数字、案例、引语，初稿里就写"待补充"占位，不许现编。
5. **不改写用户大纲的章节结构与顺序**——对结构有意见就在交付说明里提，初稿忠于大纲。

## 输入输出示例

输入 `outline`：
```json
{
  "outline": {
    "title": "FastAPI 性能优化",
    "sections": [
      {"heading": "为什么慢", "points": ["同步I/O", "N+1"], "word_count_target": 300}
    ]
  },
  "audience": "intermediate",
  "tone": "technical",
  "research_notes": "optional raw material"
}
```

**真实脚本输出**（骨架，`draft` 是占位提示语）：
```json
{
  "title": "FastAPI 性能优化",
  "hook": "",
  "sections": [
    {
      "heading": "为什么慢",
      "draft": "同步I/O。\n\n（intermediate 读者视角：解释为什么 + 怎么做 + 注意事项）\n\nN+1。\n\n（intermediate 读者视角：解释为什么 + 怎么做 + 注意事项）\n",
      "word_count": 66,
      "target": 300,
      "status": "draft_placeholder",
      "note": "Production: LLM generates full text based on outline + research",
      "id": null
    }
  ],
  "conclusion": "",
  "total_words_target": 2000,
  "status": "draft",
  "needs_review": true
}
```

**agent 填充后**（步骤 2–3 之后的最终交付）：
```json
{
  "title": "FastAPI 性能优化",
  "hook": "同一个接口，压测 QPS 从 120 掉到 9——排查了两小时，元凶是循环里的一条查询。",
  "sections": [
    {
      "id": 1,
      "heading": "为什么慢",
      "draft": "FastAPI 本身是异步框架，但只要在路由里写了一行同步阻塞调用，事件循环就整体停摆……（正文）",
      "word_count": 318,
      "target": 300,
      "status": "ok",
      "note": ""
    }
  ],
  "conclusion": "（总结 + CTA）",
  "total_words_target": 2000,
  "status": "draft",
  "needs_review": true
}
```

> 下游衔接：`content-editor` 的 `--draft` 直接读本文件，要求顶层含 `title` 与 `sections[]`（每项含 `heading`/`draft`），本输出满足。

## 受众风格规则

| 受众 | 术语密度 | 示例 | 代码 |
|------|---------|------|------|
| Beginner | 最少，全解释 | 每节 3-4 个 | 完整片段 |
| Intermediate | 适中，标准术语 | 每节 2-3 个 | 关键片段 |
| Expert | 高密度，假定已懂 | 每节 0-1 个 | 单行片段 |

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| `--outline` | 文件路径 | 大纲 JSON（见输入示例），必需之一 |
| `--topic` | 字符串 | 无大纲时的快速主题（产出空骨架） |
| `--section` | 字符串 | 只起草单个章节 |
| `--audience` | beginner/intermediate/expert | 默认 `intermediate`；脚本不校验，归一由 agent 负责 |
| `--output` | 文件路径 | 写出初稿 JSON |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|-------------|------|------|
| `[ERROR] 大纲文件不存在` | 路径错误 | 确认文件存在，修正路径后重跑 |
| `Need --outline, --topic, or --section` | 缺输入 | 补 `--outline` 或改用纯提示词模式 |
| 某节字数偏离 >20% | 要点过少/过多 | 拆分或合并 `points`，重生成该节；不注水 |
| `audience` 取值非法 | 自由文本 | agent 归一到三档枚举并向用户复述映射 |
| 想边写边改 | 起草纪律缺失 | 停止。把想改的点记进 `note`，交付后统一交给 content-editor |
| research_notes 为空 | 无米之炊 | 向用户索要素材；否则数据处写"待补充"，禁止编造 |

## 交付标准

- 成功定义：产出完整初稿，所有章节 `draft` 非空，总字数接近 `total_words_target`。
- 产物命名：`draft.json`（结构化）或 `draft.md`（Markdown）。
- 保存位置：用户指定目录；脚本用 `--output` 指定，默认标准输出。
- 完整性验证：`sections` 数量 == 大纲章节数；每节 `word_count` 落在目标 ±20%；`status=="draft"` 且 `needs_review==true`。

## 参考

- `references/drafting-tips.md` —— 分章节类型的写作技巧，撰写步骤 2 时按需读取。
- `references/sources-and-methodology.md` —— 暗知识逐条来源与采信纪律。
