---
name: knowledge-graph-builder
description: >
  Turn a folder of markdown notes into an explicit knowledge graph: extract
  entities and relations into nodes plus edges, export as JSON, Graphviz DOT,
  or Mermaid, and compute structural metrics such as degree centrality,
  connected components, and isolated nodes. Use when the user asks to
  build a knowledge graph / turn notes into a graph / extract entity relations /
  export a graphviz or mermaid diagram / find isolated nodes in notes /
  analyze note-link structure / build a knowledge graph /
  extract entities and relations / map my notes / find isolated notes /
  knowledge base / documentation / wiki / information architecture / research. Do NOT
  use for indexing or searching a note vault (use personal-wiki), for extracting
  durable facts into agent memory (use memory-extractor), or for drawing
  architecture diagrams (use arch-diagram).
license: Apache-2.0
compatibility: Requires Python 3.8+; the script is stdlib-only. Rendering DOT needs a local graphviz (optional, for validation).
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: knowledge
  pattern: single-task
  tier: standard
  verified-date: "2026-09-17"
---

# Knowledge Graph Builder

Turn a pile of Markdown notes into a graph of **nodes + edges**: notes are nodes, `[[double links]]` are edges,
and bolded words join the graph as candidate concept entities. It produces three consumable forms —
JSON for programs, DOT for graphviz, Mermaid for documents — plus a set of graph metrics
(degree centrality, connected components, isolated nodes) to answer: **where is the skeleton of this note set, and where is it broken**.

The "extraction" step uses **heuristic rules**, not NLP: a `[[link]]` is an edge, an H1 is the node title,
`**bold**` is a candidate entity. So the graph's accuracy depends on how disciplined your note-writing is —
read the extraction contract in step 2 before writing.

This skill **does not** do retrieval and indexing (that is `personal-wiki`), **does not** do entity disambiguation and knowledge fusion
(which needs NLP models; this skill deliberately does not introduce them), and **does not draw** architecture diagrams (that is `arch-diagram`).

## Input Checklist

| Input | Required | Default | Notes |
|---|---|---|---|
| Notes directory | Yes | — | Recursively scans `.md`/`.markdown`/`.txt` |
| Export format | No | json | One of `json` / `dot` / `mermaid` |
| Include candidate entities | No | Included | Add `--note-only` to see only the link skeleton between notes |
| Centrality stat scope | No | All nodes | When `--notes-only`, ignores concept nodes |
| Output path | No | stdout / `<dir>/graph.json` | Prints to stdout if unspecified |

When inputs are missing, ask for all at once:

> Please provide: ① where is the notes directory? ② what format do you want (JSON for programs / DOT for graphviz /
> Mermaid to paste into a document)? ③ do you only care about links between notes, or should bolded concepts also be included?
> ④ are there any known isolated notes you want to check first?

## Pre-flight Self-check

Run each item; on any failure → take the stated action:

```bash
# 1. Python version
python3 --version
# expect: Python 3.8+. Fail → STOP.

# 2. The script is available
# python3 scripts/graph_build.py --help >/dev/null && echo "script ok"
# expect: script ok. Fail → check the scripts/ path.

# 3. The directory has parseable notes
find <notes-dir> -name "*.md" -not -path "*/.*" | head -5
# expect: at least 1 file. Fail → the script will report "no Markdown notes found"; confirm the path first.

# 4. Optional: is graphviz local (only affects DOT-to-image, not export)
which dot >/dev/null && echo "graphviz ok" || echo "no graphviz (DOT can still be exported for the user to render)"
```

## Workflow

### Step 1: Confirm the Notes' Writing Conventions

The graph's shape is entirely determined by how the notes are written; the extraction contract is:

| How it is written in a note | Extracted as | Notes |
|---|---|---|
| `# Title` (first H1) | The note node's `label` | Falls back to the file name if there is no H1 |
| File path | The note node's `id` | Unique identifier, relative to the directory |
| `[[target]]` / `[[target\|display]]` | note → note edge (`rel=links`) | The target is resolved by file name or H1 title |
| `**bold word**` / `__bold word__` | note → concept edge (`rel=mentions`) | Same-name bold words across notes merge into the same concept hub |
| Content inside code blocks / inline code | **Not extracted** | Avoids treating `foo_bar()` as a concept |

- **Expected**: the user's notes contain at least one `[[link]]`, otherwise the graph will be all isolated nodes.
- **On failure**: the notes have no links at all → the graph can still be produced (concept edges only),
  but tell the user honestly that "this only reflects bold-word co-occurrence, not relationships between notes."

### Step 2: Extract the Graph Data

```bash
python3 scripts/graph_build.py extract assets/sample-notes   # bundled sample notes; replace with your notes/
```

Produces `<notes-dir>/graph.json`, containing `nodes` / `edges` / `meta` / `unresolved_links`.

- **Expected**: prints counts for `nodes` (note / candidate split out), `edges`, and `unresolved`,
  and prints nodes and unresolved links one by one. Example: `nodes: 13 (note 5 / candidate 8)`.
- **On failure**: `unresolved` not being 0 means some `[[link]]` points to a note that does not exist —
  this is a **content problem, not a script problem**; relay it to the user to decide whether to "add the note" or "delete the link."

### Step 3: Export to the Target Format

