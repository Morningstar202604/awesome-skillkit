---
name: deep-research
description: "Multi-round search with information synthesis and structured report generation. Query decomposition, quality scoring, trustworthiness assessment, deduplication. Use when the user asks to research a topic in depth and needs a comprehensive report with sources, deep research, multi-round retrieval into a report, or to investigate a topic. Do NOT use for casual single-question lookups (use web-search)."
license: Apache-2.0
compatibility: Pure prompt-based; may read project structure via Bash.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: planning
  pattern: web-search
  tier: powerful
  verified-date: "2026-09-09"
---

# Deep Research — Deep-Research Agent

Multi-round search + information synthesis + structured report generation.
All commands are run from the skill directory (the directory containing this file).

## Core Capabilities

| Capability | Description |
|------|------|
| **Multi-round search** | Automatically splits queries and deepens over multiple iterative rounds |
| **Information dedup** | URL dedup + domain-quota filtering |
| **Source verification** | Domain trustworthiness scoring (official/blog/forum tiering) |
| **Citation tracking** | Every conclusion has a source link |
| **Report generation** | Dual output in Markdown + JSON |

## Input Checklist

| Input | Required | Description |
|------|------|------|
| topic | Yes | The research topic |
| depth | No | Search depth: `basic` / `standard` / `deep` (default standard) |
| max_rounds | No | Max search rounds (default 3, maps to the CLI `--rounds`) |
| min_sources | No | Minimum number of sources (default 5) |
| output_format | No | Output format: `markdown` / `json` / `both` (default markdown, maps to the CLI `--format`) |
| focus_areas | No | Areas of focus (default all) |

When missing, ask all at once: "Please provide: (1) the research topic. I'll use defaults for everything else."
Note: the CLI directly exposes topic / `--rounds` / `--format` / `--no-cache`; depth, min_sources, and focus_areas are applied by the agent during synthesis and reporting.

## Pre-flight Checks

Run in order; if a fatal item fails → fix it, then STOP.

```bash
# 1. Python available (fatal)
python3 --version                                            # Expected: Python 3.x

# 2. The web-search skill is in place (fatal; this skill reuses its search client)
test -f ../web-search/scripts/search_client.py && echo OK    # Expected: OK; failure → confirm the web-search skill exists as a sibling directory

# 3. Import-chain verification (no network needed)
PYTHONPATH=../web-search/scripts python3 -c "from search_client import search; print('search_client OK')"
# Expected output: search_client OK; failure → PYTHONPATH doesn't point to ../web-search/scripts
```

- Network reachability (required for real search): any public SearXNG instance being reachable is enough; if an instance is down, the script automatically falls back to DuckDuckGo; if all fail, see the failure-handling table.
- `BRAVE_API_KEY` is only needed when the underlying engine selects brave; credentials go through environment variables only.

## Parameter Cheat Sheet

`python3 scripts/research_agent.py` (run):

| Parameter | Values | Description |
|------|------|------|
| topic (positional) | Research topic text | Required |
| --rounds / -r | integer | Max search rounds, default 3 |
| --format / -f | markdown / json / both | Report format, default markdown |
| --no-cache | switch | Disable the search cache |
| Env var PYTHONPATH | `../web-search/scripts` | Must be set, otherwise the search client fails to load |

## Workflow

### Step 1: Query analysis and sub-question decomposition (done automatically by the script)

Action (internal read logic): QueryAnalyzer splits sub-queries by pattern ("A and B" → compare/vs; "best X" → best practices/pros & cons; "how to X" → method/tutorial/examples), appends a year dimension and English queries, dedupes to at most 10 sub-queries, and picks a strategy:

| Topic type | Strategy | Engine | Depth |
|---------|------|------|------|
| Technical docs | Precision search | SearXNG | standard |
| News/events | Multi-source verification | SearXNG + DDG | deep |
| Comparison analysis | Comparative search | SearXNG + DDG | deep |
| Introductory tutorial | Basic search | SearXNG | standard |

Expected: the sub-query list is non-empty (contains at least the original topic).
On failure (topic empty) → the CLI reports a parameter error; return to the input checklist.

### Step 2: Multi-round search and auto-fallback

Action (run):

```bash
PYTHONPATH=../web-search/scripts python3 scripts/research_agent.py "FastAPI vs Flask: which to choose" --rounds 3 --format both
```

Expected: stdout outputs the report; round 1 uses the first 5 sub-queries, and later rounds generate follow-ups from existing result titles (up to 5 per round); if results are <5 and the round cap hasn't been reached, it auto-continues searching.
On failure: stderr/results show `web-search skill not found` → PYTHONPATH isn't set or the path is wrong; go back to pre-flight Step 3.

### Step 3: Dedup and quality/trustworthiness assessment (done automatically by the script)

Dedup strategy:

| Dedup level | Method | Threshold |
|---------|------|------|
| URL dedup | Exact match | 100% |
| Domain dedup | At most 3 entries per domain | 3 entries |
| Content dedup | Merge when similarity > 0.8 | 0.8 |
| Opinion dedup | Merge citations with the same conclusion | - |

