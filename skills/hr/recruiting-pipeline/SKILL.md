---
name: recruiting-pipeline
description: >-
  Track and manage recruiting pipeline stages. Trigger with "recruiting update", "candidate pipeline", "how many candidates", "hiring status", or when the user discusses sourcing, screening, interviewing, or extending offers.
description_zh: "跟踪与管理招聘流程各阶段：候选人管道、来源筛选、面试与发 offer 进度，以及招聘状态汇总。"
license: Apache-2.0
compatibility: 任意兼容 Agent Skills 的工具可用；部分技能假设已连接企业系统（CRM/HRIS/文档库），未连接时按文内提示降级。
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

## If ATS Connected

Pull candidate data automatically, update statuses, and track pipeline metrics in real time.

---

## 来源与署名 / Source & Attribution

本技能收录自上游开源仓库 anthropics/knowledge-work-plugins（Apache-2.0，见该仓库 LICENSE 与版权声明，作者：anthropics/knowledge-work-plugins 上游（Apache-2.0））。
awesome-skillkit 保留上游正文与参考文件，仅补齐本仓库 frontmatter 元数据、为长参考文档增补目录、按本仓库链接口径归一化相对路径；同步上游时以官方仓库为准。
