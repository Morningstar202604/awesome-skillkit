---
name: latex-formatter
description: "Check and normalize paper LaTeX: document class/template sniffing (IEEE etc), balanced environments, unescaped special chars, bibliography presence, and cross-file undefined \\cite/\\ref. Use when the user asks to check LaTeX / paper format check / pre-compile check / typeset a paper / fix LaTeX errors / normalize tex per template / check for unclosed environments / check paper formatting / normalize LaTeX / fix LaTeX errors. Fails with rc=1 when the input file does not exist. Do NOT use for writing paper content or generating figures (use figure-maker / article-drafter)."
license: Apache-2.0
compatibility: Stdlib-only static checks; optional chktex/latexindent/tex-fmt when installed (honest fallback to stdlib otherwise).
metadata:
  version: "2.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-21"
---

# LaTeX Formatter (SOTA)

Gatekeep a LaTeX draft before compile / journal submission: sniff the template, verify environment pairing by name, flag escaping/citation issues, and **cross-file** check for undefined `\cite`.

> Honest disclosure: by default it runs `method=stdlib-fallback` (pure Python, no dependencies, reproducible offline); if the system has `chktex` installed, it layers in real lint and labels `method` as `external-lint`. The script doesn't run pdflatex compilation; `compilable` is for you to verify yourself.

## Input Checklist

| Input | Required | Notes |
|------|------|------|
| draft file | yes | `--input draft.tex` reads a .tex file; **rc=1** if it doesn't exist |
| target template | no | `--template ieee/acm/neurips/generic`, default `ieee` |
| .bib file | no | `--refs refs.bib`, used to cross-file-check whether `\cite` has a matching entry |
| output path | no | `--output clean.json`; default prints to stdout |

When missing, ask everything at once: "Please provide: ① draft file path `--input` ② target template `--template` (optional) ③ whether to provide `--refs` for cross-file citation checking ④ whether to save `--output`. Otherwise defaults: template=ieee, JSON to stdout."

## Pre-flight Checks
```bash
python3 --version                           # expect >= 3.8, else error and STOP
test -f scripts/latex_formatter.py && echo OK   # expect OK printed, else script missing STOP
test -f draft.tex && echo SRC_OK             # only when using --input; if missing the script rc=1 STOP
```
If `python3` is missing -> prompt to install Python >=3.8; if the script is missing -> say the directory is incomplete; if the `--input` file doesn't exist -> the script returns **rc=1**; add the file first.

## Workflow

### Step 1: Run the Format Gate
```bash
python3 scripts/latex_formatter.py --input draft.tex --template ieee --refs refs.bib --output clean.json
python3 scripts/latex_formatter.py --input draft.tex --template neurips
```
Expected: JSON output containing `template`, `class`, `method` (`external-lint`/`stdlib-fallback`), `status`, `issues[]`, `warnings[]`, `suggestions[]`, `external_lint`, `n_lines`.
If it fails: process exits 1 with `{"status":"error","error":"File not found: ..."}` -> the `--input` path doesn't exist; STOP and add it.

### Step 2: Read the Verdict and Fix
- `status == "pass"` (`issues` empty) -> pass; can move downstream.
- `status == "issues_found"` -> fix per `issues[]` and `suggestions[]`:
  - `Unbalanced environment '{xxx}'` (**checked by name** on begin/end counts) -> pair them up one by one;
  - `Citations present but no \bibliography` -> add `\bibliography{refs}` or `\addbibresource`;
  - `Undefined \cite keys` (only checked when `--refs` given) -> add a .bib entry or delete the citation;
  - `Raw & / % / #` -> escape to `\&` / `\%` / `\#`;
  - `Missing \begin{document}` -> add the document structure.
Expected: each `issues` item has locatable text, and `suggestions` give the fix action.
If it fails: still `issues_found` after fixing -> review `issues[]` item by item until empty.

### Step 3: Archive (Optional)
Expected: the JSON file at `--output` exists and is valid.
If it fails: path not writable -> switch to a writable directory and retry.

## Parameter Quick Reference

| Parameter | Value | Notes |
|------|------|------|
| `--input` | path | .tex draft (required) |
| `--template` | ieee / acm / neurips / generic | Target template, default ieee |
| `--refs` | path | .bib; enables cross-file undefined `\cite` checking |
| `--output` | path | Results JSON output path |

## Failure Remediation Table

| Symptom / Error Code | Cause | Remedy |
|------------|------|------|
| Exit 1 + File not found | `--input` doesn't exist | Verify the path exists and retry |
| Exit 1 + refs not found | The `--refs` path doesn't exist | Verify the .bib path or drop the parameter |
| `Unbalanced environment` | `\begin`/`\end` mismatched (checked by name) | Pair up environments one by one |
| `Raw & needs escaping` | Unescaped special characters in the body | Change to `\&`/`\%`/`\#` |
| `Undefined \cite keys` | The `.bib` lacks the matching entry | Add to .bib or delete that citation |
| Compile reports `Undefined control sequence` | Used a macro/command not defined by the template | Add the corresponding `\usepackage` to the preamble, or use a command the template already has |
| Image path not found | Used a relative path, and the compile dir differs from the source dir | Change to a path relative to the tex file, or declare the directory with `\graphicspath` |
| Chinese compile garbled | Engine and font settings mismatch | Switch to xelatex/lualatex with the `ctex` package and recompile |

## Delivery Standard

Success: `status == "pass"` (no issues), or you've completed fixes per `issues_found`.
Artifact name: `clean.json` (if `--output` is given).
Save location: the caller's current directory or the `--output` path.
Verification: `python3 -c "import json;d=json.load(open('<output>'));assert d['status'] in ('pass','issues_found')"` passes.
Honest rule: `method=stdlib-fallback` means no external lint tool, pure Python static check; `method=external-lint` means chktex's real output is layered in (visible in the `external_lint` field).

## References

No external reference files; the template table is built into `scripts/latex_formatter.py`'s `TEMPLATES` (class / options / columns / font_size). Check logic is in `format_latex` (by-name environment pairing + escaping + cross-file references) and `_external_lint` (chktex probe).

## Chain Position

Upstream connects to figure-maker / arch-diagram / neural-net-draw figure outputs; after checks pass, hand off to self-reviewer for content review, then into journal-adapt to switch templates.
