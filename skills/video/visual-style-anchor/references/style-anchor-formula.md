# Style Anchor Formula

> The style anchor is the visual DNA of the whole film: one page, five slots; every generation cites
> the style slot verbatim. This document gives finer ways to fill each slot, with examples.

## Slot 1: Color palette

Three-layer structure:

```text
Dominant color ×1 (~60% of frame): the ambient base
Accent color ×1 (~10%): only for the focal object (protagonist, product, button)
Supporting colors ×1-2 (~30%): transitions and layering
```

- Every color must carry a HEX value (`#0E1A2B`); "deep blue" is a feeling, not a spec
- How to sample colors from a reference image: screenshot → eyedropper → record the values of 3 key regions (sky/subject/shadow)
- Consistency rule: the fewer times the accent color appears, the more premium it feels; ≤3 dominant colors across the whole film; when distributing to multiple platforms, don't change the colors of the same anchor

## Slot 2: Lighting

Three variables:

| Variable | Options | Example |
|------|------|------|
| Light type | natural / practical / studio | practical = light sources visible in frame (neon, desk lamp, screen) |
| Time of day | dawn / noon / golden hour / blue hour / night | time of day sets the color-temperature base |
| Contrast | high-contrast / soft / flat | high contrast = drama, soft = gentle, flat = document feel |

One assembled example: `night exterior, practical neon signage as key light, high contrast with cyan-orange split`

## Slot 3: Materials

- List 3-5 surfaces that recur throughout the film: `wet reflective asphalt / matte plastic / glass storefront`
- The do-not list matters just as much: write out the "textures forbidden" (e.g. flat color blocks, low-saturation matte)—
  the generation model's default texture is often not what you want, and negative constraints lock the picture better than positive descriptions

## Slot 4: Era

- State the decade and the "era markers": objects appearing on screen must be ≤ the story's era
- Positive phrasing: `modern city, 2020s`; negative phrasing: `film-wide ban: CRT TVs, film grain, flip phones`
- Era markers are a high-frequency anachronism zone—viewers have zero tolerance for period slips

## Slot 5: Medium

Pick one by project type and reuse the whole phrase:

| Type | Medium phrase |
|------|----------|
| Narrative / cinematic | `cinematic live-action, 35mm depth-of-field feel, subtle handheld breathing` |
| Product / commercial | `product-commercial gloss, clean studio backdrop, crisp reflections` |
| Animated / stylized | `anime cel style, flat shading with rim light` |

## Full example (rainy-night convenience-store short)

```markdown
# Style Anchor: rainy-night convenience store
## Palette
Dominant #0E1A2B / Accent #FF6B35 / Supporting #7FD1C9 (teal)
Rule: accent color only on story props and the protagonist's highlights.
## Lighting
Night exterior, practical neon as key light, cyan-orange contrast, highlights allowed to blow out.
## Materials
Wet reflective asphalt, matte plastic, glass storefront. Forbidden: flat color blocks, low-saturation matte.
## Era
2020s city. Film-wide ban: CRT TVs, film grain.
## Medium
cinematic live-action, 35mm depth-of-field feel, subtle handheld camera breathing.
```

## Acceptance

- All five slots present + colors have HEX + materials have a do-not list + medium picked from the three
- ≤60 lines: more than that means you're writing a prompt, not an anchor—the fine content belongs at the prompt layer
