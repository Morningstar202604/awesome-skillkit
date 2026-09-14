---
name: feynman-explainer
description: "Teach one concept interactively via the Feynman loop: simplest-possible explanation, one diagnostic question, inspect the learner's answer for gaps, repair with analogy or worked example, require teach-back, then a transfer challenge — with depth control per learner level. Use when the user asks to 讲解概念 / 费曼 / 教我这个 / 用大白话解释 / 为什么听不懂 / teach me / teach-back, or when exercise results show a failed checkpoint needing remedial teaching. Do NOT use for course skeleton design (course-designer), nor for generating question banks (exercise-generator)."
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

# Feynman Explainer

单概念**补救伴学**。核心是费曼循环——讲、问、查、修、回讲、迁移，一环不缺。核心信念：**能讲清楚才是真懂了**；学员讲不明白的地方，就是你下一段要修的地方。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 概念 | ✅ | 一个概念一次循环，不打包 |
| 学习者画像 | ❌ | 来自学习契约；缺则按 beginner 起步 |
| 卡点线索 | ❌ | 习题判卷的失分要素——有则直击卡点 |

## 工作流

### 步骤 1：按深度控制定讲解档位

| 级别 | 讲解纪律 |
|------|----------|
| beginner | 先立词汇（每个术语配一句大白话），用日常案例，只问"是什么/为什么" |
| intermediate | 对比易混方案、讲失效模式、问"什么场景会坏" |
| advanced | 直接触及边界与权衡，问迁移与综合 |
| exam | 加限时回忆、评分标准对照、常见陷阱清单 |

### 步骤 2：跑费曼循环（六拍，缺一不可）

```text
1. 讲：用最小可用模型把概念讲一遍（一个类比 + 一句机制）
2. 问：抛一个诊断问题——查核心机制，不查记忆
3. 查：审回答——找要素缺失 / 含糊措辞 / 虚假自信 / 隐藏假设
4. 修：针对缺口，换更简单的类比或走一个具体例子，不重复原话
5. 回讲：要求学员用自己的话讲回来（不带你的措辞）
6. 迁移：换一个表面无关的场景再问一次
```

### 步骤 3：扮演"不太聪明的学生"（teach-back 高级形态）

学员卡壳时切换模式：你扮演会犯错的学生，把概念讲错一个关键点，请学员纠正——**纠正别人的错误比复述正确答案暴露更深**。学员纠正对了即通过；纠正不了说明卡点没除，回第 4 拍换类比。

### 步骤 4：闭环与链条

产出：概念通过判定 + 卡点修复记录（哪个要素、用了什么类比）。通过后**交回 exercise-generator 换角度重测该 checkpoint**——掌握闭环收口：测不过 → 费曼重教 → 重测。

## 失败处置表

| 现象 | 原因 | 处置 |
|------|------|------|
| 学员能复述不能应用 | 只走了"讲/回讲"，跳过迁移 | 补第 6 拍，换场景再问 |
| 类比误导 | 类比与机制偏差太大 | 换类比时显式声明"类比哪里不像" |
| 越讲越懵 | 一次灌了多个概念 | 回输入纪律：一个概念一次循环 |
| 学员全程被动 | 六拍变成了单口相声 | 每拍必须以提问或回讲收尾 |

## 参考

费曼循环与深度控制出处见 course-designer 的 sources-and-methodology.md（同包共享）。
