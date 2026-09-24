---
name: product-copywriter
description: "Write conversion-focused e-commerce product copy from raw product facts: framework selection (FAB / PAS / AIDA), benefit-first headlines, objection-handling section, and fact hygiene (no invented specs). Chain entry of growth-marketing — its copy feeds campaign-designer and channel-adapter directly. Use when the user asks to write product copy / detail page / selling points / product description / sales copy / product description / seeding copy / marketing campaign / conversion. Do NOT use for full campaign calendars (campaign-designer), nor per-platform reformatting of finished copy (channel-adapter)."
license: Apache-2.0
compatibility: Pure prompt-based; no runtime dependencies.
metadata:
  author: "awesome-skillkit"
  version: "1.1"
  category: marketing
  pattern: single-task
  tier: standard
  verified-date: "2026-09-21"
---

# Product Copywriter

The chain's entry point. Turn product facts (specs / scenarios / reviews) into **copy that converts**. The core is **framework first** — start writing without picking a framework and you inevitably produce a spec list; a spec list does not convert.

## Domain Dark Knowledge (four things you must know before writing)

**1. Users are skimming, not shopping.** Detail-page dwell time is extremely short; most visitors decide to stay or leave after skimming only the first screen — this matches the broad consensus of landing-page analysis, though the exact ratio varies by category and traffic, so do not write it into the copy as a constant. It means the hook headline in the four-part structure is not "the first paragraph" but **the only paragraph guaranteed to be read**; putting the main persuasive load here is not exaggerated rhetoric, it is the true location of the stay/leave decision. The next three parts are read by the people who stayed, so they can be denser, but do not expect to work equally hard everywhere.

**2. Objections are not brainstormed — they are dug out of the negative reviews.** A "3 hesitation points" list with no real objection data is the writer self-indulging — you think users fear the price, but the negative-review section is full of "serious color difference" and "does not match the pictures." Before writing, dig: high-frequency words in the negative reviews, repeated questions in support records, follow-up questions in the Q&A. Without these data sources, the objection-handling section must explicitly note "inferred from category common sense; recommend calibrating against real reviews" — do not pretend you did the research.

**3. Beyond extreme words there is a second minefield: unqualified functional claims.** "Best / #1 / national-level" are known to everyone to avoid; the real high-frequency crashers are functional claims — words like "whitening," "antibacterial," "zero formaldehyde," "barrier repair" **need test reports or qualification backing**. Writing them without an evidence chain = advertising-law risk plus platform takedown, a double kill. When doing fact-hygiene self-check, go through functional claims one by one demanding evidence; this protects you better than only checking the extreme-word list.

**4. A credible benefit always wears a spec's face.** "Warm" is a category word every competitor uses, and users are already immune; "3mm thicker than the last generation, locks in heat for 4 hours" is a credible benefit — it wears a spec's face, which is why it sounds real. Putting FAB discipline into practice means: every benefit must answer "why should I believe you?"; a benefit that cannot answer is an adjective — send it back to step 3 to be re-smelted.

## Conversion Honesty Statement

Copy affects only one factor of conversion; traffic quality, price band, review maintenance, and landing-page experience together decide the final sale. This skill does not promise "a X% conversion lift" — if the user pushes for a performance guarantee at delivery, explain honestly that conversion is the conclusion of an A/B experiment, not a property of the copy, and suggest producing 2–3 hook-headline variants for ad testing.

## Input Checklist

| Input | Required | Notes |
|------|------|------|
| Product facts | Yes | Specs, materials, usage scenarios, real reviews — facts only, no adjectives |
| Audience | Yes (ask if missing) | Who buys, why, what they fear most |
| Copy type | No | Detail page (default) / short-video spoken / poster short copy |

When inputs are missing, ask for all at once: "Please provide: ① product facts (specs / materials / scenarios / real reviews, the more specific the better); ② the audience (who buys, why, what they fear most); ③ the copy type (defaults to detail page)."

## Pre-flight Self-check

Do the product facts contain **verifiable concrete numbers or materials**? "Good quality, great looks" is not a fact — it is a conclusion; send it back for facts. **Ask for the three veins of real reviews too**: high-frequency words in negative reviews, repeated questions in support records, follow-up questions in the Q&A (dark knowledge 2) — the ammunition for the objection-handling section comes from here. No facts means no evidence chain; copy built entirely on invention is prepayment for a refund rate.

Reference-presence self-check (optional; failure does not block):

```bash
test -f references/sources-and-methodology.md && echo OK
```

## Red Lines (hard bans, non-negotiable)

