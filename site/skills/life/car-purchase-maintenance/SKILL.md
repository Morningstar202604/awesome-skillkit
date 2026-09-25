---
name: car-purchase-maintenance
description: >-
  Use when the user is buying a car (new or used), negotiating price, doing
  delivery inspection, or planning maintenance. Triggers: car buying, price
  negotiation, delivery inspection, maintenance schedule, used car check,
  dealer tricks, first service, oil change interval. Do NOT use for mechanical
  diagnosis (take the car to a licensed mechanic), insurance claims, or
  investment / financing advice beyond reading a loan contract.
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

# Car Purchase & Maintenance (Consumer Protection)

Consumer protection for Chinese car buyers and owners. Covers dealer tricks at
purchase, delivery inspection with date-code checks that catch accident repairs
and swapped parts, maintenance-interval truths that counter 4S-shop
over-servicing, and minimums for used-car buying. **This is not mechanical
diagnosis** — for actual repairs, go to a licensed mechanic.

> Guiding principle: **the owner's manual is the real authority; the 4S shop's
> service adviser is a helpful neighbor.** The manual says what the car
> actually needs; the shop's upsell list is a sales pitch.

## Applicability Decision Table

| Stage | Use this | Output |
|-------|----------|--------|
| Researching models / budget | partial | point to comparison; do not recommend a car |
| Negotiating price at dealer | yes | negotiation script, bare-car price demand |
| Signing the contract | yes | contract red-flag review |
| Delivery day | yes | date-code inspection checklist |
| Scheduled maintenance | yes | true interval table vs 4S shop push list |
| Buying a used car | yes | third-party inspection minimums + record demands |
| "Why is my engine making a noise?" | NO | mechanical diagnosis; take it to a mechanic |

## Input Checklist

- New car or used car?
- Budget range (out-the-door, not monthly payment)
- City (affects license-plate policy, EV incentives, traffic rules)
- Fuel type: gas / hybrid / EV / PHEV
- Buying from a dealer, 4S shop, or private seller?
- Current mileage (if used or existing car)
- Target delivery / service date

## Pre-flight Checks

- This skill does **not** diagnose mechanical problems. If the car is broken,
  quote, or smoking, send the user to a licensed mechanic.
- Date-code inspection on delivery day is a **consumer verification** step
  (catching swapped parts or accident repairs), not an engineering assessment.
- Maintenance intervals below are general reference values; the **owner's
  manual for the specific model wins** whenever they differ.
- Never encourage paying a deposit before price is final and in writing.

## Workflow

Five steps.

| Step | Action | Output |
|------|--------|--------|
| 1 Price prep | demand bare-car price, separate loan from cash, compare offers | negotiation script (see `references/price-negotiation.md`) |
| 2 Contract review | check red flags before signing | red-flag list (see `references/contract-red-flags.md`) |
| 3 Delivery inspection | check date codes: build date, tires, glass, screws, paint, mileage, VIN | inspection checklist (see `references/delivery-inspection.md`) |
| 4 Maintenance schedule | build a true-interval table from the owner's manual | maintenance table (see `references/maintenance-intervals.md`) |
| 5 Used-car extras | third-party inspection, records demand, walk-away signals | minimums list (see `references/used-car-checks.md`) |

## Core Dealer Tricks

| Trick | What it looks like | Counter |
|-------|--------------------|---------|
| Combined discount (bundled offer) | big number on the sign, but bundles worthless add-ons | insist on the bare-car price in writing |
| Inventory car (long-stock car) | new-car discount but car has been sitting for months | check door-jamb build date; negotiate 5-10% off |
| Mandatory decoration package | "must buy" floor mats, film, coating at inflated price | refuse; buy accessories yourself |
| Loan markup | "cash price" vs "loan price" with hidden dealer markup | compare loan offers separately from the car price |
| Insurance bundling | "must buy insurance through us" | legally you can buy anywhere; decline politely |
| Deposit trap | non-refundable deposit paid before price is final | never pay until price, delivery date, free items are written |

