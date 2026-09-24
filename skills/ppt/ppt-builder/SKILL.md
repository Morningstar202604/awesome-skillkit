---
name: ppt-builder
description: >
  Build presentation decks: structured outline, per-slide content spec, and a
  real .pptx file via bundled script (with graceful markdown fallback). Use
  when the user asks to make a PPT / build a presentation / write slides /
  create slides / make a deck / prepare a presentation about X / PowerPoint /
  presentation design / deck. Do NOT use for Word documents,
  spreadsheets, or PDF forms.
license: Apache-2.0
compatibility: Optional python3 with python-pptx for .pptx export; fallback needs nothing.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: office-productivity
  verified-date: "2026-08-26"
---

# PPT Builder (Brief → Presentation)

Produces two things: a per-slide content spec (JSON), and — when python-pptx is available — the real .pptx rendered from it. The spec is the single source of truth; rendering is just mechanical execution.

## Input Checklist

| Input | Required | Default | Notes |
|---|---|---|---|
| Topic | Yes | — | What this PPT should argue or explain |
| Audience | No | General business | Decides tone and depth |
| slide_count | No | `10` | Including the cover and closing slide |
| Style | No | Clean business | e.g. academic defense / fundraising pitch / teaching courseware |

When the topic is missing, ask once:

> Please give the PPT topic and purpose (who is the audience). Optionally tell me: the slide count (default 10),
> the style (defaults to clean business), and whether you already have an outline or asset files.

## Pre-flight Self-check

```bash
python -c "import pptx; print('pptx-ok')"
```

- Prints `pptx-ok` → enable .pptx export (step 3a).
- ModuleNotFoundError → take the markdown path (step 3b). Tell the user in one sentence: running `pip install python-pptx` next time enables direct .pptx export. Do not install on your own unless the user explicitly agrees.

## Workflow

### Step 1: Build the Outline

Organize the argument in this order (not a list of topics): a hook opening (a question or a counter-intuitive
fact) → the global map → 2–3 core arguments (each with evidence/a case) → rebuttal or boundaries → a call to action.

Expected: a numbered outline, each slide stating exactly one argument.

### Step 2: Per-slide Spec

Write `slides_spec.json`:

```json
{
  "deck_title": "...",
  "slides": [
    {"title": "...", "bullets": ["<=18 chars each, at most 5"], "notes": "the spoken version of the script", "visual": "chart/screenshot/whitespace cue"}
  ]
}
```

Rules: title ≤ 16 chars and carries a point (not an empty word like "introduction"); notes must be complete sentences you can read aloud.

### Step 3a: Render the .pptx (when pptx is available)

```bash
python "<skill-dir>/scripts/make_pptx.py" slides_spec.json deck.pptx
```

Expected: exit 0 plus `wrote deck.pptx (N slides)`. Exit 3 means python-pptx is missing
→ switch to step 3b and tell the user why. Exit 2 means the spec is invalid — read the printed error,
fix slides_spec.json, and rerun.

### Step 3b: Fallback Deliverable

Output `deck_outline.md`: H1 is the deck title, one H2 per slide, with bullets and that slide's speaker notes. The user can paste it into any tool.

### Step 4: Self-review Before Delivery

Check: each slide makes only one argument; no slide has over 5 bullets; each slide's visual has a concrete cue;
the total notes word count supports the target duration (about 1 minute/slide). On finding a violation, fix the spec and re-render; do not hand-patch prose.

## Failure Handling Table

| Symptom | Likely cause | Action |
|---|---|---|
| Script exits 2 and points at slide N | The spec violates the schema | Fix that slide's fields per the step 2 structure |
| Script exits 3 | python-pptx missing | Switch to step 3b and give the pip hint |
| A bullet repeatedly exceeds 18 chars | The outline is too dense | Split that slide into two and re-render |
| The user wants a company template applied | v1 has no styling customization | Deliver the spec + outline.md for manual styling changes |

## Delivery Standards

Success = `deck.pptx` (opens, slide count matches the spec) or `deck_outline.md`, plus `slides_spec.json`; report all three paths with the slide count. Missing any one means it is incomplete — say so honestly.

## References

- `scripts/make_pptx.py` — run directly (execute, do not read); validates the spec first, then renders
- [layout-and-chart-rules.md](references/layout-and-chart-rules.md) — the layout and chart rules lexicon: font-size hierarchy table, three information-density tiers, the chart-selection decision tree (which data pairs with which chart), alignment grid, color-contrast baselines, and a negative list (consult when setting layout specs and choosing charts)
