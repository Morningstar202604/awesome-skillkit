# Sources & Methodology

- Skill: `chart-recommender` (authored from scratch by awesome-skillkit, Apache-2.0).
- Positioning: the selection-side skill of the `dataviz` scenario pack; pure prompt-based, no scripts.
  Its division of labor with `dashboard-designer` (the generation side) is: this skill answers "what to draw," and that one handles "drawing it."

## Methodology borrowed (ideas and taxonomy only; no text or code copied)

| Source | License | Methodology points borrowed |
|---|---|---|
| Jacques Bertin's *Semiology of Graphics* visual-variables theory (public retelling) | See the original book | "Position/length/angle/area/lightness/hue" as encoding channels, and their differences in readable precision |
| William Cleveland & Robert McGill's public research on graphical perception precision | See the paper | The empirical conclusion that "humans judge position and length more precisely than angle and area," which underpins the pie-chart and bubble-chart warnings |
| Leland Wilkinson's public concepts in *The Grammar of Graphics* | See the original book | Graphics = data + mapping + scale + geometric object; the order of "fix dimensions and measures first, then pick the geometry" |
| Chart-selection guides and anti-pattern lists widely cited in the data-viz community | See each source | Mainstream consensus such as "avoid 3D, avoid rainbow palettes, dual y-axis with care, bar baseline must be 0" |
| Public sequential/diverging palette design specs (e.g. ColorBrewer's classification) | Apache-2.0 | The division into qualitative / sequential / diverging palettes and each one's use cases |

All the above sources were re-expressed as a **methodology skeleton**. All the tables in
`references/chart-selection.md`, the chart-type applicability conditions and counterexamples, the 12-item error list, the seven output specs, and this SKILL.md's workflow
were written and organized from scratch by this repo; no upstream document's passage, example, or code was translated, rewritten, or excerpted.
The color values come from public qualitative-palette conventions and were contrast-verified separately.

## Key design decisions (why this way)

1. **Force asking intent first**: two datasets with the same shape should pick different charts by intent.
   Giving a chart type without asking intent is passing off "I think it looks nice" as "fits your scenario."
2. **Every option must state its tradeoff**: chart selection is a tradeoff, not a single correct answer.
   An option comparison that lists only the pros has no decision value.
3. **The lexicon is its own file with a table of contents**: over 100 lines must have a TOC (this repo's convention),
   and SKILL.md stays lean, only pointing to "when to read it" in the steps.
4. **Counterexamples and taboos matter as much as recommendations**: most chart-picking errors aren't failing to pick a good chart,
   but picking one that obviously shouldn't be used; hence the "taboo" column sits beside the "recommended" column in the mapping table.
5. **Visual encoding priority comes before the error list**: first build the "precision has a hierarchy" framework,
   so the later anti-patterns (3D pie, area encoding) have a unified explanation rather than a string of rules to memorize.
6. **Pure prompt-based, no script**: this skill produces judgments and specs, not files.
   Adding a script would disguise "tradeoff" as "computed result."

## Limitations and boundaries

- **No final verdict**: gives options and tradeoffs; the user decides in their business context.
- **Doesn't draw or validate real data**: the input is the shape the user describes; if the description is wrong, the recommendation fails with it;
  when you need a real-data profile, run `dashboard-designer inspect` first.
- **Doesn't cover very obscure chart types** (e.g. chord diagrams, horizon graphs): you can reason it out via the visual-encoding priority,
  but it's outside the lexicon.
- **Color is only general advice**: formal delivery must re-check contrast against brand guidelines and accessibility requirements.

## License

This skill and its reference files are distributed under Apache-2.0; the upstream documents listed carry their own license terms, which do not apply to this file.
