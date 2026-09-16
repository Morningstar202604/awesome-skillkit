---
name: own-voice-rewrite
description: "Rewrite a homework draft in the student's own voice: calibrate wording to grade level (primary / middle / high-school vocabulary, sentence-length caps, rhetoric depth), force-inject the student's real personal materials in place of generic filler, add restrained human touches (burstiness, concrete scenes, one natural flaw), then re-audit with ai-trace-auditor and deliver with a read-through-before-submitting reminder. The human-warmth core of the homework-autopilot chain. Use when the user asks to 学生口吻重写 / 改得像我写的 / 去掉作文腔 / rewrite in student voice / make it sound like me / 降维到我的水平 / 像学生写的. Do NOT use for experiences the student never had, nor as a guarantee against AI detection."
license: Apache-2.0
compatibility: Pure prompt-based; no runtime dependencies.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: education
  pattern: workflow
  tier: powerful
  verified-date: "2026-09-16"
---

# Own Voice Rewrite（学生口吻重写）

AI 初稿工整但冷血，一眼机器。本技能是 homework-autopilot 链条的"有温度"核心：把 solution-drafter 的初稿降维到学生本人的语言水平，用真实素材替换空话，再交给 ai-trace-auditor 复检——终稿必须经得起老师追问"这段你自己写的？说说你怎么想的"。

## 输入清单

| 输入 | 必需 | 说明 |
|---|---|---|
| draft | 是 | solution-drafter 的 draft JSON；须含 content / used_materials / checklist_pass |
| 年级与学科 | 是 | "初中二年级语文"——决定语言水平校准档位 |
| 补充素材 | 否 | 重写中发现的素材缺口，允许中途补一轮 |

缺输入时一次性问齐：

> 请提供：① 初稿（draft JSON 或全文）② 年级和学科。
> 另外确认一下：初稿里的经历都是你的真实经历吗？有出入现在指出。

## 前置自检

本技能纯 prompt 驱动：无脚本、无端点、无环境变量。三点核对：

1. draft 里有 used_materials 吗？——空数组意味着正文不该有任何个人经历，重写只做语言降维。
2. 年级明确吗？——不明确则语言校准失去基准，必须先问，不猜学段。
3. 正文里有没有用户没提供过的经历？——有则先核对（红线 1），核对不过就删。

## 红线（硬性禁令，不可协商）

1. 不虚构用户未提供的经历：重写只能调度 used_materials 里已有的素材，缺料处保留占位并提示用户补充。
2. 终稿保留学生可复述的难度：改写完成后学生必须能复述全文大意与关键细节——答不上老师追问 = 失败交付。
3. 交付物必须附"建议通读一遍再提交"：终稿附誊写建议，建议学生读一遍、顺手改成自己的习惯用词，再手抄或提交。
4. 不担保过 AI 检测：复检分数下降是设计目标，但禁止向用户承诺"老师看不出来"。
5. 信息层只减不加：数字、术语、结论、引用不可动（对齐 humanize-rewriter 禁改清单），改写只动表达层。

## 工作流

### 步骤 1：语言水平降维

- **动作：** 按年级档位校准全文（参照表如下；上限均为经验值，可调）：

| 学段 | 词汇上限 | 单句长度上限 | 修辞深度 | 禁用腔调 |
|---|---|---|---|---|
| 小学 | 常用字词，成语每篇 ≤3 个 | ≤20 字 | 比喻 / 拟人各 1-2 处 | 论文腔、四字堆砌、"首先其次最后" |
| 初中 | 成语与书面语可用 | ≤30 字 | 排比、引用课文可用 | "综上所述"式总结、政论腔 |
| 高中 | 抽象概念可用 | ≤40 字 | 辩证、让步、反问可用 | 空洞口号、堆砌名言 |

- **动作（续）：** 逐句扫描——超限句拆短；超档词换同义常用词；命中禁用腔调整句重写。
- **预期：** 全文无超档词与超限长句；高中生作文里不出现"综上所述，本文构建了……"。
- **若失败：** 某术语无法降维（如数学专名）→ 保留术语，并确保上下文给了白话解释。

### 步骤 2：素材注入替换空话

- **动作：** 找出正文所有空话句（"我明白了坚持的意义""这让我受益匪浅"），用 used_materials 里的真实素材替换或锚定。
- **预期：** "上周我弟把牛奶打翻在作业本上，我盯着那滩渍子发呆"替代"我认识到细节的重要性"——感受必须落到具体场景。
- **若失败：** 素材不够撑全文 → 一次性列出缺口请用户补；补不齐处保留 <<material:xxx>> 占位，禁止编造（红线 1）。

空话句替换对照示例：

```text
空话：这次经历让我明白了坚持的意义
替换：跑到第 4 圈时我腿肚子直转筋，但还是迈过去了——原来"坚持"就是那时候没停

空话：这本书内容深刻，令我受益匪浅
替换：读到主角把最后的面包分给妹妹那段，我停下来看了天花板好一会儿

空话：我认识到细节的重要性
替换：上周我弟把牛奶打翻在作业本上，我盯着那滩渍子发呆——少盖一秒杯盖，作业就得重写
```

