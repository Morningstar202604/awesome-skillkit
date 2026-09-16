---
name: assignment-intake
description: "Parse a homework assignment into a machine-usable assignment-plan JSON: identify the type via a 9-type decision table (essay / diary / reading response / math / english writing / handmade poster / slides / survey report / lab report), extract hard requirements (word count, format, deadline, must-include, forbidden items) with per-item evidence, map scoring dimensions, and list the personal materials the student must supply. Entry point of the homework-autopilot chain; output feeds solution-drafter. Use when the user asks to 审题 / 拆解作业 / 帮我做作业 / 分析题目要求 / 作业拆解 / assignment intake / homework analysis / 解析作业要求. Do NOT use during live exams or quizzes (考场现场不适用), nor for pure tutoring questions without a graded deliverable."
license: Apache-2.0
compatibility: Pure prompt-based; no runtime dependencies.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: education
  pattern: single-task
  tier: standard
  verified-date: "2026-09-16"
---

# Assignment Intake（作业审题拆解）

"帮我做作业"一句话开不了工。本技能把作业原文拆成机器可执行的作业计划单：题型是什么、老师卡什么（硬性要求）、得分点在哪（评分点）、还缺学生哪些真实素材——输出 assignment-plan JSON，是 homework-autopilot 链条的地基。

## 输入清单

| 输入 | 必需 | 说明 |
|---|---|---|
| 作业原文 | 是 | 拍照转写 / 直接粘贴 / 口述转写均可；不接受"就是老师说的那个作文"式转述 |
| 年级与学科 | 是 | "小学五年级语文"——决定评分点默认维度与下游语言水平校准档位 |
| 已有素材 | 否 | 学生已想到的经历 / 感受 / 数据；缺了不阻塞，由步骤 5 补齐清单 |

缺必填项时一次性问齐（一轮问完，不追问第二轮）：

> 请提供：① 作业原文（拍照转写或粘贴全文）② 年级和学科 ③ 截止时间（原文写了就不用答）。
> 已有的想法、经历、数据可以一并发来；没有也没关系，我会在计划单里列出还缺什么。

## 前置自检

本技能纯 prompt 驱动：无脚本、无端点、无环境变量。开工前核对三点：

1. 作业原文完整吗？——转写文本若以省略号或"后面还有"结尾，先要全文再拆题；半份题目拆出来的要求必漏。
2. 年级学科明确吗？——两者都缺不算完备，评分点映射依赖学段。
3. 是不是考试现场？——用户在考场、随堂测验、限时作业进行中发来题目，触发红线 1，立即停止。

## 红线（硬性禁令，不可协商）

1. 考试与现场测验不适用本链路：任何考试、测验、限时作业进行中的拆题请求一律拒绝，并说明这是课后作业流程。
2. 绝不虚构个人经历：needed_materials 列出的经历 / 感受 / 数据，用户没提供就是没提供——宁可标占位符缺料开工，禁止编造"我奶奶""上周比赛"式细节。
3. 只拆题不作答：本技能禁止输出任何答案内容，作答是下游 solution-drafter 的职责。
4. requirements 逐条可回溯：每条硬性要求必须附原文引用（evidence）；原文没有的项标 not_specified，禁止臆造"老师要求 800 字"。

## 工作流

### 步骤 1：作业原文入库

- **动作：** 拿到原文与年级学科，标注来源（拍照转写 / 粘贴 / 口述）。
- **预期：** 完整文本在手，年级学科明确。
- **若失败：** 转写有乱码或缺页 → 指出缺口请用户补传，一次问清，不逐字猜。

### 步骤 2：题型识别（决策表）

- **动作：** 按下表逐行判定，取第一个命中的行；输出唯一 type。

| 题型 type | 判定依据（满足即命中） | 典型措辞信号 |
|---|---|---|
| essay（作文/记叙文） | 有题目或话题 + 要求成文 + 无"读后/观后/调查"限定 | "写一篇作文""不少于 600 字" |
| diary（日记/周记） | 标题或要求含日记/周记 + 有日期或"记录一天/一周" | "写一篇日记""周记一则" |
| reading_response（读后感/观后感） | 要求围绕某本书、文章或影片写感受 | "读《XX》有感""观后感" |
| math（数学应用题/计算题） | 有具体数字与问题，答案可验算 | "求解""列式计算""应用题" |
| english_writing（英语作文） | 题干为英文且要求成文 | "Write a passage about..." |
| handmade_poster（手抄报） | 要求图文排版的手工或电子版面 | "手抄报""黑板报""配图" |
| slides（PPT 作业） | 要求以页/张为单位的多页演示 | "做一份 PPT""不少于 8 页" |
| survey_report（调研报告） | 要求收集数据、问卷或访谈后成文 | "调查""问卷""统计一下" |
| lab_report（实验报告） | 有实验步骤或观察记录模板 | "实验报告""实验目的""实验步骤" |

- **预期：** type 唯一；复合题（如"调研 + PPT 汇报"）拆成主 plan + 附加 plan，标注 primary / secondary。
- **若失败：** 九类都不命中 → 归入 other，在 notes 写明不确定点请用户确认，不硬套。

### 步骤 3：硬性要求提取

- **动作：** 从原文逐条抽取：字数、格式（稿纸 / 横线本 / 页数）、截止时间、必含要点（如"要有环境描写"）、禁含项（如"不得出现真实校名"）。
- **预期：** requirements[] 每条含 item + evidence（原文引用）+ status（specified / not_specified）。
- **若失败：** 原文某维度完全没提 → 该项 status 填 not_specified，不按惯例臆造。

