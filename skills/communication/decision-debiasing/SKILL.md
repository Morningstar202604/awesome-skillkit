---
name: decision-debiasing
description: >-
  Structured debiasing protocol for consequential decisions that compensates for
  the assistant's own sycophancy and the user's cognitive biases (anchoring,
  confirmation, sunk cost). It forces a past-tense pre-mortem, a dedicated
  red-team argument against the user's favorite option, and a written decision
  record. Use when the user faces a consequential decision and wants to avoid
  cognitive bias, or asks for a pre-mortem, red-team, second opinion, or decision
  review. Triggers: decision debiasing / pre-mortem / red team / cognitive bias /
  second opinion / risk review. Do NOT use for simple everyday choices, or for
  financial / legal / medical professional advice (route to licensed professionals),
  or when the user just wants validation.
license: Apache-2.0
compatibility: Pure prompt skill, no scripts or runtime deps.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: communication
  pattern: adversarial-protocol
  tier: pilot
  verified-date: "2026-09-25"
---

# Decision Debiasing

A meta-skill that compensates for its own sycophancy: assistants anchor on the
user's first option, confirm what they already believe, and soften every objection.
For consequential, hard-to-reverse decisions that default is dangerous. This skill
runs an adversarial protocol — past-tense pre-mortem, bias-buster questions, a
red-team against the preferred option, and a decision record — so the call is
stress-tested. It improves judgment; it does not guarantee outcomes.

## Overview

Given a real decision on the table, this skill does NOT help rationalize the
favorite option. It frames the decision multiple ways, runs a Klein-style past-tense
pre-mortem ("it failed, explain why"), asks disconfirming questions, builds the
strongest case against the preferred option, rates reversibility, and records it.

## Applicability Decision Table

| Decision type | Use this skill? | Alternative / Note |
|---------------|-----------------|--------------------|
| Career change, job offer, relocation | Yes, full protocol | high stakes, hard to reverse |
| Investment / capital allocation | Yes, with boundary | framework only; route money strategy to a licensed advisor |
| Taking / rejecting an opportunity (vendor, partner, project) | Yes | medium-high stakes |
| Product / architecture bet, hire, buy-vs-build | Yes | pre-mortem + red-team especially useful |
| What to eat, what to wear, movie pick | No | trivial, easily reversible |
| Relationship / health / major life choice | Yes, gently | pair with emotional support; route clinical questions to professionals |
| Legal case, medical treatment, tax structure | No | stop; route to licensed professionals |
| User already decided and only wants validation | No | flag it; this skill argues, it does not cheerlead |

## Input Checklist

| Input | Required | Notes |
|-------|----------|-------|
| Decision statement | yes | the actual question, in the user's words |
| Options considered | yes | list every live option, not just the favorite |
| Time horizon | yes | when will we know if it worked? (sets the pre-mortem frame) |
| Stakes | yes | what is gained / lost; how much lives on this |
| Who is affected | yes | stakeholders beyond the user |
| Current preferred option | yes | which way the user is already leaning (the thing to attack) |

If inputs are missing, ask once: decision statement, options, time horizon, stakes,
and which option the user currently favors.

## Pre-flight Checks

1. **Professional boundary.** If the decision is primarily financial (portfolio
   sizing, specific securities), legal (contract interpretation, litigation), or
   medical (treatment, diagnosis), run the framework ONLY as general thinking
   structure and add a clear disclaimer that this is not professional advice and a
   licensed expert must be consulted before acting.
2. **Reversibility gate.** Rate the decision: easy to reverse (light scrutiny —
   frame + a quick bias check) vs hard to reverse (full six-step protocol +
   mandatory second opinion). Do not spend full protocol effort on a trivially
   undoable call.
3. **Sycophancy guard.** State explicitly up front: "I am going to argue against
   your preferred option. That is the point — it is not me doubting you."

## Workflow

Six steps. Each step has a required output; do not skip ahead.

| Step | Action | Required output | If it stalls |
|------|--------|-----------------|--------------|
| 1 Frame the decision | one-sentence question; state >=2 frames | framed question + alternative frames | vague question -> pin it to one sentence |
| 2 Pre-mortem | past-tense "it failed, explain why" | 10-15 failure reasons | generic reasons -> force concrete mechanisms (see references) |
| 3 Bias-buster | disconfirming questions | what would change the user's mind | user deflects -> restate the uncomfortable question |
| 4 Red-team | strongest case AGAINST the favorite option | steelmanned anti-case, in a dedicated skeptic voice | weak objection -> sharpen until it hurts |
| 5 Reversibility & second opinion | rate reversibility; require external opinion if hard | reversibility rating + second-opinion step | user resists -> ask "what would you tell a friend?" |
| 6 Decision record | lock the call and assumptions | decision-record block | no record -> this step is mandatory, not optional |

### Step 1: Frame the decision

Write the decision as a single question, then reframe it at least twice:
- **Gain vs loss:** "Which option maximizes upside?" vs "Which option minimizes
  what I cannot afford to lose?"
- **Short vs long term:** "What helps this quarter?" vs "What do I want to say in
  five years?"
Different frames surface different options. If only one frame ever feels right, the
user may be framed into the answer already.

### Step 2: Pre-mortem (Klein protocol)

Use the past tense, NOT "what could go wrong":
> "It is [time horizon] from now. This decision failed. Write down 10-15 reasons
> why it failed."

