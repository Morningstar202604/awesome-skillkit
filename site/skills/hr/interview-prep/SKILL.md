---
name: interview-prep
description: >-
  Create structured interview plans with competency-based questions and scorecards. Trigger with
  "interview plan for", "interview questions for", "how should we interview", "scorecard for", or
  when the user is preparing to interview candidates. Do NOT use for job-description writing or
  pipeline metrics (use recruiting-pipeline) or background-check compliance.
description_zh: "制定结构化面试方案，包含基于胜任力的面试问题与评分卡，适用于准备面试候选人、设计面试流程与评分标准。"
license: Apache-2.0
compatibility: 纯提示型，任意兼容 Agent Skills 的工具可用；无外部系统依赖。
metadata:
  author: "anthropics/knowledge-work-plugins 上游（Apache-2.0）"
  version: "1.0.0"
  category: hr
  pattern: single-task
  tier: standard
  verified-date: "2026-09-27"
  source: "https://github.com/anthropics/knowledge-work-plugins/tree/main"
---

# Interview Prep

Create structured interview plans to evaluate candidates consistently and fairly.

## Interview Design Principles

1. **Structured**: Same questions for all candidates in the role
2. **Competency-based**: Map questions to specific skills and behaviors
3. **Evidence-based**: Use behavioral and situational questions
4. **Diverse panel**: Multiple perspectives reduce bias
5. **Scored**: Use rubrics, not gut feelings

## Interview Plan Components

### Role Competencies
Define 4-6 key competencies for the role (e.g., technical skills, communication, leadership, problem-solving).

### Question Bank
For each competency, provide:
- 2-3 behavioral questions ("Tell me about a time...")
- 1-2 situational questions ("How would you handle...")
- Follow-up probes

### Scorecard
Rate each competency 1-4 with quoted evidence, using this rubric (adapt the level descriptions to each competency):

| Score | Meaning | Evidence standard |
|---|---|---|
| 4 | Exceptional | Multiple concrete verified examples above the bar; has taught or led others in it |
| 3 | Strong | Specific example(s) meeting the bar with a measurable outcome |
| 2 | Mixed | Partial or vague examples; needed prompting to produce specifics |
| 1 | Below bar | No credible example, or the answer contradicts the competency |

Rules: every score cites at least one quoted answer; never score without evidence; write "insufficient data" instead of guessing.

### Debrief Template
Each interviewer submits independently BEFORE the group debrief (no score sharing first, to avoid anchoring):

- **Recommendation**: Strong Hire / Hire / No Hire / Strong No Hire
- **Confidence**: High / Medium / Low
- **Top strengths** (quote the answer): 1) ... 2) ...
- **Top concerns** (quote the answer): 1) ... 2) ...
- **Competency scores**: `<competency>: 1-4` + one-line evidence each
- **Own-team test**: would you put this person on your own team? Yes/No + one line why

Group debrief order: strongest dissent speaks first, then the majority; the hiring manager decides and records the rationale.

## Output

Produce a complete interview kit: panel assignment (who interviews for what), question bank by competency, scoring rubric, and debrief template.

---

## 来源与署名 / Source & Attribution

本技能收录自上游开源仓库 anthropics/knowledge-work-plugins（Apache-2.0，见该仓库 LICENSE 与版权声明，作者：anthropics/knowledge-work-plugins 上游（Apache-2.0））。
awesome-skillkit 保留上游正文与参考文件，仅补齐本仓库 frontmatter 元数据、为长参考文档增补目录、按本仓库链接口径归一化相对路径；同步上游时以官方仓库为准。
