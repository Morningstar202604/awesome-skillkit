---
name: vendor-management
description: >-
  Selects, contracts, and manages suppliers and vendors — requirements,
  evaluation, negotiation support, onboarding, performance management, and
  exit. Use this to choose a vendor, run a selection process, structure a
  service agreement's operational terms, manage an underperforming supplier,
  plan an exit or migration, or assess concentration and continuity risk.
description_zh: "供应商全周期管理：需求、评估、合同、上线、绩效管理与退出。"
license: MIT
compatibility: 纯提示型；涉及财务、合规或法律判断时建议人工复核。
metadata:
  author: "cbrock84/headcount 上游（MIT）"
  version: "1.0.0"
  category: ops
  pattern: single-task
  tier: standard
  verified-date: "2026-09-27"
  source: "https://github.com/cbrock84/headcount/tree/main/plugins/operations/skills/vendor-management"
---

# Vendor management

## Define requirements before looking at options

Written before any demo: what the vendor must do, the volume and service level required, what must
integrate with what, and the constraints that are genuinely non-negotiable.

Requirements written after seeing a product describe that product. This is the most common way
selections are decided before they are run.

Separate **must-have** from **nice-to-have** and weight them in advance. Weighting after scoring is
how a preferred vendor wins a process designed to be objective.

## Evaluating

- **Reference checks with customers of your size and use case.** A reference running a tenth of your
  volume tells you nothing about whether it scales.
- **Test the actual failure modes**, not the demo path. What happens when data is malformed, volume
  spikes, or an integration times out?
- **Assess the vendor, not just the product** — financial stability, roadmap direction, support
  responsiveness, and whether you are a meaningful customer to them. Being a rounding error to your
  critical supplier is a risk in itself.
- **Total cost including your side**: implementation, integration, migration, training, and the
  ongoing effort to operate it. License cost is frequently the smaller half.

## Terms that matter operationally

Beyond the legal review: service levels with real remedies, support response times by severity,
data export in a usable format on demand, notice periods that give you time to migrate, and price
protection at renewal. The absence of the last two is what makes exit expensive later.

## Managing

- **One named owner** on your side. Vendors without an internal owner drift and renew automatically.
- **Review on a schedule against the service levels**, with evidence. Vendor-supplied performance
  reports mark their own work.
- **Log issues.** At renewal, a documented pattern is leverage; a recollection is not.
- **Diarize renewals well before the notice deadline.** Auto-renewal past an unnoticed deadline is
  the most common and most avoidable vendor loss.

## Concentration and exit

Know which vendors you could not operate without and what happens if one fails, is acquired, or
triples its price. For each, know the exit path and roughly what it costs — an exit plan that has
never been thought through is not an option, it is a hope.

Maintain your own copy of your data continuously where the vendor holds anything critical.

## Sources

`references/sources.md` in this skill lists the outside authorities that settle the questions
here — what each one is authoritative for, and what you may do with it. Check them before
answering on anything they cover, and cite what you used. Most are free to read and not free
to reproduce; the use note on each is binding.

## Never

- Sign before you know what leaving costs — data export, notice period, transition support.
- Let the vendor write the requirements you evaluate them against.
- Reach a renewal date without having started the renewal. The auto-renew clause is their leverage.
- Concentrate a critical dependency on one vendor without saying so out loud and pricing the risk.

---

## 来源与署名 / Source & Attribution

本技能收录自 [cbrock84/headcount](https://github.com/cbrock84/headcount/tree/main/plugins/operations/skills/vendor-management)（MIT）；awesome-skillkit 仅做规范化（frontmatter 归一、补中文描述、路径与链接清理）与署名，内容与更新以上游为准。
