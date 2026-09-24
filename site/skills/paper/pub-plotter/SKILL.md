---
name: pub-plotter
description: "Publication-grade plots with REAL journal physical widths (Nature/Science/IEEE/ACM/NeurIPS), Type-42 font embedding (pdf.fonttype=42, arXiv/LaTeX-safe), colorblind-safe palettes by default, and optional real `scienceplots` integration. Covers line / bar / boxplot / heatmap. This is the CANONICAL paper plotting skill — it supersedes `figure-maker`, which is kept only as a compatibility shim. Outputs PDF/PNG. Use when the user asks for journal-style figures / IEEE-style line plots / paper figures / publication-grade charts / camera-ready figures / figures sized to Nature/Science layout / heatmaps / publication plot. Do NOT use for architecture diagrams (use arch-diagram) or neuron-level networks (use neural-net-draw)."
license: Apache-2.0
compatibility: Requires matplotlib (Agg backend). Uses real `scienceplots` if installed, else built-in equivalent rcParams (offline). When matplotlib absent -> status "mock" (no image, MUST tell user).
metadata:
  version: "2.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-21"
---

# Publication Plotter

One-click produce publication-grade figures from a data JSON: **real journal physical widths + Type-42 font embedding + colorblind-safe palette by default**, no hand-tuning rcParams; if the `scienceplots` package is installed it automatically uses the official style.

**This skill is the paper domain's single plotting entry** (`line` / `bar` / `boxplot` / `heatmap`). The same-domain `figure-maker` is deprecated and downgraded to a thin delegation shim (see its SKILL.md); don't add new calls based on it.

> Honest disclosure (two tracks): matplotlib installed -> `status:"success"`, `rendered:true`, the artifact is a real PDF/PNG (with embedded fonts); not installed -> it doesn't error but reports `status:"mock"`, **no image produced**, and you MUST tell the user no figure was generated; don't pass the JSON report as the deliverable.