The past-tense framing licenses doubt that a hypothetical "risk" list suppresses.
Demand concrete causal mechanisms, not generic worry. See
`references/premortem-protocol.md`.

### Step 3: Bias-buster questions

Ask, and actually wait for real answers:
- What evidence would DISCONFIRM my favorite option?
- What specific data, if I saw it tomorrow, would change my mind?
- Who already disagrees with me, and what is their strongest argument?
- What would I tell a close friend who faced this exact choice?

### Step 4: Red-team

Adopt a dedicated skeptic voice and write the strongest possible case AGAINST the
user's preferred option. Steelman it — quote the strongest version of the opposing
view, build the anti-case fairly, then ask the user to rebut it. A weak red-team is
worse than none; it creates an illusion of scrutiny. See
`references/red-team-framework.md`.

### Step 5: Reversibility & second opinion

Rate reversibility 1 (fully reversible, cheap to undo) to 5 (locked in, large
sunk cost). At 4-5, the protocol REQUIRES an independent second opinion: a person or
source not invested in the user's current leaning. The user must actually seek it,
not just nod.

### Step 6: Decision record

Write it down. Chosen option, rejected options with the reason each lost, the key
assumptions the decision rests on, and the explicit trigger conditions that would
make the user revisit it. Template in `references/decision-record-template.md`.

## Core Protocols (compact)

| Protocol | One-liner |
|----------|-----------|
| Pre-mortem | "It failed. Explain why." (past tense, >=10 concrete reasons) |
| Bias-buster | name the disconfirming evidence, not the confirming evidence |
| Red-team | argue the strongest case against the favorite option, on purpose |
| Reversibility test | rate undo-ability; hard-to-reverse => mandatory second opinion |
| Decision record | write choice, rejected options, assumptions, revisit triggers |

## Common Biases Quick Reference

| Bias | What it looks like here | One-line debiasing action |
|------|-------------------------|----------------------------|
| Anchoring | first number / first option set the range | list all options before picking any anchor |
| Confirmation | only seeking reasons the favorite works | actively hunt disconfirming evidence |
| Sunk cost | "I have already invested so much" | ask "if I walked in today fresh, would I choose this?" |
| Availability | vivid recent example drives the call | ask for base rates, not the memorable story |
| Framing | gain-framed vs loss-framed flips the choice | reframe the decision both ways |
| Groupthink | the room agrees because no one pushed back | assign a named skeptic on purpose |
| Overconfidence | "I'm sure it works" | require a pre-mortem count of failure reasons |

Fuller table in `references/bias-buster-checklist.md`.

## Safety & Boundaries

- This is a **judgment scaffold, not advice**. It supplies thinking frameworks; it
  does not tell the user what to choose and does not predict outcomes.
- **Not** financial, legal, or medical advice. If the stakes are in one of those
  domains, run the framework for clarity and route the actual decision to a
  licensed professional.
- The adversarial tone is methodological: keep it clinical and fair — do not bully
  the user or talk them out of a call they have sound reasons for. Even a perfectly
  debiased decision can lose.

## Failure Remediation Table

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Pre-mortem reasons are generic ("things might go wrong") | no concrete causal mechanism | force "because X failed, which made Y happen" chains |
| Red-team argument is weak / strawman | reluctant to attack the favorite | explicitly adopt skeptic voice; steelman the opposition |
| User keeps deflecting disconfirming questions | confirmation bias talking | restate the question; ask what data WOULD change their mind |
| No decision record gets written | feels like extra admin | stop; the record is a required deliverable, not optional |
| User wants validation, not scrutiny | misrouted request | name it honestly: "I notice you want reassurance; here is the hard case instead" |
| Protocol run on a trivial choice | reversibility gate skipped | collapse to step 1 + one bias check; do not over-process |
| Reversibility rated 5 but no second opinion sought | skipping the hard step | pause and require an external, non-invested opinion |

## Quality / Delivery Checklist

- [ ] Decision is framed as one sentence, with at least one alternative frame
- [ ] Pre-mortem produced in past tense with >=10 concrete failure reasons
- [ ] Bias-buster questions asked, with the disconfirming ones actually answered
- [ ] A real red-team case against the preferred option exists (not a strawman)
- [ ] Reversibility rated; hard-to-reverse calls include a second-opinion step
- [ ] A written decision record (choice, rejected options, assumptions, triggers)
- [ ] No financial/legal/medical call presented as a recommendation; disclaimer present

## Chain Position

- Downstream to `tactful-communication` for how to communicate the decision and its
  rationale to stakeholders, bosses, or the user who will live with it.
- Downstream to `session-handoff` (where available) to carry the decision record and
  revisit triggers into a follow-up review session.

## References

- `references/premortem-protocol.md` — detailed Klein pre-mortem procedure, how to
  avoid generic answers, time-horizon framing, and a worked career example
- `references/bias-buster-checklist.md` — 12 cognitive biases: name, what it looks
  like in a decision, the specific debiasing question/action, and an example
- `references/red-team-framework.md` — how to red-team your own decision,
  steelmanning the opposing view, the skeptic role, and common failure modes
- `references/decision-record-template.md` — template: context, options, choice,
  rationale, assumptions, trigger conditions, review date
- `references/sources-and-licenses.md` — sources and attribution (Klein,
  Howard-Abbas, Kahneman, Wikipedia CC BY-SA)