- **预期（对照）：** 每条替换都满足"感受落到场景、场景来自 used_materials"两个条件。
- **若失败：** 替换句写得很具体但素材库里没有对应条目 → 那就是编造，删掉换占位。

### 步骤 3：人味微调（克制版）

- **动作：** 沿用 humanize-rewriter 的手法但更克制——连续两个长句后接一个 ≤8 字短句（burstiness）；抽象概括换具体名词与数字；允许一处合理的口语化表达、一个不算华丽的排比；留一点"想写但没写透"的余地。
- **预期：** 全篇满分作文腔消失；但不刻意堆口语——学生腔是"真诚的平实"，不是"扮嫩"。
- **若失败：** 改过头（口语密度过高）→ 回滚上一版，降低改动密度重试。

### 步骤 4：ai-trace-auditor 复检

- **动作：** 对终稿跑 ai-trace-auditor，与改写前的初稿分数对比。
- **预期：** 复检分数必须低于改写前；verdict 至少提升一档。
- **若失败：** 分数不降反升 → 按 findings 定位回步骤 3 针对性再改；两轮仍不过则如实告知剩余痕迹。

### 步骤 5：输出终稿与誊写建议

- **动作：** 汇总为 final JSON（结构见产出规格），结尾必须附提示："建议通读一遍再提交——读出声，别扭的地方改成你自己的说法，老师问起来你也答得顺。"
- **预期：** JSON 可被 json.loads 解析；reaudit.after 大于 reaudit.before；read_through_note 存在。
- **若失败：** 字数跌破 requirements 下限 → 用素材细节补足后重跑步骤 4，禁止注水空话。

可复述性快测（红线 2 的落点，30 秒完成）：

```text
1. 请学生用一句话说终稿写了什么；
2. 抽问一个具体细节（"第 3 段那件事发生在哪天？"）；
3. 两问都答得上 → 可复述达标；答不上 → 该处简化或回炉。
```

## 产出规格

final JSON 结构：

```json
{
  "content": "学生口吻终稿",
  "changes": [
    {"pos": "第 2 段", "before": "我明白了坚持的意义", "after": "跑到第 4 圈时我腿肚子直转筋，但还是迈了", "why": "空话换具体场景"}
  ],
  "reaudit": {"before": 42, "after": 78},
  "read_through_note": "建议通读一遍再提交：读出声，别扭处改成自己的说法",
  "placeholders": ["<<material:春游感受>>"],
  "grade_check": "小学档：无超 20 字长句，成语 2 个"
}
```

| 字段 | 约束 |
|---|---|
| changes | 每条含 before / after / why，可逐条回溯 |
| reaudit.after | 必须大于 before（ai-trace-auditor 分数越高越像人写） |
| read_through_note | 必填（红线 3） |
| grade_check | 写明所用学段档位与核对结论 |

## 失败处置表

| 现象 | 原因 | 处置 |
|---|---|---|
| 复检分数不降反升 | 降维时引入新套话 | 按 findings 定位回改，两轮不过如实告知剩余痕迹 |
| 素材撑不起全文 | 用户给料太少 | 一次性列缺口请补；补不齐保留占位，禁止编造 |
| 学生说"不像我写的" | 校准档位错或口头禅没对齐 | 请学生给一段自己写的文字对照，重新校准后重改 |
| 字数跌破下限 | 删空话删过头 | 补真实细节（素材展开），不加空话 |
| 学生怕老师追问 | 可复述性不达标 | 让学生对终稿做一次复述练习，卡壳处简化到能复述为止 |
| 高年级仍带论文腔 | 步骤 1 档位没用对 | 按禁用腔调清单逐句重扫 |
| 老师要求"华丽文风" | 与人味目标冲突 | 以老师要求为准——升维文采，但素材仍必须真实 |
| 正文含引用名句 | 用户初稿自带 | 保留引用并核对出处标注未丢（红线 5） |
| 数学/英语题被改出歧义 | 表达层改动动了术语 | 回滚该句：理科术语与英语句型框架不可降维，只降说明文字 |
| 学生年级跨档（如复读生） | 档位表只有三档 | 按学生实际写作水平就近取档，grade_check 里注明取档理由 |
| 占位符忘在终稿里 | 步骤 5 汇总遗漏 | 交付前全文搜 <<material:，有残留就先提示用户补素材或删除该段 |

## 交付标准

- final JSON 可被 json.loads 解析，reaudit.after 大于 reaudit.before。
- changes 可逐条回溯：每条 before 能在初稿定位，after 能在终稿定位。
- 全文无虚构素材：每个场景、数字、感受都能溯源到 used_materials。
- 年级校准通过：无超档词汇、无超限长句、无禁用腔调命中。
- read_through_note 在场；学生对照终稿能完成一次复述。

## 参考

- `references/sources-and-methodology.md` —— 需要说明年级语言水平校准依据、burstiness 手法来源或对外署名时读。

## 链路位置

- 上游：solution-drafter（必接——本技能只吃 draft JSON）。
- 联动：ai-trace-auditor（改后复检，步骤 4）；humanize-rewriter（writing 域同源手法，本技能更克制）。
- 下游：feynman-explainer 闭环——把终稿复述给他人听一遍（复述 = 内化），讲不顺的段落回炉。