### 步骤 4：评分点映射

- **动作：** 按题型给默认评分维度，每条写成可判定的检查点：

| 题型 | 默认评分维度 |
|---|---|
| essay / diary / reading_response | 立意切题 / 结构完整 / 素材真实具体 / 文采与卷面 |
| math | 列式正确 / 步骤完整 / 计算无误 / 有验算 |
| english_writing | 要点覆盖 / 语法准确 / 句型多样 / 书写规范 |
| handmade_poster / slides | 主题突出 / 版面结构 / 内容充实 / 图文配合 |
| survey_report | 方法交代 / 数据真实 / 分析有据 / 结论对应数据 |
| lab_report | 步骤完整 / 记录如实 / 结论对应现象 / 有反思 |

- **预期：** scoring_points[] 共 3-6 条，全部可判定（"有验算"可以，"写得真好"不行）。
- **若失败：** 老师给了明确评分标准 → 以老师标准整体替换默认维度，并标注 source: teacher。

### 步骤 5：真实素材清单（关键步骤）

- **动作：** 列出完成这份作业必须由学生提供的个人真实素材，按题型定向：essay / diary 要亲身经历与当时的感受；reading_response 要真实读过的证据（印象最深的情节）；math 要题目原文（学生抄错题最常见）；survey_report 要真实收集的数据；lab_report 要真实实验记录。
- **预期：** needed_materials[] 每条含 material + why + how_to_provide；当场能给的就收下，给不了的进占位。
- **若失败：** 用户说"你自己编" → 触发红线 2，解释为什么不行，然后缺料开工。

### 步骤 6：输出计划单并移交

- **动作：** 汇总为 assignment-plan JSON（结构见产出规格），接着说："审题完成，继续调用 solution-drafter 按题型作答。"
- **预期：** JSON 可被 json.loads 解析；plan[] 与评分点一一对应。
- **若失败：** JSON 序列化失败 → 修复转义后重出，禁止交付半结构化文本。

## 产出规格

assignment-plan JSON 结构：

```json
{
  "type": "essay",
  "grade_subject": "小学五年级语文",
  "requirements": [
    {"item": "不少于 400 字", "evidence": "原文：不少于 400 字", "status": "specified"}
  ],
  "scoring_points": ["立意切题", "结构完整", "素材真实具体", "文采与卷面"],
  "needed_materials": [
    {"material": "一件亲身经历的小事", "why": "记叙文核心素材", "how_to_provide": "口述或列出 2-3 件候选"}
  ],
  "plan": ["确定立意与素材", "列段落大纲", "成文"],
  "notes": "复合题在此标注 primary/secondary"
}
```

| 字段 | 约束 |
|---|---|
| type | 步骤 2 决策表枚举值之一（essay / diary / reading_response / math / english_writing / handmade_poster / slides / survey_report / lab_report / other） |
| requirements[].status | specified / not_specified，禁止第三态 |
| scoring_points | 3-6 条，全部可判定 |
| needed_materials | 允许为空数组（材料齐全时），但不允许含虚构内容 |
| plan | 步骤序列，与 solution-drafter 的执行顺序一致 |

## 失败处置表

| 现象 | 原因 | 处置 |
|---|---|---|
| 照片转写有错字 | 拍摄模糊 / 手写体 | 指出可疑处请用户核对；数字与题目条件必须人工确认 |
| 复合题型 | "调研 + 汇报"式组合 | 主 plan 标 primary，附加部分标 secondary，下游分别执行 |
| 素材问不齐 | 用户不愿提供 | 缺料开工，计划单标 <<material:简述>> 占位，绝不虚构 |
| 老师标准与默认维度冲突 | 步骤 4 用了默认表 | 以老师标准整体替换，标注 source: teacher |
| 题目含糊（"写一篇文章"） | 缺题型与字数 | 按 other 归类，一次性问清题型与字数再出计划单 |
| 用户在考试现场求助 | 触碰红线 1 | 拒绝并说明边界，不提供任何拆题或作答 |
| 用户只要答案不要计划 | 跳过地基 | 坚持先出 assignment-plan——没有 requirements 的作答无法自检 |
| 口述题目记不全 | 学生记忆偏差 | 请用户回看作业本或群通知补全，不按"大概是这样"拆题 |

## 交付标准

- assignment-plan JSON 可被 json.loads 解析，六个顶层字段齐全。
- 每条 requirement 带 evidence 且能在原文定位；not_specified 如实标注。
- 题型判定有据：能指出命中决策表哪一行的哪个依据。
- needed_materials 只含"待学生提供"条目，无任何编造素材。
- 学生能看懂计划单——这份作业要做什么、卡在哪、还缺什么，三件事一页说清。

## 参考

- `references/sources-and-methodology.md` —— 需要说明题型分类依据、评分维度出处（布鲁姆分类）或对外署名时读。

## 链路位置

- 上游：老师布置的作业原文（拍照 / 粘贴 / 口述）；与 exercise-generator（老师视角出题）互为镜像——它从知识点生成题目，本技能从题目还原要求。
- 下游：solution-drafter（必接，接收本技能的 assignment-plan 与素材清单）。
- 红线提醒：考试与现场测验不适用本链路，链路上任何技能都不豁免这一条。
