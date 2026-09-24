---
name: personal-wiki
description: >
  Build and maintain a personal markdown wiki with a two-layer raw/notes
  layout, then index, full-text search, lint, and report on it. Turns loose
  clippings into a linked, tagged, searchable knowledge base and surfaces
  orphan notes, broken wiki links, and empty stubs. Use when the user asks to
  build a personal knowledge base / set up a wiki / organize my notes /
  link notes to each other / search my note vault / build a personal wiki /
  organize my notes / find orphan notes / search my note vault /
  knowledge base / documentation / wiki / information architecture / research. Do NOT use for extracting durable facts into agent memory
  (use memory-extractor), for building an entity-relation graph with metrics
  (use knowledge-graph-builder), or for publishing notes as a website.
license: Apache-2.0
compatibility: Requires Python 3.8+; this skill's scripts use only the standard library, with no third-party dependencies.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: knowledge
  pattern: single-task
  tier: standard
  verified-date: "2026-09-17"
---

# Personal Wiki

Gather scattered clippings and drafts into a **two-layer** knowledge base: `raw/` holds source material (write-only, never edited),
`notes/` holds your compiled notes (with `[[double links]]` and `#tags`), and a JSON index ties the two together.
The core judgment is: **source material and your conclusions must live apart** — mixed together, the index cannot tell
"what the author said" from "what I thought," and retrieval weighting loses its meaning.

This skill handles directory management, indexing, retrieval, and health checks; it **does not** distill knowledge into agent long-term memory
(that is `memory-extractor`), nor **build** entity-relation graphs and centrality analysis (that is `knowledge-graph-builder`).

## Input Checklist

| Input | Required | Default | Notes |
|---|---|---|---|
| Wiki root directory | Yes | — | Created if absent; reused if already initialized |
| Source material | Yes | — | Where the clippings/drafts live, or "write from scratch" |
| Existing note naming habit | No | File name as slug | Affects link resolution: match by file name or by H1 title |
| Tag system | No | Free tags | Follow any existing classification scheme to avoid splitting synonymous tags |
| Retrieval need | No | Full-text search | Say so if you need "title hits only" |

When inputs are missing, ask for all at once (do not drip-feed follow-ups):

> Please provide: ① which directory should the wiki live in? ② where is the existing material (or write from scratch)?
> ③ do you want links resolved by file name or by H1 title? ④ is there an established tag system?
> ⑤ what do you most often look for when searching (title / tags / body)?

## Pre-flight Self-check

Run each item; on any failure → take the stated action:

```bash
# 1. Python version (the scripts need 3.8+, using pathlib.rglob and f-strings)
python3 --version
# expect: Python 3.8+. Fail → STOP; this skill's scripts cannot run.

# 2. The script is present and executable
# python3 scripts/wiki_build.py --help >/dev/null && echo "script ok"
# expect: prints script ok. Fail → confirm the path; the script sits in scripts/ next to SKILL.md.

# 3. The target directory's state (distinguish "new" from "reuse")
ls -d <wiki-dir> 2>/dev/null && ls <wiki-dir> || echo "OK-NEW"
# expect: OK-NEW goes to init; if it exists and contains notes/, go to index — do not re-init.
```

## Workflow

### Step 1: Initialize the Directory Skeleton

```bash
python3 scripts/wiki_build.py init <wiki-dir>   # use this to initialize a new wiki (add --force for an existing directory)
```

Produces the four pieces `raw/`, `notes/`, `index.json`, `README.md`, and immediately builds an empty index.

- **Expected**: outputs `initialized: <absolute path>` and the four entries; `find <wiki-dir>` shows `raw/` and `notes/`.
- **On failure**: if it reports "directory not empty" → this is the anti-overwrite protection. First confirm the target directory has no existing user notes;
  only add `--force` when you truly want to initialize there; **do not add it for an empty directory**.

### Step 2: Place the Material (raw / notes split)

This is the only step in this skill that needs human judgment:

| Material nature | Goes to | Why |
|---|---|---|
| Web clippings, paper originals, what others said | `raw/` | Only indexed, not linted; allowed to be scattered and link-free |
| Your own summaries, conclusions, todos | `notes/` | Participates in orphan / broken-link / empty-note checks |
| A copied long article + your highlights | Split in two | The original goes to `raw/`, the highlights go to `notes/` and link back to the original |

Note-writing conventions (the parser works per these):

```markdown
# Vector search                        <- the first H1 is the title, with the highest retrieval weight

Encoding text into vectors and finding neighbors is the recall stage of [[RAG architecture]].   <- [[double links]] establish relations

Complementary to [[inverted index]].           <- the target can be a file name, or someone else's H1

#search #infra                         <- #tags are for classification
```

- **Expected**: every note under `notes/` has a unique H1; wherever a relation is needed, `[[target]]` is written.
- **On failure**: a note has no H1 → the parser falls back to the file name as the title, no error but poor title quality;
  add H1s uniformly and rerun step 3.

### Step 3: Rebuild the Index

```bash
python3 scripts/wiki_build.py index assets/sample-wiki   # bundled sample wiki; replace with your wiki-dir
```

