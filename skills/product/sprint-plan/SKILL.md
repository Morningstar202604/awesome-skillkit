---
name: sprint-plan
description: >-
  Plan a sprint with capacity estimation, story selection, dependency mapping, and risk identification. Use when preparing for sprint planning, estimating team capacity, selecting stories, or balancing sprint scope against velocity.
description_zh: "规划迭代冲刺：估算团队产能、挑选故事、梳理依赖关系并识别风险，平衡迭代范围与速率"
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

## Sprint Planning

Plan a sprint by estimating team capacity, selecting and sequencing stories, and identifying risks.

### Context

You are helping plan a sprint for **$ARGUMENTS**.

If the user provides files (backlogs, velocity data, team rosters, or previous sprint reports), read them first.

### Instructions

1. **Estimate team capacity**:
   - Number of team members and their availability (PTO, meetings, on-call)
   - Historical velocity (average story points per sprint from last 3 sprints)
   - Capacity buffer: reserve 15-20% for unexpected work, bugs, and tech debt
   - Calculate available capacity in story points or ideal hours

2. **Review and select stories**:
   - Pull from the prioritized backlog (highest priority first)
   - Verify each story meets the Definition of Ready (clear AC, estimated, no blockers)
   - Flag stories that need refinement before committing
   - Stop adding stories when capacity is reached

3. **Map dependencies**:
   - Identify stories that depend on other stories or external teams
   - Sequence dependent stories appropriately
   - Flag external dependencies and owners
   - Identify the critical path

4. **Identify risks and mitigations**:
   - Stories with high uncertainty or complexity
   - External dependencies that could slip
   - Knowledge concentration (only one person can do it)
   - Suggest mitigations for each risk

5. **Create the sprint plan summary**:

   ```
   Sprint Goal: [One sentence describing what success looks like]
   Duration: [2 weeks / 1 week / etc.]
   Team Capacity: [X story points]
   Committed Stories: [Y story points across Z stories]
   Buffer: [remaining capacity]

   Stories:
   1. [Story title] — [points] — [owner] — [dependencies]
   ...

   Risks:
   - [Risk] → [Mitigation]
   ```

6. **Define the sprint goal**: A single, clear sentence that captures the sprint's primary value delivery.

Think step by step. Save as markdown.

---

### Further Reading

- [Product Owner vs Product Manager: What's the difference?](https://www.productcompass.pm/p/product-manager-vs-product-owner)

---

## 来源与署名 / Source & Attribution

本技能收录自上游开源仓库 phuryn/pm-skills（MIT，见该仓库 LICENSE 与版权声明，作者：phuryn/pm-skills 上游（MIT））。
awesome-skillkit 保留上游正文与参考文件，仅补齐本仓库 frontmatter 元数据、为长参考文档增补目录、按本仓库链接口径归一化相对路径；同步上游时以官方仓库为准。
