---
name: design-brief-interpreter
description: >-
  Interpret a vague visual design request into a machine-checkable design spec:
  purpose, audience, platform + exact canvas size/ratio, composition, style
  anchor, color palette, text hierarchy, and text budget. This is the entry skill
  of the visual-design-studio chain — its output feeds image-prompt-engineer
  directly, and layout-spec-auditor verifies the final image against it. Use
  when the user asks to make an image / design a cover / poster / infographic /
  illustration / cover / banner. Do NOT use for video frame prompts
  (video-prompt-engineer owns motion), nor for UI code generation.
license: Apache-2.0
compatibility: Pure prompt-based; no runtime dependencies.
metadata:
  author: "awesome-skillkit"
  version: "2.0"
  category: design
  pattern: single-task
  tier: standard
  verified-date: "2026-09-21"
---

# Design Brief Interpreter

Chain entry. Translate a vague "help me make an image" into a **design spec**—
every downstream step (prompt engineering, spec audit) references this spec.
Generating an image without a spec is pulling cards: wrong platform size means
redo, messy text hierarchy means redo.

## Applicability Decision Table (Judge First, Then Translate)

| What User Has | How to Handle |
|---|---|
| "Help me make a XX cover/poster/infographic" (has platform) | Standard flow: three questions → 7-field spec → handoff |
| "Just design something" (no platform, no theme) | Give 2 preset directions for user to pick, don't accept "whatever" |
| Want two images at once (theme beyond one sentence) | Split into multiple specs, each goes through chain |
| Video storyboard frames / UI code | **Don't use**: storyboards go to video-prompt-engineer, UI to frontend skills |
| Only want to resize/retext existing image | No full chain: directly hand to layout-spec-auditor for audit |

## Domain Tacit Knowledge (Four Things to Know Before Writing the Spec)

**1. Emphasizing everything = emphasizing nothing—hierarchy is design's only hard
currency.** This comes from Robin Williams' CRAP four principles in "The
Non-Designer's Design Book" (Contrast / Repetition / Alignment / Proximity), and
is a direct corollary of Gestalt psychology (proximity, similarity, figure-ground):
the eye first looks at the strongest contrast element, then at adjacent grouped
elements. On the spec this becomes three judgeable rules: **hierarchy uses only 3
levels, size gaps must be clearlydifferentiated** (design consensus: five hard-to-distinguish font
sizes aren't hierarchy, they're noise); **strongest luminance contrast reserved
for the most important element**; **proximity groups** (title near body =
ownership relationship, standard usage from IEEE ProComm visual communication
tutorial). Actionable test: imagine the design as grayscale and ask "where do I
look first" (the universal squint test); if you can't answer, hierarchy failed.

**2. Accent color's power comes from scarcity.** 60-30-10 rule (originating in
interior design, collected in Figma's official resource library): about 60%
dominant color (usually neutral background), 30% secondary, 10% accent. The key
insight isn't the ratio itself, but **"the boldest color should be the rarest"**—
a design with accent color across 40% of the frame fails because it no longer
points to anything. This is the most common divide between amateur and
professional color work. The spec palette field's discipline follows: one main +
one secondary + one accent; accent must correspond to "focal object" in the
composition note; "sprinkled everywhere" is forbidden.

**3. On-image text budget has empirical basis, not gut feel.** Converged finding
from multiple sources: cover text ≤5 words (YouTube creator empirical consensus),
Chinese platforms ≤12 characters for a single glance (Chinese platform creator
experience); text must be **readable at ~150px-wide mobile thumbnail size**—
mobile dominates views; text-to-background contrast 4.5:1 is the WCAG AA floor
(accessibility standards additionally suggest body text no smaller than 16px—note
16px is industry convention, not WCAG text; when text is burned into the image
both apply). So step 1's "cut text if possible" isn't aesthetic preference, it's
readability arithmetic: halving the word budget's readability loss is far less
than crammed-together-at-thumbnail loss.

**4. Style anchor is set against the competitor feed, not against empty air.**
Color grading's famous lesson: teal & orange became Hollywood standard in 2012,
cliché by 2020—**once a style is overused it no longer conveys any emotion, only
"I applied a LUT"**. Thumbnails same: high-click cover designers "design
differences against same-topic competitor feeds" (feed-level contrast), not
pursue beauty in a vacuum. So before finalizing the style field, ask one more
question: in the feed of similar content, does this style blend in or stand out?
User's answer "want to jump out" or "want to blend in" (brand consistency
scenarios) directly determines style direction.

## Input Checklist

| Input | Required | Notes |
|------|------|------|
| Rough need | yes | User's original words: "WeChat official account needs a cover about AI video" |
| Platform/purpose | yes (ask if missing) | Determines canvas size and composition direction, don't guess |
| Brand context | no | If brand colors/fonts/tone exist, record; otherwise give suggestions |

When inputs are missing, ask all at once (no multi-round drip): "Please add: 1)
which platform/occasion (determines canvas size); 2) one-sentence theme to
convey at first glance; 3) which text appears on the image (title/subtitle/byline)."

## Red Lines (Hard Bans, Non-Negotiable)

1. Platform/purpose can't be guessed: if any of three questions is missing, ask
   back; inventing a platform = wrong canvas size = whole chain rework.
2. Don't write non-judgeable style words: "nice/high-end/grand" forbidden in the
   spec—must convert to judgeable description (see step 2 style anchor discipline).
