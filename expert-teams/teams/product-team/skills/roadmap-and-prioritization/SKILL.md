---
name: roadmap-and-prioritization
description: 路线图与优先级指南。覆盖 RICE/Kano/MoSCoW 优先级模型、版本节奏规划、依赖排序、机会成本权衡与季度路线图模板，把有限资源排到高价值事项上。适用于 product-roadmap-planner、product-manager 做版本规划与优先级决策。
license: MIT
compatibility: universal
---

# 路线图与优先级指南

本 skill 是 product-roadmap-planner 的工作手册。核心原则：**优先级不是拍脑袋，而是用模型把价值、成本、风险摆到桌面上比较；路线图是方向假设，不是合同。** 资源永远不够，关键是排序逻辑可被复现和复盘。

## 这是什么

一套优先级与路线图方法。核心工具：RICE（Reach×Impact×Confidence/Effort）排功能，Kano 区分基本型/期望型/兴奋型需求，MoSCoW 圈定本期 Must/Should/Could/Won't。每个版本标注时间盒与依赖，季度路线图按主题滚动。

## 何时使用

- product-roadmap-planner 接到"下个版本做什么/排优先级"任务时，必须加载本 skill。
- product-manager 在多需求冲突、需要说服干系人时，参考本指南用模型量化排序。
- product-data-analyst 提供 Reach/Impact 数据输入时，参考本指南明确需要哪些指标。
- product-qa-reviewer 终检路线图时，核对优先级是否有依据、Won't 范围是否明确。

## 核心步骤

1. **列全候选需求**：把所有待做事项汇总成清单，每条写清来源（用户反馈/数据/业务）。
2. **打 RICE 分**：估算 Reach（影响用户数/周期）、Impact（0.25/0.5/1/2/3 档）、Confidence（%）、Effort（人周），算 RICE 得分排序。
3. **套 Kano 修正**：把需求分基本型（不做会掉分）、期望型（越多越好）、兴奋型（惊喜）；基本型先保底。
4. **圈本期范围**：用 MoSCoW 定 Must/Should/Could/Won't Have，Won't 明确写出，防蔓延。
5. **排依赖与节奏**：识别前后依赖，按时间盒切版本（如 2 周迭代/季度主题），标出关键路径。
6. **定复盘点**：每个版本/主题标注成功指标与复盘时间，路线图按数据滚动调整。

## 清单

- [ ] 候选需求清单完整，每条标了来源。
- [ ] 每条需求有 RICE 估算（Reach/Impact/Confidence/Effort）。
- [ ] Kano 分类标注了基本型需求是否已保底。
- [ ] 本期 Must/Should/Could/Won't 圈定，Won't 明确。
- [ ] 依赖关系与关键路径标出。
- [ ] 版本按时间盒切分，节奏可执行。
- [ ] 每个主题定了成功指标与复盘时间。
- [ ] 排序逻辑可复现（换个人用同样数据能得到相近结果）。
- [ ] 资源总量与需求总量做了机会成本说明。

## 易错点

- **只看价值不看成本**：把高价值但超贵的需求排第一，导致版本永远做不完。Effort 必须进模型。
- **Confidence 虚高**：拍脑袋给 100%，实际是猜测。没有数据支撑时降到 50-80%。
- **路线图当承诺**：把季度路线图写成不可变合同，数据变了也不调。路线图是方向假设。
- **没有 Won't**：什么都想做，本期范围无限膨胀。必须显式写"本期不做"。
- **忽略依赖**：A 功能排在 B 前面，但 B 是 A 的前置，排期直接崩。
