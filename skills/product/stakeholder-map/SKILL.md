---
name: stakeholder-map
description: >-
  Build a stakeholder map using a power/interest grid, identify communication strategies per quadrant, and generate a communication plan. Use when managing stakeholders, preparing for a launch, aligning cross-functional teams, or planning stakeholder engagement.
description_zh: "用权力/利益矩阵构建干系人地图，识别各象限沟通策略并生成沟通计划"
license: MIT
compatibility: 纯提示型，任意支持 SKILL.md 的工具可用；无外部依赖。
metadata:
  author: "phuryn/pm-skills 上游（MIT）"
  version: "1.0.0"
  category: product
  pattern: single-task
  tier: standard
  verified-date: "2026-09-27"
  source: "https://github.com/phuryn/pm-skills/tree/main"
---

## Stakeholder Mapping & Communication Plan

Map stakeholders on a Power × Interest grid and create a tailored communication plan for each group.

### Context

You are helping build a stakeholder map for **$ARGUMENTS**.

If the user provides files (org charts, project briefs, team rosters), read them first. If they describe the product or initiative, use that context to infer likely stakeholders.

### Instructions

1. **Identify stakeholders**: List all relevant individuals and groups — executives, engineering leads, designers, marketing, sales, support, legal, finance, external partners, and end users.

2. **Classify each stakeholder** on two dimensions:
   - **Power** (High/Low): Their ability to influence decisions, resources, or outcomes
   - **Interest** (High/Low): How much the project directly affects them or how engaged they are

3. **Place stakeholders in the Power × Interest grid**:

   | | High Interest | Low Interest |
   |---|---|---|
   | **High Power** | **Manage Closely** — Regular 1:1s, involve in decisions, seek their input early | **Keep Satisfied** — Periodic updates, escalate only critical issues |
   | **Low Power** | **Keep Informed** — Regular status updates, invite to demos, gather feedback | **Monitor** — Light-touch updates, available on request |

4. **For each quadrant**, recommend:
   - Communication frequency (daily, weekly, bi-weekly, monthly)
   - Communication format (1:1, email, Slack, meeting, dashboard)
   - Key messages and framing
   - Potential risks if this stakeholder is neglected

5. **Create a communication plan table**:

   | Stakeholder | Role | Power | Interest | Strategy | Frequency | Channel | Key Message |
   |---|---|---|---|---|---|---|---|

6. **Flag potential conflicts**: Identify stakeholders with competing interests and suggest alignment strategies.

Think step by step. Save the stakeholder map as a markdown document.

---

### Further Reading

- [The Product Management Frameworks Compendium + Templates](https://www.productcompass.pm/p/the-product-frameworks-compendium)
- [Team Topologies: A Handbook to Set and Scale Product Teams](https://www.productcompass.pm/p/team-topologies-a-handbook-to-set)

---

## 来源与署名 / Source & Attribution

本技能收录自上游开源仓库 phuryn/pm-skills（MIT，见该仓库 LICENSE 与版权声明，作者：phuryn/pm-skills 上游（MIT））。
awesome-skillkit 保留上游正文与参考文件，仅补齐本仓库 frontmatter 元数据、为长参考文档增补目录、按本仓库链接口径归一化相对路径；同步上游时以官方仓库为准。
