---
name: campaign-designer
description: "Design an e-commerce/growth marketing campaign around finished product copy: marketing-calendar placement (festival nodes vs everyday), channel matrix with roles per channel, and single-variable A/B variant pairs (one change per pair, hypothesis stated). Reads copy from product-copywriter, hands variant matrix to channel-adapter. Use when the user asks to plan a campaign / marketing calendar / ad plan / A/B test / campaign / channel matrix / marketing campaign / growth / content marketing / conversion. Do NOT use for writing the base copy itself (product-copywriter), nor for per-platform reformatting (channel-adapter)."
license: Apache-2.0
compatibility: Pure prompt-based; no runtime dependencies.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: marketing
  pattern: single-task
  tier: standard
  verified-date: "2026-09-14"
---

# Campaign Designer

Upgrade copy into a **rhythmic campaign**. The core discipline is **single-variable A/B** — change two variables at once and, even if you win, you do not know why, making the data run for nothing.

## Input Checklist

| Input | Required | Notes |
|------|------|------|
| Base copy | Yes | product-copywriter's output |
| Campaign goal | Yes (ask if missing) | Drive sales / build awareness / clear inventory — the goal sets the rhythm and channel weights |
| Budget tier | No | Affects the width of the channel matrix; do not guess |

When inputs are missing, ask for all at once: "Please provide: ① the base copy (or say product-copywriter should produce it first); ② the campaign goal (drive sales / build awareness / clear inventory); ③ the timing window and budget tier (optional)."

## Pre-flight Self-check

This skill is pure-prompt driven: no runtime dependencies, no endpoints, no environment variables. Self-check point:

```bash
test -f ../product-copywriter/references/sources-and-methodology.md && echo OK
```

Expect to output `OK` (the shared methodology reference is in place); failure does not block — the framework discipline is self-contained in this file, so note the missing reference at delivery.

## Workflow

### Step 1: Set the Rhythm (Festival Node vs Everyday)

- **Festival-node type** (618 / Double 11 / back-to-school): three phases — warm-up (seed interest) → burst (conversion) → encore (long tail), each with a different channel mix
- **Everyday type**: a weekly cadence, one primary channel + 2 supporting channels rotating, avoiding firing on all platforms at once and scattering ammunition
- Output a marketing calendar table: date | node | primary channel | action | asset needs

### Step 2: Lay Out the Channel Matrix (One Role per Channel)

| Channel type | Role | Content form |
|----------|------|----------|
| Seeding (Xiaohongshu / Douyin) | Acquisition and awareness | Scenario-based content, soft sell |
| Search (e-commerce site / search engines) | Capture intent | Strong selling points + price-comparison info |
| Private domain (community / Moments / email) | Repurchase and referrals | Personable communication + exclusive perks |

Discipline: **each channel has its own job**; blasting the same asset across all channels = making all three channels mediocre (adaptation is handed to channel-adapter).

### Step 3: Design A/B Variant Pairs (Single-variable Discipline)

Each variant pair allows exactly one differing dimension, and states the hypothesis:

```markdown
- Pair 1 [Headline hook] Hypothesis: numeric hook > suspense hook
  A: "The truth behind selling 2000 units in 3 days" / B: "Why everyone is grabbing this"
- Pair 2 [CTA wording] Hypothesis: loss aversion > action command
  A: "Don't miss tonight's 8pm price" / B: "Click to lock in the offer"
```

- Test ≤2 pairs at a time — the more pairs, the thinner the traffic per pair, and the less trustworthy the conclusion
- Write the winning variant back into the base copy; the next round iterates on the new baseline

### Step 4: Chain Handoff

Deliver the marketing calendar + channel matrix + variant-pair list. **Then say: "The campaign is laid out; call channel-adapter to turn the base copy into per-channel variants"** — the chain unfolds automatically.
- Expected: the matrix channel-adapter receives has a role per channel, and each variant pair has only one differing dimension.
- On failure: returning data shows a channel underperforms → take the data back to step 2 to adjust the matrix roles and weights, do not overturn the overall rhythm.

## Delivery Standards

- Artifacts: the marketing calendar table (date | node | primary channel | action | asset needs) + channel matrix (one role per channel) + A/B variant-pair list (hypothesis per pair).
- Save location: output directly in the conversation (this skill writes no files), for channel-adapter to reference.
- Integrity verification: each variant pair can point verbatim to its single differing dimension; ≤2 pairs tested at once; the warm-up phase of a festival-node campaign is scheduled ≥7 days ahead.

## Failure Handling Table

| Symptom | Cause | Action |
|------|------|------|
| A/B test proved nothing | One variant pair changed multiple things | Re-cut variants against the single-variable discipline |
| Same asset across all channels | Missing channel role division | Return to step 2 and assign a role to each channel |
| Selling before the warm-up has volume | Rhythm compressed | Festival-node warm-up starts at least 7 days ahead |
| Data conclusions contradict each other | Multiple pairs running at once and contaminating each other | Isolate the test periods or bucket by channel |

## References

The framework and variant discipline are recorded in product-copywriter's
[sources-and-methodology.md](../product-copywriter/references/sources-and-methodology.md) (shared within the package).
