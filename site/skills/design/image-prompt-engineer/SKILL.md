---
name: image-prompt-engineer
description: >-
  Engineer text-to-image prompts from a design spec: five-segment structure
  (canvas + subject + composition + style anchor + text spec), prompt-priority
  ordering (position = weight), lighting and camera physics vocabulary,
  text-rendering rules (quote exact strings, match length), negative terms as
  nouns, and per-model dialects including the text-rendering rule of thumb.
  Write or audit modes. Use when the user asks to write an image prompt / text-to
  -image prompt / make image more professional / prompt audit. Do NOT use for
  video prompts (shot-designer), nor for choosing canvas sizes
  (design-brief-interpreter already fixed them).
license: Apache-2.0
compatibility: Pure prompt-based; no runtime dependencies.
metadata:
  author: "awesome-skillkit"
  version: "2.0"
  category: design
  pattern: dual-mode
  tier: standard
  verified-date: "2026-09-22"
---

# Image Prompt Engineer

Write and audit text-to-image prompts from a design spec. Core is **five-segment
structure** + **text rendering rules**—image models don't read minds, and on-image
text is the #1 failure source.

This skill only produces prompts (or audit reports), **doesn't generate images**:
the prompt sets the "upper bound"; output quality also depends on model
capability, seed, and parameters. Stating this up front saves all the later
"why does it still not look good when I follow it" back-and-forth.

## Applicability Decision Table

| Your Situation | This Skill's Role | Go To |
|----------|--------------|------|
| Have design spec, need to write image prompt | yes, write mode | here |
| Have prompt, suspect issues, want audit | yes, audit mode | here |
| Need video prompt | out of scope | shot-designer |
| Aspect ratio/size not set | wrong order | design-brief-interpreter (set ratio) → come back |
| Image generated, want to audit size/safe area | out of scope | layout-spec-auditor |
| On-image readable text needed, but don't want to check model dialect | must check: wrong model = wasted image | step 2 + model-dialects.md iron rule 1 |

## Input Checklist

| Input | Required | Notes |
|------|------|------|
| Mode | yes | `write` (write prompt per spec) \| `audit` (audit existing prompt) |
| Design spec | write required | 7-field spec from design-brief-interpreter |
| Target model | no | default generic structure; if specified, apply dialect (see references/model-dialects.md) |
| Prompt to audit | audit required | paste original |

When inputs are missing, ask all at once: "Please provide: 1) mode (write new
prompt / audit existing prompt); 2) design-brief-interpreter's 7-field spec
(write required); 3) target model (optional); 4) prompt original to audit
(audit required)."

## Pre-flight Checks

This skill is pure prompt-driven: no runtime dependencies, endpoints, or env
vars. Only self-check:

```bash
test -f references/model-dialects.md && echo OK
```

Expected output `OK`; failure means skill package incomplete—generic five-segment
structure (step 1) still usable, but skip step 2 dialect lookup, and note dialect
table missing in delivery. **Environments that can't run shell are treated as
pass** (skill package built uniformly by this repo, dialect table ships with
package), don't stop or ask user for environment info because this command can't
run. Input incomplete (missing mode, or write missing spec, or audit missing
original) → ask all first then STOP, don't guess.

## Tacit Knowledge (What Actually Decides Prompt Success)

### 1. Position Is Weight: Non-Negotiable Elements Go First

Most models weight **earlier prompt tokens higher**. If the subject must be a red
bicycle, it can't be the 8th phrase in the prompt. Ordering discipline: **subject
> action > environment > lighting > style > technical params > negative**.

### 2. Lighting Is the Biggest Quality Multiplier

