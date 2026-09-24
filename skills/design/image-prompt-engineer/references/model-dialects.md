# Image Model Dialect Notes / Image Model Dialects (VERIFY BEFORE USE)

> ⚠️ **Time-sensitivity notice**: image models update at a **monthly** cadence (model names/capabilities/pricing all change).
> This file is a 2026-09-14 web research snapshot; before executing, re-confirm per the "verification method" column
> (SKILL-STANDARD-v2 precept 7 / precept 8). Source grading: 🟢 official · 🟡 third-party · 🔵 community.

## Cross-model hard rules (check this first before writing prompts)

1. **Text rendering iron rule**: if the image needs readable text (headings/labels/chart axes/OG copy) → choose
   the GPT Image family; Gemini-family image models basically do not render readable text. 🟡🟢
2. **Transparent background (icons/logos)**: if RGBA alpha is needed, choose a model with native transparency support
   (e.g. GPT Image 1.5); not all image models can output an alpha channel. 🟡
3. **Natural language full sentences** beat keyword stuffing—universal across all modern image models. 🟡
4. **Wrap text in verbatim double quotes** + use the "change 'old' to 'new'" pattern for edits + drastic character count
   changes will break layout. 🟡
5. **Negative constraints should be noun-style**: `blurry, watermark` rather than `no blur`. 🟡

## Model selection quick reference

| Need | First choice | Rationale |
|------|--------------|-----------|
| Photorealistic scenes/atmosphere | Gemini 3.x Flash Image family | Good depth and environmental complexity; does not render text |
| Posters/infographics/OG images with text | GPT Image 2 family | Usable text rendering (including multilingual) |
| Batch style exploration (same composition, multiple colors) | GPT Image 2 family | Native multi-variant in a single call |
| Transparent icons/logos | GPT Image 1.5 | Native RGBA |
| Quick draft iteration | Flash tier | Free quota / low latency |
| Open-source self-hosted | SD family / Flux family | Full control but weaker text rendering; pair with post-layout |

*Verification method: search each vendor's latest "image model docs"; model IDs drift with versions—
check the official model list API before executing.*

## Photography and composition vocabulary (cross-model universal) 🔵

- **Film/lens**: Kodak Portra 800 (portrait skin tones), Fuji Velvia 50 (high-saturation landscapes),
  50mm f/1.4 (shallow depth of field), 24mm wide angle, tilt-shift (miniature effect)
- **Lighting**: Rembrandt lighting (triangle light), soft diffused (soft studio light),
  rim/backlight (rim light), volumetric (volumetric fog feel)
- **Composition**: rule of thirds, centered symmetry, generous negative space,
  bird's-eye / low-angle hero shot
- **Style naming**: if you can't name the style, describe features—"visible brushstrokes, thick paint
  texture" beats "painterly style"

## Universal fallback

When dialect is uncertain: **five-part structure + double quotes around text + noun-style negatives**, skip model-specific parameters. Writing the wrong specific marker is worse than not writing one.

## Audit vs dialect

The five-part structure is the cross-model invariant; model selection and specific parameters are verified manually against this file. Two layers of checking, neither may be skipped.

## Change maintenance

When a dialect is found to be invalid: update the corresponding entry + the snapshot date at the top; PRs go through normal gates.
