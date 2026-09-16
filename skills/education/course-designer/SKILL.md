---
name: course-designer
description: "Design a mastery-based course from a topic: learning contract (scope/level/target/constraints, <=3 questions), checkpoint breakdown with dependency order, per-module study path, and exam-mode adjustments. Chain entry of edu-craft — checkpoints feed exercise-generator directly. Use when the user asks to 设计课程 / 做大纲 / 学习计划 / syllabus / curriculum / 训练营大纲 / 教我某学科. Do NOT use for generating exercises (exercise-generator), nor for interactive concept teaching (feynman-explainer)."
license: Apache-2.0
compatibility: Pure prompt-based; no runtime dependencies.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: education
  pattern: single-task
  tier: standard
  verified-date: "2026-09-14"
---

# Course Designer

链条入口。把一个主题变成**掌握式课程包**。核心是**学习契约先行**——不定"学到什么程度算学会"，课程就是知识点的随机堆砌；掌握式设计的全部价值在 checkpoint 的依赖排序。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 主题 | ✓ | "深度学习入门" / "给初中生讲光合作用" |
| 学习者画像 | ✓（缺就问，≤3 问） | 现有水平 / 目标产出（能解释？能做？能考？）/ 时间预算 |
| 约束 | ✗ | 教材范围、禁用前置知识、语言 |

缺输入时一次性问齐（≤3 问，一轮问完）："请补充：① 现有水平 ② 结业时想能做什么（能解释/能做/能考试）③ 每周可投入时间。有教材范围或禁用前置知识也一并说明。"

## 前置自检

本技能纯 prompt 驱动：无运行时依赖、无端点、无环境变量。唯一自检点：

```bash
test -f references/sources-and-methodology.md && echo OK
```

预期输出 `OK`；失败说明技能包不完整——掌握式设计纪律（步骤 2 排序纪律、步骤 3 深度控制）仍可执行，交付时注明方法论文献缺失。

## 工作流

### 步骤 1：订立学习契约（≤3 问）

```markdown
- scope:     学什么、学到哪个边界（明确"不学什么"同样重要）
- level:     beginner / intermediate / advanced / exam
- target:    结业时能解释什么、能做出什么、能通过什么
- constraints: 时间盒 / 案例领域偏好
```

信息足够时声明假设直接继续，**不许拿三个问题当开场白拖延**。

### 步骤 2：checkpoint 分解（4-6 个，依赖排序）

```markdown
CP1 概念地图：能用自己的话画出 X 与 Y 的关系
  ↓（依赖：CP1 的词汇）
CP2 核心机制：能解释 X 为什么会发生
CP3 动手应用：能在给定场景里用 X 解决一个具体问题
CP4 迁移挑战：能把 X 用到表面上无关的新场景
```

排序纪律：**每个 checkpoint 只依赖已通过的 checkpoint**——出现前向依赖就拆分重排。每项产出必须可判定（"能解释"可以，"理解"不行）。

### 步骤 3：按深度控制调整内容

| 级别 | 内容侧重 |
|------|----------|
| beginner | 词汇先行、日常案例、识别类问题 |
| intermediate | 方案对比、失效模式、应用类问题 |
| advanced | 边界情况、权衡取舍、迁移与综合 |
| exam | 追加回忆训练、限时题、评分标准、常见陷阱 |

### 步骤 4：链条移交

交付课程包（契约 + checkpoints + 每模块学习路径）。**接着说："课程骨架就绪，继续调用 exercise-generator 为每个 checkpoint 生成习题，或 feynman-explainer 做单概念伴学"**——链条自动展开。
- 预期：下游拿到的每个 checkpoint 目标可判定、依赖有序，可直接出题。
- 若失败：学员中途反馈起点不合适 → 回步骤 1 重校 level，插补齐模块，不推翻整包。

## 交付标准

- 产物：一份课程包 = 学习契约（4 字段）+ 4-6 个 checkpoint（含依赖标注）+ 每模块学习路径。
- 保存位置：直接输出在对话中（本技能不写文件），供 exercise-generator / feynman-explainer 引用。
- 完整性验证：每个 checkpoint 目标用"能解释/能做出/能通过"句式（可判定）；依赖只指向更早的 checkpoint；总时长 ≤ 契约时间盒。

## 失败处置表

| 现象 | 原因 | 处置 |
|------|------|------|
| checkpoint 之间跳步 | 前向依赖 | 拆分重排，保证只依赖已通过项 |
| 学员学不动 | 起点高于现有水平 | 回契约重校 level，插入补齐模块 |
| 产出不可判定 | 目标写成"理解/熟悉" | 改写为"能解释/能做出/能通过" |
| 课程太长学不完 | 没守时间盒 | 按 constraints 砍 checkpoint 数，保依赖完整 |

## 参考

- [sources-and-methodology.md](references/sources-and-methodology.md) —— 掌握式学习与学习契约的出处
