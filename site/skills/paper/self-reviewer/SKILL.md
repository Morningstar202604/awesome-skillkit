---
name: self-reviewer
description: "Simulate a peer review pass on your own draft: structural gates + ML reproducibility rubric (statistical significance, ablation, baselines, code/data/seeds), each check with reviewable evidence. Use when simulating a review / self-checking a paper / pre-submission check / reviewer-perspective check / paper structure self-review / checking whether it is ready to submit / after receiving reviewer comments that need self-checking. Do NOT use for LaTeX formatting cleanup (use latex-formatter) or adapting to a journal template (use journal-adapt) or writing the paper itself."
license: Apache-2.0
compatibility: Stdlib only; reads .tex or plain-text drafts. Optional LLM evidence via --llm-evidence JSON.
metadata:
  version: "2.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-21"
---

# Self Reviewer (SOTA)

Before submission, be your own reviewer #4: structural gates + ML reproducibility rubric, with every check item backed by **reviewable evidence snippets** (not just a boolean), and uncertain items explicitly flagged as "needs LLM/human review".

> Honest disclosure: default `method=keyword-fallback` (pure string/word-count statistics, reproducible offline); when you provide `--llm-evidence` (JSON: `{check: {evidence, confidence}}`) it switches to `method=llm-evidence`, using the model's evidence + confidence instead of keyword hits. **Regardless of method, when `uncertain` is non-empty, `status` is always `needs_work`; you must not conclude from the score alone.**

## Input Checklist

| Input | Required | Notes |
|------|------|------|
| paper file | yes | `--paper draft.tex` (.tex or plain-text draft); **rc=1** if missing |
| LLM evidence | no | `--llm-evidence llm_review.json` (`{check: {evidence, confidence}}`); if missing, falls back to keywords |
| full checklist | no | `--checklist` only prints the four-category checklist JSON and exits, no review |
| output path | no | `--output review.json`; default prints to stdout |

When missing, ask everything at once: "Please provide: ① paper file path `--paper` ② whether to provide `--llm-evidence` (otherwise keyword fallback) ③ whether you only want to see the checklist `--checklist` ④ whether to save `--output`."

## Pre-flight Checks
```bash
python3 --version                            # expect >= 3.8, else error and STOP
test -f scripts/self_reviewer.py && echo OK  # expect OK printed, else script missing STOP
test -f "$PAPER" && echo PAPER_OK            # expect PAPER_OK; if missing the script rc=1, STOP first
```

## Workflow

### Step 1: Run the Structure + Rubric Review
```bash
# keyword fallback (reproducible offline)
python3 scripts/self_reviewer.py --paper draft.tex
# LLM-evidence augmented
python3 scripts/self_reviewer.py --paper draft.tex --llm-evidence llm_review.json --output review.json
```
Expected: JSON output containing `word_count`, `score` (0-100), `method` (`keyword-fallback`/`llm-evidence`), `passed[]`, `failed[]`, `uncertain[]`, `evidence{}`, `status`, `next_steps[]`, `file`; if the file doesn't exist, `{"error": "File not found: <path>"}` and **rc=1**.
If it fails: rc=1 -> check the `--paper` path and retry; output isn't JSON -> check whether the file is readable (non-UTF-8 encoding throws).

### Step 2: Read the Judgment
- **hard gate (failed means needs_work)**: abstract, `\section` count >= 4, has `\cite`/`\bibliography`, word count >= 3000.
- **rubric items (uncertain means needs_work)**: Statistical significance tested / Ablation / Baselines(2+) / Limitations / Reproducibility(seeds,code,data) — a keyword hit or LLM confidence >=0.6 records passed (with `evidence`), otherwise goes to `uncertain` pending review.
- `status == "ready"`: `score >= 80` **and `uncertain` is empty**.
- `status == "needs_work"`: `score < 80` or `uncertain` non-empty; `failed[]`/`uncertain[]` point to what's missing, `evidence{}` gives the hit snippets.
If it fails: `uncertain[]` non-empty -> review each item with LLM/human (add `--llm-evidence` or hand-fix); never finalize on `score` alone.

### Step 3: Use the Checklist to Semantically Check Remaining Items
```bash
python3 scripts/self_reviewer.py --paper draft.tex --checklist
```
Expected: prints the four-category checklist JSON (`structure` / `content` / `writing` / `formatting`, including items the script doesn't auto-check).
If it fails: none (pure printout); the semantic items in the checklist are judged pass/fail by the model against the original text, one by one, with evidence sentences.

### Step 4: Hand Off Downstream
Expected: `ready` (and uncertain empty) -> hand off to journal-adapt to switch the target template, and finally tex-cleaner closes out; `needs_work` -> take `next_steps[]` back to revise the body, then rerun Step 1 to re-check that the score rose.
If it fails: after fixes the rerun score is unchanged -> confirm the edits were actually written back to the same file `--paper` points to.

## Parameter Quick Reference

| Parameter | Value | Notes |
|------|------|------|
| `--paper` | path | Paper file (required), .tex or plain text |
| `--llm-evidence` | path(JSON) | `{check:{evidence,confidence}}`; if missing, keyword fallback |
| `--checklist` | flag | Only prints the four-category checklist JSON and exits |
| `--output` | path | Results JSON output path; default prints to stdout |

## Failure Remediation Table

| Symptom / Error Code | Cause | Remedy |
|------------|------|------|
| rc=1, `File not found` | The `--paper` path doesn't exist | `ls` to confirm the path and retry |
| `uncertain` non-empty but score is high | Rubric items didn't hit keywords | Add `--llm-evidence` or confirm manually; don't mark `ready` on this basis |
| Word count far exceeds expectations | The .bib/comments got counted in the split | This is a static-counting convention, only a lower-bound check; exact typeset word count follows the compiled PDF |
| Non-UTF-8 file read error | Legacy-encoded file | Transcode with `iconv -f GBK -t UTF-8` and retry |

## Delivery Standard

Success: the output JSON's judgment fields are complete (`status`/`score`/`method`/`passed`/`failed`/`uncertain`/`evidence`/`next_steps`), and all `uncertain` items have been human/LLM reviewed; `ready` only when uncertain is empty.
Artifact name: `review.json` (if `--output` is given).
Save location: the caller's current directory or the `--output` path.
Verification: `python3 -c "import json;d=json.load(open('<output>'));assert d['status'] in ('ready','needs_work')"` passes.

## References

No external reference files; the rubric and four-category checklist are built into `scripts/self_reviewer.py`'s `review_paper` / `CHECKLIST` / `KEYWORDS`. Reproducibility checks align with the papers-with-code checklist and IMRaD statistical thresholds.

## Chain Position

Upstream connects to latex-formatter (format passes first). On `needs_work`, return to body revision; on `ready` (uncertain empty), hand off to journal-adapt to switch the target template, and finally tex-cleaner closes out.
