---
name: personal-voice-profile
description: "Distill a reusable personal voice profile from >=3 samples of the user's own writing: lexical habits and catchphrases, syntactic stats (sentence length median/variance, paragraph habits), tonal markers, structural tics, plus 3 verbatim representative snippets; outputs voice-profile.json and a one-page imitation card. Use when the user asks to 风格画像 / 提炼我的文风 / 分析我的写作习惯 / 让AI像我一样写 / voice profile / writing style analysis / mimic my writing style. Do NOT use on third-party text without the author's consent, and never to impersonate someone else."
license: Apache-2.0
compatibility: Pure prompt-based; no scripts, no environment probing. Optionally pairs with ai-trace-auditor's stdlib scanner downstream, but needs nothing itself.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: writing
  pattern: single-task
  tier: standard
  verified-date: "2026-09-16"
---

# Personal Voice Profile（个人风格画像）

"像我写的"的前提是知道"我"是谁。本技能从用户自己的历史文本中蒸馏出可复用的风格画像——词汇、句法、语气、结构四层加三段原文样本——让下游改写与写作技能有的放矢，而不是泛泛地"口语一点"。

## 输入清单

| 输入 | 必需 | 说明 |
|---|---|---|
| 历史文本样本 | 是 | ≥3 篇用户本人写的文章/帖子/邮件，越长越准；单篇 ≥200 字为宜 |
| 主要发布平台 | 否 | 公众号 / 知乎 / 即时通讯随笔——多平台样本风格可能分裂，需声明主样本 |
| 画像用途 | 否 | 供 humanize-rewriter 对齐 / 供自己复盘；用途影响指令卡的详略 |

缺必填项时，只问一次：

> 请一次性提供：① 至少 3 篇你本人写的文本（直接粘贴或给路径，单篇 200 字以上越好）；② 这些主要发在什么平台；③ 画像打算给谁用。

## 前置自检

本技能为纯 prompt 技能，无需探测运行环境，只检查输入完备性：

- 样本 ≥3 篇？不足 → 按红线 1 拒绝产出，用上面的问齐话术一次性补齐，不要拿 2 篇硬造。
- 样本是用户本人所写、或已获作者授权？未声明 → 先问一句归属与授权，再动手。
- 样本间风格差异是否异常大（如一篇论文 + 一篇闲聊）？是 → 在步骤 1 按语域分组，画像只对用户指定的主语域负责。

## 红线（硬性禁令，不可协商）

1. 样本 <3 篇拒绝产出：两篇文本撑不起风格画像，硬造出来的画像会误导下游改写——宁可问齐。
2. 授权边界：只分析用户本人创作或已获授权的文本；"模仿某某作家的文风"这类第三方模仿请求一律拒绝——本技能只做用户自己的画像。
3. 画像不得用于冒充他人：voice-profile.json 交付时附用途声明，用户将其用于身份冒充的，本技能不为后果背书。

## 工作流

### 步骤 1：通读与语域分组

- **动作：** 通读全部样本，判断是否同一语域（正式/口语、平台差异）；不同语域按用户指定分主次。
- **预期：** 一份语域判定记录：主样本是哪些、次样本如何降权。
- **若失败：** 用户说不清平台差异 → 全部按主样本处理，并在画像中注明语域局限。

### 步骤 2：词汇层统计

- **动作：** 统计高频实义动词（"搞/弄/盘" vs "执行/推进"）、口头禅与起手词（"其实""讲真""对了"）、标点习惯（破折号、省略号、感叹号的使用频率与位置）、中英夹杂倾向。
- **预期：** 每项给出频次或比例，附 1-2 处原文引用作证据；不写"偶尔使用"这类不可验证的模糊词。记录格式示例：

```text
高频动词：搞（14 次） > 踩坑（6 次） > 实现（3 次）
口头禅："其实"（11 次，7 次在句首）；"讲真"（4 次，全部段首）
标点：破折号每千字 2.1 次；省略号仅用于留白句尾；感叹号全样本 1 次
中英夹杂：技术词保留英文（pipeline / review），其余全中文
```

- **若失败：** 样本总量太小导致频次无意义 → 改为枚举式记录（出现过什么），并注明统计意义不足。

### 步骤 3：句法层统计

- **动作：** 统计句长中位数与方差（口径与 ai-trace-auditor 一致：有效字符数）、段落平均长度与段内句子数、列表使用习惯（爱不爱用列表、列表项平均长度）。
- **预期：** 数值可复核——按同样的口径人工抽测任意一段应对得上。记录格式示例：

```text
句长：中位数 22 字 / cv 0.58（口径：有效字符，去标点空白，与 trace_scanner 一致）
段落：平均 3.2 句/段；有 1 处一句话独段（转折用）
列表：5 篇仅 1 篇用列表，且项均 ≤ 12 字 → list_usage: rare
```

- **若失败：** 样本以短帖为主无段落概念 → 段落层标注 not_applicable，不硬造。

### 步骤 4：语气层归纳

- **动作：** 归纳自嘲/兴奋/冷静的基线比例、感叹词与语气词（哈、啊、嗯、hhh）、对读者的称呼（"你/大家/各位"）、情绪表达方式（直给 vs 反讽）。
- **预期：** 每项结论附原文片段支撑；样本覆盖不到的语气场景标注"未知"，不猜。归纳示例：

