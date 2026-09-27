---
name: archify-review
description: >-
  Review Archify issues, PRs, or code through value, cost, and impact to support evidence-based maintenance decisions. Use for issue triage, change reviews, and code quality assessments.
description_zh: "从价值、成本与影响维度审查 Archify 的 issue、PR 与代码质量。"
license: MIT
compatibility: 纯提示型（含少量模板），任意支持 SKILL.md 的工具可用。
metadata:
  author: "tt-a1i/archify 上游（MIT）"
  version: "1.0.0"
  category: design
  pattern: single-task
  tier: standard
  verified-date: "2026-09-27"
  source: "https://github.com/tt-a1i/archify/tree/main"
---

# Archify Review

Judge whether a problem is worth addressing and an approach is worth maintaining over time.

- **Value**: Identify the real problem, who benefits, how often it occurs, its consequences, and whether it is worth addressing now.
- **Cost**: Consider implementation and verification effort, along with the future cost of understanding, changing, and maintaining the code. Prefer existing capabilities and keep the solution proportional to the problem.
- **Impact**: Identify affected behavior and modules, consequences for users and future development, and whether the change improves maintainability or adds coupling and constraints.

Consider maintainability, complexity, compatibility, performance, and other relevant concerns within these three dimensions, according to the specific problem.

Ground judgments in evidence: verify the target revision and relevant facts, distinguish direct verification from existing evidence and assumptions, and choose checks that resolve the key uncertainties.

Explain whether the work is worthwhile, the approach's cost and impact, any better alternatives, and unresolved questions that matter to the decision. Give reasons and scale the detail to the importance of each concern.

For repository-specific review and contribution requirements, consult [REVIEWING.md](../../../REVIEWING.md) and [CONTRIBUTING.md](../../../CONTRIBUTING.md) as needed.

---

## 来源与署名 / Source & Attribution

本技能收录自上游开源仓库 tt-a1i/archify（MIT，见该仓库 LICENSE 与版权声明，作者：tt-a1i/archify 上游（MIT））。
awesome-skillkit 保留上游正文与参考文件，仅补齐本仓库 frontmatter 元数据、为长参考文档增补目录、按本仓库链接口径归一化相对路径；同步上游时以官方仓库为准。
