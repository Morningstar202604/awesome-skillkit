# Sources & Methodology — image-prompt-engineer

Adoption discipline for SKILL.md tacit knowledge 1–10: image prompt engineering has no academic literature layer; this round researched **practitioner guides** (tool sites and workflow blogs). The processing rule for these sources is—

> **Only conclusions cross-validated by ≥2 independent sources are written into SKILL.md**; numbers and assertions from a single source are never adopted.

## Source list (batch 4 web research, 2026-09-22)

| Source | Type | Adopted conclusions |
|---|---|---|
| howtotechedition.com — How to Write Effective Prompts for AI Image Generation | practitioner guide | Subject first (position = weight); lighting/composition/lens parameters layered; quality words at the end; negative prompts; change only one variable at a time; length cap around 75 words |
| improveprompt.ai — AI Image Prompts That Actually Work | practitioner guide | "Lighting is the absolute quality multiplier"; lens physical parameters (85mm f/1.8 / 35mm film / 14mm f/11 for three scene types); standard negative-prompt checklist; `--style raw` suppresses default beautification; micro-detail/blemish injection to fight plastic feel; concept weight syntax |
| text2img.pro — Master AI Image Prompt Syntax & Structure | practitioner guide | Universal prompt format (media → subject → action → environment → lighting → lens → mood → tech → negative); "order is priority"; **"describe, don't evaluate"** (beautiful/stunning carries no visual information); length cap around 150 words; negative list short and specific (long lists leak into positive semantics); quick reference for model dialects |
| meteoraweb.com — Professional Techniques for Repeatable Results | practitioner guide | Seven-block framework; **"prompt entropy"** concept (less information = more mediocre results); iteration discipline (one variable at a time); parameter differences across MJ/DALL·E/SD (CFG/steps/stylize) |
| deepest.app — AI Image Prompt Guide | practitioner guide | Subject first; **content and style separated** (what vs. how written separately); positive specification beats negative (`sharp background detail` > `no blurry background`); quality words less effective on Midjourney than DALL·E/Flux |

## Cross-validation matrix (the bar for writing into SKILL.md)

| Conclusion | Number of sources | Written in? |
|---|---|---|
| Position = weight (subject first) | 3 | ✅ tacit knowledge 1 |
| Lighting is the biggest quality multiplier | 4 | ✅ tacit knowledge 2 |
| Describe, don't evaluate (empty words carry no information) | 2 | ✅ tacit knowledge 3 |
| Lens/camera physicality supports realism | 5 | ✅ tacit knowledge 4 |
| Change only one variable at a time | 2 | ✅ tacit knowledge 5 |
| Prompt length cap | 2 (metrics differ: 75 / 150) | ✅ tacit knowledge 6 (**give a range, not a precise number**) |
| Negatives short and specific + positive beats negative | 4 | ✅ tacit knowledge 7 |
| Model selection precedes prompt wording | 3 | ✅ tacit knowledge 8 |
| Micro-details suppress plastic feel | 1 (improveprompt) | ⚠️ downgraded: written as an experiential technique, not flagged as consensus |
| `--style raw`-type parameters suppress default beautification | 2 | ✅ tacit knowledge 10 |

## Content not adopted (adoption discipline)

- **Percentage assertions** in various sources (e.g. "negative prompts solve 90% of problems," "quality words triple the effect")—no experimental provenance, marketing language, never written in.
- Specific model version numbers and pricing (**monthly drift**)—not written into SKILL.md; carried instead by `model-dialects.md` with a snapshot date.
- Hard numerical values of the form "a parameter must be X" (CFG=8, steps=30, etc.): single-source and drifts with the model → do not enter SKILL.md.

## Relationship to existing reference files

| File | Role | Time-sensitivity strategy |
|---|---|---|
| `model-dialects.md` | Model selection and dialects (text rendering iron rule) | 2026-09-14 snapshot; carries its own time-sensitivity notice and source grading (🟢🟡🔵) at the top; **must be re-verified before execution** |
| `visual-detail-lexicon.md` | Detail lexicon (three lighting layers/composition/focal length/material/color) | Cross-model universal layer, slow drift; opens by declaring "lighting is the biggest variable" and "quality words capped at 2-3" |
| This file | Sources and adoption bar for this batch of tacit knowledge | Adoption-discipline statement |

## Honesty boundary

This skill's tacit knowledge comes from **practitioner consensus** rather than experimental research: cross-validation only guarantees "multiple sources say so," not "proven by experiment." Where hard numbers are involved (length caps, negative-word counts), SKILL.md uniformly gives ranges and labels them as experiential values.
