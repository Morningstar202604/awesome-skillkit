# Sources and Methodology

This skill is self-authored; its methodology skeleton is distilled from the following public materials (structural borrowing only, no text copied):

| Source | Type | What was borrowed | License/attribution |
|------|------|----------|-----------|
| [designskills](https://github.com/ArnavPuri/designskills) (ArnavPuri, MIT) | open-source skill library | The `design-context` first pattern—brand/audience/style context as shared parameters for all downstream skills, ensuring series consistency | MIT, structural borrowing with attribution |
| [Anthropic canvas-design](https://github.com/anthropics/skills) (official) | 🟢 official | The two-stage method "visual philosophy first → canvas execution"; anti-AI-slop discipline (minimal text, strong visual dominance, magazine-grade composition) | Official methodology cited with attribution |
| The division-of-labor perspective from the designskills full suite | open-source skill library | The three-stage chain division: spec (context) → generation (prompt) → evaluation (critique) | MIT, structural borrowing with attribution |

## Design decisions

1. **Spec sheet fixed at 7 fields**: purpose/platform/subject/style/palette/text/do-not—the fields are the auditable unit, more verifiable than free prose.
2. **Style anchors must be decidable**: adopting canvas-design's "philosophy first," but forced into
   3-5 decidable words—philosophy descriptions are for humans; decidable words are for models and audit scripts.
3. **Text listed one by one and word-capped**: on-image text is the #1 failure source for generative models; lock it to the minimum at the spec stage.

## v2.0 Research Sources (2026-09-21, domain tacit-knowledge reinforcement)

The four "domain tacit knowledge" items in SKILL.md v2.0 all come from the following public sources (cited after multi-source cross-validation;
unsourced pseudo-precise statistics are discarded):

| Tacit knowledge item | Source | Content adopted |
|------|------|----------|
| 1. Hierarchy hard currency (emphasizing everything = emphasizing nothing) | Robin Williams, *The Non-Designer's Design Book* (CRAP four principles); IEEE ProComm, *Elements of Visual Communication* (Melissa Clarkson); Gestalt psychology (proximity/similarity/figure-ground laws since Max Wertheimer); Affinity Studio design blog (three size tiers, squint test) | CRAP four principles, three-tier hierarchy gaps, proximity grouping, squint test |
| 2. Accent color scarcity | 60-30-10 rule (originated in interior design; cataloged in Figma official resource library *Types of color palettes*; consistently cited by multiple UI color guides) | 60/30/10 ratio, "the boldest color should be the rarest" |
| 3. Text budget evidence | YouTube creator empirical consensus (0-5 words); Chinese-platform creator experience (≤12 characters); WCAG 2.x AA (4.5:1, body text from 16px); Australian Government Accessibility Toolkit (45-75 character line-length metric) | Text upper limit, mobile thumbnail readability, contrast floor |
| 4. Style anchors vs. competitor feed | filmit.io, *Teal & Orange Explained* ("became standard in 2012, became cliché in 2020" evolution arc); high-earning creator cover frameworks (feed-level contrast, cross-confirmed by multiple creator-tool guides) | Cliché risk, control-group discipline |

**Adoption discipline**: only cite principles that have clear sources and multi-source agreement;
single-source precise percentages (e.g. "62% improvement") are never adopted, replaced with qualitative statements.