3. Don't exceed text budget: on-image text total ≤12 chars (Chinese) / ≤5 words
   (English); over, cut to only the hook, don't shrink font to cram.
4. Don't pile on accent colors: palette gives one "main/secondary/accent" set
   only, accent is unique; when user asks "a few more bright colors", explain
   scarcity rule per tacit knowledge 2.
5. Don't promise aesthetic evaluation: this skill delivers auditable specs, not
   "guaranteed beautiful"—aesthetic success is judged by layout-spec-auditor's
   structural checks and user feedback.

## Pre-flight Checks

This skill is pure prompt-driven: no runtime dependencies, endpoints, or env
vars, nothing to install. Only self-check:

```bash
test -f references/sources-and-methodology.md && echo OK
```

Expected output `OK`; failure means skill package incomplete, continue with
built-in methodology (style anchor discipline in step 2), and note methodology doc
missing in delivery.

## Workflow

### Step 1: Three Questions Set the Table (Missing → Ask Back, Don't Invent)

1. **Who sees it, where**—platform determines canvas (WeChat header 2.35:1,
   Xiaohongshu 3:4, Bilibili cover 16:9…)
2. **What to convey at first glance**—one-sentence theme; beyond one sentence
   means two images' work
3. **Which text appears**—list title/subtitle/byline one by one; every character
   on the image is a failure point, cut if possible (basis in tacit knowledge 3)

Expected: all three questions answered, platform resolved to specific name (not vague
like "post online").
If it fails: user can't answer platform → give 2 most common presets (WeChat
header / Xiaohongshu 3:4) to choose, don't assume; theme beyond one sentence →
return to failure table and handle as "split into multiple specs"; text over 12
characters → cut to hook then continue.

### Step 2: Produce Spec (Fixed 7 Fields)

```markdown
## Design Spec
- purpose:    one-sentence purpose and audience
- platform:   platform name + canvas W×H + ratio
- subject:    image subject (write "what to draw", not "what to express")
- style:      style anchor (3-5 judgeable words: media texture + color emotion + composition method)
- palette:    main + secondary + accent (give color name/value, not "high-end"; accent unique, see tacit knowledge 2)
- text:       list on-image text one by one (hierarchy + word cap); write none if no text
- do-not:     reverse constraints (what elements/styles not to include)
```

**Style anchor discipline** (drawing on Anthropic canvas-design's "visual
philosophy first"): set 3-5 judgeable words before entering prompt—"magazine-grade
minimalism, generous whitespace, single accent color" is auditable; "beautiful,
high-end" isn't. Same-series material must reuse the same style anchor, this is
the only anchor for series consistency.

**Hierarchy three questions** (self-check before finalizing step 2, per tacit
knowledge 1): are the size/luminance gaps clearly differentiated across subject, title, and
secondary info three levels? Is first-glance landing = subject? Does accent color
only appear on the focal object? If any is "no", fix the spec, don't hand off
with defects.

Expected: all 7 fields filled, no "TBD/TODO/whatever"; hierarchy three
questions all pass.
If it fails: some field can't be filled (like unclear brand color) → give 2-3
concrete color value sets for user to choose per failure table, don't invent;
style can only produce non-judgeable adjectives → convert via reference object
("high-end = low saturation + large dark areas + single accent color") and
confirm with user before finalizing.

### Step 3: Hand Off Downstream

- Say directly: "Spec ready, continue calling image-prompt-engineer to write the
  prompt; after generating the image, use layout-spec-auditor to audit against
  this spec"—**the chain unfolds automatically, user doesn't need to issue
  another command**.
- Expected: downstream skill gets a 7-field complete spec, no need to ask back.
- If it fails: user changes requirement mid-way → return to step 2 to revise
  corresponding field then re-hand off, don't transmit verbally from memory.

## Delivery Criteria

- Artifact: one `## Design Spec` spec, all 7 fields filled, no "TBD/TODO/
  whatever".
- Location: output directly in conversation (this skill doesn't write files),
  for downstream skills to quote verbatim.
- Integrity verification: check item by item—platform includes concrete W×H and
  ratio (not vague like "vertical image"); palette gives color names or values
  and accent unique (not "high-end"); text itemized with word cap or writes none;
  do-not at least 1 item; hierarchy three questions (step 2) all pass.

## Failure Handling Table

| Symptom | Cause | Action |
|------|------|------|
| User says "just design something" | Three questions zero info | Give 2 preset directions to choose, don't accept "whatever" |
| Theme beyond one sentence | Wants two images at once | Split into multiple specs, each goes through chain |
| On-image text over 12 chars | Wants to cram article into image | Image text keeps hook only, body returns to article (tacit knowledge 3 readability arithmetic) |
| Brand color unclear | "that kind of blue" | Give 2-3 concrete color value sets to choose |
| User wants accent color everywhere | Hits red line 4 | Explain scarcity rule per tacit knowledge 2; insist accent unique |
| User insists on "high-end" and won't change | Abstract word not auditable | Convert via reference object then confirm with user; once confirmed, lock as judgeable description |
| Same-series images drift in style | Reused different style anchors within series | Return to spec and reuse same style field; forbid reinventing style per image |

## References

- [sources-and-methodology.md](references/sources-and-methodology.md) — methodology
  open-source source (design-context / canvas-design) and this v2.0 investigation
  basis (Gestalt/CRAP/60-30-10/WCAG/platform empirical).
