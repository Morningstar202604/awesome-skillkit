---
name: arch-diagram
description: "Generate paper-style architecture/framework diagrams as compile-ready TikZ (LaTeX) plus well-formed editable SVG: pipelines with row/wrap/stack layouts, per-block colourblind-safe colours, automatic LaTeX/XML escaping. Use when the user asks to draw an architecture diagram / method overview figure / framework diagram / draw a flowchart / pipeline diagram / generate a methods-section figure / block diagram. Do NOT use for data charts (use pub-plotter) or neuron-level networks (use neural-net-draw)."
license: Apache-2.0
compatibility: Stdlib only; requires python3; outputs TikZ source and SVG, no LaTeX compile required.
metadata:
  version: "2.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-21"
---

# Arch Diagram (SOTA)

Generate method-overview diagrams (TikZ + valid SVG) for the "Model Architecture" figure.

> **v1's three hard bugs are fixed**: ① TikZ wrote `\sffootnotesize`, which is **not a valid LaTeX command** (compile always errors with Undefined control sequence) -> changed to `\footnotesize`; ② SVG referenced `url(#arrow)` but **never defined a marker** (arrows didn't render) -> now outputs `<defs><marker id="arrow">`; ③ all blocks crammed on one line -> added `row` / `wrap` / `stack` layouts.

## Input Checklist

| Input | Required | Notes |
|------|------|------|
| diagram type | yes | `--type pipeline` (module flow) / `nn` (layered schematic) / `svg` (pure SVG) |
| blocks or layers | conditional | pipeline uses `--blocks "Encoder,Decoder,Head"`, supports `Label#color` (`blue/orange/green/red/purple/gray/yellow/cyan`); nn uses `--layers` |
| layout | no | `--layout row` (default) / `wrap`/`stack`; `wrap` pairs with `--per-row 3` |
| output format | no | `--format tikz` (default) / `svg` |
| output path | no | `--output arch.tex`; default writes `/tmp/arch.tex` |

When missing, ask everything at once: "Please provide: ① diagram type (pipeline / nn / svg) ② block names or layer spec ③ layout (row/wrap/stack; choose wrap when there are many blocks) ④ output path (default `/tmp`)."

## Pre-flight Checks
```bash
python3 --version                       # expect >= 3.8, else error and STOP
test -f scripts/arch_diagram.py && echo OK   # expect OK printed, else script missing STOP
```
If `python3` is missing -> prompt to install Python >=3.8; if the script is missing -> say this skill's directory is incomplete and don't continue.

## Workflow

### Step 1: Generate a Pipeline / Block Diagram
```bash
python3 scripts/arch_diagram.py --type pipeline --blocks "Encoder,Decoder,Head" --output arch.tex
python3 scripts/arch_diagram.py --type pipeline --blocks "A,B,C,D,E" --layout wrap --per-row 3 --format svg --output arch.svg
python3 scripts/arch_diagram.py --type pipeline --blocks "Input#green,Encoder#blue,Head#red" --output arch.tex
```
Expected: JSON output containing `output`, `format`, `layout`, `n_blocks`, `blocks`, `escaped` (whether any label was escaped), `font_command: "\\footnotesize"`, `compilable: true` (TikZ) or `has_marker_def`/`valid_root`/`editable: true` (SVG).
If it fails: `--blocks` empty -> the script uses default blocks (Data/Feature/Model/Loss); an illegal color name -> falls back to `blue`, no error.

### Step 2: Generate a Layered Schematic (nn)
```bash
python3 scripts/arch_diagram.py --type nn --layers "input(256)" "hidden(128)" "output(10)" --output nn.tex
```
Expected: JSON with `n_layers`, `layers`, `note`.
If it fails: omitting `--layers` uses `input(4)/hidden(8)/hidden(4)/output(2)`.
**Note**: this mode is only a schematic dot grid — for publication-grade neuron-level network diagrams use **neural-net-draw** (the script's `note` says so too).

### Step 3: Compile / Open to Verify
```bash
pdflatex -interaction=nonstopmode arch.tex        # TikZ: needs \usepackage{tikz} + \usetikzlibrary{arrows.meta,positioning}
python3 -c "import xml.etree.ElementTree as ET; ET.parse('arch.svg')"   # SVG: verify the XML is valid
```
Expected: TikZ produces a PDF with exit code 0; SVG parses without exception.
If it fails: `Package tikz Error` -> add the package to the preamble; SVG parse failure -> a label contains an unescaped character; check the `escaped` field.

## Parameter Quick Reference

| Parameter | Value | Notes |
|------|------|------|
| `--type` | pipeline / nn / svg | Diagram type, default pipeline |
| `--blocks` | comma-separated | Pipeline block names, supports `Label#color` |
| `--layers` | multiple `name(size)` | nn layer spec, e.g. `input(4) hidden(8)` |
| `--layout` | row / wrap / stack | Arrangement, default row |
| `--per-row` | int | Blocks per row when `--layout wrap`, default 3 |
| `--format` | tikz / svg | default tikz; forced to svg when `--type svg` |
| `--output` | path | Output file, default `/tmp/<type>.tex` |

## Failure Remediation Table

| Symptom / Error Code | Cause | Remedy |
|------------|------|------|
| Output file empty / not generated | No `--output` and `/tmp` isn't writable | Explicitly specify a writable `--output` |
| TikZ reports `Undefined control sequence` | Used an illegal font-size command (v1's `\sffootnotesize` was one) | This version fixes it to `\footnotesize`; when styling custom, only use LaTeX standard font sizes |
| TikZ compile error | Preamble missing tikz or libraries | Add `\usepackage{tikz}` + `\usetikzlibrary{arrows.meta,positioning}` |
| Arrows don't show in browser/Inkscape | SVG marker undefined (v1 bug) | This version outputs `<defs><marker id="arrow">`; if still not shown, check `has_marker_def` |
| SVG won't open in an editor | A label has unescaped `&`/`<`, or `--format svg` wasn't used | This version auto-escapes; self-check the XML with `ET.parse` |
| After compiling, arrows cross boxes and cover text | Default anchor and node spacing insufficient | When there are many blocks, switch to `--layout wrap` or `stack` to reduce horizontal squeezing |
| TikZ text overflows the node box | Label too long | Shorten the label, or use `\\` inside the label to wrap manually |
| Chinese text renders as boxes in the SVG | The preview environment lacks Chinese fonts | Use in-figure English labels, or install fonts before opening the SVG |

## Delivery Standard

Success: for TikZ the JSON has `compilable: true` and no illegal command like `\sffootnotesize`; for SVG `valid_root: true` and `has_marker_def: true`, and it parses through an XML parser.
Artifact name: e.g. `arch.tex` / `arch.svg` / `nn.tex`, determined by `--output`.
Save location: the caller's current directory or the `--output` path.
Verification: TikZ compiles with `pdflatex` (or visually confirm it contains `\begin{tikzpicture}` and `\end{tikzpicture}`); SVG parses with `ET.parse` or opens in a browser.

## References

No external reference files; the generation logic is built into `scripts/arch_diagram.py` (`generate_tikz_pipeline` / `generate_svg_pipeline` / `generate_neural_net`), escaping in `escape_latex` / `escape_xml`, layout in `_positions`, and the colourblind-safe palette in `PALETTE` (same source as pub-plotter).

## Chain Position

One of the figure sources alongside pub-plotter; artifacts feed uniformly into latex-formatter for assembly. Neuron-level network structure is handed off to neural-net-draw.