1. Do not invent facts: numbers, materials, certifications, and reviews must trace back to the input facts; if a fact is missing, ask the user — never fill it in.
2. Do not write extreme words or unqualified functional claims: zero tolerance for "best / #1 / national-level"; claims at the "whitening / antibacterial / zero formaldehyde" level are deleted without an evidence chain (dark knowledge 3).
3. Do not name or disparage competitors: write only your own verifiable advantages.
4. Do not promise conversion results: conversion is the conclusion of an A/B experiment, not a property of the copy (see the conversion honesty statement).
5. Exactly one CTA: two CTAs equal no CTA.

## Workflow

### Step 1: Pick the Framework (by the Audience's Decision Stage)

| Framework | Structure | When to use |
|------|------|--------|
| FAB | Feature → advantage → benefit | The audience already knows the product category and needs persuading to "pick this one" — technical specs must be translated into life benefits |
| PAS | Problem → agitate → solve | The audience has a pain but does not realize the solution — hit the nerve first, then offer the medicine |
| AIDA | Attention → interest → desire → action | Cold first-touch traffic — grab the eye first |

### Step 2: Write the Four-Part Structure (detail-page skeleton)

```markdown
1. Hook headline: benefit-first, one sentence on "how life changes after buying"
2. Body: expand per the chosen framework, each feature paired with a benefit (FAB discipline: a feature never stands alone)
3. Objection handling: the 3 hesitation points must come from real sources — high-frequency negative-review words, support records, Q&A follow-ups (dark knowledge 2);
   when data is missing, infer from category common sense and explicitly note "inferred from category common sense; recommend calibrating against real reviews"
4. CTA: a single action command, no more than one — two CTAs equal no CTA
```

### Step 3: Fact-Hygiene Self-check

- Numbers, materials, and certifications each trace back to the input facts; inventing means rework
- Ban extreme words like "best / #1 / national-level" (advertising-law red line) — on finding one, rewrite to a comparable expression ("2mm thinner than the last generation")
- **Demand evidence for functional claims one by one** (dark knowledge 3): words at the "whitening / antibacterial / zero formaldehyde" level with no test report or qualification backing → rewrite to a verifiable expression or delete
- For competitors, write only your own verifiable advantages; do not name or disparage
- Run each benefit through the "why should I believe you?" test (dark knowledge 4): what cannot answer is an adjective — send it back to be re-smelted

### Step 4: Chain Handoff

Deliver the copy + the framework used. **Then say: "The copy is ready; call campaign-designer to lay out the campaign rhythm, or channel-adapter to produce per-platform variants"** — the chain unfolds automatically.
- Expected: the downstream receives copy with all four parts complete and an identifiable framework, no need to re-ask for facts.
- On failure: downstream adaptation finds a fact gap → return to step 3 and check the evidence chain item by item; for the gap, ask the user for the fact — do not invent.

## Delivery Standards

- Artifacts: the four-part copy (hook headline / body / objection handling / CTA) + the framework used (FAB/PAS/AIDA).
- Save location: output directly in the conversation (this skill writes no files), for campaign-designer / channel-adapter to reference.
- Integrity verification: every feature pairs with a benefit; objection handling has exactly 3 items with traceable sources (real reviews / support records, or marked as category inference); exactly 1 CTA; no extreme words or unqualified functional claims (against the step 3 checklist).

## Failure Handling Table

| Symptom | Cause | Action |
|------|------|------|
| The whole thing is a spec list | No framework picked / FAB gap | Force every feature to follow with "this means you…" |
| The copy has no conversion feel | Missing the objection-handling section | Add 3 hesitation points answered fact by fact; prioritize digging from negative reviews / support records (dark knowledge 2) |
| Reads like a manual, not copy | Missing the hook | Rewrite the benefit-first headline before the body; the hook carries the first-screen stay/leave decision (dark knowledge 1) |
| Benefits are vague ("warm / good / high quality") | Benefits cannot answer "why should I believe you?" | Re-smelt per dark knowledge 4: a credible benefit wears a spec's face |
| Advertising-law risk | Extreme words / fabricated certifications / unqualified functional claims | Clear against the step 3 self-check list; demand evidence for functional claims one by one |
| The user asks for a conversion-rate promise | Touches the conversion honesty statement | Refuse to promise; explain conversion is multi-factor, and offer an A/B hook-headline variant plan |

## References

- [copywriting-formulas.md](references/copywriting-formulas.md) — the copywriting formula library: 10 headline formulas (with examples), PAS/FAB/AIDA structure templates, a CTA word bank by scenario, a table of platform-tone differences, and a negative list (check this before writing headlines and body)
- [sources-and-methodology.md](references/sources-and-methodology.md) — the direct-marketing framework provenance and attribution
