---
name: frontend-design-director
description: >-
  Act as a frontend design director who pulls AI-generated UI away from templated
  defaults toward opinionated, brief-specific design. Runs a two-pass workflow -
  first produce a named design-token plan (palette, type, layout concept, unique
  principle) without touching code, audit that plan against an AI-tell checklist,
  then implement with restrained motion and typographic care, and close with
  self-critique. Use when the user asks for frontend design / page design / UI
  design / landing page / visual design / website page / page beautification. Do
  NOT use for image or poster generation (design-brief-interpreter owns that),
  nor for backend or non-visual code tasks.
license: Apache-2.0
compatibility: Pure prompt-based; no runtime deps.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: design
  pattern: single-task
  tier: standard
  verified-date: "2026-09-16"
---

# Frontend Design Director

AI-generated frontend pages are universally "safe but mediocre": technically
flawless, visually from the same template—swap the logo and it could hang on any
product. This skill works like a design director: **design plan first, code
second**, using a two-pass workflow (design plan → default-taste self-check →
implement → self-critique) paired with an AI-tell checklist to pull output from
"the default every brief gets" to "designed only for this brief". Core judgment
in one sentence: **is this a choice made for this brief, or a default every
brief would get?**

## Input Checklist

| Input | Required | Notes |
|------|------|------|
| brief | yes | what product/page, what action should visitors take ultimately |
| Topic domain | yes (ask if missing) | industry, users, content tone—the only source of visual language |
| Platform | yes (ask if missing) | Web desktop / mobile / H5, determines breakpoints and interaction assumptions |
| Constraints | no | brand colors, specified fonts, elements to preserve, existing page style |

When inputs are missing, ask all at once (no multi-round drip):

> Please add: 1) what product, for whom; 2) tone you hope to convey (one word is
> fine); 3) which platform; 4) existing constraints like brand colors/fonts.

Minimum runnable input = brief + topic direction + platform. Once all three are
there, start; if tone uncertain, give 2 directions for user to pick first; with
only brief, must ask first, don't start.

## Pre-flight Checks

This skill is pure prompt-driven: no runtime dependencies, endpoints, or env
vars. Only self-check:

```bash
test -f references/ai-design-tells.md && echo OK
```

Expected output `OK`. Failure means skill package incomplete: continue using
built-in judgment for self-check, and note checklist file missing in delivery.

## Workflow

Four-step overview (expected and failure fallback per step):

| Step | Action | Expected Output | If Fails |
|------|------|----------|--------|
| 1 design plan | distill topic, produce token system | four-field plan table | can't distill topic → return to input checklist and ask all at once |
| 2 default-taste self-check | go through plan against checklist line by line | ≥1 default replaced, with record | almost all hit → return to step 1 to redo plan |
| 3 implement | code per revised plan | code matches token and motion/typography discipline | implementation drifts → stop and reread plan, don't improvise |
| 4 self-critique | screenshot review, strip one accessory | cut 1 decoration and record | nothing to cut → suspect insufficient rigor, re-review whole |

### Step 1: First Pass · Design Plan (No Code)

First distill topic from brief: what is this industry, these users, this content?
Visual language comes from the topic—what materials, colors, density, rhythm in
the topic world can be borrowed (a ceramic brand and a quant trading terminal
should look nothing alike). When distilling, ask three questions:

1. **Material and tactile feel**: what is this industry's "physical presence"—
   paper, metal, wood, code, water? Which direction does the page texture lean?
2. **Usage state**: what emotion and scenario is the user opening it in (tense/
   casual/professional/leisure)? This determines information density and page
   rhythm.
3. **Ready-made assets**: visual content the material itself brings—numbers,
   objects, jargon, place names—which can go directly into the design.

If topic can't be distilled, return to input checklist and ask back; **don't
invent a "generic beautiful"**.

Produce token system, four fields, none missing:

| Field | Requirement | Counterexample (failing) |
|------|------|------|
| Palette | 4-6 named hex, names related to topic | only "primary #3B82F6", a name universal to any project |
| Typography | at most two families, division of labor in one sentence (who does titles, who does body) | "use sans-serif" / can't explain why one or two families |
| Layout concept | one sentence + ASCII wireframe, state main alignment | only says "top-bottom structure, then three columns" |
| Unique principle | one sentence, explains why this design doesn't look like others | "minimal grand, high-end" |

Example (topic: community used bookstore homepage):

| Field | Example Value |
|------|------|
| Palette | dusk paper #F3EBDD · smoke ink #2B2723 · spine green #3E5641 · seal red #B5442D |
| Typography | titles use serif family (bookish, can carry large sizes); body uses sans-serif (lists and price tags need clarity) |
| Layout | asymmetric two columns: left 2/3 vertical bookshelf list, right 1/3 sticky-note sidebar; body left-aligned |
| Unique principle | whole page like flipping through an annotated book: margins leave annotation room, palette only uses colors actually found in a bookstore |

```text
+--------------------------------+--------------------+
|  dusk paper base · smoke ink large title (left-aligned)  |  sticky-note sidebar         |
|  this week's bookshelf — vertical list            |  (events/store cat/messages) |
|  each row: title · author · annotation slot      |  right margin whitespace as annotation area   |
+--------------------------------+--------------------+
|  seal red: only for "pick up in store" action                       |
+----------------------------------------------------+
```

Design plan uniformly outputs with the skeleton below (no extra beyond four
fields):

