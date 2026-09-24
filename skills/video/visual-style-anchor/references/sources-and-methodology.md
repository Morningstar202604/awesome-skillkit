# Methodology sources and acknowledgements

## Main sources

| Source | License | Methodology points borrowed |
|------|--------|------------------|
| [agentara/skills — video-storyboard](https://github.com/agentara/skills) | see its repo | The discipline of treating character identity constraints and character-sheet assets (character sheet / turnaround / casting reference) as generation prerequisites |
| This repo's ai-baby-podcast (viral-entertainment pack) | Apache-2.0 (original to this repo) | The seven-piece character-card set, locked seed/voice, drift audit every 10 takes, and the practice of **never regenerating the character from text** (only extend from the finalized reference image) come from that skill's proven references/character-consistency.md, generalized here |
| Community consensus | — | "Copy-paste the identity line, no rewriting," "no negative prompts," and "do-not-change lists" are common practices cross-validated across multiple open-source projects |

## Generalization notes

This skill abstracts ai-baby-podcast's discipline specific to a "single cute creature character" into
a general manual for any character: it removes the baby/creature-specific visual formulas, keeps the
four-layer skeleton of "fixed description, reference-first, drift audit, variation mechanism," and adds
a voice-consistency dimension.

## v2.0 research sources (2026-09-21, domain tacit-knowledge reinforcement)

All four "domain tacit knowledge" items in SKILL.md v2.0 come from the public sources below (cited
after multi-source cross-validation; unsourced pseudo-precise statistics are dropped):

| Tacit-knowledge item | Source | What is trusted |
|------|------|----------|
| 1. The physical mechanism and cliché-ification of teal-and-orange | filmit.io "Teal & Orange Explained: Why Every Hollywood Movie Looks the Same"; Creative Comment "Beyond the Teal"; multiple Chinese color-grading analyses (color-code blog), consistent across sources | Skin tones across all ethnicities fall in the orange range; teal is the complementary color that creates depth; industrialized in 2007 (digital cameras + Resolve LUTs), became a standard in 2012, a cliché by 2020; differentiation comes from subject matter and lighting structure |
| 2. Correct before creative, leave headroom | Colorist practical guides, consistent across sources (weddingfilmphotography grading guide, Airframe Media grading tutorial) | The three-stage order: correction → matching → creative; LUT opacity 50-70% (30-80% range cited); only push shadows, don't touch midtones; cap skin-tone saturation; "pushing green or magenta into skin reads as sickly/forced" (weddingfilmphotography) |
| 3. Color-temperature dictionary | A general vocabulary of color in narrative grading (consistent across sources); classic examples (The Matrix monochrome green, Moonlight adjacent neon, The Grand Budapest Hotel pastels) | Warm = nostalgic/intimate, cool = distant/tense; high saturation + lifted blacks = commercial feel, low saturation + crushed blacks = cinematic feel |
| 4. Consistency beats beauty | Colorist consensus ("inconsistent skin tones across shots immediately exposes an amateur") is isomorphic with the character-consistency discipline | The anchor is a contract, not a reference; quote it verbatim, no rewriting |
| 5. Accent-color scarcity (SKILL.md red line 5) | The 60-30-10 rule (originated in interior design, collected in Figma's official resource library "Types of color palettes") | The accent color is unique and reserved for the focal object only |

**Trust discipline**: only cite principles that have a clear source and are consistent across multiple
sources; single-source precise percentages are never trusted and are replaced with qualitative statements.
