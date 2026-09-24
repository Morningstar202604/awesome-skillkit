---
name: frontend-component-lab
description: >-
  Scaffold production-grade React/TypeScript UI components wired to a design
  token system: component + CSS Modules + design-tokens.json, plus a review
  checklist that kills the classic LLM frontend sins (magic numbers, inline
  styles, untyped props, missing a11y). Use when the user asks to build a
  component / create a React component / component scaffold / UI component library
  / design system token / frontend design system / component spec. Do NOT use for
  pure image/design-mockup generation (use image-prompt-engineer) or for backend
  work.
license: Apache-2.0
compatibility: Outputs .tsx/.css/.json source files; user wires into their TS project themselves (no network, no npm install needed to generate).
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: design
  pattern: script
  tier: standard
  verified-date: "2026-09-20"
---

# Frontend Component Lab (Component Scaffold + Design System Token)

Turn a component requirement into a **runnable React/TS component + CSS Modules
+ design token file**, plus a review checklist of "the mistakes LLMs most often
make writing frontend". Adapted from mattpocock/skills' `frontend-design`
concept and ECC's `frontend-patterns` (React/Next conventions), trimmed to an
offline, zero-dependency scaffold + discipline layer.

Core judgment: **the model's frontend disease isn't "can't write"—it's "magic
numbers + inline styles + untyped props"**. This skill blocks these three problem
types directly with token files and strongly-typed skeletons.

> Red lines: default **dry-run** only prints what would be generated; `--write`
> saves; existing same-named files need `--force`. Zero network, no npm install.

## Input Checklist

| Input | Required | Notes |
|---|---|---|
| Component name | yes | PascalCase, e.g. `PricingCard` |
| props | no | comma-separated string-typed props |
| Token override | no | Pass a JSON to override default color/spacing/radius/font |
| Output directory | no | Default current directory |

## Pre-flight Checks

1. Is component name PascalCase? (script rejects lowercase-start)
2. Does the target project use CSS Modules? If not (Tailwind/Styled), after
   `--write` manually rename `.module.css` to corresponding approach—this skill
   doesn't assume the build tool.
3. Do design tokens need to inherit existing brand? If so, prepare an override
   JSON first.

## Workflow

```bash
# 1. Dry run: see which files would be generated
python3 scripts/scaffold_component.py --name PricingCard --props title,price,cta --out ./src/ui

# 2. Real generation
python3 scripts/scaffold_component.py --name PricingCard --props title,price,cta \
  --out ./src/ui --write

# 3. With brand token override
python3 scripts/scaffold_component.py --name PricingCard --tokens ./brand.json \
  --out ./src/ui --write --force
```

After generation, go through TSX per the checklist in
[references/frontend-sins.md](references/frontend-sins.md), filling `// TODO`
with real render logic.

## Delivery Criteria

- `design-tokens.json` is the **only** source of color/spacing/radius, components
  have **zero magic numbers**
- `XxxProps` interfaces complete, no `any`
- Every interactive element has `role` / `aria-*` or `data-component` anchor
- File compiles with tsc (passes `tsc --noEmit` in user project)

## Failure Handling Table

| Symptom | Root Cause | Action |
|---|---|---|
| Component name rejected | Not PascalCase / contains non-letters | Change `--name` to a valid name |
| Existing file not overwritten | Default idempotent | Add `--force` |
| Color still default blue | Didn't pass token override | Prepare override JSON and pass `--tokens` |
| CSS not recognized | Project doesn't use CSS Modules | Manually change styling approach |
| a11y missing role | TODO not filled | Fill interactive semantics per sins checklist |

## References

- Frontend "eight sins" review checklist: [references/frontend-sins.md](references/frontend-sins.md)

## Pipeline Position

- Upstream: `design-brief-interpreter` (translates vague need into design spec)
- Downstream: `layout-spec-auditor` (audits output against platform layout spec)
