---
name: solution-drafter
description: "Draft a homework solution per assignment type from an assignment-plan: math goes 审题→列式→逐步算→验算 with no skipped steps, essays go 立意→素材分配→段落大纲→成文, reports stay outline-first, English uses sentence frames then fills content; every step shows full working and the draft self-checks against every requirement in the plan. Middle stage of the homework-autopilot chain — the draft is deliberately AI-neat and must pass through own-voice-rewrite. Use when the user asks to 起草作业 / 分题型作答 / 写初稿 / 解答题目 / draft solution / solve homework / 按题型写作业. Do NOT use without an assignment-plan from assignment-intake, nor during live exams."
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

# Solution Drafter（分题型作答）

初稿机器。拿 assignment-plan 与真实素材，按题型路由到对应执行模板，产出"工整但带 AI 味"的初稿——工整是本技能的职责，人味是下游 own-voice-rewrite 的职责，两层不混。

## 输入清单

| 输入 | 必需 | 说明 |
|---|---|---|
| assignment-plan | 是 | 来自 assignment-intake 的 JSON；没有就先回上游跑审题 |
| 真实素材 | 是* | 对应 plan.needed_materials；*材料问不齐时允许占位模式开工 |
| 澄清答复 | 否 | 用户对计划单疑问的回应 |

缺输入时一次性问齐：

> 还差两样：① assignment-plan（上一步审题的结果；没有的话我先跑 assignment-intake）② 素材清单里你能提供的部分。给不了的全部告诉我，我按占位模式开工。

## 前置自检

本技能纯 prompt 驱动：无脚本、无端点、无环境变量。三点核对：

1. assignment-plan 在吗？type 与 requirements / scoring_points 可读吗？——缺了直接回上游，不裸开工。
2. 素材对齐吗？——逐条对照 needed_materials 分"已提供 / 缺料"两栏；缺的标占位，不允许顺手编。
3. 是不是考试现场？——plan.notes 或用户语境显示考场 → 触发红线 1，停止。

## 红线（硬性禁令，不可协商）

1. 考试与现场测验不适用本链路：与 assignment-intake 红线 1 同源，全链生效，本技能同样拒绝考场请求。
2. used_materials 只能记录用户提供的真实素材：正文出现的每个经历、数字、数据都必须能在 used_materials 里找到出处，找不到就删。
3. 数学必须验算：无验算行的数学题不允许交付。
4. 引用他人内容必须标注：名句、范文片段、教材定义一律注明出处，禁止化装成原创。
5. 理科步骤不可跳：跳步 = 学生看不懂 = 交付失败。

## 工作流

### 步骤 1：计划与素材对齐

- **动作：** 逐条核对 needed_materials，分"已提供 / 缺料"两栏；缺料项在正文标 <<material:xxx>>。
- **预期：** 对齐表完成，无模糊地带。
- **若失败：** 用户中途又给新素材 → 补进 used_materials 并重跑本步。

### 步骤 2：按题型路由执行

按 plan.type 进入对应模板，plan.plan 里的步骤逐项落实：

| type | 执行模板 | 产出形态 |
|---|---|---|
| math | 审题（已知/求）→ 列式 → 逐步计算 → 验算 | 分步过程 + 答案 + 验算行 |
| essay | 立意（一句话中心）→ 素材分配到段 → 段落大纲 → 成文 | 完整文章 + 段落大纲附后 |
| diary / reading_response | 定日期或书目 → 定感受锚点（哪件事/哪个情节）→ 叙议结合成文 | 正文 + 感受锚点标注 |
| english_writing | 审要点 → 句型框架（每要点 1-2 句）→ 填内容 → 语法自检 | 英文正文 + 要点覆盖表 |
| handmade_poster | 定主题 → 版面分区（标题区/内容区/插图区）→ 逐区写文案 | 版面方案 + 各区文案 |
| slides | 定大纲（每页一句结论）→ 逐页要点 → 讲稿提示 | 页级大纲 + 每页文案 |
| survey_report | 提纲确认（方法/数据/分析/结论四段）→ 逐段填充 | 提纲 + 成文 |
| lab_report | 按模板顺序填：目的/器材/步骤/记录/结论/反思 | 六段报告；记录段只填真实数据 |
| other | 按 plan.plan 步骤序列执行 | 与步骤序列一致 |

- **动作（续）：** 模板执行中每完成一段就回看 plan.requirements，防止跑偏。
- **预期：** 产出形态与表格一致；essay 成文不超过字数上限的 110%（经验值，可调）。
- **若失败：** 模板与 plan 冲突 → 以 plan.requirements 为准，模板让路。

math 模板最小示例（四步缺一不可）：

```text
题目：甲乙两地相距 360 km，汽车 3 小时行完，平均每小时行多少千米？
  审题：已知路程 360 km、时间 3 小时；求平均速度
  列式：360 ÷ 3
  逐步算：360 ÷ 3 = 120（千米/小时）
  验算：120 × 3 = 360，与已知路程一致 ✓
```

