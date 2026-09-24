---
name: visual-style-anchor
description: "Create a reusable visual style anchor for a video or image project: one-page style guide locking color palette, lighting scheme, materials, era, and medium texture — plus a character consistency card (identity line, wardrobe, props, forbidden changes) that keeps every generated shot on-model. Use when the user asks to set the visual style / style setting / character setting / keep the character consistent / keep the face on-model / style guide / character sheet / visual consistency before batch generation. Do NOT use for writing per-shot prompts (use video-prompt-engineer), nor for generating the images themselves."
license: Apache-2.0
compatibility: Pure prompt-based design skill; no scripts, no API keys.
metadata:
  author: "awesome-skillkit"
  version: "2.0"
  category: video
  pattern: single-task
  tier: standard
  verified-date: "2026-09-21"
---

# Visual Style Anchor

Produce two reusable assets: a **style anchor** (style-anchor.md, the film's visual DNA) + a **character consistency card** (character-card.md, the contract that keeps the face on-model). Locking the style before batch generation is the cheapest way to unify the whole film's visuals — reworking image by image costs ten times more than writing one anchor doc first.

## Applicability Decision Table (Judge First, Then Anchor)

| Your Situation | Use This Skill? | How |
|---|---|---|
| Before batch-generating shots/images, need to unify visuals first | yes | Full flow: style anchor + (if needed) character card |
| One-off single image, no reuse | light use | Only produce the style anchor; skip the character card and reuse notes |
| Project already has an old style anchor | edit the old file | **Don't start from scratch** — change the anchor and every already-generated shot is void |
| Just want to generate one image, no style wait | no | Use the image-generation tool directly; this skill is a pre-batch planning step |
| Per-shot prompt writing | no | Belongs to video-prompt-engineer (this skill is its upstream) |

## Domain Tacit Knowledge (Four Things You Must Know Before Anchoring a Style)

**1. Teal-orange contrast isn't aesthetic fashion, it's physiology — but it's already a cliche.** Color-grading consensus (cross-referenced across colorist essays and multiple grading tutorials): human skin, regardless of ethnicity, sits in the orange band of the spectrum, and teal is orange's complementary color — push the shadows toward teal and warm the skin, and faces "pop" off the background; this is a physical mechanism that creates depth without compositing tricks. But it was industrialized by Hollywood around 2007 (Transformers + digital cameras + DaVinci Resolve LUT workflows), **became standard by 2012 and a cliche by 2020** — viewers can recognize it after two grading tutorials. The discipline for the style anchor: when you choose "cinematic", you must know it's a cliche starting point; differentiation comes from subject matter and light structure (in-frame sources / practical light), not smearing the shadows teal. What you actually lock into the anchor is the contrast structure and source types, not a popular hue itself.

**2. The first principle of grading: correct first, create later, leave headroom.** Colorist workflow (consistent across sources): do technical correction first (white balance / exposure), then creative grading; reversing the order amplifies rather than hides color casts; when applying a LUT, bring opacity down to **50-70%** (preset LUTs are pushed hard for preview); **push only the shadows, don't touch midtones**, so skin stays salvageable; cap saturation at skin tones — skin going green or magenta = a sickly look. For the style anchor: the palette rules column should spell out "what may bloom (highlights), what gets a cap (skin / accent-color saturation)" — this is the "saturation discipline" in the anchor.

**3. Color emotion has an industry temperature dictionary; don't invent mappings.** General lexicon of color storytelling (consistent across sources): warm (amber/gold/orange) = nostalgia, intimacy, comfort; cool (teal/blue/gray) = distance, tension, melancholy; high-saturation + lifted blacks = commercial/bright; low-saturation + crushed blacks = cinematic/foreboding. Complementary colors (teal-orange, red-green, yellow-purple) create tension; analogous colors create soft unity (Moonlight-style neon); monochrome creates oppressive mood (The Matrix green). The anchor's "color emotion" slot takes words from this dictionary; convert the user's "premium vibe / atmosphere" into dictionary words via reference objects — don't invent private mappings like "gray = premium".

**4. Consistency beats beauty — cross-shot stability is the professional dividing line.** The old color-grading saying: viewers first notice unnatural skin tones, and **inconsistent skin across shots instantly exposes the amateur**. The entire value of the style anchor is in the word "lock": what drifts during batch generation isn't taste, it's entropy — each image looks good on its own but together isn't one film. So the anchor is a contract, not a reference: the five slots are copied verbatim per shot; changing one word is restarting the project.

## Input Checklist

| Input | Required | Notes |
|------|------|------|
| one-line project brief | yes | At the granularity of "rainy-night convenience-store neon short" |
| reference (text/image link) | optional | Something on the order of "like Blade Runner's rainy night" is enough |
| character count | no | 0 = style anchor only; >=1 = one consistency card per character |
| aspect ratio / platform | no | Default 16:9 |

When missing, ask everything at once: "Please provide: ① one-line project brief ② character count (default 0, style anchor only). I'll take defaults for the rest."

## Red Lines (Hard Bans, Non-Negotiable)

1. If an old anchor exists, don't start from scratch: changing the style anchor mid-project voids all already-generated shots; if a change is truly needed -> explicitly state the rework scope and get user confirmation.
2. The identity line forbids negations: `not wearing hat` will generate a hat — always rewrite negatives as positives or move them into the "forbidden changes" section.
3. The identity line forbids paraphrase: every prompt's subject slot containing the character is copy-pasted verbatim; change one word and the model may swap the face.
4. Emotion words must be converted to concrete descriptions: abstract words like "premium vibe" don't go into the anchor; convert them via reference objects into judgeable descriptions and confirm with the user.
5. Palette <=3 main colors + a single accent: the accent color goes only on the focal object (60-30-10 scarcity rule); "sprinkled everywhere" is forbidden.

## Pre-flight Checks

- Does this project already have an old `style-anchor.md` / `character-card-*.md`? If so -> update the old file,
  don't start from scratch — change the anchor and all generated shots are void (Red Line 1).
- The reference file is on disk: `test -f references/style-anchor-formula.md` (needed when expanding the formula);
  if missing -> STOP and report the repo is incomplete.

## Workflow

### Step 1: Set the Style Anchor Per the Five-Slot Formula

```markdown
# Style Anchor: <project name>

## Palette
Main #0E1A2B (night-sky blue-black) / Accent #FF6B35 (neon orange) / Secondary #7FD1C9 (teal)
Rules: <=3 main colors across the film; accent only on focal objects; cap skin-tone saturation (tacit knowledge 2).

## Lighting
Night exterior: practical neon (in-frame sources) dominant, teal-orange contrast structure, highlights may bloom.

## Materials
Wet reflective asphalt, frosted plastic, glass storefronts. Forbidden: flat color blocks, low-saturation matte.

## Era
Modern city, no conflicting period markers (film-wide ban: CRT TVs, film grain).

## Medium Texture
cinematic live-action, 35mm depth-of-field feel, subtle handheld breathing.
```

Expected: all five slots filled, the palette gives HEX values, and palette rules include saturation discipline.
If it fails: the user only gave emotion words ("premium vibe") -> convert via tacit-knowledge-3's temperature dictionary: "premium vibe = low saturation + large dark areas + single accent color"; confirm the conversion with the user before finalizing (Red Line 4).

### Step 2: Produce the Character Consistency Card (If Needed)

```markdown
# Character Card: Xiaoyu

## Identity line (single sentence, embeddable in any prompt)
a young woman, short black bob hair, tired but sharp eyes, black oversized hoodie, white sneakers

## Turnaround list
front / 3/4 side / back (if you have an image tool, lock these three first; all later shots reference them)

## Locked wardrobe & props
black hoodie (hood usually down), white shoes, blue lighter (plot prop)

## Forbidden changes
hairstyle, hair color, eye color, height proportions — no prompt may add glasses/hat/costume changes
(if the plot needs a costume change -> stop, return to this card and open a variant card variant-B; on-the-fly edits are forbidden)
```

Expected: identity line <=25 words (too long won't fit in every prompt), no negations (Red Line 2).
If it fails: identity line over 25 words -> cut non-identifying features (wardrobe detail belongs in the wardrobe section), keep only face-defining elements; a negation appears in the identity line -> rewrite as a positive or move it into "forbidden changes"; the user can't supply a reference image -> still produce a text identity line and note "reference images not finalized; drift risk is on you".

### Step 3: Write Reuse Notes

At the end of each file, add a "how to use" section:
- style-anchor -> cite the whole style slot block in every prompt
- character-card identity line -> embed verbatim into every character-bearing prompt's subject slot; paraphrase is forbidden (change one word and the model may swap the face — Red Line 3)

Expected: both files have "how to use" sections explicitly stating "cite verbatim / no paraphrase".
If it fails: the project doesn't need reuse (one-off image) -> skip this step and note in the delivery standard "non-reuse scenario, no reuse notes attached".

### Step 4: Delivery Check

| Check Item | Pass Criterion |
|--------|----------|
| Five slots complete | Palette has HEX, lighting has source types, palette rules include saturation discipline |
| Identity line usable | <=25 words, no negations ("not wearing hat" makes the model generate a hat) |
| Forbidden list exists | >=3 items per character |
| Emotion words converted | No abstract words like "premium vibe" in the anchor (Red Line 4) |

Expected: all four pass before delivery.
If it fails: any item fails -> return to the corresponding step (a missing slot -> Step 1; a bad identity line -> Step 2; forbidden list under 3 -> add items and re-check; residual emotion words -> convert via tacit knowledge 3); don't deliver with failing items.

## Failure Remediation Table

| Symptom | Cause | Remedy |
|---|---|---|
| Generation still swaps the face | The identity line was paraphrased in the prompt | The identity line must be copy-pasted; paraphrase is forbidden (Red Line 3) |
| Palette drifts across shots | The style slot isn't carried in every prompt | The style slot is mandatory; see video-prompt-engineer's six slots |
| The user adds a new character mid-project | The card had no variant mechanism | Open a variant card and update the continuity constraint table (storyboard-designer's output) |
| Emotion words can't land | Abstract words like "premium vibe" | Force conversion via tacit-knowledge-3's temperature dictionary and confirm with the user |
| The user insists on "that teal-orange blockbuster look" | Hits the cliche risk (tacit knowledge 1) | Don't refuse but call it out: it's been a cliche since 2020; rewrite as "teal-orange contrast structure + subject-matter-specific sources"; differentiation comes from light and subject |
| Skin tone inconsistent across shots | No saturation discipline locked | Return to Step 1 to add a saturation cap; regenerate the affected shots |
| The user asks to change the anchor mid-project | Hits Red Line 1 | List the voided shots and rework cost; open a new anchor after confirmation |

## Delivery Standard

- `style-anchor.md` one page (<=60 lines), five slots complete, palette rules include saturation discipline
- `character-card-<name>.md` one per character, identity line + forbidden list complete
- Both files include a "how to use" section
- No unconverted emotion words in the anchor (Red Line 4 fully checked)

## References

- [style-anchor-formula.md](references/style-anchor-formula.md) — expanded formulas for the style anchor's five slots and more examples
- [character-consistency.md](references/character-consistency.md) — full discipline for character consistency (incl. seed/voice locking, drift audits)
- [sources-and-methodology.md](references/sources-and-methodology.md) — methodology provenance (incl. this repo's existing ai-baby-podcast practice and open-source ecosystem credits) and v2.0 research sources (colorist workflow / teal-orange evolution / color temperature dictionary)

## Chain Handoff (Downstream Suggestions)

This skill is the upstream "visual planning" skill in the video-domain production chains. Suggested orchestration order:
visual-style-anchor -> storyboard-designer -> shot-recipe-designer -> video-prompt-engineer -> video-script-writer, then plug into the already-registered video-domain talking_character / meme chains (video-voice-synth -> video-lip-sync -> video-editor -> video-subtitles -> video-thumbnail).
Currently this skill isn't registered in skill_chains.json's video-domain skills list (standalone); the handoff above is descriptive only, with no cross-directory hard links.
