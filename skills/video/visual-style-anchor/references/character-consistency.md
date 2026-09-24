# Character Consistency Discipline

> "The face doesn't drift" isn't mysticism—it's three disciplines: **fixed description,
> reference-first, drift audit**. This document is the full operating manual for the
> visual-style-anchor skill's character card, integrating the proven practices of this repo's
> ai-baby-podcast skill (viral-entertainment pack) and open-source community methods.

## Table of Contents

1. [Identity line](#1-identity-line)
2. [Turnaround sheets](#2-turnaround-sheets)
3. [Locking and do-not-change](#3-locking-and-do-not-change)
4. [Drift audit](#4-drift-audit)
5. [Variation mechanism](#5-variation-mechanism)
6. [Voice consistency (dubbed characters)](#6-voice-consistency-dubbed-characters)

---

## 1. Identity line

A **single sentence** you can drop straight into any prompt's subject slot, ≤25 words:

```text
a young woman, short black bob hair, tired but sharp eyes, black oversized hoodie, white sneakers
```

Rules:
- **Copy-paste it; no synonym rewriting**—change "hoodie" to "sweatshirt" and the model may swap the clothing
- Order appearance features from "hard to change" to "easy to change": hair style/color → facial features → body type → clothing → accessories
- No negative prompts: `not wearing glasses` can still generate glasses (the model's handling of "not" is unreliable)
  → to convey "no glasses," simply don't mention glasses at all

## 2. Turnaround sheets

When you have an image-generation tool, finalize three sheets before the character appears:

| View | Use |
|------|------|
| Front | Facial-feature baseline |
| 3/4 side | The actual angle of most shots |
| Back | Back-view shots + hairstyle completeness |

Once finalized, store the three images in the project's `characters/` directory, named
`char-<name>-front.png` etc. In later generation, feed them as reference images (when the model
supports image reference) or as the description baseline (when text-only).

## 3. Locking and do-not-change

The character card must have a "do not change" list (≥3 items):

```text
Do not change: hairstyle (black ear-length bob), hair color (pure black), eye color (dark brown)
```

Criterion: **any feature the plot doesn't require changing goes on the do-not-change list**. Features
the plot does require to change (wardrobe, injury makeup) don't go on the list—use the variation
mechanism (see §5); ad-hoc changes inside a single prompt are forbidden.

## 4. Drift audit

During batch generation, audit on a cadence:

- Sample 1 out of every 10 shots, side by side against the turnaround baseline
- Compare dimensions: hair outline / facial-feature proportions / clothing color value (sample and compare HEX)
- Two consecutive sampled shots drift → pause generation, go back and check whether the prompt rewrote the identity line
- For long videos (>30 shots), raise the cadence to 1 sample per 5 shots

## 5. Variation mechanism

The only legitimate path when the plot requires the character's state to change (wardrobe/injury/old age):

1. Stop the current batch generation
2. Open a variation section inside the character card: `## Variant B: injury makeup (from scene-05)`
3. The variation description = the original identity line + the minimal change set (write only the difference: `+ left cheek bandage`)
4. Update storyboard-designer's continuity constraint table, marking the scene range where the variation is in effect

Forbidden: tacking a description onto the prompt ad hoc—that also pollutes reuse of the identity line.

## 6. Voice consistency (dubbed characters)

When a character has lines, the voice is also part of the "face" (practice from ai-baby-podcast):

- Lock it: the TTS voice ID / voice description (`high-pitched, fast, sarcastic adult in baby voice`)
- Never swap: the same character uses the same voice throughout; never re-render with a different TTS vendor
- Drift audit like the picture: sample-listen 5 seconds, score on voice/tempo/accent
- Write the catchphrase onto the character card—"fixed catchphrase + contrast persona" is the memory-point formula

## Quick checklist

- [ ] Identity line ≤25 words, reused by copy-paste
- [ ] Turnaround sheets finalized and archived
- [ ] Do-not-change list ≥3 items
- [ ] Sampling plan set (1 sample per 10 shots)
- [ ] Variations go through a variation section, not polluting the identity line
- [ ] For dubbed characters: voice locked + catchphrase written on the card
