---
name: lit-review
description: "Literature review helper: scan a topic across venues, build a citation relationship map, and produce a structured summary with research-gap callouts. Use at the start of a paper project or when the user asks for 文献综述 / 相关工作梳理 / 找参考文献. 当用户要求 调研某方向论文 / 写相关工作 时使用。 Do NOT use for topic selection (use paper-topic-selector first)."
license: Apache-2.0
compatibility: Stdlib only. --arxiv makes a real HTTPS call to export.arxiv.org (20s timeout, one 429 backoff retry); on any network/parse failure it falls back to MOCK data and flags it via top-level data_source/warning. SKILLKIT_MOCK=1 forces mock (no network).
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-15"
---

# Lit Review

Scan literature for a topic and produce a structured review skeleton.

## When to Use

- Starting the related-work section of a paper
- Mapping who-cited-whom in a subfield
- Summarizing 10-30 papers into a comparison table

## Quick Use

```bash
python3 scripts/lit_review.py --topic "LLM agents" --venues "ACL,NeurIPS" --max 20
python3 scripts/lit_review.py --topic "diffusion models" --output review.json
```

## Output

JSON with per-paper entries (title/venue/year/summary), a relationship map,
and gap callouts you can feed into the writing phase.

## Chain Position

上游接 paper-topic-selector；跑完把 gap callouts 交给正文写作，
图表需求移交 figure-maker 或 pub-plotter，LaTeX 组装移交 latex-formatter。

## Honesty Note

`--arxiv` now calls the **real arXiv API** (Atom XML, timeout 10s). Output top-level
`data_source` is `"arxiv"` (real retrieval) or `"mock"` (synthetic). Network/parse
failure **auto-falls-back to mock** with a top-level `warning` — such results MUST
be labeled 模拟数据, never presented as real retrieval. Set `SKILLKIT_MOCK=1` to
force mock (CI/offline). arXiv does not provide citation counts: `citations` is
always 0 for arXiv results, and `--venues` filtering only applies to mock data.