```markdown
## Design Plan
- subject:   one-sentence topic: what industry, for whom, content tone
- palette:   color name #HEX × 4-6 (names related to topic, reject primary/secondary)
- type:      title family:… (responsible for what); body family:… (responsible for what)
- layout:    one-sentence layout + main alignment + mobile assumption
- principle: one-sentence unique principle
```

### Step 2: Default-Taste Self-Check (Change Plan, Not Code)

Go through the whole design plan against [references/ai-design-tells.md](references/ai-design-tells.md)
line by line, each time only asking that one question: **"is this a choice made
for this brief, or a default every brief would get?"**

- Is a choice → keep, and keep that reason.
- Is a default → change it, write what it was changed to.

Expected: at least find 1-2 defaults and replace. If almost all hit, the plan
itself is a template, return to step 1 and redo, don't patch on a bad plan.
Self-check record (what hit, what changed, why) must land in the deliverable,
format as:

| Checklist Hit | Judgment | Action |
|----------|------|------|
| everything is rounded-corner cards | default | change to container-free zoning, rely on whitespace and thin dividers |
| all-caps small eyebrow labels | default | delete, merge eyebrow info into body first sentence |
| always centered alignment | keep | only opening sentence centered ("title page" feel comes from topic), rest left-aligned |

### Step 3: Second Pass · Implement

Write code per the self-checked plan. Implementation order matters:

1. First build skeleton—layout grid and breakpoints; at this stage only colors
   and fonts already named in the token table may enter.
2. Then do the core element or moment corresponding to the "unique principle"—
   it's the page's memory point, resources lean toward it.
3. Finally fill in regular components (nav, footer, form), regular components
   stay quiet, don't steal the core element's show.

Two hard disciplines:

- **Restrained motion**: only give **one** choreographed moment on page load or
  user action, everything else stays quiet. Forbid every element fading in and
  floating up, forbid every card having the same hover animation. User-action
  motion (expand, submit, confirm) is prioritized—they answer "what just
  happened".
- **Typographic detail**: body line length <80 characters; line-height hierarchy
  follows font size hierarchy (small text denser, large text looser: body about
  1.5-1.7 line-height, large titles can compress to 1.1-1.2); titles treated as
  visual elements—weight, size, spacing themselves participate in composition,
  not just content carriers; pick one technique (oversized type, cross-column,
  local whitespace, interlock with graphics) and use it fully, don't dabble
  everywhere. Also watch CSS selector specificity overriding each other
  (especially block spacing padding/margin canceled by component class names), a
  common generated-code accident.

Quality floor, unflashy but held: mobile usable, keyboard focus visible, respect
system "reduce motion" preference, body contrast meets standard. These not done
will fail; done doesn't need to be advertised.

### Step 4: Self-Critique

- If screenshot possible, screenshot after build and review in three layers:
  first squint at light/dark blocks (is overall tone right), then look at
  whitespace rhythm (is there breathing room), finally look at type (line length,
  hierarchy, alignment)—one screenshot beats a thousand tokens of self-description.
- **"Strip one accessory before leaving the house"**: cut one unnecessary decoration
  before delivery. Whichever is most eye-catching is which to scrutinize—if it's
  not on the "unique principle" track, cut it first.
- Write what was cut into delivery notes. Not cutting anything usually means
  review wasn't harsh enough.

## Delivery Criteria

| Deliverable | Passing Standard |
|--------|----------|
| token system table | palette 4-6 named hex, typography division, layout one sentence, unique principle one sentence, four complete, no "TBD" |
| ASCII wireframe | ≥1, annotated with main alignment |
| self-check record | hits item-by-item checkable: kept with reasons, changed with replacement |
| code/page | implemented per revised plan; responsive doesn't break; motion no more than "one choreographed moment"; line length and line-height match typography discipline |

Integrity verification: four deliverables missing any means incomplete; empty
self-check record counts as not executing step 2, return to redo.

Delivery order: design plan (token table + wireframe) and self-check record
output to user before code, default execute continuously without waiting for
confirmation; pause only when user asks for segmented confirmation. All
deliverables output directly in conversation, this skill doesn't write files.

## Failure Handling Table

| Symptom | Cause | Action |
|------|------|------|
| Brief too empty ("help me make a beautiful page") | topic domain completely missing | Return to input checklist and ask all at once; if user won't answer, propose 2 differentiated directions to choose, don't accept "whatever" |
| Client explicitly names some "AI-taste" style | brief explicitly specified default-taste features | Client's original words always win; say clearly you'll follow; in delivery notes note this feature came from client spec, don't pass off as your own choice |
| Palette all conflicts | topic color, brand color, accent color fighting each other | Return to topic and re-distill, cut to 1 main 1 secondary 1 accent; subtract, don't stack |
| Mobile breaks | only implemented by desktop width | Fix breakpoints first then discuss style; step 1 wireframe stage should have written mobile assumption |
| Self-check checklist almost all hits | plan itself is default template | Overthrow token system and redo step 1, don't patch on bad plan |
| Existing old page to redesign | Constraints didn't give current state | First read old page/screenshot, record existing brand assets in input checklist, then go through flow |

## References

- [ai-design-tells.md](references/ai-design-tells.md) — AI-taste design feature
  self-check list, used line by line in step 2
- [sources-and-methodology.md](references/sources-and-methodology.md) — methodology
  source and originality statement