## Maintenance Interval Truth (compact)

Full table in `references/maintenance-intervals.md`. Quick truth:

| Item | True interval | 4S shop might say |
|------|---------------|-------------------|
| Oil + filter (full synthetic) | 10,000 km or 1 year | 5,000 km (that is mineral oil) |
| Air filter | 20,000 km (inspect at 10k) | "replace every service" |
| Cabin / AC filter | 20,000 km or 1 year | "every 6 months" |
| Brake fluid | 2 years or 40,000 km | "every year" |
| Brake pads | replace when < 3 mm | "replace at 5 mm to be safe" |
| Coolant | per manual (long-life, ~4 yr / 80k km) | "flush every 2 years" |

Common push-list items that are usually unnecessary unless you have specific
symptoms: engine flush, fuel-system cleaning, throttle-body cleaning.

## Safety & Boundaries

- **Not mechanical diagnosis.** Unusual noises, warning lights, fluid leaks,
  or driveability problems -> licensed mechanic.
- Date-code inspection is consumer verification, not a replacement for a
  professional pre-purchase inspection.
- Used-car inspection by a shop the dealer recommends is not independent;
  always use a third-party inspector chosen by the buyer.
- Maintenance numbers are general; the owner's manual for the exact year, make,
  and model is the authority.

## Failure Remediation Table

| Situation | Cause | Action |
|-----------|-------|--------|
| Dealer refuses to show bare-car price | hiding markups inside combined discount | walk away; another dealer will show it; price is negotiable |
| Discovered the car was long-stock after delivery | did not check door-jamb build date before signing | review contract; if age was misrepresented, escalate to dealer manager and consumer hotline 12315 |
| 4S shop pushes engine flush / fuel cleaning at first service | upsell list | refuse in writing; show owner's manual; service is not required to include unscheduled items |
| Used car has hidden accident history | skipped independent inspection | if records were demanded and hidden, walk away / sue; never buy a car with hidden structural damage |
| Contract says "final price" but on the day extra fees appear | vague contract language | do not pay; point to written price; escalate to sales manager |
| Maintenance light comes on earlier than manual | oil-life monitor vs fixed interval | follow the car's monitor AND the manual; ask the service adviser to explain the discrepancy in writing |
| EV-specific: battery warranty unclear | sales pitch vague | get battery warranty terms in writing: years, km, capacity threshold (e.g. 70% retention) |

## Quality / Delivery Checklist

- [ ] Output includes a negotiation script that demands bare-car price in writing
- [ ] Contract red flags are listed (price basis, decoration package, delivery date, deposit, loan terms)
- [ ] Delivery inspection checklist includes date codes: door-jamb build, tire DOT, glass dates, engine-bay screws, paint, mileage, VIN
- [ ] Maintenance table separates true intervals from the 4S push list
- [ ] Used-car section requires independent third-party inspection + records demand
- [ ] No mechanical diagnosis offered; repairs deferred to licensed mechanics

## Chain Position

- Downstream: hands off to `file-organizer` for receipts, service records, and
  contract storage; to `rental-contract-guide` for parking / garage rental
  contracts.
- Upstream: receives budget, city, fuel-type preferences from the user.

## References

- `references/price-negotiation.md` — bare-car price demand, inventory-car rules, timing, deposit rules
- `references/delivery-inspection.md` — delivery-day checklist: door-jamb build date, tire DOT code, glass date codes, screw torque marks, paint, mileage, VIN
- `references/maintenance-intervals.md` — detailed interval table and the 4S-shop push list
- `references/used-car-checks.md` — independent inspection, records demand, walk-away signals, flood and accident signs
- `references/contract-red-flags.md` — car purchase contract red flags to check before signing
- `references/sources-and-licenses.md` — sources and license attribution