Quality-score weights (implemented in the script, max 1.0): domain trustworthiness 40% + content completeness 20% + title relevance 20% + engine authority 10% + freshness 10%. See `DOMAIN_TRUSTWORTHINESS` in `scripts/research_agent.py` for the domain trust baseline (official docs 1.0, github.com 0.9, stackoverflow.com 0.85, tech blogs 0.55-0.7, forums 0.5).
Expected: the result list is sorted by `quality_score` descending, with `trust_scores` per URL.
On failure (all results score the default 0.5) → domain resolution failed; check URL validity.

### Step 4: Deep analysis (optional, agent-run)

- Multiple perspectives: sort results into four perspectives — technical implementation / performance comparison / best practices / community feedback — and write them into the report's "multiple viewpoints" table.
- Conflict detection: when sources disagree on the same sub-topic, list them side by side in "Controversies and disagreements" honestly; don't force a unified view.
- Information gaps: against the focus areas the topic should cover, write uncovered items into "Information gaps"; if needed, add a round of search (back to Step 2).

Expected: the report's corresponding sections correspond one-to-one with sources (every conclusion traces back to a URL).
On failure (a perspective has no results) → that section honestly notes "no relevant information found".

### Step 5: Generate and save the report

Action (run, the script persists it automatically): output per `--format`; also write `research_<first 8 chars of md5(topic)>.json` (full results, with `markdown_report`/`json_report` fields).
Expected: stderr hints `Results saved to: research_*.json`; the report has three sections — summary / key findings / full sources.
On failure: writing the file reports a permission error → run from a writable directory, or move the file afterward.

## Report Structure

### Markdown report template

```markdown
# Research Report: {topic}

**Generated at:** {timestamp}
**Search rounds:** {rounds}
**Number of sources:** {source_count}
**Overall trustworthiness:** {trust_score}/1.0

---

## Summary

{2-3 sentence core finding}

---

## Key Findings

### 1. {Finding title}
{Detailed description}

**Sources:**
- [Source 1](url) (trust: ★★★★★)
- [Source 2](url) (trust: ★★★★)

---

## Multiple Viewpoints

| Perspective | Main view | Support |
|------|---------|--------|
| Technical implementation | {view} | ★★★★ |
| Community feedback | {view} | ★★★★★ |

---

## Controversies and Disagreements

{List conflicting information here, if any}

---

## Information Gaps

{List uncovered points here, if any}

---

## Full Sources

| # | Title | URL | Trust |
|---|------|-----|--------|
| 1 | {title} | [link](url) | ★★★★★ |
```

### JSON report structure

```json
{
  "topic": "Research topic",
  "generated_at": "2026-09-09T10:00:00Z",
  "search_stats": {
    "rounds": 3,
    "queries": 12,
    "sources": 25,
    "deduped_sources": 18
  },
  "summary": "Core finding summary",
  "findings": [
    {
      "title": "Finding title",
      "content": "Detailed description",
      "evidence": [
        {"source": "url", "title": "Title", "trust": 0.95}
      ],
      "confidence": 0.88
    }
  ],
  "perspectives": {
    "technical": {},
    "performance": {},
    "community": {}
  },
  "conflicts": [],
  "gaps": [],
  "sources": []
}
```

## Collaboration with code-intent-planner

When the research topic involves technology selection, hand the conclusions to the planner: feed deep-research's recommendation (e.g. "recommend FastAPI") into code-intent-planner's input, e.g. `raw_input: "implement the user-auth module using FastAPI"`, `context: "per the research, FastAPI suits this scenario better"`, and let it produce intent_type and sub_tasks.

## Failure Handling Table

| Symptom / error code | Cause | Action |
|------|------|------|
| `web-search skill not found` | search_client import failed | Set `PYTHONPATH=../web-search/scripts` and rerun |
| All search engines time out | Network issue | Prompt the user to check the network |
| Insufficient results | Query too specific | Broaden the query terms; add `--rounds` |
| Low trustworthiness | Sources are mostly blogs/forums | Flag low trust; suggest manual verification |
| Severe conflicts | Widely divergent views | Present honestly; don't force unity |
| `research_*.json` not generated | Current directory not writable | Run from a writable directory |

## Delivery Criteria

- Definition of success: the report is generated and source count ≥ min_sources (default 5); when short, the report must honestly flag the gap — sources and citations must not be fabricated.
- Artifact naming: `research_<first 8 chars of md5(topic)>.json` (script persists automatically); if Markdown delivery is needed, additionally save `research_<YYYYMMDD>_<slug>.md`.
- Save location: default current working directory; recommended to consolidate into `reports/` and preserve URLs verbatim with the report.
- Completeness verification: `python3 -m json.tool research_*.json` parses cleanly; the report has all three sections (summary/key findings/full sources); each finding has at least 1 clickable source link; trust is marked with ★.

## References

- references/search-strategies.md — read when unsure about Step 1 strategy selection (detailed search strategies)
- references/report-templates.md — read before generating a report (report templates and wording conventions)
- references/examples.md — read when calibrating report quality (real research cases)