```bash
# Paste into a Markdown document (most common)
python3 scripts/graph_build.py export assets/sample-notes --format mermaid --note-only

# Hand to graphviz for a vector image
python3 scripts/graph_build.py export assets/sample-notes --format dot --out graph.dot   # bundled sample
dot -Tsvg graph.dot -o graph.svg

# For a downstream program
python3 scripts/graph_build.py export assets/sample-notes --format json --out graph.json
```

The exporter already handles two common pitfalls: Mermaid node ids are all rewritten to `n0`, `n1`…
(the `/` and `.` in paths break Mermaid syntax), with the original title in brackets;
DOT titles are quote-escaped.

- **Expected**: Mermaid output starts with ` ```mermaid `, opens the graph with `flowchart LR`, and ends with ` ``` `,
  ready to paste into Markdown for rendering; DOT output starts with `digraph knowledge {`.
- **On failure**: if Mermaid exceeds `--max-edges` (default 200) it truncates and inserts
  a `%% ... truncated` comment; when the graph is too large, use `--note-only` or raise the limit.

### Step 4: Analyze the Graph Metrics

```bash
python3 scripts/graph_build.py analyze <notes-dir> --top 10
```

Outputs four groups of information, plus one **actionable diagnostic conclusion**:

- **Degree centrality top N**: `degree` is the edge count, `centrality = degree / (N-1)` (normalized).
  Those near the top are the hub concepts of this note set.
- **Connected components**: by size descending. More than 1 component means the notes split into several disconnected chunks.
- **Isolated nodes**: degree 0 — neither a neighbor of any note nor linked outward.
- **Diagnostic line**: one of three conclusions (no edges at all / graph split into N chunks / a single connected component).

- **Expected**: the centrality list has a bar chart and node-type labels; the diagnostic line gives the next action.
- **On failure**: concept nodes crowd the list → add `--notes-only` to look only at notes;
  or `--top 20` to widen the view.

### Step 5: Deliver and Give Improvement Suggestions

At delivery, explain four things: the graph file path and format, the node/edge scale, **the 2-3 highest-centrality nodes**
(i.e. the thematic skeleton of this note set), and the isolated-node list with remediation suggestions.

Typical suggestion: an isolated note either gets a `[[link]]` added to connect it into the main graph,
or you accept that it really is an independent topic; both are reasonable conclusions, but make it clear.

- **Expected**: the user gets the graph file + an actionable conclusion (skeleton nodes, broken spots, a link-to-add list).
- **On failure**: the `nodes` count from `extract` and `analyze` disagree → the notes changed between the two scans;
  rerun once to align before delivering; if `unresolved_links` is non-empty and the user does not plan to add the notes → keep these
  broken edges in the graph but list them one by one in the delivery note; do not silently drop them.

## Delivery Standards

- Artifacts: at least one `graph.json`; plus one or two more in Mermaid / DOT as the user needs.
- Location: `extract` defaults to writing `<notes-dir>/graph.json`; `export` prints to stdout when `--out` is not given.
- Integrity verification (do at least the first two):
  - The `nodes` count from `analyze` equals the `nodes` count from `extract` (two scans of the same directory should agree);
  - The number of node declarations + edges in the Mermaid output equals the scale reported by `analyze`;
  - Every entry in `meta.unresolved_links` is mentioned in the delivery note.
- `graph.json` is a generated artifact; remind the user **not to hand-edit it** (rerunning `extract` overwrites it).

## Failure Handling Table

| Symptom / error | Cause | Action |
|---|---|---|
| `directory does not exist: ...` | The path is mistyped or the directory was not created | Check the path; no need to pre-create an empty directory when the notes directory does not exist |
| `no Markdown notes found under ...` | The directory is empty, or the extension is not on the allowlist | Confirm there are `.md` files; `.txt` is also allowed; other extensions are unsupported |
| All nodes have degree=0 | No `[[link]]` between the notes | Output normally, but explain "this is not a relation analysis, only co-occurrence" |
| Concept nodes dominate and notes are invisible | Bold-word concept nodes are naturally high-degree | Use `--notes-only` to limit centrality to notes |
| Pasted Mermaid does not render in the document | Used `export --format json` output, or the truncation comment is misplaced | You must use `--format mermaid`; confirm the first line is ` ```mermaid ` |
| The Mermaid graph is too dense to read | Hundreds of edges; Mermaid's auto-layout turns into a tangle | Add `--note-only`, or `--max-edges 30` to see only the most relevant edges |
| Bold words were not extracted as entities | The bold spans a line break (`**` and `**` not on the same line), or exceeds 40 chars | Keep bold on a single line and under 40 chars; bold inside code blocks is deliberately ignored |
| A `[[link]]` was written but is unresolved | The target name matches neither "file name / H1 title" (case-insensitive, but typos are not accepted) | Fix the link text, or first add the note in `personal-wiki` |
| DOT-to-SVG reports a syntax error | The title contains unescaped characters (the script already escapes `"` and `\`) | If it still fails, shrink the graph with `--note-only` and attach the full offending `.dot` to the user |

## References

- `references/sources-and-methodology.md` — the design rationale for the extraction heuristics, the definitions and provenance of the graph metrics,
  and the borrowing from existing tools (Zettelkasten double links, graph-database import formats).
- `scripts/graph_build.py --help` — the three subcommands and all parameters.
- Related skills: `personal-wiki` (build the knowledge base first, then extract the graph),
  `memory-extractor` (solidify stable conclusions into agent memory).
