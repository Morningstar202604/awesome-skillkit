---
name: episode-publisher
description: "Package a rendered podcast episode for publishing: markdown shownotes (summary, guest/links, terminology table), timestamped chapter markers (podcasting 2.0 style), platform metadata (title formulas, episode numbering, cover spec) for Chinese platforms (Xiaoyuzhou/Ximalaya) and Apple Podcasts, plus the AI-content disclosure line. Reads the script and synthesis plan from upstream chain steps. Use when the user asks to 发播客 / shownotes / 章节标记 / 播客发布 / 小宇宙发布 / 节目元数据. Do NOT use for writing the script (podcast-producer), nor for synthesis/voice selection (tts-voice-director)."
license: Apache-2.0
compatibility: Pure prompt-based; no runtime dependencies.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: audio
  pattern: single-task
  tier: standard
  verified-date: "2026-09-14"
---

# Episode Publisher

链条收口。把合成好的音频打包成**可发布件**：shownotes、章节标记、平台元数据、AI 披露声明。音频好了发布件拉胯 = 白做——小宇宙的转化一半在 shownotes。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 脚本 | ✓ | podcast-producer 产出（有分段结构才能推时间戳） |
| 合成计划/音频 | ✓ | tts-voice-director 产出（段落时长用于章节估算） |
| 平台 | ✗ | 默认小宇宙 + Apple Podcasts 双规格 |

缺输入时一次性问齐："请提供：① 已合成的脚本 ② 每段实际时长（或音频文件时长）③ 期号与节目名（应来自节目配置，不手填）。"

## 前置自检

本技能纯 prompt 驱动：无运行时依赖、无端点、无环境变量。自检点是输入而非环境：**脚本与每段实际时长缺一不可**——没有实际时长就只能估时间戳，章节必然对不上音（见失败处置表第 1 行）。缺则问齐后 STOP。

## 工作流

### 步骤 1：写 shownotes（固定结构）

```markdown
## 一句话摘要（≤40 字，钩子式）
## 本期要点（3-5 条，每条一句话）
## 提及资源（链接 + 一句话说明）
## 术语表（脚本里易读错的词 → 正确读音/释义）
## 时间线（见步骤 2）
## 制作说明
- 本期使用 AI 语音合成制作，内容经人工审校。
```

纪律：摘要写"这期让你明白什么"，不写"我们聊了聊"；术语表直接复用 podcast-producer 阶段记录的易错词；**AI 披露是硬要求**——多平台已要求合成内容标注，写死在模板里。

预期：六段结构齐全、含 AI 披露行，摘要为钩子式且 ≤40 字。
若失败：上游没留易错词记录 → 术语表写「本期待补」并在交付说明里点出来，不要编造读音；摘要写成"我们聊了聊"这类大纲式 → 重写为结论式；披露行缺失 → 立即补上，这是平台硬要求，不补不许交付。

### 步骤 2：生成章节标记（podcasting 2.0 风格）

按脚本分段 + 合成计划里每段的实际时长推时间戳：

```text
00:00 开场
00:35 现象：工具从 3 个涨到 30 个
02:10 反直觉：演示与落地的差距
04:20 怎么做：分段流水线
06:00 收尾与预告
```

格式按 `HH:MM 章节名`；正片开始后的第一章节不早于 00:30（平台规范）。

预期：逐行 `HH:MM 章节名`，末章时间戳 ≤ 音频实际总时长。
若失败：手上只有预估时长没有实际时长 → 先向用户要实际音频时长（见前置自检），不要用预估凑；末章超出音频总时长 → 按实际时长整体重算一遍；第一章节早于 00:30 → 与开场合并或后移，符合平台规范。

### 步骤 3：平台元数据

| 字段 | 纪律 |
|------|------|
| 标题 | `[期号] 主题钩子`——期号放前便于排序；钩子 ≤20 字 |
| 副标题/一句话简介 | 与 shownotes 摘要同源，不另写 |
| 封面 | 3000x3000 方图（Apple 规范）；复用 visual-design-studio 链产出 |
| 分类 | 按平台分类表选一级；科技类默认「科技」+「教育」 |

预期：四个字段全部落值，标题带期号且钩子 ≤20 字。
若失败：期号无从获取 → 向用户要节目配置（期号不手填，见失败处置表）；平台不在分类表内 → 选最接近的一级并注明所选平台与原分类的差异，等用户确认后再定稿。

### 步骤 4：交付与链条闭环

交付：shownotes.md + chapters.txt + 各平台元数据卡。**链条到此收口**——"选题 → 脚本 → 合成 → 发布件"四步走完，缺哪步回哪步。
- 预期：发布件可直接粘贴到平台后台，无需再补字段。
- 若失败：平台审核驳回 → 按失败处置表对症修正后重交，不换平台绕审核。

## 交付标准

- 产物：`shownotes.md`（含 AI 披露行）、`chapters.txt`（`HH:MM 章节名` 逐行）、平台元数据卡（标题/副标题/封面规格/分类）。
- 保存位置：直接输出在对话中；存文件时按上述命名。
- 完整性验证：章节时间戳总和与音频实际时长一致（±1 章）；shownotes 六段结构齐全且含披露行；标题带期号且钩子 ≤20 字。

## 失败处置表

| 现象 | 原因 | 处置 |
|------|------|------|
| 章节时间戳对不上 | 用了预估时长没回填实际值 | 合成后按实际音频时长重算一遍 |
| 小宇宙审核不过 | AI 内容未披露 / 封面违规字 | 检查披露行；封面去极限词 |
| shownotes 没人看 | 写成了大纲 | 每条要点带信息量，直接给结论 |
| 期数乱 | 手写期号 | 期号从节目配置读，不手填 |

## 参考

方法论文献在 podcast-producer 技能包内（同包共享，技能包内不重复存放）：进入 podcast-producer 技能目录，读其 references 目录下的 sources-and-methodology 文档。平台披露要求与开源出处一并记录在该文件。
