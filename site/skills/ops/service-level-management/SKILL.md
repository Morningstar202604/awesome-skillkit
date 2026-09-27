---
name: service-level-management
description: >-
  Defines and manages service levels — setting targets that reflect what
  customers need, measuring honestly, and handling breaches. Use this to
  write or negotiate an SLA, decide what to measure and at what threshold,
  respond to a missed service level, or work out why a service that meets
  its targets still has unhappy customers.
description_zh: "服务等级管理：设定贴合客户需求的目标、如实度量并处理违约。"
license: MIT
compatibility: 纯提示型；涉及财务、合规或法律判断时建议人工复核。
metadata:
  author: "cbrock84/headcount 上游（MIT）"
  version: "1.0.0"
  category: ops
  pattern: single-task
  tier: standard
  verified-date: "2026-09-27"
  source: "https://github.com/cbrock84/headcount/tree/main/plugins/operations/skills/service-level-management"
---

# Service level management

A service level is a promise with a number attached. The number is the easy part; choosing what to
measure is where these go wrong.

## Measure what the customer feels

The characteristic failure is a service meeting every target while customers are angry. It happens
when the measure is chosen for availability of data rather than relevance:

- **Uptime that excludes degraded operation.** Technically up and unusably slow is down.
- **Response time instead of resolution time.** An instant acknowledgment that resolves nothing
  measures the autoresponder.
- **Averages instead of percentiles.** A mean hides the tail, and the tail is who complains. Commit
  at p95 or p99, not the mean.
- **Measurement from inside your own perimeter**, which excludes the part of the path the customer
  actually traverses.

## Set targets you would fund

A target is a spending decision. Each added nine costs disproportionately more than the last, so the
question is never "what would be good?" but "what is the gap worth to the customer, and does it
exceed what closing it costs?"

Set the internal objective tighter than the external commitment. The gap between them is your
warning margin; without it, the first thing you learn about a breach is the breach.

## Write them so both sides can tell

An unmeasurable clause is a future dispute. Every service level needs: what is measured, where it is
measured from, how it is calculated, what is excluded, over what window, and what happens when it is
missed.

Exclusions are the substance — planned maintenance, force majeure, customer-caused failures,
dependencies outside your control. Vague exclusions get read narrowly when it matters. For anything
with contractual teeth, `legal-risk:contract-review` owns the remedy language; this skill owns
whether the number is achievable.

## When you breach

Say so before the customer does. A breach reported by the provider with a cause and a fix costs far
less trust than one the customer discovers and raises.

Then separate the incident from the pattern. One breach is an incident, handled by
`customer-experience:escalation-management`. Repeated breaches of the same target mean the target was
never fundable — renegotiate it honestly rather than continuing to miss it.

## Sources

`references/sources.md` in this skill lists the outside authorities that settle the questions
here — what each one is authoritative for, and what you may do with it. Check them before
answering on anything they cover, and cite what you used. Most are free to read and not free
to reproduce; the use note on each is binding.

## Never

- Commit to a level you have not measured yourself achieving for a sustained period.
- Report availability on a mean when the customer experiences the tail.
- Agree an SLA whose exclusions are undefined.
- Let a target stand that you have missed repeatedly without either funding it or renegotiating it.

---

## 来源与署名 / Source & Attribution

本技能收录自 [cbrock84/headcount](https://github.com/cbrock84/headcount/tree/main/plugins/operations/skills/service-level-management)（MIT）；awesome-skillkit 仅做规范化（frontmatter 归一、补中文描述、路径与链接清理）与署名，内容与更新以上游为准。