```text
基线：冷静克制，自嘲仅在踩坑场景出现（3 篇中 2 次）
称呼：通篇用"你"，从不出现"各位读者/家人们"
情绪方式：反讽 > 直给——吐槽用"挺好的，又炸了"式反话
感叹词："哈"单独成句表示无语，非笑声
```

- **若失败：** 样本全是工作邮件、语气单一 → 如实记录语域局限，提示用户补口语样本。

### 步骤 5：结构层归纳

- **动作：** 提炼开头套路（直接上干货 / 场景切入 / 先抛问题）、结尾套路（戛然而止 / 总结一句 / 抛问题给读者）、过渡习惯（小标题、分隔符、还是硬转）。
- **预期：** 每条套路给出现频次（如"5 篇中 4 篇直接上干货"）。
- **若失败：** 结构特征高度不一致 → 结论降级为"无明显固定套路"，这本身就是有效画像。

### 步骤 6：产出 voice-profile.json 与模仿指令卡

- **动作：** 汇总为 JSON，并另写一页模仿指令卡（给下游技能或人看的可执行指令）。

```json
{
  "lexical": {"catchphrases": ["其实", "讲真"], "punct_habits": {"dash_per_1k_chars": 2.1}},
  "syntactic": {"median_sentence_len": 22, "sentence_len_cv": 0.58, "list_usage": "rare"},
  "tonal": {"baseline": "冷静偏自嘲", "reader_address": "你", "interjections": ["哈"]},
  "structural": {"opening": "直接上干货(4/5)", "closing": "抛问题给读者(3/5)"},
  "example_snippets": ["原文片段1", "原文片段2", "原文片段3"]
}
```

- **预期：** JSON 可被 `json.loads` 解析；example_snippets 是逐字原文，最能代表风格的 3 段；指令卡含" DO / DON'T "各不少于 3 条。指令卡样例：

```text
模仿指令卡（一页）
DO   句子中位 22 字，长句后敢用三字短句收尾
DO   段首可用"其实""讲真"，但每篇最多两次
DO   技术词保留英文原词，不强行翻译
DON'T 用"综上所述/值得注意的是"这类公文套话
DON'T 连排三个感叹号——全样本感叹号只有 1 个
DON'T 结尾喊口号；用一个问题或一句收住
```

- **若失败：** JSON 序列化失败 → 修复转义重出；找不到 3 段代表性原文 → 如实减少并说明。

## 产出规格

| 产物 | 结构 | 说明 |
|---|---|---|
| voice-profile.json | lexical / syntactic / tonal / structural / example_snippets 五层 | 字段名英文；频次口径注明；可被下游程序读取 |
| 模仿指令卡 | 一页：四层结论 + DO/DON'T 清单 | DO 写"该怎么做"，DON'T 写"这个作者绝不会怎么做" |
| 语域声明 | 一句话 | 画像适用的语域与平台；超范围使用由调用方自担 |

## 失败处置表

| 现象 | 原因 | 处置 |
|---|---|---|
| 样本只有 1-2 篇 | 用户着急 | 按红线 1 拒绝，用问齐话术补样本；告知为什么不能硬造 |
| 样本风格严重分裂 | 多平台多语域混投 | 分组出画像或让用户指定主语域；画像标注适用范围 |
| 拿到的是别人的文章 | 想模仿第三方 | 触碰红线 2：拒绝，说明只做用户本人画像 |
| 画像空泛（"用户比较幽默"） | 结论缺证据 | 逐条回贴原文引用；贴不出的结论删除 |
| 样本全是正式文书 | 语域单一 | 如实产出并声明局限；建议补充日常文本 |
| example_snippets 凑不齐 3 段 | 样本太短 | 少于 3 段就少给，注明原因，不重复凑数 |
| 用户事后要求补入名人语料 "顺便学学他" | 触碰红线 2 | 拒绝；画像样本集一经确认不再混入第三方文本 |
| 同一用户要求出"另一个平台的画像" | 语域扩展需求 | 用该平台的样本另出一版画像，两版独立交付，不合并 |

## 交付标准

- voice-profile.json 可被 `json.loads` 解析，五层字段齐全（不适用的层标注 not_applicable）。
- 每条画像结论可追溯：附原文引用或出现频次；无凭空的风格断言。
- example_snippets 为逐字原文（可标注截取范围），3 段为宜、不足时如实说明。
- 模仿指令卡一页内可执行：下游 humanize-rewriter 拿到卡即可按 DO/DON'T 校准。
- 授权确认记录在案：样本归属与用途声明已向用户确认过一次，非默认假设。
- 频次口径可复算：换一个样本重跑统计，口径一致、结果不同属正常，口径漂移属缺陷。

## 参考

- `references/sources-and-methodology.md` —— 需要说明风格分析方法论的出处（voice/tone 区分、风格计量思路）或对外署名时读。

## 链路位置

- 上游：用户提供的历史文本；与 article-drafter 闭环——它产出的旧文也可作为画像样本。
- 下游：humanize-rewriter（喂 voice-profile.json，让改写对齐到"你本人"）；article-drafter 写新文时亦可读取画像对齐。
- 平行：own-voice-rewrite（education 域的学生作文场景，用的画像粒度更粗、以年级为锚）。