## Publication-Grade Key Points (Why Plots Are Made This Way)
- **Font embedding**: `pdf.fonttype=42` / `ps.fonttype=42` (Type 42 subset embedding); arXiv / LaTeX won't reject it, and it stays sharp when scaled.
- **Plot to the layout**: `--journal nature_single|science|ieee|acm|neurips` uses real physical widths (Nature single column 3.504"~89mm, Science 4.76", IEEE 3.5"); "design to final size" avoids text being too big/small after inserting back into the layout.
- **Width contract (a silent bug fixed)**: `--style` only controls font size/line width/grid, `--journal` only controls physical width; the two are separated and both explicitly report `width_inches`. The old version stuffed the journal name into `--style` for lookup, and `nature_single`/`science` weren't in the table -> **silently fell back to IEEE 3.5" width while still reporting success**. Now an unknown `--journal` exits with code 2; `--style science` also has its own 4.76" geometry, no longer borrowing ieee. How to verify: read the produced PDF's `/MediaBox`; `--journal science` must be visibly wider than `--journal ieee`.
- **Colorblind-safe**: Paul Tol / Okabe-Ito palettes on by default (`--no-colorblind` to turn off) — a hard review criterion for paper color choices.
- **Vector output**: `.pdf` vector (recommended for submission), `.png` 300 dpi as fallback.

## Input Checklist

| Input | Required | Notes |
|------|------|------|
| data JSON | recommended | `--data data.json`; **if the path doesn't exist the script errors out (no longer silently uses demo data)**; confirm first |
| chart type | no | `--type line\|bar\|boxplot\|heatmap` (default `line`) |
| style | no | `--style ieee\|acm\|neurips\|nature\|science\|colorblind_safe` (default `ieee`) |
| journal layout | no | `--journal nature_single\|science\|ieee\|acm\|neurips` (uses real physical width; unknown value -> exit code 2) |
| palette | no | colorblind-safe by default; `--no-colorblind` to turn off |
| output path | no | `--output fig.pdf`; extension decides the format, default `/tmp/fig_pub_<type>.pdf` |

The data JSON uses keys per chart type (bar optionally takes `errors` for error bars/CI; heatmap optionally takes `annotate`/`cmap`):
```json
{"x":[0,1,2,3],"series":[{"name":"Ours","values":[0.7,0.8,0.85,0.9]}]}
{"labels":["Baseline","Ours"],"values":[0.75,0.85],"errors":[0.02,0.01]}
{"groups":["Baseline","Ours"],"data":[[0.8,0.82,0.78],[0.88,0.91,0.85]]}
{"matrix":[[0.8,0.72,0.65],[0.68,0.85,0.79]],"rows":["A","B"],"cols":["x","y","z"],"xlabel":"method","ylabel":"dataset"}
```
Heatmap defaults: all-positive -> `cividis` (colorblind-safe sequential); contains negatives -> `RdBu_r` (diverging); override with `cmap`, turn off value annotations with `annotate:false`.
When missing, ask everything at once: "Please provide: ① data JSON path `--data` (confirm it exists) ② chart type `--type` ③ style `--style` or layout `--journal` ④ whether you want colorblind-safe (default on) ⑤ output name `--output` (.pdf or .png)."

## Pre-flight Checks
```bash
python3 -c "import matplotlib; print(matplotlib.__version__)"   # missing -> mock track, STOP and tell the user
python3 -c "import scienceplots" 2>/dev/null && echo SCIENCE_OK  # optional; uses the official style if installed
test -f scripts/pub_plotter.py && echo OK
```

## Workflow

### Step 1: Plot
```bash
python3 scripts/pub_plotter.py --type line --journal nature_single --data data.json --output fig_nature.pdf
python3 scripts/pub_plotter.py --type bar --style acm --data data.json --output fig.png
python3 scripts/pub_plotter.py --type boxplot --style colorblind_safe --data data.json --output fig.pdf
python3 scripts/pub_plotter.py --type heatmap --journal ieee --data matrix.json --output fig_hm.pdf
```
Expected: stdout JSON containing `output`, `style`, `journal`, `type`, `rendered:true`, `font_embedded:true`, `colorblind_safe`, `width_inches` (**reported for all four chart types**, used to verify layout width); heatmap additionally has `cmap`, `shape`, `value_range`, `annotated`.
If it fails: matplotlib missing -> `status:"mock"`; `--data` doesn't exist -> the script reports "`--data` file does not exist" (exit code 2); fix the path first; `--journal` typo -> reports "unknown --journal" (exit code 2).

### Step 2: Check the Artifact
Expected: the file at `output` exists and is non-empty (`test -s <output>`); PDF vector-readable, PNG 300 dpi; `font_embedded:true`.
If it fails: figure content doesn't match the data -> check key names (line -> `series`, bar -> `labels`+`values`, boxplot -> `groups`+`data`).

### Step 3: Hand Off Downstream
Expected: experiment-runner's `results.json` can go straight in as `--data`; finished figures go to latex-formatter for inserting into the body (`\includegraphics[width=\columnwidth]{fig.pdf}`).
If it fails: downstream misses a field -> rearrange the data JSON per the "input checklist" key names.

## Parameter Quick Reference

| Parameter | Value | Notes |
|------|------|------|
| `--type` | `line`/`bar`/`boxplot`/`heatmap` | Chart type, default `line` |
| `--style` | `ieee`/`acm`/`neurips`/`nature`/`science`/`colorblind_safe` | Style preset (font size/line width/grid), default `ieee` |
| `--journal` | `nature_single`/`science`/`ieee`/`acm`/`neurips` | **Only overrides preset width with real physical width**; unknown value errors out |
| `--no-colorblind` | flag | Turn off the colorblind-safe palette (default on) |
| `--data` | path | Data JSON; **errors out if it doesn't exist (no longer silent demo)** |
| `--output` | path | .pdf/.png; default `/tmp/fig_pub_<type>.pdf` |

## Failure Remediation Table

| Symptom / Error Code | Cause | Remedy |
|------------|------|------|
| `status: "mock"` | matplotlib not installed | Only report no figure; `pip install matplotlib` and rerun |
| "`--data` file does not exist" (exit code 2) | Wrong path | First `test -f` and fix the path; don't expect silent demo |
| `json.JSONDecodeError` | Invalid JSON data | Locate with `python3 -c "import json;json.load(open('<f>'))"` |
| Text too big/small | Didn't plot to the layout | Add `--journal <target>` to align with the real layout width |
| Figure blurs when scaled / arXiv rejects it | Font not embedded | This script always sets `pdf.fonttype=42`; confirm the output is `.pdf` not `.png` |
| Color choice flagged in review | Used a non-colorblind-safe palette | Keep the default palette; only `--no-colorblind` if custom is truly needed |

## Delivery Standard

Success: `status:"success"` and `rendered:true`, `font_embedded:true`, the `output` image file exists and is non-empty.
Artifact name: `fig.pdf`/`fig.png` or `--output`; if unspecified, `/tmp/fig_pub_<type>.pdf`.
Verification: `test -s <output>` passes; when `status:"mock"` you MUST only deliver the report and declare no figure was produced.

## References

Style presets / real journal widths / plotting logic is built into `scripts/pub_plotter.py`: `JOURNAL_WIDTHS`, `STYLES`, `setup_style` (`pdf.fonttype=42` + optional `scienceplots`), `plot_line`/`plot_bar`/`plot_boxplot`/`plot_heatmap`.
SOTA toolchain: `scienceplots` (official IEEE/Nature/Science presets), `pdf.fonttype=42`/`ps.fonttype=42` (font embedding), Paul Tol / Okabe-Ito colorblind-safe palettes, `cividis`/`RdBu_r` (colorblind-safe sequential/diverging heatmaps), real journal column widths (Nature single column 89mm).

## Chain Position

**The paper domain's plotting entry**: upstream connects to experiment-runner's `results.json`; artifacts go into latex-formatter for assembly, and tex-cleaner closes out the submission. `paper_pipeline.py`'s figures stage has already migrated from `figure-maker` to this skill (plotting per `--journal ieee`).
The same-domain `figure-maker` is a compatibility shim (`deprecated: true`, internally delegating to this skill), kept only for external callers that pinned its CLI; don't write new code on it. `arch-diagram` handles architecture block diagrams and `neural-net-draw` handles neuron-level network diagrams — a complementary division of labor with this skill.
