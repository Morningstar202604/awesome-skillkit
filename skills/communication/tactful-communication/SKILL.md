---
name: tactful-communication
description: >-
  Scenario-based communication coaching for Chinese high-context social and
  workplace settings, where generic AI output lands as blunt, stiff, or hollow.
  It supplies culturally specific scripts and a literal-to-intent lookup so the
  reply preserves face and carries real meaning. Use when the user needs
  tactful communication / Chinese etiquette / high-EQ phrases / decline
  gracefully / workplace reporting / subtext decoding / social scripts, or wants
  to rewrite a blunt or uncanny AI reply into something culturally appropriate.
  Do NOT use for formal document drafting (internal-comms-writer owns that),
  salary-negotiation strategy (route to a career coach), or any crisis involving
  grief, domestic violence, or self-harm (route to professionals immediately).
license: Apache-2.0
compatibility: Pure prompt skill; no scripts or runtime deps. The references
  contain Chinese phrase banks as subject matter (like a grammar reference).
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: communication
  pattern: scenario-coaching
  tier: pilot
  verified-date: "2026-09-25"
---

# Tactful Communication (Chinese High-Context Settings)

Coaching skill that fixes a structural AI blind spot: in Chinese high-context
communication, models refuse bluntly, comfort hollowly, and read indirect speech
as a genuine maybe. This skill does not invent facts or flatter; it injects
structured, culturally specific formulas and scripts so the user's words are
honest, face-preserving, and read the way they were meant. Chinese phrase
examples live in `references/` as subject matter, the way a grammar reference
holds example sentences.

## Overview

Given a social or workplace moment, this skill turns a rough intent into 2-3
ready-to-say scripts at different registers (formal / casual / close), flags
what NOT to say, and decodes what the other person actually meant. It covers
six recurring moves: refusal, comfort, apology, criticism, subtext reading, and
concise workplace reporting.

## Applicability Decision Table

| Scenario | Use this skill? | Alternative / Note |
|----------|-----------------|--------------------|
| Decline a request (extra work, favor, invite) | Yes | sandwich formula in `references/phrase-banks.md` |
| Comfort a grieving or failed friend / colleague | Yes | presence-only; no advice |
| Apologize for a missed deadline or mistake | Yes | specific-behavior formula |
| Give feedback / push back on a peer | Yes | behavior-not-person formula |
| Decode an indirect Chinese reply | Yes | `references/subtext-decoder.md` |
| Write a formal email, memo, or report document | No | hand off to internal-comms-writer |
| Negotiate salary or a job offer | Yes, with boundary | give framing only; defer strategy to a coach |
| Plan gifts, money amounts, banquet seating | Yes | `references/social-etiquette.md` |
| Crisis: grief, domestic violence, self-harm | No | stop scripts; route to professionals |

## Input Checklist

| Input | Required | Notes |
|-------|----------|-------|
| Scenario type | yes | decline / comfort / apology / criticism / report / subtext |
| Relationship tier | yes | boss / senior / peer / junior / friend / family / stranger |
| Setting | yes | public meeting / private chat / WeChat / phone |
| Goal | yes | what outcome the user wants (keep relationship, set boundary, etc.) |
| Constraints | no | must not offend, must stay honest, known deadline, etc. |

If inputs are missing, ask once: scenario, relationship, setting, and goal.

## Pre-flight Checks

1. **Honesty gate.** Is the user asking to convey a real intent? If a script
   would require lying, gaslighting, or manipulating the other party into a
   decision they would not freely make, refuse and explain the boundary.
2. **Crisis gate.** If the signal includes grief of a loved one, domestic
   violence, suicidal wording, or self-harm, stop coaching. Do NOT supply
   scripts; encourage reaching a friend, hotline, or professional, and offer
   to stay present. This is not a crisis service.
3. **Compliance gate.** If a "gift" to a boss or official looks like a bribe,
   flag it (see `references/social-etiquette.md`) rather than optimizing it.

## Workflow

| Step | Action | Output |
|------|--------|--------|
| 1 scenario & tier | identify the move and the relationship tier | scenario locked |
| 2 goal & register | pick goal and which registers the user needs | target register(s) |
| 3 select formula | pull the matching formula from references | formula chosen |
| 4 generate options | write 2-3 scripts (formal / casual / close) | script drafts |
| 5 boundary check | honest, respectful, no manipulation | final scripts + notes |

### Core Communication Formulas (compact)

Full phrase banks in `references/phrase-banks.md`. Details in
`references/workplace-scripts.md`; subtext table in
`references/subtext-decoder.md`.

| Move | Formula |
|------|---------|
| Refusal | affirmation + reason + alternative (the sandwich) |
| Comfort | observe emotion + acknowledge + presence; NO advice |
| Apology | specific behavior + its impact + concrete remedy |
| Criticism | behavior (not person) + joint problem-solving + blocker inquiry |
| Subtext | look up literal phrase -> likely intent; context overrides |
| Workplace report | conclusion (one line) -> evidence/data -> decision request |

## Safety & Boundaries

- This is a communication skill, **not manipulation**. Scripts must be honest and
  respect the other party's autonomy: no lying, no gaslighting, no PUA-style
  control, no engineered guilt.
- Never coach the user to feign illness, fake commitment, or string someone
  along (e.g. ghosting, or leaning on the soft "let us reconsider" deflection
  deceptively when the honest answer is no).
- Decoding subtext is for the user's own understanding; do not weaponize it to
  manipulate.
- Crisis signals (grief, domestic violence, suicidal wording) route to
  professionals; do not improvise therapy.

## Failure Remediation Table

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Script sounds too blunt (a flat "this task cannot be done") | missing affirmation / alternative | wrap in sandwich: affirm + reason + offer |
| Script sounds stiff / over-formal | register too high for the relationship | drop a tier toward casual/close |
| Script sounds over-familiar to a boss | wrong relationship tier | raise register; keep distance and deference |
| User missed that a "maybe" was actually a "no" | subtext not decoded | consult `references/subtext-decoder.md` first |
| Comfort reply gives unsolicited advice | advice leaked in | strip advice; keep observe + acknowledge + presence |
| Report buries the conclusion | bottom line not up front | lead with one-sentence conclusion, then evidence |
| Gift amount or item feels off | etiquette gap | check `references/social-etiquette.md` |

## Quality / Delivery Checklist

- [ ] Output gives 2-3 register options (formal / casual / close), not one line
- [ ] Each script is honest and does not ask the user to lie or manipulate
- [ ] Notes what NOT to say (the blunt / hollow / stiff version to avoid)
- [ ] Comfort scripts contain no advice; refusal scripts keep face on both sides
- [ ] Any indirect reply from the other party is checked against the subtext table
- [ ] Crisis or compliance signals are routed, not scripted

## Chain Position

- Downstream to `internal-comms-writer` for turning a chosen line into a formal
  email, memo, or report document.
- Downstream to `personal-voice-profile` for matching the scripts to the user's
  own tone so they do not sound translated.

## References

- `references/phrase-banks.md` — Chinese phrase banks for decline, comfort,
  apology, and criticism, with bad-example bans and register variants
- `references/subtext-decoder.md` — literal-to-intent lookup for high-context
  Chinese utterances, plus context cues and rules of thumb
- `references/workplace-scripts.md` — three-part reporting, pushback framing,
  meeting rules, declining extra work from a boss
- `references/social-etiquette.md` — gift money amounts, gift taboos, banquet
  seating and toast order, bribery boundary
- `references/sources-and-licenses.md` — sources, license, and attribution
