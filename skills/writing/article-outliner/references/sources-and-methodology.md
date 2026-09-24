# Sources & Methodology — article-outliner

This skill's **methodology body lives in the reference files** (the templates and criteria in `outline-templates.md`, the logic-flow design in `flow-guide.md`). This file does only two things: declares which tacit knowledge has an external source, and attaches live-test records of script behavior (evidence for the honest disclaimers).

## Tacit-knowledge sources

| Tacit knowledge (SKILL.md number) | Source | Degree of trust |
|---|---|---|
| 1. Q&A chain (each section answers the previous section's question) | Barbara Minto's *The Pyramid Principle* Q&A chain and pyramid structure; verified online this round | Trusted: principle-level conclusions, not numbers |
| 2. Conclusion-first vs suspense buildup is decided by the reader's situation | Same Minto (conclusion-first / BLUF); the "reader's situation decides" decision dimensions are our group's induction from common content-operations practice | Half-trusted: the Minto part has a source; the decision-dimension table is empirical induction, already labeled "rule of thumb" in flow-guide.md |
| 3. MECE's applicability boundary | Same Minto; that MECE is hard to fully achieve and unsuited to open-ended exploration is a widely recognized limitation of the framework | Trusted (with the limitation stated) |
| 4. A title containing "and/&" = two sections compressed into one | Our group's empirical criterion, no external source | Labeled heuristic: for prompting self-check, not a hard rule |
| 5. Division of labor between title and hook | Common content-operations practice (the title serves search/feed, the hook serves the arrived user); no single authoritative original text verified online this round | Common-knowledge caliber: trusted as an induction from practice, not claimed as an empirical result |
| 6. The word budget is an anti-crushing device | Our group's design criterion (the purpose of the script's `word_count_target` field) | Original declaration: this is an interpretation of the script field's semantics |
| 7. Reverse outlining | Common academic-writing teaching practice (reverse outlining); no single authoritative original text verified online this round | Common-knowledge caliber: trusted as an induction from teaching practice |
| 8. CTAs differ by platform | Public facts about each platform's interaction buttons | Trusted: directly checkable platform facts |

## Content we did not trust (evidence discipline)

- Any unsourced "writing efficiency up X%" / "read-through rate Y%" numbers are never written into SKILL.md.
- Minto's pyramid "conclusion-first" was not expanded into "every article must be conclusion-first" — the original text itself states the framework doesn't apply to open-ended exploration, and this skill accordingly restricts it to technical/news scenarios.

## Script-behavior live-test record (2026-09-22)

Live-run verification of `scripts/outliner.py` (`--type technical --points async caching "DB indexing"`):

| Fact | Measured value |
|---|---|
| Section-title source | Fixed template table (`problem background / cause analysis / solution / comparison test / summary`), independent of topic |
| `title` shape | `{topic}: from beginner to mastery` (fixed suffix) |
| `hook` shape | "Have you hit the pain point of {topic}?" |
| `conclusion` shape | The literal string "key takeaways + CTA" |
| `points` distribution | When point count ≤ section count, one point per section; > section count, it round-robins (no point dropped) |
| `word_count_target` | Evenly split, remainder shifted forward; the sum per section always equals `total_words_target` |
| `reading_time_min` | `total_words_target // 250` (the English 250 wpm convention; conservative for Chinese) |
| `level` | Always 2 (no nested headings produced) |
| Invalid `--type` value | argparse errors out, rc=2 (no automatic fallback) |

> The purpose of this section is to make the "honest disclaimers" auditable: if any entry disagrees with the code, the code wins and SKILL.md is corrected.

## Division of labor with the reference files

| File | Content | Trust status |
|---|---|---|
| `outline-templates.md` | 5 templates, length shares, outline acceptance criteria | Carries its own "rule of thumb" disclaimer; the share numbers are rules of thumb, not platform rules |
| `flow-guide.md` | Cognitive load, conclusion-first decision, inter-section relations, transition library, logic gaps, flow checklist | Carries its own "rule of thumb" disclaimer |
| This file | Sources and live tests | Evidence-discipline declaration |