Scans both directories, extracts title / tags / word count / link relations, and writes back to `index.json`.
**Rerun it every time you finish editing a note**; both retrieval and the health check read this index.

- **Expected**: outputs `pages` (notes/raw split out), `tags` count, the resolved / unresolved counts for `links`,
  plus a per-page list, each line like `- [notes] Vector search (98w, 2 tags, 2 out)`.
- **On failure**: `unresolved` not being 0 is **normal** (writing links before adding the note is common);
  but if `resolved` is 0, the link syntax was wrong — check whether you used full-width brackets `【【】】`.

### Step 4: Search

```bash
python3 scripts/wiki_build.py search assets/sample-wiki "idempotent"   # bundled sample (two notes in notes/, searching idempotent)
```

Ranking weights: **a title hit scores 10 > a tag hit scores 5 > a body hit scores 1**, with repeated occurrences accumulating by count.
This weighting is deliberate: a title hit means the note's **topic is** that word, far more important than a passing mention in the body.

- **Expected**: outputs the hit count and per-hit scores, each like `14  [notes] Vector search` plus a line `(title×1, body×4)`.
- **On failure**: 0 hits → first confirm the word is already in the index (run `index`);
  Chinese search is **substring matching**, so searching "vector" hits "vector search," but searching "search vector" does not.

### Step 5: Health Check

```bash
python3 scripts/wiki_build.py lint assets/sample-wiki
```

Checks four classes of problems: **orphan notes** (no incoming links, unreachable by search), **broken links** (`[[target]]` does not resolve),
**empty notes** (body under 5 words), and **untagged notes** (info-level, not an error).

- **Expected**: lists the four problem classes in sections; when all are clean, each section prints `(none)`.
- **On failure**: exit code 1 means **something was found** (not that the script errored) — this is the signal for CI;
  when there are false positives, handle them per the failure table below.

### Step 6: Produce Stats and Deliver

```bash
python3 scripts/wiki_build.py stats <wiki-dir>
```

Outputs the note count, total word count, average links per note (incoming + outgoing), and the tag distribution top 10 (with a bar chart).

- **Expected**: gives the wiki's absolute path, note count, and link density; `generated_at` is the just-run timestamp.
- **On failure**: `stats` reports "index does not exist" → first run step 3's `index`, then rerun;
  the stats disagree with the on-disk `*.md` count → some notes landed in a directory outside `notes/` and `raw/`; move them in and re-`index`.

At delivery, explain three things to the user: the wiki's absolute path, the current note count and link density,
and every unfixed problem class from `lint` with the reason. Ongoing maintenance just repeats "edit note → `index` → `lint`,"
with no need to re-`init`.

## Delivery Standards

- Artifacts: an initialized wiki directory + an `index.json`, with the index consistent with the on-disk content.
- Location: the user-specified directory; when unspecified, use `wiki/` under the current directory.
- Integrity verification (do at least the first two):
  - The `pages` count from `index` equals `find <dir>/notes <dir>/raw -name "*.md" | wc -l`;
  - `stats`'s `generated_at` is the just-run timestamp;
  - every problem class from `lint` has a clear "fixed / to be fixed + reason" account.
- `index.json` is a generated artifact; the delivery note should remind the user **not to hand-edit it** (the next `index` overwrites it).

## Failure Handling Table

| Symptom / error | Cause | Action |
|---|---|---|
| `directory not empty: ...; add --force to confirm initialization` | init's anti-overwrite protection | Confirm the directory has no existing user notes; add `--force` only if it is an empty shell |
| `directory does not exist: ... (run init first)` | Ran index/search on an uninitialized path | First `init`, or check the path spelling |
| `index does not exist: ... (run index first)` | Manually deleted index.json then searched directly | Rerun `index`; search reads the index only |
| `index corrupted (...)` | index.json was hand-edited or the write was interrupted | Delete `index.json` and rerun `index`; do not try to patch the JSON |
| resolved is 0 but links were clearly written | Used full-width brackets `【【】】` or the full-width bar `｜` | Switch to half-width `[[target]]` / `[[target\|alias]]` and rerun index |
| Lots of notes judged orphans | The link direction was written backwards (A linked B, but you assumed B links back to A) | Orphan judgment only looks at **incoming links**; add outgoing links in the relevant notes, or accept that it really is an independent note |
| `#tags` not recognized | A `#` immediately followed by a digit (e.g. `#1`), or preceded by a letter (`a#b`) | Tags must start with a letter or Chinese character; digit-leading ones use forms like `#v2` |
| Chinese tags misalign in stats | An early version used `len()` to align full-width characters | Use a version aligned by display width; if it still misaligns, the terminal font is non-monospace |
| lint's exit code 1 breaks CI | The exit code means "something found," not "an error" | Wrap it in CI with `\|\| true`, or first clear orphans and broken links |

## References

- `references/sources-and-methodology.md` — methodology provenance, the public ideas borrowed from Zettelkasten / double-link notes,
  and the originality statement; read when asked "what is this structure based on."
- `scripts/wiki_build.py --help` — the five subcommands and their parameters.
- Related skills: `memory-extractor` (distill long-term memory), `knowledge-graph-builder` (entity-relation graph).