essay 模板最小示例（大纲先行）：

```text
题目：《一件小事》
  立意：小事里藏着家人的在意
  素材分配：开头场景（打翻牛奶）→ 经过（谁处理的、我怎么想）→ 结尾（当时的感受）
  大纲：4 段，每段一句话概括，成文时逐段展开
```

- **预期（示例对照）：** 自己的产出能对上示例的颗粒度——每步一行、有依据、可验算或可回溯。
- **若失败：** 产出颗粒度明显粗于示例（一步并了三步）→ 按示例拆细重写该部分。

### 步骤 3：过程完整展示

- **动作：** 理科每一步写出"为什么这么做"；作文把大纲附在正文后。
- **预期：** 学生能顺着初稿复述每一步的依据。
- **若失败：** 某步自己也讲不清为什么 → 停下重解，禁止糊弄过去。

### 步骤 4：对照 requirements 逐项自检

- **动作：** 把 plan.requirements 逐条变成检查项，pass / fail 逐条判定；scoring_points 同步过一遍。
- **预期：** checklist_pass 覆盖 100% requirements；fail 项当场修复后复检。
- **若失败：** 有 fail 修不动（如素材不足）→ 如实标 fail 并写明原因，禁止静默放行。

### 步骤 5：输出初稿并移交

- **动作：** 汇总为 draft JSON（结构见产出规格），接着说："初稿完成，工整但带 AI 味，继续调用 own-voice-rewrite 学生化。"
- **预期：** JSON 可被 json.loads 解析；content 与 checklist_pass 对应同一份正文。
- **若失败：** content 改动后忘了同步 checklist → 重跑步骤 4，禁止交付过期自检。

## 产出规格

draft JSON 结构：

```json
{
  "content": "初稿全文（或分步解答全文）",
  "checklist_pass": {
    "不少于 400 字": "pass",
    "必须有环境描写": "pass"
  },
  "used_materials": [
    "用户提供：上周弟弟把牛奶打翻在作业本上"
  ],
  "outline": "段落大纲（作文类附）",
  "verify_line": "验算行（math 类型必附）",
  "placeholders": ["<<material:春游感受>>"]
}
```

| 字段 | 约束 |
|---|---|
| checklist_pass | key 与 plan.requirements 一一对应，值只有 pass / fail |
| used_materials | 只含真实素材（红线 2）；空数组合法，但正文不得出现任何个人经历 |
| verify_line | type=math 时必填且验算成立 |
| placeholders | 与正文中 <<material:xxx>> 数量一致 |

## 失败处置表

| 现象 | 原因 | 处置 |
|---|---|---|
| 数学结果验算不过 | 列式或计算错误 | 回到列式重推，修到验算通过为止，禁止"答案差不多" |
| 正文出现没给过的素材 | 红线 2 被绕过 | 删掉该处或换占位符，重跑步骤 4 |
| 字数超限或不足 | 成文失控 | 超限砍修饰句，不足补素材细节，改后复检 |
| 用户直接要最终版 | 跳过下游 | 交付初稿并说明：学生化必须走 own-voice-rewrite |
| 题目本身有歧义 | 上游没问清 | 退回 assignment-intake 补问，不猜测作答 |
| 实验报告没有真实数据 | 学生没做实验 | 记录段全部留占位，禁止编数据（与红线 2 同源） |
| 英语作文要点漏写 | 要点覆盖表没对齐 | 补写漏点后重跑步骤 4 |
| 两道题步骤互相引用混乱 | 题序串了 | 每题独立成块，重新编号 |
| type=other 无既定模板 | 上游归类为 other | 严格按 plan.plan 序列执行，每步落一段，不自由发挥 |
| 素材与题目时间线对不上 | 学生口误或记错 | 与用户确认后改正时间线，禁止硬套进题目情境 |
| 手抄报 / PPT 只写了文案 | 忽略了版面维度 | 按产出形态补齐分区方案或页级大纲，缺版面的不算交付 |

## 交付标准

- draft JSON 可被 json.loads 解析，checklist_pass 覆盖全部 requirements。
- type=math 时 verify_line 存在且验算成立。
- 正文每个个人素材都能在 used_materials 追溯；placeholders 与正文占位一一对应。
- 理科每步有依据，无跳步；引用内容全部带出处。
- 初稿明确标注"工整但带 AI 味"——这是有意为之的中间态，不是缺陷。

## 参考

- `references/sources-and-methodology.md` —— 需要说明数学四步解题出处（波利亚）、过程性写作法来源或对外署名时读。

## 链路位置

- 上游：assignment-intake（必经，提供 assignment-plan 与素材清单）。
- 下游：own-voice-rewrite（必接——初稿是"AI 味工整版"，学生口吻化不在本技能职责内）。
- 平行：exercise-generator 从知识点出题，本技能从题目作答，方向相反；course-designer 的 exam 档 checkpoint 可作为本技能的练习来源。
