---
name: exercise-generator
description: "Generate strict mastery exercises for course checkpoints: open-ended conceptual questions (MCQ banned to prevent guessing), difficulty ladder (recall / apply / transfer), answer rubric with point bands, and common-trap annotations. Machine-checkable block format enforced by exercise_lint.py. Use when the user asks to 出题 / 生成习题 / 题库 / quiz / 练习题 / 考题, or automatically after course-designer produces checkpoints. Do NOT use for designing the course skeleton (course-designer), nor for teaching interactively (feynman-explainer)."
license: Apache-2.0
compatibility: Python 3.8+ (exercise_lint.py); no third-party dependencies.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: education
  pattern: single-task
  tier: standard
  verified-date: "2026-09-14"
---

# Exercise Generator

给 checkpoint 生成**防蒙的严格习题**。核心纪律：**开放题为主、选择题默认禁用**——选择题能蒙对 25%，蒙对的分数会污染"是否掌握"的判定，掌握式设计毁于一旦。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| checkpoint | ✓ | course-designer 的产出（可判定目标） |
| 题型配比 | ✗ | 默认 概念解释 2 + 应用 2 + 迁移 1 |
| 难度 | ✗ | 跟随学习者画像，不单独放水 |

## 工作流

### 步骤 1：按难度阶梯出题

| 层级 | 题型样例 | 判定 |
|------|----------|------|
| recall | "用自己的话定义 X，不抄教材原句" | 是否覆盖核心要素 |
| apply | "给定场景 S，你会怎么用 X 解决，写出步骤" | 步骤是否正确使用机制 |
| transfer | "表面无关的 T 场景里，X 的哪个性质适用" | 是否抓住不变量 |

### 步骤 2：每题按五字段块输出

```markdown
### Q1 [apply]
题干：给定 <具体场景>，<需要动用 checkpoint 机制的问题>
参考答案：<关键要素清单，要素齐全即满分>
评分标准：5 分制——关键要素各 1 分 + 表述完整 1 分；要素缺失按档扣
常见陷阱：<学员最常踩的坑，判卷时优先核对>
关联：CP2
```

纪律：**评分标准与题同时出**（判卷时不能现编标准）；常见陷阱来自 checkpoint 的易混概念；每题标注归属 checkpoint，通过判定不跨题。

### 步骤 3：跑习题 lint（机器守门）

```bash
python3 exercise_lint.py --file quiz.md
python3 exercise_lint.py --file quiz.md --no-mcq
```

检查：五字段齐全、难度标签合法、checkpoint 关联存在、（--no-mcq 时）禁选择题。非零退出码 = 有违规。

### 步骤 4：链条移交

交付题库（lint 全绿）。**接着说："题库就绪，可交 feynman-explainer 对未通过的概念做补救伴学"**——掌握闭环：测不过 → 费曼重教 → 重测。

## 失败处置表

| 现象 | 原因 | 处置 |
|------|------|------|
| 学员蒙对 | 用了选择题 | --no-mcq 重出，开放题改写 |
| 答案背书也能得高分 | 题干含答案关键词 | 题干重写，场景化包装 |
| 判卷尺度漂移 | 评分标准缺失或含糊 | 五字段块强制，要素化评分 |
| 全员不及格 | 难度超 checkpoint 目标 | 回 course-designer 校 level，不是加简单题 |

## 参考

掌握式测验设计出处见 course-designer 的 sources-and-methodology.md（同包共享）。
