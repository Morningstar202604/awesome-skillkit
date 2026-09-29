---
name: recruiting-pipeline
description: >-
  Track and manage recruiting pipeline stages. Trigger with "recruiting update", "candidate
  pipeline", "how many candidates", "hiring status", or when the user discusses sourcing,
  screening, interviewing, or extending offers. Do NOT use for interview question design (use
  interview-prep) or offer/comp decisions (use comp-analysis).
description_zh: "跟踪与管理招聘流程各阶段：候选人管道、来源筛选、面试与发 offer 进度，以及招聘状态汇总。"
license: Apache-2.0
compatibility: 需要候选管道数据来源（ATS 导出 / 表格 / 口头更新）；未连接 ATS 时按文内 "No ATS connected?" 以共享表格跟踪，指标口径不变。
metadata:
  author: "anthropics/knowledge-work-plugins 上游（Apache-2.0）"
  version: "1.0.0"
  category: hr
  pattern: single-task
  tier: standard
  verified-date: "2026-09-27"
  source: "https://github.com/anthropics/knowledge-work-plugins/tree/main"
---

# Recruiting Pipeline

Help manage the recruiting pipeline from sourcing through offer acceptance.

## Pipeline Stages

| Stage | Description | Key Actions |
|-------|-------------|-------------|
| Sourced | Identified and reached out | Personalized outreach |
| Screen | Phone/video screen | Evaluate basic fit |
| Interview | On-site or panel interviews | Structured evaluation |
| Debrief | Team decision | Calibrate feedback |
| Offer | Extending offer | Comp package, negotiation |
| Accepted | Offer accepted | Transition to onboarding |

## Metrics to Track

- **Pipeline velocity**: Days per stage
- **Conversion rates**: Stage-to-stage drop-off
- **Source effectiveness**: Which channels produce hires
- **Offer acceptance rate**: Offers extended vs. accepted
- **Time to fill**: Days from req open to offer accepted

## Input Checklist (ask once before starting)

Missing any of these? Ask the user in one batched message, then proceed with defaults flagged as assumptions:

1. **Role & level**: title, seniority, team.
2. **Headcount & timeline**: openings and target close dates.
3. **Pipeline source**: ATS export, spreadsheet, or verbal update?
4. **Stage definitions**: the standard six stages below, or team-custom ones?
5. **Decision owner**: who extends and rejects offers.

## Stage Outputs & Failure Branches

| Stage | Expected output | If it stalls |
|---|---|---|
| Sourced | Candidate list with source tags | Widen channels; revisit sourcing criteria with the owner |
| Screen | Screen notes + advance/reject per candidate | Fewer than 2 advances per 10 screens -> recheck the job requirement with the owner |
| Interview | Scorecard per interviewer (see interview-prep) | Missing scorecards -> chase before debrief; no debrief without all cards |
| Debrief | Written hire/no-hire with rationale | Split vote -> collect concerns, set a follow-up; do not re-vote the same day |
| Offer | Extended offer with comp approved | Comp not approved -> escalate to the owner before promising a date |
| Accepted | Start date + handoff to onboarding | Decline/reneg -> run a post-mortem on debrief-stage signals |

No ATS connected? Track the same stages in a shared sheet; the metrics below stay identical.

## If ATS Connected

Pull candidate data automatically, update statuses, and track pipeline metrics in real time.

---

## 来源与署名 / Source & Attribution

本技能收录自上游开源仓库 anthropics/knowledge-work-plugins（Apache-2.0，见该仓库 LICENSE 与版权声明，作者：anthropics/knowledge-work-plugins 上游（Apache-2.0））。
awesome-skillkit 保留上游正文与参考文件，仅补齐本仓库 frontmatter 元数据、为长参考文档增补目录、按本仓库链接口径归一化相对路径；同步上游时以官方仓库为准。