Same subject, different lighting = different emotion and tier. Write four lighting
elements: **light source type** (natural/dramatic/artificial) → **direction**
(backlight/side/top) → **quality** (soft/hard/diffuse) → **color temperature or
time of day**. Can't write? Look up words in `references/visual-detail-lexicon.md`'s
three-layer lighting table.
(This is a multi-source consensus, also the opening iron rule of this repo's lexicon.)

### 3. Describe, Don't Evaluate

`beautiful` / `stunning` / `masterpiece` carry no visual information—they only
express "I want it to look good". Replacement: swap evaluation for one to three
**observable details** (`soft rim light on hair`, `visible pores and skin texture`,
`scuffed metal edges`). **Judgment criterion**: can another person holding this
prompt reproduce a similar image? If not, it's not written clearly.

### 4. Camera Physics Drives Realism

Diffusion models learned real lens optical characteristics. Write focal length
and aperture, and the model simulates depth of field, distortion, and grain:
- portrait: `shot on 85mm, f/1.8, shallow depth of field, bokeh background`
- landscape: `shot on 14mm ultra-wide, f/11 deep focus`
- street: `35mm, f/5.6, film grain, Kodak Portra 400`
(One "professional photography feel" doesn't equal one focal length.)

### 5. Iteration Discipline: Change One Variable at a Time

Changing prompts must be attributable: one round moves one slot (changed
lighting, don't also swap style), otherwise if it looks good you don't know which
phrase worked. Accumulate effective combos, build your own prompt library—
reproduction beats inspiration.

### 6. Prompt Budget: Overlong Dilutes Weight

Sources give different length caps (about 75–150 words), consensus is **overlong
dilutes key information**. This skill gives a range not a precise number: when
prompt exceeds about 150 words, cut from the top per tacit knowledge 1 priority.
**Quality words capped at 2–3** (`8K, masterpiece, ultra-detailed` piled to five
fight each other, actually lose weight).

### 7. Three Disciplines for Negative Constraints

1. **Noun-style list**: `blurry, watermark, extra fingers, garbled text`—`no
   blur` gets rendered as body text (imperative is the most common negative failure).
2. **Short and specific**: long negative lists leak into positive semantic space,
   degrading overall quality. 3–8 high-value words capped.
3. **Positive specification more reliable than negative**: want sharp background,
   write `sharp background detail`, don't rely on `no blurry background`. Only
   models with an independent negative field (SD family) put negatives in the
   independent field; on other models negative effect is weak.

### 8. Model Choice Comes Before the Prompt

The same prompt across models differs more than changing the prompt ten times on
the same model. **Want on-image text → first pick a text-rendering-reliable model
family per iron rule 1** (see `references/model-dialects.md`)—this step wrong,
no matter how good the prompt, it's a wasted image.

### 9. Plastic Feel's Antidote Is Micro-Details and Imperfections

AI images "obviously fake" often because too clean. Inject real grime: `pores and
skin texture visible`, `dust particles in the air`, `micro-scratches on the
glass`, `fuzz on the wool sweater`.
(Credibility: single-source experiential technique, hasn't reached multi-source
cross-validation threshold—use as a tryable technique, not a consensus claim.)

### 10. Turn Off the Model's "Beauty Filter"

Some models default to adding a beautification filter that overrides your designed
lighting (automatically retouches hard light to soft). When available, use
`--style raw`-type parameters to suppress default aesthetics, so prompt
instructions truly take effect.

## Red Lines (Hard Bans)

1. **Don't pad with extreme quality words** (`8K`/`masterpiece`/`ultra-detailed`):
   carry no visual info, piling on loses weight; replace with concrete details per
   tacit knowledge 3.
2. **Don't write `no xxx` imperative negatives** (gets rendered as body text);
   also don't write negative lists as essays.
3. **Don't put copyrighted style names/character names as deliverable content**:
   in commercial delivery, `in the style of <living artist>`, famous IP character
   names carry legal risk; when a style is requested, rewrite as describable
   features (brushwork/color/era).
4. **Audit mode doesn't change design unilaterally**: only fix mechanics (missing
   segments, missing quotes, negative phrasing, evaluation words, pronouns);
   changing design intent (swap subject/swap style/swap composition) must ask user
   first.
5. **Don't promise output quality and text rendering success rate**: this skill
   delivers prompt text; whether a good image comes out depends on model,
   parameters, and randomness (honesty declarations 1, 6).

## Honesty Declarations

1. **This skill doesn't generate images**: artifact is prompt text (write) or audit
   report (audit). All "final effect" is delivered by the image model.
2. **`references/model-dialects.md` is a 2026-09-14 web research snapshot**, file
   top carries its own timeliness declaration. Image models update at **monthly**
   speed—before executing, must reconfirm per that file's "verification method"
   column; this skill doesn't guarantee table conclusions are currently valid.
3. **"Five-segment structure" is this repo's operationalized framework**, not any
   model vendor's official spec; its cross-model generality comes from practice
   induction.
4. **Negative constraint effectiveness varies by model**: models with independent
   negative field are strong; those only writing noun-style in prompt are weak
   and may be rendered as elements.
5. **Prompt length cap (75–150 words) sources differ**: this skill gives a range
   not a precise threshold; the principle (overlong dilutes) is trustworthy,
   numbers are reference only.
6. **Text rendering not guaranteed**: even with the right model family, long text,
   small font, multi-language mixing still frequently breaks. The safe approach is
   "textless base image + post-typesetting" fallback—proactively tell the user this
   as an option.

## Workflow

### Step 1 (write): Order by Priority + Fill Five Segments

```text
[canvas ratio+size] + [subject image content] + [composition shot size+layout] + [style anchor quote spec] + [text text wrapped in quotes verbatim]
```

Rules (each from hard-won lessons):

- **Natural language full sentences**, not keyword piles—"keyword chanting" is
  2023 writing, modern models understand grammar
- **Precise enough to reproduce**: write "Kodak Portra 800 skin tones",
  "Rembrandt lighting", "50mm f/1.4 shallow depth of field", not "professional
  photography feel"
- **No pronouns**: models can't tell "it/that person"—directly say "short-black-
  haired woman", "red sedan"
- **Text rules (highest priority)**: text to appear on image wrapped **verbatim in
  double quotes** in the prompt; new/changed text matches original length where
  possible (character count swings squeeze layout); change text with "change 'old
  text' to 'new text'" edit phrasing
- **Negative constraints noun-style**: `blurry, watermark, extra fingers, garbled
  text`—don't write "no blur" (rendered as body text)

Expected: output prompt contains all five segments, subject info first, on-image
text already verbatim double-quoted, negative constraints a short noun list.
If it fails: some segment can't be filled (like spec didn't give composition) →
return to design spec to complete then write, don't invent; text segment can't
produce readable copy → return to design-brief-interpreter's text field for
original; negative constraints contain "no xxx" phrasing → rewrite as noun list
and re-output.

### Step 2: Apply Model Dialect (Check This First for Images With Text)

Look up [model-dialects.md](references/model-dialects.md). **#1 hard rule: on-image
readable text (title/label/data) → prioritize text-rendering-reliable models (like
GPT Image family); Gemini family basically doesn't render readable text**—wrong
model, no matter how good the prompt, it's a wasted image.

Expected: already rewritten per target model's dialect, and "on-image text needed"
hard rule checked.
If it fails: user-specified model conflicts with "on-image readable text" →
first explain tradeoff to user (swap model / textless base image + post-typesetting),
choose one then proceed, don't force.

### Step 3 (audit): Check Against Five Segments

Output checklist: each segment hit/miss + whether text is verbatim quoted +
whether negatives are noun-style (**and explain the mechanism**: `no xxx` gets
rendered as body text, long lists leak into positive semantics—tacit knowledge 7)
+ **whether evaluation words are piled** (**name specific phrases in the original
prompt one by one**, like "the feeling of coffee tasting good", "professional
photography feel", don't just name the category) + **whether pronouns exist**
(rule 4). Missing segments filled per spec, deliver before/after fix comparison.

**Rewrite produces only one integrated draft**: keep all elements of original
intent (subject / scene / purpose / photo feel), only add executable details;
**don't give multi-style alternatives** ("realistic vs fashion editorial"
branching = unilaterally changing design direction, violates red line 4). When
there's a genuinely worth-branching option, list it on a separate line at the end
noting "needs your decision", not counted in the main deliverable.
**Report language follows user's question language**; prompt body can be English
per model dialect, but diagnosis and explanation in user's language.

Fix priority: **wrong model (if text needed) > on-image text not verbatim quoted >
negative imperative > evaluation word pile > missing segment > missing technical
params**. First two are "definitely breaks", fix first.
If it fails: prompt to audit lacks spec for comparison → ask for spec first; user
can't provide spec → degrade to pure structural audit (only check five segments
complete, quotes and noun-style rules), and note in report "not compared against
spec".

