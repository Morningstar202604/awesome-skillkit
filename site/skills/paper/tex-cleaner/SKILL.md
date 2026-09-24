---
name: tex-cleaner
description: "Pre-flight cleanup for arXiv/venue submission: strip comments (escape/verbatim-aware), flag packages installed-but-unused via a command->package map, list missing assets (\\input/\\bibliography/\\includegraphics), undefined refs, TOC leftovers, non-ASCII in TeX source. Learned from google-research/arxiv-latex-cleaner (7k stars). Use when the user asks for pre-arXiv-submission cleanup / clean up a LaTeX project / slim down tex / delete tex comments / check undefined references / latex cleanup / pre-submission packaging check / clean up a tex project / remove extra packages / check undefined refs / arxiv packaging / strip latex comments. Fails with rc=1 when the input file does not exist (or when --clean is given without --output). Do NOT use for fixing LaTeX compilation errors (use latex-formatter) or for writing paper content."
license: Apache-2.0
compatibility: Stdlib only; static scan/clean on .tex files. Never modifies the input file.
metadata:
  version: "2.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-21"
---

# TeX Cleaner (SOTA)

The last mile before the submission zip: comment stripping + unused-package detection + asset inventory + arXiv-ready verdict.

> Honest disclosure: **read-only by default** — without `--clean` it only prints a report and doesn't touch any file; `--clean` **must** come with `--output` (otherwise rc=1; never silently no-ops), and it writes a **new file**, leaving the original untouched. `arxiv_ready` is a static-scan conclusion, **with no compile verification**.

## Input Checklist

| Input | Required | Notes |
|------|------|------|
| TeX source file | yes | `--input draft.tex`; rc=1 if missing |
| clean switch | no | `--clean`; errors out alone, must pair with `--output` |
| output path | no | `--output draft_clean.tex`; only takes effect when `--clean` is also given |
| base directory | no | `--dir`; checks whether `\input`/figures/bib exist (defaults to the directory containing `--input`) |

When missing, ask everything at once: "Please provide: ① input file `--input` ② check-only or also clean ③ if cleaning, the save path `--output`."

## Pre-flight Checks
```bash
python3 --version                           # expect >= 3.8, else error and STOP
test -f scripts/tex_cleaner.py && echo OK   # expect OK printed, else script missing STOP
test -f "$INPUT" && echo TEX_OK             # expect TEX_OK; if missing the script rc=1, STOP first
```

## Workflow

### Step 1: Read-Only Check (dry-run)
```bash
python3 scripts/tex_cleaner.py --input draft.tex
python3 scripts/tex_cleaner.py --input draft.tex --dir paper/   # also checks asset existence
```
Expected: JSON output containing `status` (`"clean"`/`"issues_found"`), `issues[]`, `unused_packages[]`, `assets{groups,missing}`, `removed_comments`, `full_line_comments_removed`, `n_lines_original`, `n_lines_cleaned`, `arxiv_ready` (bool); **no file written** at this point.
If it fails: rc=1 with `{"status":"error","error":"Not found: ..."}` -> check the `--input` path.

### Step 2: Handle Issues by Category

| type | Meaning | Remedy |
|------|------|------|
| `unused_packages` | Package loaded but no command uses it (judged by a command->package map) | Delete `\usepackage`; **note** packages that act implicitly are in the `NEVER_UNUSED` whitelist and won't be flagged |
| `external_files` | `\input`/`\include` references exist | Confirm all external files are in the submission package |
| `missing_assets` | Referenced figures/bib/inputs not found under `--dir` | Add the files or fix the path (the most common omission in submission packages) |
| `low_res_figures` | Figure path contains `lowres` or `.bmp` | Convert to PDF/PNG (>=300dpi) |
| `toc_present` / `lof_present` | `\tableofcontents` / `\listoffigures` | Delete for arXiv submissions |
| `long_urls` | `\url{...}` content >=50 chars | Switch to `\href{url}{short text}` |
| `undefined_refs` | `\ref`/`\eqref`/`\autoref`/`\cref` has no matching `\label` | Add `\label` or delete the reference |
| `non_ascii` | Non-ASCII characters | Replace with LaTeX commands or delete |

If it fails: after fixing, rerun Step 1 until `status: "clean"` and `arxiv_ready: true`.

### Step 3: Write the Cleaned File
```bash
python3 scripts/tex_cleaner.py --input draft.tex --clean --output draft_clean.tex
```
Expected: stdout additionally reports `cleaned_to: "<output>"`; the new file has comments stripped (trailing comments truncated, full-line comments deleted, `\%` and `%` inside verbatim preserved), and **the original draft.tex is byte-for-byte unchanged**. The report does **not** include `cleaned_text` (to avoid feeding body text back).
If it fails: rc=1 with the error mentioning `--output` -> add `--output` and rerun; path not writable -> switch to a writable path.

### Step 4: Hand Off Downstream
Expected: package `draft_clean.tex` together with the files listed in `assets.groups`; if a semantic re-review is still needed, run another pass back through self-reviewer.
If it fails: compile reports a missing file -> check whether the `missing_assets` issue file was omitted.

## Parameter Quick Reference

| Parameter | Value | Notes |
|------|------|------|
| `--input` | path | TeX source file (required) |
| `--clean` | flag | Enable cleaning; must be used with `--output` (else rc=1) |
| `--output` | path | Path to the cleaned **new** file; the original is never modified |
| `--dir` | path | Base directory for asset-existence checks; defaults to the `--input` directory |

## Failure Remediation Table

| Symptom / Error Code | Cause | Remedy |
|------------|------|------|
| rc=1, `Not found` | The `--input` file doesn't exist | Check the path and retry |
| rc=1, error mentions `--output` | Passed `--clean` without `--output` | Give `--clean --output <f>` together |
| `missing_assets` false positive | `--dir` isn't the real project root | Point `--dir` at the directory containing the figures/bib |
| `unused_packages` false positive | The package acts via implicit mechanisms (e.g. `hyperref` rewriting `\ref`) | Add the package to the script's `NEVER_UNUSED`, or manually ignore that row |
| `non_ascii` count is large | Chinese annotations / full-width symbols slipped in | Replace each with a LaTeX command or delete; if the compiler doesn't support them, the count MUST be zeroed |
| Issues won't clear after repeated passes | The file you edited isn't the same one `--input` points to | Confirm you're editing the file `--input` points to, then rerun Step 1 |

## Delivery Standard

Success: `status: "clean"` and `arxiv_ready: true`; if cleaning, the new file at `cleaned_to` exists and the original file is byte-for-byte unchanged.
Artifact name: `draft_clean.tex` or the `--output` name.
Save location: the caller's current directory or the `--output` path.
Verification: `python3 -c "import json,sys;r=json.load(sys.stdin);assert r['arxiv_ready']"` reading the stdout report passes; cleaning correctness is double-checked by "original file unchanged + new file has no trailing comments".

## References

No external reference files; comment stripping (`strip_comments`, escape + verbatim aware), unused packages (`find_unused_packages` + `PACKAGE_COMMANDS`/`NEVER_UNUSED`), and asset inventory (`collect_assets`) logic is built into `scripts/tex_cleaner.py`. Benchmarked against google-research/arxiv-latex-cleaner.

## Chain Position

The closing step across all paper-domain chains (full_paper / quick_draft / polish_only / submit_ready all end with this skill); after closing, if a re-review is needed, return to self-reviewer.
