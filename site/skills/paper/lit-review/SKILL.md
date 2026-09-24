---
name: lit-review
description: "Multi-source literature review: real retrieval via Semantic Scholar Graph API (--s2, with true citations/venue/year/abstract) or arXiv (--arxiv), honest mock fallback for offline/CI; builds a REAL co-citation graph (shared references) instead of sequential links; synthesizes trends/gaps via LLM (model_route) with keyword-cooccurrence fallback. Use for literature review / related work / finding references / researching papers in a direction / surveying a topic / citation graph. Do NOT use for topic selection (use paper-topic-selector first)."
license: Apache-2.0
compatibility: Stdlib. --s2 hits api.semanticscholar.org, --arxiv hits export.arxiv.org (20s timeout, 429 backoff 3s). Any network/parse failure -> honest mock fallback (data_source=mock + warning). SKILLKIT_MOCK=1 forces mock. LLM synthesis via skills/meta/_shared/model_route when SKILLKIT_MODEL_URL set; else keyword-cooccurrence (offline).
metadata:
  version: "2.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-21"
---

# Lit Review

Do **multi-source real retrieval** around a topic, build a **real citation graph based on shared references**, and produce a review skeleton annotated with research gaps (LLM synthesis + keyword co-occurrence fallback).

> Honest disclosure: `data_source` is always `s2` | `arxiv` | `mock`. Any fallback is written into `warning`; **`mock` results MUST be labeled "simulated data"**; don't present them as real retrieval. `retrieval_date` records the fetch date (reproducibility requires "store the DOI, not the query"; use it to re-check).

## Input Checklist

| Input | Required | Notes |
|------|------|------|
| topic | yes | `--topic "LLM agents"` |
| data source | no | `--source s2\|arxiv\|mock` (default mock); or shortcuts `--s2` / `--arxiv` |
| venue filter | no | `--venues "ACL,NeurIPS"` (only s2/mock; arXiv has no venue filter) |
| max count | no | `--max 20` (default 10) |
| LLM synthesis | no | On by default (when an LLM gateway is available); `--no-llm` forces keyword co-occurrence (offline/verifiable) |
| output path | no | `--output review.json`; default prints to stdout |

When missing, ask everything at once: "Please provide: ① topic `--topic` ② data source `--source` (s2 real citation counts / arxiv / mock) ③ venue filter `--venues` (only s2/mock) ④ count `--max` ⑤ whether to `--no-llm` ⑥ whether to save `--output`."

## Pre-flight Checks
```bash
python3 --version                       # expect >= 3.8, else STOP
test -f scripts/lit_review.py && echo OK
# real retrieval needs network; offline first export SKILLKIT_MOCK=1 (force mock)
```

## Workflow

### Step 1: Retrieve and Produce
```bash
python3 scripts/lit_review.py --topic "LLM agents" --s2 --max 20 --output review.json   # real citation counts/venue
python3 scripts/lit_review.py --topic "diffusion models" --arxiv --no-llm                # real retrieval, no citation counts
SKILLKIT_MOCK=1 python3 scripts/lit_review.py --topic "LLM agents"                       # offline/CI
```
Expected: JSON with `topic`, `data_source`, `warning`, `retrieval_date`, `papers[]`, `citation_graph`, `summary`.
If it fails: you wanted real data but didn't add `--s2`/`--arxiv` -> add it; offline -> `SKILLKIT_MOCK=1`.

### Step 2: Read data_source (Honest Labeling)
- `data_source == "s2"` -> Semantic Scholar real retrieval; `citations` are **real citation counts**, `abstract` truncated to 600 chars; the citation graph is `co-cited` (shared references).
- `data_source == "arxiv"` -> real retrieval but `citations` always 0; `--venues` has no effect; the citation graph degrades to `same-venue-year` (low confidence).
- `data_source == "mock"` -> synthetic data; **MUST be labeled simulated data**.
If it fails: `warning` contains "fell back to MOCK" -> the chosen network source failed and the result is actually mock.

### Step 3: Use the Artifacts
Expected: `papers[]` goes into the body text, `summary.gaps_identified` into Related Work, `citation_graph` visualized (note `citation_graph.method` explains edge-type confidence). With `--no-llm`, `summary.synthesis_method == "keyword-cooccurrence"` and is verifiable.
If it fails: artifact `status: empty` -> broaden the topic / change keywords / switch source.

## Parameter Quick Reference

| Parameter | Value | Notes |
|------|------|------|
| `--topic` | string | Retrieval topic (required) |
| `--source` | `s2`/`arxiv`/`mock` | Data source, default mock |
| `--s2` / `--arxiv` | flag | Equivalent to `--source s2/arxiv` |
| `--venues` | comma-separated | Venue filter, only s2/mock |
| `--max` | int | default 10 |
| `--no-llm` | flag | Disable LLM synthesis, force keyword co-occurrence |
| `--output` | path | Results JSON output path |

## Failure Remediation Table

| Symptom / Error Code | Cause | Remedy |
|------------|------|------|
| `warning` contains "fell back to MOCK" | The chosen network source failed | Label as mock; retry or `SKILLKIT_MOCK=1` |
| `data_source: mock` but claimed as real | Misread the source | Force-label simulated data |
| `status: empty` | No hits | Broaden topic/venue/switch source |
| Graph has no `co-cited` edges | No citation metadata (arxiv) or no shared references | Look at `citation_graph.method`; don't treat low-confidence edges as strong associations |
| `s2` 429/403 rate limit | Semantic Scholar shared egress quota | Lower `--max`, retry later, or switch to `--arxiv` |
| Citation counts don't match the official DB | Different source caliber / fetch time | Re-check with `retrieval_date` + `doi`; don't treat as authoritative statistics |

## Delivery Standard

Success: the JSON structure is complete, and top-level `data_source` and `warning` honestly reflect the source.
Artifact name: `review.json` (if `--output` is given).
Verification: `python3 -c "import json;d=json.load(open('<out>'));assert d['data_source'] in ('s2','arxiv','mock') and 'method' in d['citation_graph']"` passes.

## References

Multi-source retrieval/graph/synthesis logic is built into `scripts/lit_review.py`: `_fetch_s2`/`_fetch_arxiv`/`search_papers`/`build_citation_graph`/`summarize`/`_keyword_fallback`.
SOTA toolchain: Semantic Scholar Graph API (real citations), arXiv API, Scite (support/contrasting citations), ResearchRabbit / Connected Papers (co-citation graphs), Zotero + Better BibTeX (.bib management).

## Chain Position

Upstream connects to paper-topic-selector; `summary.gaps_identified` goes to the body, figures to pub-plotter, and LaTeX assembly to latex-formatter.
