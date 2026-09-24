---
name: neural-net-draw
description: "Draw neural-network structure diagrams as compile-ready LaTeX TikZ from a layer spec. Learned from PlotNeuralNet (25k stars). Use when the user asks to draw a network architecture diagram / draw a CNN layer diagram / draw an MLP structure diagram / neural network schematic / neural network diagram / TikZ network diagram / network architecture figure. Do NOT use for pipeline/block diagrams (use arch-diagram)."
license: Apache-2.0
compatibility: Stdlib only; emits TikZ source for the PlotNeuralNet toolchain (compilation requires pgfplots + tikz in the preamble).
metadata:
  version: "2.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-21"
---

# Neural Net Drawer (SOTA)

Generate compile-ready neural-network structure TikZ from a layer spec. Supports two drawing modes:

- **per-neuron** (v1-compatible): draws one dot per neuron per layer (at most 10 visible dots per layer when very wide; layer height capped at 3cm);
- **typed-blocks** (PlotNeuralNet style): draws colored `nnblock`s by layer type (conv/pool/residual/linear/attention/...), closer to a real architecture.

> Honest disclosure: `compilable: true` is an assertion of **static syntactic self-consistency** — the script doesn't run pdflatex; it only mathematically guarantees TikZ self-consistency. Whether compile passes depends on whether the preamble includes pgfplots + tikz.

## Input Checklist

| Input | Required | Notes |
|------|------|------|
| layer spec | yes | `--layers`: comma-separated. Legacy pure-width `"784,512,10"` (default fully-connected) or typed `"784:input,64:conv,64:pool,128:linear,10:output"`. Legal types: `input,conv,pool,residual,linear,fc,attention,dropout,output` |
| figure caption label | no | `--label "CNN+MLP"` (default `Model`; written into the generated file's first-line comment) |
| activation function name | no | `--activation relu` (default `relu`; **only written to output JSON metadata, doesn't change the drawing**) |
| drawing style | no | `--style auto/per-neuron/typed-blocks` (default `auto`: typed -> typed-blocks, otherwise per-neuron) |
| output path | no | `--output net.tex`; by default **always writes to disk** at `/tmp/nn_model.tex` |

When missing, ask everything at once: "Please provide: ① layer spec `--layers` (may include types) ② caption `--label` (optional) ③ whether to specify `--output` (otherwise writes to /tmp/nn_model.tex)."

## Pre-flight Checks
```bash
python3 --version                                # expect >= 3.8, else error and STOP
test -f scripts/neural_net_draw.py && echo OK    # expect OK printed, else script missing STOP
```
If the artifact needs a compile preview: `which pdflatex`, and the preamble needs `\usepackage{pgfplots}` + `\usepackage{tikz}`; without a LaTeX environment, deliver only the .tex source and don't claim compilation was verified.

## Workflow

### Step 1: Generate the TikZ Source
```bash
# legacy (pure width, auto per-neuron)
python3 scripts/neural_net_draw.py --layers "784,512,256,10,1" --label "CNN+MLP" --output net.tex
# SOTA (typed, auto typed-blocks)
python3 scripts/neural_net_draw.py --layers "784:input,64:conv,64:pool,128:linear,10:output" --style typed-blocks
python3 scripts/neural_net_draw.py --layers "512:residual,256:attention,10:output"
```
Expected: stdout prints JSON containing `output` (the actual .tex on-disk path), `layers` (the parsed `w:type` list), `n_params_est`, `method` (`per-neuron`/`typed-blocks`), `compilable: true`, `note`; and the file at `output` exists.
If it fails: `--layers` has a non-integer width or unknown type -> `ValueError`; keep only digits for widths and legal enums for types, then retry.

### Step 2: Check Artifact Boundaries
- `n_params_est` only estimates for **fully-connected/linear** layers as the product of adjacent layers + bias; conv/attn layers depend on kernel size/head count and can't be modeled here, so this tool counts them as 0 and marks the approximation — for exact parameter counts, use model export (`torch`'s `num_parameters()`).
- per-neuron: at most 10 visible nodes per layer (schematic only when layers are very wide), layer height capped at 3cm.
If it fails: the figure doesn't match expectations -> remember this is a layer/module schematic that doesn't express real tensor shapes/convolution kernels; for module-level flowcharts use arch-diagram.

### Step 3: Compile Verification (Optional)
```bash
pdflatex -interaction=nonstopmode net.tex
```
Expected: produces `net.pdf`, exit code 0.
If it fails: `pgfplots.sty not found` -> add `\usepackage{pgfplots}` to the preamble; no right to change the preamble -> deliver the .tex directly and note the dependency.

## Parameter Quick Reference

| Parameter | Value | Notes |
|------|------|------|
| `--layers` | `w` or `w:type` | Per layer (required); type enum above |
| `--label` | string | Caption, default `Model` |
| `--activation` | string | default `relu`, recorded only in JSON, doesn't affect drawing |
| `--style` | auto/per-neuron/typed-blocks | default auto |
| `--output` | path | Output .tex; default fixed `/tmp/nn_model.tex` |

## Failure Remediation Table

| Symptom / Error Code | Cause | Remedy |
|------------|------|------|
| `ValueError: unknown layer type` | The type in `w:type` isn't a legal enum | Only use `input,conv,pool,residual,linear,fc,attention,dropout,output` |
| `ValueError: invalid literal for int()` | `--layers` width contains non-digits | Pass only integers for widths (types use the `:type` suffix) |
| Artifact written to /tmp/nn_model.tex | No `--output` passed | The script defaults to this path; to place it elsewhere you must explicitly pass `--output` |
| `pgfplots.sty not found` | Preamble missing the package | Add `\usepackage{pgfplots}`; note this dependency at delivery |
| Fewer neurons drawn than the layer's number | per-neuron caps at 10/layer and layer height is capped | Expected behavior, not a bug; for the full dot grid / exact height you must modify the script |

## Delivery Standard

Success: the .tex file at stdout JSON's `output` exists, content starting with `\begin{tikzpicture}` and ending with `\end{tikzpicture}`.
Artifact name: `net.tex` or the `--output` name; if unspecified, `/tmp/nn_model.tex`.
Save location: the caller's current directory or the `--output` path.
Verification: `grep -c "\\\\begin{tikzpicture}" <output>` returns 1; when delivering a compiled artifact you MUST attach the note "requires pgfplots + tikz"; if never compiled, don't claim the PDF was verified.

## References

No external reference files; drawing and parameter-estimation logic is built into `scripts/neural_net_draw.py`'s `draw_nn` / `_render_per_neuron` / `_render_typed_blocks` / `_estimate_params`. Benchmarked against PlotNeuralNet (HarisIqbal88).

## Chain Position

Complements arch-diagram as a figure source: network layers go to this skill, module flow goes to arch-diagram. Artifacts feed uniformly into latex-formatter for assembly.
