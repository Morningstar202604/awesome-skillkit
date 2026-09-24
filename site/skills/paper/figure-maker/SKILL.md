---
name: figure-maker
description: "DEPRECATED — use `pub-plotter` instead. This skill is kept only as a compatibility shim: it preserves the original CLI (--data / --type bar|line|boxplot|heatmap / --output) and delegates to pub-plotter, adding `deprecated: true` / `superseded_by: \"pub-plotter\"` to its output. Kept for repo indexes (manifest/packs/skill_chains) and external callers that pinned the old CLI; the in-repo consumer (`paper_pipeline.py`) has already migrated to pub-plotter. Use when the user asks to plot experiment results / make a paper chart / results plot / turn experimental data into a figure / draw a bar chart — but prefer pub-plotter for anything new (it adds real journal widths, font embedding, and full heatmap support). Do NOT use for neural-network structure diagrams (use neural-net-draw) or architecture diagrams (use arch-diagram)."
license: Apache-2.0
compatibility: DEPRECATED. Requires matplotlib (only indirectly, via pub-plotter). Delegates to `../pub-plotter/scripts/pub_plotter.py`.
metadata:
  version: "3.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: deprecated
  verified-date: "2026-09-21"
  superseded-by: pub-plotter
---

# Figure Maker (DEPRECATED -> pub-plotter)

> **This skill is deprecated.** It fully overlaps with `pub-plotter`, which is a strict superset:
> it supports the same `line`/`bar`/`boxplot` (plus `heatmap`, which this skill never actually implemented), and additionally provides
> **real journal physical widths, Type-42 font embedding, a colourblind-safe palette, and scienceplots integration**.
>
> The body implementation of `figure_maker.py` has now been deleted and replaced with a **thin delegation shim**: the CLI and JSON contract are unchanged,
> internally it calls `pub-plotter`, and stamps `deprecated: true` / `superseded_by: "pub-plotter"` into its output.

## Why Keep It Instead of Deleting Outright

**In-repo consumers have migrated**: the paper-domain orchestrator `paper_pipeline.py`'s figures stage used to point at this skill (the only hard reason not to delete it), and has now been changed to call `pub-plotter` directly (`--journal ieee`). So the reasons to keep the thin shim are now:

1. **Intra-repo compatibility**: the repo-root `manifest.json`, the ai-research-writing `pack.json` under `packs`, `skill_chains.json`, and the generated site `site/` still reference this skill by name; deleting it outright would break these indexes and require a coordinated change.
2. **External callers that pinned the CLI**: this repo is a user-facing skill set; someone may have already written `figure_maker.py --type ... --data ...` into their scripts; the thin shim keeps them from breaking.

The thin shim = remove duplicate implementation + don't break existing consumers + explicitly expose deprecation in output. **It can be deleted outright in the next major version** (then sync `manifest.json` / packs / `skill_chains.json` and rebuild `site/`).

## Migration (Recommended)

Point the call at pub-plotter:

```bash
# old (still works, but with deprecation overhead and one extra hop)
python3 scripts/figure_maker.py --type bar --data results.json --output fig.pdf

# new (recommended)
python3 ../pub-plotter/scripts/pub_plotter.py --type bar --journal ieee --data results.json --output fig.pdf
```

## Behavior Contract (Differences from v1)

| Item | v1 | Now (thin shim) |
|------|----|--------------|
| `line`/`bar`/`boxplot` | self-implemented, hand-set figsize, no font embedding | delegates to pub-plotter -> journal width + font embedding + colourblind-safe |
| `heatmap` | **always `status:"unsupported"`** (never implemented) | **real rendering** (delegates to pub-plotter, cividis / RdBu_r) |
| Output JSON extra fields | — | `deprecated: true`, `superseded_by`, `deprecation_note` |
| `--data` path doesn't exist | silently uses demo data | **errors out (rc=2)** |
| Exit codes | always 0 | 0 success; 2 param/data problem; 1 delegation target missing |
| New pass-through params | — | `--journal`, `--no-colorblind` |

## Input Checklist

| Input | Required | Notes |
|------|------|------|
| data JSON | recommended | `--data results.json`; rc=2 if it doesn't exist |
| chart type | no | `--type bar\|line\|boxplot\|heatmap` (default `bar`, keeping v1's default) |
| journal layout | no | `--journal nature_single\|science\|ieee\|acm\|neurips` (pass-through) |
| palette | no | colourblind-safe by default; `--no-colorblind` to disable (pass-through) |
| output path | no | `--output fig.pdf`; default decided by pub-plotter |

## Failure Remediation Table

| Symptom / Error Code | Cause | Remedy |
|------------|------|------|
| rc=1, `delegation target missing` | `../pub-plotter/scripts/pub_plotter.py` doesn't exist | This repo is incomplete; use the pub-plotter path or restore the directory structure |
| rc=2, `--data file does not exist` | Wrong data path | First `test -f` and fix the path (v1 silently used demo data; don't rely on that) |
| rc=2, `unknown --journal` | The layout name isn't in `JOURNAL_WIDTHS` | Use `nature_single`/`science`/`ieee`/`acm`/`neurips` |
| `status:"mock"` | matplotlib not installed | `pip install matplotlib` and rerun |

## Delivery Standard

Success: `status:"success"` + `rendered:true`, and the `output` file exists and is non-empty.
Artifact name: determined by `--output`.
Verification: `python3 -c "import json;d=json.load(open('<out>'));assert d['deprecated'] is True"` confirms it went through the deprecated shim.
**New code should deliver pub-plotter directly; don't add new dependencies on this skill.**

## References

This skill has no own plotting implementation; all behavior delegates to `../pub-plotter/scripts/pub_plotter.py` (`JOURNAL_WIDTHS` / `STYLES` / `setup_style` / `plot_*`).

## Chain Position

Compatibility placeholder. The paper-domain plotting canon is **pub-plotter**, and `paper_pipeline.py`'s figures stage has **already** migrated to pub-plotter; this skill now only serves in-repo indexes (manifest/packs/skill_chains/site) and external callers that pinned the CLI, and can be deleted alongside the indexes in the next major version.
