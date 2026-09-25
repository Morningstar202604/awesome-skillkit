---
name: rental-contract-guide
description: >-
  Consumer-protection guide for Chinese urban renters: avoid fake landlords,
  rent-loan traps, and deposit loss; understand contract terms and
  move-in/move-out inspection. Use when the user is renting an apartment,
  signing a lease, checking a rental contract, dealing with deposit disputes, or
  doing move-in / move-out inspection. Triggers: rental contract / lease review /
  deposit dispute / move-in inspection / lease agreement / sub-landlord. Do NOT
  use for: home purchase contracts (different legal framework), or as a
  substitute for legal advice.
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

# Rental Contract Guide (Tenant Protection)

Knowledge-reference skill that turns "should I sign this lease?" into an
**identity check, a contract red-flag scan, and a deposit-recovery plan**. It
protects urban renters from fake landlords, sub-landlord scams,
rent-loan traps, illegal partitions, and unfair deposit
deduction. Core judgment: **verify who you are paying before money moves; get
every term in writing; document the condition of the unit at both ends.**

## Applicability Decision Table

| Stage | Use This | What It Outputs |
|-------|----------|------------------|
| Before paying / meeting landlord | identity-verification.md | identity & ownership check list |
| Reviewing the lease contract | contract-red-flags.md | must-have clauses + red flags |
| Moving in | move-in-walkthrough.md | photo/video + meter + handover list |
| During the lease | contract-red-flags.md | tenant rights, repairs, rent-increase rules |
| Deposit / move-out | deposit-rules.md + move-out-checklist.md | what is deductible + recovery steps |

## Input Checklist

| Input | Required | Notes |
|-------|----------|-------|
| Renting or buying | yes | this skill is for renting only |
| City | no | local rental rules / market hotlines vary |
| Sub-landlord? | yes | if yes, extra ownership permission check |
| Lease term | no | total term; note the 20-year ceiling |
| Monthly rent | no | to test the earnest-money 20% cap |
| Deposit amount | no | compare against 1-2 months norm; flag rent-loan |

When inputs are missing, ask at once:

> Please provide: 1) which city; 2) is the counterparty the owner or a
  sub-landlord; 3) lease term and monthly rent; 4) deposit / earnest money asked;
  5) whether you have already signed or paid anything.

## Pre-flight Checks

This is **legal information, not legal advice.** Backed by the PRC Civil Code:
a lease term may not exceed **20 years (Art. 705)**. For live disputes consult a
lawyer or the **12348 legal-aid hotline**. Do not draft court pleadings or give
a definitive legal ruling; route disputes to 12345, 12348, or small-claims
procedures.

## Workflow

Five-step pipeline. Each step produces a structured action list.

| Step | Action | Output | If Missing |
|------|--------|--------|------------|
| 1 identity | verify owner / sub-landlord | identity check list result | stop, do not pay |
| 2 contract scan | red-flag the lease | must-have clauses / red flags table | ask for the contract text |
| 3 move-in walkthrough | joint inspection | photo + meter + defect list | do not receive keys first |
| 4 during lease | tenant rights | repair / increase / entry rights | n/a |
| 5 move-out | deposit recovery | move-out checklist + recovery steps | n/a |

## Core Traps

| Trap | How It Shows Up | Your Move |
|------|-----------------|-----------|
| Earnest money vs prepayment confusion | pressured to pay "earnest money" | know earnest money is non-refundable, capped at 20% |
| Rent-loan trap | "monthly rent" is actually a consumer loan | refuse; only pay rent to landlord, never a loan app |
| Fake landlord | "forgot the certificate", "owner is my relative" | see property certificate + ID; verify ownership |
| Illegal partition | over-divided room in a big apartment | illegal in many cities; check fire/egress |
| Normal-wear deduction | withholds deposit for scuffs/aging paint | normal wear is not deductible; demand evidence |

## Key Legal Reference

Full detail in `references/deposit-rules.md`. Hard points:

| Item | Rule |
|------|------|
| Earnest money | non-refundable; capped at **20% of annual rent** (Civil Code) |
| Prepayment | refundable if no deal |
| Maximum lease term | **20 years** (Civil Code Art. 705) |
| Deposit deduction | landlord must provide **evidence of damage**; normal wear excluded |
| Rent-loan | monthly payments routed to a loan product = do not sign |

## Safety & Boundaries

This is **not legal advice.** Cite Civil Code articles (Art. 705 lease term;
Arts. 586-588 on earnest money) as reference, but recommend consulting a lawyer
for real disputes. Route tenant disputes to the **12348 legal-aid hotline** or
**12345**. Do not guarantee a legal outcome or draft enforceable legal documents.

## Failure Remediation Table

| Situation | Cause Pattern | Remediation Steps |
|-----------|---------------|-------------------|
| Landlord refuses to return deposit | vague "damage" claims | demand written evidence + receipts; cite normal-wear rule; escalate to 12345 / 12348 |
| Discovered illegal partition after moving in | was not disclosed | document egress/fire hazards; report to 12345 / housing authority; demand early termination |
| Sub-landlord has no sublet permission | never checked original lease | stop paying sub-landlord; contact registered owner; preserve chat records; 12348 aid |
| Signed a rent-loan unknowingly | onboarding flow hid the loan | screenshot the loan agreement; dispute to the lender + 12378 financial hotline; keep paying rent directly to owner |
| Landlord enters unit without notice | no entry clause in lease | object in writing; cite privacy; negotiate 24h notice clause |

## Quality / Delivery Checklist

- [ ] Output includes an identity-verification result (owner vs sub-landlord)
- [ ] Contract red flags scanned against must-have clauses
- [ ] Move-in walkthrough list (photos, meters, defects, joint sign-off)
- [ ] Move-out checklist (notice, condition, written deposit return)
- [ ] Key legal references cited (earnest-money 20% cap, prepayment refundable, 20-year term)
- [ ] Rent-loan trap explicitly flagged if monthly payment looks like a loan
- [ ] Boundary stated: legal information, not legal advice; route to 12348 / 12345

## Chain Position

- Downstream: `home-renovation-avoidance` if the tenant later renovates;
  `file-organizer` for storing the lease, receipts, and move-in photos

## References

- `references/identity-verification.md` — property certificate + ID check,
  sub-landlord permission, fake-landlord patterns
- `references/contract-red-flags.md` — must-have clauses and red flags,
  including the rent-loan trap
- `references/deposit-rules.md` — earnest money vs prepayment, normal wear, evidence rule,
  deduction scams
- `references/move-in-walkthrough.md` — photo/video, meter readings, defects,
  joint handover list
- `references/move-out-checklist.md` — notice, condition, joint walkthrough,
  deposit recovery and dispute channels
- `references/sources-and-licenses.md` — Civil Code articles, housing
  regulations, legal-aid hotline
