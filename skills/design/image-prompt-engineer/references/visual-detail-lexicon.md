# Visual Detail Lexicon: Lighting · Composition · Focal Length · Material · Mood (visual-detail-lexicon)

> Look up this table by slot when writing image prompts. **Lighting changes an image more than any other slot**—same subject, swap the lighting = swap the mood.
> Iron rule: replace abstract adjectives with concrete nouns (`beautiful` → `soft rim light on hair`); quality words (8K/masterpiece) capped at 2-3—piling more dilutes weight.
> Model differences see [model-dialects.md](model-dialects.md); this table is the model-agnostic detail layer.

## Table of Contents

- [1. Lighting Lexicon (three layers)](#1-lighting-lexicon-three-layers)—natural light / studio light / light effects and mood
- [2. Composition Lexicon](#2-composition-lexicon)—shot size / camera angle / composition rules
- [3. Focal Length and Lens Feel](#3-focal-length-and-lens-feel-one-word--one-perspective-personality)—one word = one perspective personality
- [4. Material and Micro-Details](#4-material-and-micro-detailssubstitutes-for-beautiful)—substitutes for "beautiful"
- [5. Color Palette Words](#5-color-palette-words)
- [6. Mood and Emotion Words](#6-mood-and-emotion-words-mood-slot)—mood slot
- [7. "Motion" Words in Static Images](#7-motion-words-in-static-images-quiet-but-with-wind)—quiet, but with wind
- [8. Negative Prompts and Restraint](#8-negative-prompts-and-restraint)
- [9. Scene Templates](#9-scene-templates-edit-four-brackets-and-go)—edit four brackets and go

## 1. Lighting Lexicon (three layers)

### Natural Light

| Term | Description | Effect & emotion | When to use |
|------|-------------|------------------|-------------|
| `golden hour` | Golden hour (low-angle warm light around sunset) | Warm, soft, the most flattering portrait light | Portraits, landscapes, nostalgia |
| `blue hour` | Blue hour (deep blue sky glow after sunset) | Cool, serene, urban feel | City night scenes, atmospheric shots |
| `overcast diffused light` | Overcast diffused light | Even soft light, no hard shadows | Products, skin tone reproduction |
| `dappled light through leaves` | Dappled light filtering through leaves | Summer, languid, cinematic | Outdoors, youth themes |
| `harsh midday sun, strong shadows` | Harsh midday sun with strong shadows | Power, documentary, desert feel | Tough-guy style, street |
| `moonlight, cool blue tones` | Moonlight, cool blue tones | Solitude, suspense | Night scenes, horror |

### Dramatic Light

| Term | Description | Effect & emotion | When to use |
|------|-------------|------------------|-------------|
| `chiaroscuro` | Chiaroscuro (Rembrandt-style strong contrast) | Oil painting feel, mysterious | Portraits, still life |
| `Rembrandt lighting` | Rembrandt lighting (one side of face lit, triangular patch on the other cheek) | Classic portrait standard | Male portraits, composed feel |
| `rim lighting / backlit` | Rim lighting / backlit | Subject edged with glowing border, separated from background | Hair detail, atmosphere |
| `volumetric lighting, god rays` | Volumetric light / Tyndall beams | Sacred, epic | Churches, forests, ruins |
| `silhouette` | Silhouette | Shape-driven narrative, blank-space imagination | Sunset, minimal |
| `lens flare` | Lens flare | Cinematic, imperfect realism | Spotlight shots |
| `[color] gel lighting` | Colored gel lighting (e.g. `teal and orange gel`) | MV feel, cyberpunk | Fashion, music |

### Studio and Artificial Light

| Term | Description | Effect & emotion | When to use |
|------|-------------|------------------|-------------|
| `studio lighting, three-point setup` | Three-point lighting setup | Commercial standard, clean | Products, ID photos |
| `softbox / octabox` | Softbox / octabox | Large-area soft light, refined skin | Beauty, e-commerce |
| `neon lighting, colorful reflections` | Neon light + colorful reflections | Nightlife, cyberpunk | Street snaps, posters |
| `candlelight, warm flickering` | Candlelight, warm flicker | Intimate, classical | Restaurants, period drama |
| `bioluminescent glow` | Bioluminescent glow | Fantasy, deep sea | Concept art |
| `practical lights (screen glow, lamp)` | In-frame practical lights | Realism, tech feel | Late-night office, hacking |

## 2. Composition Lexicon

| Term | Description | Effect | When to use |
|------|-------------|--------|-------------|
| `rule of thirds` | Rule of thirds | Foolproof, never wrong | Default choice |
| `centered composition, symmetrical` | Centered, symmetrical | Solemn, satisfyingly ordered | Architecture, Wes Anderson style |
| `negative space on the left` | Negative space on the left | Leaves room for headline/copy | Posters, banners |
| `leading lines` | Leading lines | Eye drawn to subject | Streets, bridges, corridors |
| `framed through the doorway` | Frame within a frame | Peeping feel, layered | Narrative scenes |
| `foreground subject, background bokeh` | Sharp foreground, blurred background | Subject emphasis | Portraits, food |
| `bird's eye view / overhead` | Bird's-eye / overhead view | Order, god's-eye perspective | City flat lay, Flat Lay |
| `worm's eye view / low angle` | Worm's-eye / low angle | Subject looms large, imposing | Heroes, architecture |
| `Dutch angle` | Dutch angle | Uneasy, turbulent | Suspense, conflict |
| `over-the-shoulder` | Over-the-shoulder | Conversational immersion | Two-person scenes |
| `clean sky area for headline` | Clear sky area reserved for headline | Typography-friendly | Ad composites |

## 3. Focal Length and Lens Feel (one word = one perspective personality)

| Term | Description | Perspective personality | When to use |
|------|-------------|------------------------|-------------|
| `16mm wide angle` | 16mm wide angle | Edge stretch, scene-encompassing | Environmental narrative, interiors |
| `35mm lens, documentary feel` | 35mm documentary | Close to human eye, natural | Street, everyday life |
| `50mm lens` | 50mm standard | Neutral, no distortion | Universal default |
| `85mm portrait, creamy bokeh` | 85mm portrait | No facial distortion + creamy bokeh | Main portrait lens |
| `200mm telephoto, compressed perspective` | 200mm telephoto | Space compression, background blurred into color blocks | Street candid, animals |
| `macro lens, extreme detail` | Macro lens | Magnified to visible texture | Water droplets, insects, jewelry |
| `tilt-shift miniature effect` | Tilt-shift miniature | Real city becomes model-like | Cities, creative |
| `fisheye, distorted edges` | Fisheye, distorted edges | Exaggerated edge bending | Skateboarding, extreme sports |
| `anamorphic lens, oval bokeh` | Anamorphic widescreen | Oval bokeh + horizontal blue-line flares | Maximum cinematic feel |
| `shot on [Hasselblad / Sony A7III]` | Camera body reference | Implies color science and texture | Realistic portraits, products |

## 4. Material and Micro-Details (substitutes for "beautiful")

Material words tell AI what the surface is "made of"—this is the dividing line between photographic feel and plastic feel:

- Skin: `porcelain skin texture with visible pores` / `freckles, fine peach fuzz`
- Metal: `brushed aluminum` / `micro scratches on metal` / `oxidized copper patina`
- Wood: `weathered oak, visible grain` / `cracked lacquer`
- Fabric: `linen with natural wrinkles` / `silk sheen` / `frayed denim edges`
- Paper: `paper fibers` / `letterpress debossing` / `watercolor bleed at the edges`
- Glass: `condensation droplets` / `refractions and caustics`
- Air: `dust motes in air` / `volumetric fog` / `steam rising`
- Aging: `fine film grain` / `subtle chromatic aberration` / `light leaks`
- Ornament: `intricate filigree` / `hand-stitched seams` / `enamel chips`

**Stacking formula** (stack four layers at once—the more concrete, the more obedient):
`material (brushed aluminum) + era (Art Deco 1920s) + palette (muted teal and copper) + environment (industrial loft with tall windows)`

## 5. Color Palette Words

| Term | Description | Mood |
|------|-------------|------|
| `warm palette, amber and terracotta` | Warm: amber + terracotta | Warm, earthy |
| `cool blue and silver tones` | Cool: blue + silver | Tech, detached |
| `desaturated, muted tones` | Desaturated, low chroma | Desolate, literary |
| `high saturation, vivid colors` | High saturation, vivid | Energetic, e-commerce |
| `monochromatic, shades of blue` | Monochromatic | Minimalist, conceptual |
| `pastel palette, soft pinks and creams` | Soft pastels | Girly, healing |
| `neon palette on black` | Neon on black | Nightclub, cyberpunk |
| `teal and orange grade` | Teal-orange color grade | Hollywood blockbuster default |

## 6. Mood and Emotion Words (mood slot)

`serene` (serene) · `dramatic, intense` (dramatic tension) · `melancholic, nostalgic` (melancholic nostalgia) · `mysterious, eerie` (mysterious unease) · `romantic, warm` (romantic warmth) · `futuristic, cold` (futuristic cold) · `whimsical, dreamlike` (whimsical dream) · `gritty, raw` (gritty realism)

## 7. "Motion" Words in Static Images (quiet, but with wind)

Add verb-like modifiers to a static image and the frame instantly comes alive:

- `windswept hair` (hair blown by wind)
- `fabric billowing` (fabric billowing)
- `water splashing, frozen mid-air` (water splashing, frozen mid-air)
- `birds circling overhead` (birds circling overhead)
- `steam rising from the cup` (steam rising from the cup)
- `leaves scattered mid-fall` (leaves scattered mid-fall)

## 8. Negative Prompts and Restraint

- Exclusions use `--no text, watermark, people, blur` (Midjourney) / `negative_prompt` field (SD/Flux)
- Quality words capped at 2-3: `highly detailed` + `professional photography` is enough; piling `8K masterpiece award-winning ultra` together dilutes weight
- State what you want positively: `clear sky` rather than `sky with no clouds` (models tend to miss "no")

## 9. Scene Templates (edit four brackets and go)

```
Portrait: [age feature] [hairstyle], [material skin detail], Rembrandt lighting, 85mm creamy bokeh, rule of thirds --ar 4:5
Product: [product], [material word], softbox studio lighting, isolated on [background], sharp focus, e-commerce ready --ar 1:1
Landscape: [location], [time word golden/blue hour], [weather], wide 16mm, leading lines, volumetric god rays --ar 16:9
Poster: [theme], [style word], centered composition, negative space top for headline, [palette] --ar 2:3
Avatar: professional headshot, [expression], plain light gray background, soft studio light --ar 1:1
```
