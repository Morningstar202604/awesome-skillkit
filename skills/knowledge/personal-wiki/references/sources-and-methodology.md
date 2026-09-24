# Sources & Methodology

- Skill: `personal-wiki` (originally written for awesome-skillkit, Apache-2.0).
- Position: the entry skill of the `knowledge` scenario pack, responsible for knowledge-base directory governance, indexing, retrieval, and health checks;
  complemented by `knowledge-graph-builder` (entity-relation graphs and centrality metrics).

## Methodology borrowed (ideas and taxonomy only; no text or code copied)

| Source | License | Methodology points borrowed |
|---|---|---|
| Public writings on the Zettelkasten card-box method | see original | "Atomic notes + explicit links" beats folder-based classification; the act of building associations itself produces understanding |
| Linked-notes community (Obsidian / Roam ecosystem) public docs | see respective repos | `[[wikilink]]` syntax, backlinks as a derived view of inter-note relations, alias links `[[target\|display]]` |
| PARA / Progressive Summarization public articles | see original | Separation of raw layer from distilled layer: originals in-only, conclusions as separate notes |
| This repo's existing skill standards (SKILL-STANDARD-v2 under docs/) | Apache-2.0 | Skeleton sections, dry-run default, script subcommandization (argparse), and failure-handling table |

All the above sources are restated as a **methodology skeleton**: the two-layer split of `raw/` and `notes/`,
the "title > tag > body" retrieval weight design (10 / 5 / 1), the orphan and broken-link judgment criteria,
and the entire implementation of `scripts/wiki_build.py` are all written from scratch—no upstream passages, examples,
or code were translated, rewritten, or excerpted.

## Key design decisions (why this way)

1. **Two layers rather than one**: `raw/` does not participate in orphan detection. Clippings are inherently often isolated;
   if checked in the same pool as one's own notes, orphan alerts would drown out the signals that actually need attention.
2. **Retrieval weights 10 / 5 / 1**: a title hit means "this note's topic is exactly it," an order of magnitude different from
   an incidental body mention; using accumulated counts rather than boolean hits prevents long articles from dominating the board purely by length.
3. **Index stores only metadata, not full text**: `index.json` stores title/tags/word count/link relations;
   on retrieval, body text is read live by path. The benefit is a small index that never goes stale as notes change.
4. **`lint` uses exit code 1 to mean "findings exist"**: separated from "script crashed," easy to wire into CI;
   but this convention is stated explicitly to avoid users mistaking it for a program error.
5. **Pure standard library**: the knowledge base may be maintained on any machine; introducing third-party dependencies
   would make the skill break outright after an environment change.

## Limitations and boundaries

- Chinese retrieval is **substring matching**—no tokenization, no synonym expansion; for semantic retrieval, switch to a vector approach.
- Link resolution uses two aliases: "filename slug" and "H1 title"; when they conflict, slug takes priority.
- Link direction does not do "automatic bidirectional linking": A linking B does not make B automatically link back to A,
  but B's backlinks will record A—this is a derived view, not written back to the file.

## License

This skill and its reference files are distributed under Apache-2.0; the upstream documents listed carry their own license terms, which do not apply to this file.