### Step 4: Deliver and Chain Handoff

Deliver prompt original + five-segment annotated version. **After generation,
immediately hand to layout-spec-auditor to audit size and safe area against
design spec**—chain continues, doesn't wait for user to speak.
- Expected: downstream gets something usable verbatim—prompt original pastes
  directly into image model, annotated version has segment names per segment.
- If it fails: user only wants to use it themselves (not enter chain) → deliver
  prompt original and stop, annotated version attached for backup.

## Built-in Verification Steps (Check Each Before Delivery)

- [ ] **Five segments complete**, order matches priority (subject first)
- [ ] **Reproducibility test**: another person holding this prompt can reproduce
      similar composition and lighting (tacit knowledge 3)
- [ ] **Text test**: on-image text verbatim double-quoted; length and position
      clearly stated
- [ ] **Negative test**: all noun-style, 3–8, models with independent field put
      in independent field
- [ ] **Empty-word scan**: no `beautiful/masterpiece/8K/ultra-HD/extreme`
      no-information words
- [ ] **Pronoun scan**: no "it/this/that person"
- [ ] **Model check** (when text involved): per dialect table confirmed text
      rendering capability, and noted dialect table snapshot date
- [ ] (audit mode) named specific phrases in original prompt one by one, rewrite
      only one integrated draft (no multi-style branching), report language matches user

