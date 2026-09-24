# Sources & Methodology

- Skill: `knowledge-graph-builder` (originally written for awesome-skillkit, Apache-2.0).
- Position: the second skill in the `knowledge` scenario pack. Its division of labor with `personal-wiki` is:
  the latter handles "store materials well, make them searchable," while this skill handles "extract relations, make the structure readable."

## Methodology borrowed (ideas and taxonomy only; no text or code copied)

| Source | License | Methodology points borrowed |
|---|---|---|
| Public writings on Zettelkasten linked notes | see original | Explicit links between notes form a graph; the graph's structure itself is a readable "knowledge skeleton" |
| Mermaid official flowchart syntax docs | MIT | `flowchart LR`, square-bracket nodes, `-->` solid / `-.->` dashed; node ids must not contain path characters |
| Graphviz DOT language public docs | EPL | `digraph`, `rankdir`, node `shape`/`fillcolor` attributes, string escaping rules |
| General graph theory (degree centrality, connected components, BFS) | textbook-level public knowledge | Normalized degree centrality `deg/(N-1)`; connected components via breadth-first traversal |
| Wikipedia / knowledge-graph domain entity-relation triple formulation | CC BY-SA | The basic modeling language of "node = entity, edge = relation" |

All the above sources are restated as a **methodology skeleton**. Notably, this skill deliberately **does not adopt** any
NLP/machine-learning entity extraction scheme (e.g. NER models, dependency parsing, coreference resolution),
but instead uses three explainable heuristics: `[[wikilinks]]` + first H1 + bolded terms:
this is so it can run in a bare environment with no model dependencies, and so extraction results are **predictable and auditable**.
The entire implementation of `scripts/graph_build.py` (graph construction, deduplication, metric calculation, three exporters)
is written from scratch. No upstream passage, example, or code was translated, rewritten, or excerpted.

## Key design decisions (why this way)

1. **Two edge types instead of one**: `links` (inter-note links) are **human judgments**,
   `mentions` (bolded-term co-occurrence) are **surface statistics**. Mixing them would let "frequently appearing words"
   masquerade as "important associations." Separate types + a `--note-only` switch let users view them separately as needed.
2. **Same-named bolded terms across notes merge into one concept node**: this is the skill's only "aggregation" action,
   intended to let recurring concepts form identifiable hubs; the cost is **no semantic disambiguation**—
   homographs will be wrongly merged. This is an explicitly stated known limitation.
3. **Metrics computed on an undirected graph**: degree centrality measures "tightness of association";
   A linking B and B linking A both intuitively count as "these two are related,"
   so `adjacency()` adds edges symmetrically. If directed in/out-degree analysis is needed, separate metrics should be built.
4. **Exporters rewrite Mermaid node ids**: Mermaid fails to parse ids containing `/`, `.`, `-`;
   this is the most common source of "export succeeds but rendering explodes." Changed to sequential numbering
   `n0`, `n1`…, with titles only inside brackets, eliminating this error category at the root.
5. **Code block content is excluded from extraction**: notes often paste code; if identifiers in it were treated as concepts,
   they'd pollute the concept layer. Strip fenced and inline code with regex first, then extract.
6. **Diagnostic lines give conclusions, not numbers**: `components: 2` means nothing to the user;
   "the largest component covers 11/13 nodes; use links to bring in the isolated part" is actionable.

## Limitations and boundaries

- **No entity disambiguation**: `**HNSW**` and `**Hierarchical NSW**` count as two concepts.
- **No relation type identification**: all links are the same `links` relation,
  not distinguishing "cite/rebut/extend"; if typed relations are needed, extend on the link-alias naming convention yourself.
- **No direct graph-database connection**: the output JSON is a generic `{nodes, edges}` structure;
  importing into Neo4j etc. requires an additional mapping layer on the user side; this skill bundles no driver.
- **Scale ceiling**: fully read into memory, suitable for thousands of notes;
  hundred-thousand-scale needs a switch to an incremental index approach, out of scope for this skill.

## License

This skill and its reference files are distributed under Apache-2.0; the upstream documents listed carry their own license terms, which do not apply to this file.
