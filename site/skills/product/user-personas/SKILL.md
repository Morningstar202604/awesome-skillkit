---
name: user-personas
description: >-
  Create refined user personas from research data — 3 personas with JTBD, pains, gains, and unexpected insights. Use when building personas from survey data, creating user profiles from research, or segmenting users for product decisions.
description_zh: "基于调研数据提炼用户画像：3 个含 JTBD、痛点、收益与意外洞察的人物角色"
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

# User Personas

## Purpose
Create detailed, actionable user personas from research data that capture the true diversity of your user base. This skill generates research-backed personas with jobs-to-be-done, pain points, desired outcomes, and unexpected behavioral insights to guide product decisions.

## Instructions

You are an experienced product researcher specializing in persona development and user research synthesis.

### Input
Your task is to create 3 refined user personas for **$ARGUMENTS**.

If the user provides CSV, Excel, survey responses, interview transcripts, or other research data files, read and analyze them directly using available tools. Extract key patterns, demographics, motivations, and behaviors.

### Analysis Steps (Think Step by Step)

1. **Data Collection**: Read and review all provided research data and documents
2. **Pattern Recognition**: Identify recurring characteristics, goals, pain points, and behaviors across users
3. **Segmentation**: Group similar users into distinct personas based on shared motivations and jobs-to-be-done
4. **Enrichment**: For each persona, synthesize data into a coherent profile
5. **Validation**: Cross-reference insights to ensure personas are grounded in actual research findings

### Output Structure

For each of the 3 personas, provide:

**Persona Name & Demographics**
- Age range, role/title, company size (if B2B), key characteristics

**Primary Job-to-be-Done**
- The core outcome the persona is trying to achieve
- Context and frequency of the job

**Top 3 Pain Points**
- Specific challenges or obstacles preventing job completion
- Impact and severity of each pain

**Top 3 Desired Gains**
- Benefits, outcomes, or solutions the persona seeks
- How they measure success

**One Unexpected Insight**
- A counterintuitive behavioral pattern or motivation derived from the data
- Why this matters for product decisions

**Product Fit Assessment**
- How $ARGUMENTS addresses (or could address) this persona's needs
- Potential friction points or unmet needs

## Best Practices

- Ground all insights in actual data; avoid assumptions
- Use direct quotes from research when available
- Identify behavioral patterns, not just demographic categories
- Make personas distinct and non-overlapping where possible
- Flag any data gaps or areas requiring additional research

---

### Further Reading

- [User Interviews: The Ultimate Guide to Research Interviews](https://www.productcompass.pm/p/interviewing-customers-the-ultimate)
- [Market Research: Advanced Techniques](https://www.productcompass.pm/p/market-research-advanced-techniques)
- [Jobs-to-be-Done Masterclass with Tony Ulwick and Sabeen Sattar](https://www.productcompass.pm/p/jobs-to-be-done-masterclass-with) (video course)

---

## 来源与署名 / Source & Attribution

本技能收录自上游开源仓库 phuryn/pm-skills（MIT，见该仓库 LICENSE 与版权声明，作者：phuryn/pm-skills 上游（MIT））。
awesome-skillkit 保留上游正文与参考文件，仅补齐本仓库 frontmatter 元数据、为长参考文档增补目录、按本仓库链接口径归一化相对路径；同步上游时以官方仓库为准。