## Five-Segment Lexicon (Quickest Lookup)

| Segment | Common Phrasing |
|----|----------|
| canvas | "3:4 portrait, 1080x1440" |
| subject | "a short-black-haired woman in a black hoodie holding a book" |
| composition | "centered composition, generous negative space, low-angle hero shot" |
| style anchor | quote spec original: "flat editorial illustration, warm cream base, single coral accent" |
| text | `bold condensed sans-serif title "AI VIDEO 2026" top-left` |

## Failure Handling Table

| Symptom | Cause | Action |
|------|------|------|
| On-image text garbled | Model doesn't support text rendering | Rewrite with text-rendering-reliable model dialect; or step back: textless base image + post-typesetting |
| Subject different face every time | Subject description vague or pronoun used | Write fixed appearance feature list; multi-round editing based on previous image |
| Style drifts | Style anchor not in prompt | Each time copy spec style field wholesale, don't rely on memory |
| Elements too crowded | Composition segment missing whitespace statement | Add "generous negative space" and cut secondary elements |
| Negative not working | Written as imperative / no independent negative field | Change to noun list; models with independent field put in independent field (tacit knowledge 7) |
| Image "obviously AI" | Too clean, missing micro-details | Inject imperfections and texture (tacit knowledge 9) |
| Changed many spots, worse effect, can't explain why | Multiple variables changed at once | Roll back to previous version, change one slot at a time (tacit knowledge 5) |
| Hard light "retouched" to soft | Model default beautification override | Use `--style raw`-type parameters to suppress default aesthetics (tacit knowledge 10) |
| User asks "some artist's style" commercially | Copyright risk | Rewrite as describable features (brushwork/color/era), explain why (red line 3) |

## Delivery Criteria

- Artifact (write): prompt original one paragraph + five-segment annotated version
  (each marked `canvas/subject/composition/style/text`).
- Artifact (audit): checklist (each segment hit/miss, naming specific problem
  phrases in original prompt one by one) + **one integrated rewrite** (keep
  original intent, don't unilaterally change design direction) + before/after fix
  comparison + fix priority explanation; report language matches user's question
  language.
- Location: output directly in conversation (this skill doesn't write files).
- Integrity verification: five segments complete and order matches priority;
  on-image text verbatim double-quoted; negative constraints short noun list (no
  "no xxx" phrasing); no evaluation word pile and pronouns; style segment matches
  spec style field verbatim.
- When text needed: note used model family's text rendering check conclusion and
  dialect table snapshot date.

## References

- [model-dialects.md](references/model-dialects.md) — image model dialects and
  text rendering rules (including timeliness declaration and source grading; must
  reconfirm per "verification method" before executing)
- [visual-detail-lexicon.md](references/visual-detail-lexicon.md) — deep lexicon:
  three-layer lighting, composition, focal length perspective character, material
  micro-details, color schemes, still-image motion words, scene templates (check
  this first when writing prompts)
- [sources-and-methodology.md](references/sources-and-methodology.md) — tacit
  knowledge 1–10 source list, cross-validation matrix (≥2 sources before
  writing), and not-adopted content (reject marketing language)
