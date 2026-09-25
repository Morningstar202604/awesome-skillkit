---
name: home-renovation-avoidance
description: >-
  Consumer-protection guide for Chinese home renovation: avoid contractor scams,
  material substitution, and inflated pricing; know numeric acceptance thresholds.
  Use when the user is renovating, signing a renovation contract, selecting
  materials, or doing construction acceptance inspection. Triggers: renovation
  pitfalls / contractor scams / home renovation / construction acceptance /
  material selection / hidden-works check. Do NOT use for: interior design
  aesthetics (use design skills), or as legal advice.
license: Apache-2.0
compatibility: Pure prompt skill, no scripts.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: life
  pattern: single-task
  tier: standard
  verified-date: "2026-09-25"
---

# Home Renovation Avoidance (Consumer Protection)

Knowledge-reference skill that turns vague "renovation went wrong" reports into
**number-backed verdicts and a next-action list**. It does not design interiors;
it protects the consumer from contractor low-ball pricing, add-on inflation,
vague material specs, material substitution, and payment-milestone abuse. Core
judgment: **if a check has a number, cite the number; if a term is vague
("same grade", "first-tier brand"), demand the model and grade in writing.**

## Applicability Decision Table

| Stage | Use This | What It Outputs |
|-------|----------|-----------------|
| Before signing contract | contract-traps.md + contractor-red-flags.md | contract red flags, must-have clauses, company vetting |
| Material delivery | material-selection.md | on-delivery verification checklist, photo list |
| Hidden works (water/electric) | inspection-checkpoints.md | pressure test, wire gauge, conduit fill thresholds |
| Waterproofing / tiling | inspection-checkpoints.md | closed-water test duration, hollowing limit |
| Final handover | inspection-checkpoints.md | punch-list walkthrough items |
| Paying milestones | payment-discipline.md | what may be paid, when, and the escrow rule |

## Input Checklist

| Input | Required | Notes |
|-------|----------|-------|
| Renovation stage | yes | contract signing / material delivery / hidden works / waterproofing / tiling / final handover |
| Budget | no | total contract amount, to spot upfront-ratio abuse |
| City | no | local consumer-protection notices and standards vary |
| Contractor type | no | individual worker / small studio / large chain |

When inputs are missing, ask at once:

> Please provide: 1) your current renovation stage; 2) contract amount and
> how much is already paid; 3) your city; 4) contractor type (individual /
> studio / chain).

## Pre-flight Checks

Safety first — this is **consumer guidance, not legal advice**. For live
disputes contact the local Consumers Association or the 12315 hotline.
Hard money rule: **never pay more than 30% upfront.** Do not tell the user to
sue or interpret contract clauses as a lawyer would; route disputes to 12315,
local market-regulation authorities, or a lawyer.

## Workflow

Five-step pipeline. Each step produces a structured action list.

| Step | Action | Output | If Missing |
|------|--------|--------|------------|
| 1 stage | identify current stage | stage label | ask |
| 2 pull checklist | load stage-specific reference | checklist rows | note degraded mode |
| 3 apply thresholds | test every number against the job | pass/fail table | flag "needs on-site measurement" |
| 4 flag red flags | scan for low-ball, split items, substitution | red-flag list | none -> state "no major flags" |
| 5 act + photograph | generate action items + shot list | ordered next steps | n/a |

## Core Pitfalls

| Pitfall | How It Shows Up | Your Move |
|---------|-----------------|-----------|
| Low-ball then add-ons | cheap quote, then extras everywhere | cap add-ons in writing, total price = budget |
| Vague material specs | "first-tier brand", "same grade", no model | demand brand + model + grade per line |
| Task splitting | one wall coat split into 5-7 line items | sum line items against unit price per sqm |
| Material substitution | delivered goods differ from sample | photograph packaging, reject on the spot |
| Payment milestone abuse | demands full payment before inspection | pay only after a passed milestone |

## Numeric Thresholds Quick Reference

Full detail in `references/inspection-checkpoints.md`. Hard floors:

| Check | Threshold |
|-------|-----------|
| Water pressure test | >=0.8 MPa, hold 30 min, no leak |
| Waterproofing closed-water test | >=48 hours; inspect downstairs ceiling, not just your floor |
| Shower wall waterproof height | >=1.8 m |
| Tile hollowing | <=5%; no hollow on wall edges |
| Conduit filling rate | <=40% |
| Board grade | E1 minimum; ENF / E0 preferred for kids' room |
| Upfront payment | <=30% of contract |

## Safety & Boundaries

This is **not legal advice**. Cite the local Consumers Association and
market-regulation notices as the authoritative source. Numeric
thresholds are reference values; tell the user to verify against current local
2025-2026 consumer-protection notices and GB standards (GB 50210, GB 50327).
Do not draft legal demands or interpret liability as a lawyer.

## Failure Remediation Table

| Situation | Cause Pattern | Remediation Steps |
|-----------|---------------|-------------------|
| Already signed a bad contract | vague specs, no add-on cap | attach written supplement listing every material model/grade; do not sign further payments until done |
| Wrong material already delivered | substitution after payment | photograph packaging + invoice; reject and demand swap before installation; report to 12315 if refused |
| Contractor demands more money mid-job | unwritten add-ons | stop payment; demand written basis tied to approved design changes; pay only against passed inspection |
| Work is substandard (leak, hollow tiles) | skipped acceptance | refuse milestone payment; request rework to threshold; document with photos/video |
| Company vanishes or high-pressure tactics | red-flag contractor | stop all payments; preserve contract + receipts; file 12315 / market-regulation complaint |

## Quality / Delivery Checklist

- [ ] Output names the current renovation stage
- [ ] Stage-specific checklist pulled from references/
- [ ] Every numeric threshold cited (pressure MPa, hours, hollowing %, grade)
- [ ] Red flags flagged from core pitfalls table
- [ ] Explicit photo / video shot list for the next inspection
- [ ] Ordered next actions, each tied to a payment hold if relevant
- [ ] Boundary stated: consumer guidance, not legal advice; route to 12315 / Consumers Association

## Chain Position

- Downstream: `rental-contract-guide` for housing before renovation;
  `file-organizer` for storing receipts, contracts, and inspection photos

## References

- `references/contract-traps.md` — contract red flags, add-on cap, material
  spec clauses, payment-milestone tie-ins, common add-on scams
- `references/inspection-checkpoints.md` — stage-by-stage acceptance with
  numeric thresholds (water/electric, waterproofing, tiling, wood/paint, final)
- `references/material-selection.md` — how to verify brand/model/grade on
  delivery and common substitution tricks
- `references/payment-discipline.md` — payment milestones, escrow, final
  punch-list rule, what to do if more money is demanded
- `references/contractor-red-flags.md` — company vetting red flags
- `references/sources-and-licenses.md` — consumer-protection reporting and
  GB acceptance standards
