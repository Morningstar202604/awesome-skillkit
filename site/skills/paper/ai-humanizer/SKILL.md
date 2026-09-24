---
name: ai-humanizer
description: "Strip AI-flavored writing from academic text on two axes: lexical tells (cliches like 'delve'/'leverage'/'state-of-the-art' spam, empty intensifiers, over-qualification, repetitive openers) AND structural tells (low sentence-length burstiness, consecutive same openers, low lexical diversity, repeated 5-grams), each hit located by line:col. Use when the user asks to remove AI flavor / reduce AI traces / de-cliche academic text / remove AI tone / humanize text / de-robot writing / lower AI-detection rate. Do NOT use for defensive/hedging tone (use anti-defensive) or pure LaTeX formatting (use latex-formatter)."
license: Apache-2.0
compatibility: Stdlib only; requires python3; reads --text or --file, optional --report / --output.
metadata:
  version: "2.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-21"
---

# AI Humanizer (SOTA)

Detect and flag AI-flavored academic writing on two layers: **lexical** (`AI_PATTERNS`) + **structural** (sentence-length burstiness, repeated openers, lexical diversity, n-gram repetition), with every hit located by `line:col`.

> **Honest Disclosure (must read)**: AI text detectors remain **unreliable** in 2026 (high false-positive rates; OpenAI shut down its classifier in 2023; many universities explicitly say detector scores cannot be evidence of academic misconduct). This tool measures **stylistic traces**, not **authorship** — output is only for **rewriting suggestions** and MUST NOT be used to make accusations. The output JSON's `detector_note` field hard-codes this disclosure, and `--report` prints it too.

## Input Checklist

| Input | Required | Notes |
|------|------|------|
| text to process | yes | Pass directly with `--text "..."`, or read a file with `--file draft.tex` (if the `--file` path doesn't exist it falls through to the `--text` branch; neither given => rc != 0) |
| report mode | no | `--report` prints a human-readable summary; otherwise JSON output |
| output path | no | `--output report.json` saves JSON; default prints to stdout |

When missing, ask everything at once: "Please provide: ① the text to process (paste directly or give a file path) ② whether you want a human-readable report (--report) ③ whether to save to disk (--output path). Otherwise defaults: JSON only to stdout."

## Pre-flight Checks
```bash
python3 --version                       # expect >= 3.8, else error and STOP
test -f scripts/ai_humanizer.py && echo OK   # expect OK printed, else script missing STOP
```
If `python3` is missing -> prompt to install Python >=3.8; if the script is missing -> say this skill's directory is incomplete and don't continue.

## Workflow

### Step 1: Load and Detect the Text
```bash
python3 scripts/ai_humanizer.py --file draft.tex --report
python3 scripts/ai_humanizer.py --text "Our novel framework leverages state-of-the-art methods"
python3 scripts/ai_humanizer.py --file draft.tex --output humanize_report.json
```
Expected: JSON (without `--report`) or a human-readable summary (with `--report`), containing `score`, `status`, `method` (`lexical+structural`), `issues[]` (lexical, with `positions`), `structural[]` (structural), `metrics{}` (`burstiness`/`max_opener_run`/`type_token_ratio`/`repeated_5grams`/`n_sentences`), `detector_note`.
If it fails: `Need --text or --file` -> no input given or the file doesn't exist; go back to the input checklist and complete it.

### Step 2: Read the Verdict and Rewrite

- `status == "clean"` (`score >= 85`) -> pass; `needs_edit` -> fix item by item per `issues[].fix_hint` + `structural[].fix_hint`.
- Clear **high** items first (`buzzwords` / `template_phrases` / `llm_verb_spam`), then structural items:

| Structural Item | Threshold | Meaning | Remedy |
|--------|------|------|------|
| `low_burstiness` | burstiness < 0.35 | Sentence length too uniform (a typical LLM tell) | Alternate long and short sentences; open conclusions with short ones |
| `opener_repetition` | >=3 consecutive sentences with the same opener word | Mechanical rotation of transition words | Change the transition style or drop the transition word outright |
| `low_lexical_diversity` | TTR < 0.35 and >=20 sentences | Vocabulary too narrow / templated syntax | Check repeated sentence patterns; merge or rewrite |
| `repeated_ngram` | The same 5-gram appears >=2 times | A phrase recurs verbatim | Dedupe or merge those sentences |

Expected: each `issues` item has `type`/`matches`/`severity`/`positions`/`fix_hint`, ready to apply directly.
If it fails: still `needs_edit` after rewriting -> re-check the high items and newly appeared structural items; don't just look at the total score.

### Step 3: Archive (Optional)
Expected: `humanize_report.json` exists and is valid JSON.
If it fails: path not writable -> switch to a writable directory and retry.

## Parameter Quick Reference

| Parameter | Value | Notes |
|------|------|------|
| `--text` | string | Pass the text to detect directly |
| `--file` | path | Read a text / .tex file |
| `--report` | flag | Print a human-readable summary (with structural metrics and honest disclosure) instead of JSON |
| `--output` | path | Write JSON results to a file |

## Failure Remediation Table

| Symptom / Error Code | Cause | Remedy |
|------------|------|------|
| `Need --text or --file` | No input provided | Return to the input checklist and complete it |
| Empty `issues` but low score | Deductions come from `structural` (the structural layer) | Look at `structural[]` and `metrics{}`; it's not that the word list missed something |
| `burstiness` is `null` | Fewer than 3 sentences (variance can't be computed) | Normal; short text isn't analyzed for sentence length |
| File read failure | Path doesn't exist / encoding error | Verify the `--file` path actually exists |
| Score drops after rewriting | Deleting old wording introduced new template patterns | Rerun detection, focus on newly appeared high items; don't just watch the total score |
| Chinese paragraphs false-flagged | The word list centers on high-frequency English AI words; Chinese rules are coarse | Judge Chinese hits manually; if a false positive, note the reason and ignore it |
| Score looks normal but it still reads like AI wrote it | Static analysis can't catch argumentation logic or information-density problems | This tool only covers the lexical + shallow-structural layer; leave deep issues to a human; don't trust the score alone |

## Delivery Standard

Success: `status` is `clean`, or you've completed the rewrite per `needs_edit`'s `fix_hint`.
Artifact name: `humanize_report.json` (if `--output` is given).
Save location: the caller's current directory or the `--output` path.
Verification: `python3 -c "import json;d=json.load(open('<output>'));assert d['method']=='lexical+structural'"` passes.
Honest rule: under no circumstances may this tool's output be treated as evidence that "the author is AI".

## References

Detection rules (`AI_PATTERNS`), structural metrics (`structural_metrics`), and the locator (`_positions`) are built into `scripts/ai_humanizer.py`; no external reference file needed. The stop-word list is in `STOPWORDS`.

## Chain Position

This skill handles "AI tone", alongside anti-defensive (which handles "defensive tone"); after rewriting, hand off to tex-cleaner for final cleanup.
