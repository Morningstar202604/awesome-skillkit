---
name: anti-defensive
description: "Detect defensive academic writing and classify each hit as tighten vs retain: over-hedging (double 'may/might'), self-deprecating framing, vague attribution 'to the best of our knowledge', filler phrases — but hedges sitting next to statistical-uncertainty context (confidence interval / p-value / variance / sample size) are marked retain and never penalized. Reports hedge density per 100 words with line:col locations. Use when the user asks if the paper tone is too weak / remove defensive phrasing / strengthen statements / stop being so tentative / de-hedge text / make statements firmer / remove 'may possibly'. Do NOT use for removing AI-flavored cliches (use ai-humanizer) or LaTeX formatting (use latex-formatter)."
license: Apache-2.0
compatibility: Stdlib only; requires python3; reads --text or --file, optional --output.
metadata:
  version: "2.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-21"
---

# Anti-Defensive (SOTA)

Detect defensive/hedged phrasing in academic text and **distinguish what to tighten from what to retain** — the old version treated "every qualifier as a problem", which would wrongly rewrite statistical conclusions into bare assertions.

> **Honest Disclosure**: only hits with `action == "tighten"` are deducted; `action == "retain"` means the qualifier appears near a **statistical-uncertainty context** (confidence interval / p-value / variance / sample size / distribution shift / estimator) and is a **reasonable statistical qualifier** — deleting it is an academic error, not a style improvement.

## Input Checklist

| Input | Required | Notes |
|------|------|------|
| text to process | yes | Pass directly with `--text "..."`, or read a file with `--file draft.md`; if `--file` doesn't exist, rc=1 |
| context window | no | `--context-window 80` (default 80 chars): scan this many chars before/after a hit to find statistical context |
| output path | no | `--output report.json` saves JSON; default prints to stdout |

When missing, ask everything at once: "Please provide: ① the text to process (paste directly or give a file path) ② whether to save to disk (--output path). Otherwise defaults: JSON to stdout."

## Pre-flight Checks
```bash
python3 --version                          # expect >= 3.8, else error and STOP
test -f scripts/anti_defensive.py && echo OK   # expect OK printed, else script missing STOP
test -f "$FILE" && echo FILE_OK            # only when using --file; if missing rc=1, STOP first
```
If `python3` is missing -> prompt to install Python >=3.8; if the script is missing -> say this skill's directory is incomplete and don't continue.

## Workflow

### Step 1: Load and Detect the Text
```bash
python3 scripts/anti_defensive.py --file draft_section.md
python3 scripts/anti_defensive.py --text "Our results suggest that the method may possibly improve"
```
Expected: JSON output containing `score`, `status`, `method` (`pattern+context-classifier`), `issues[]`, `n_flags` (number of categories to tighten), `n_retained_only`, `hedge_density_per_100w`, `hedges_total`, `words`, `tighten_hits`, `retain_hits`, `note`. Each `issues[]` item has `type`/`issue`/`fix`/`severity`/`count`/`action` (`tighten`/`retain`)/`retained`/`tightened`/`positions`/`examples`.
If it fails: `Need --text or --file` -> no input given; return to the input checklist; rc=1 -> the `--file` path doesn't exist.

### Step 2: Read the Verdict and Rewrite

- `status == "clean"` (`score >= 80`) -> pass.
- `status == "rewrite_needed"` -> **only change items with `action == "tighten"`**, following `issues[].fix`:

| type | Meaning | Remedy |
|------|------|------|
| `double_hedge` | "may possibly" double hedge | Keep one qualifier; if the conclusion is statistical, keep `may` and add a CI |
| `vague_attribution` | "to the best of our knowledge" | Rewrite to cite a survey/benchmark to establish the gap |
| `filler_phrase` | "it should be noted that" | Delete outright; state the fact |
| `weak_self_criticism` | "some limitations exist" | Write it specifically with evidence: `Accuracy drops 3% on X (Table 7)` |
| `editorializing` | "unfortunately" / "not surprisingly" | Strip subjectivity; state results neutrally |
| `undersell` | "a minor improvement" | Report the number: `1.2% improvement` |

Expected: each `issues` item is ready to apply directly, and `retain` items are clearly marked as non-deletable.
If it fails: still `rewrite_needed` after rewriting -> review `double_hedge` and `weak_self_criticism` (the two highest-weight deduction categories).

### Step 3: Archive (Optional)
Expected: `anti_defensive_report.json` exists and is valid JSON.
If it fails: path not writable -> switch to a writable directory and retry.

## Parameter Quick Reference

| Parameter | Value | Notes |
|------|------|------|
| `--text` | string | Pass the text to detect directly |
| `--file` | path | Read a text / .md / .tex file; rc=1 if missing |
| `--context-window` | int | How many chars before/after each hit to scan for statistical context, default 80 |
| `--output` | path | Write JSON results to a file |

## Failure Remediation Table

| Symptom / Error Code | Cause | Remedy |
|------------|------|------|
| rc=1, `File not found` | The `--file` path doesn't exist | Verify the path and retry |
| `Need --text or --file` | No input provided | Return to the input checklist and complete it |
| Tone too hard after rewriting, reads like assertion | Deleted qualifiers straight into bare assertions | Only delete `action=tighten` items; `retain` items must stay |
| A conclusion that should stay cautious got rewritten | 'may' itself is a reasonable statistical qualifier | Raise `--context-window` so it's recognized as `retain`, or keep it manually |
| Empty `issues` but low score | Impossible (score is only deducted by tighten_hits) | Check whether you misread `hedge_density_per_100w` — it's a **metric**, not a deduction |
| The same `fix` hits repeatedly | The rewritten text wasn't written back to the original `--file` | Confirm the edits are saved before rerunning, so you're not rewriting against stale text |

## Delivery Standard

Success: `status` is `clean`, or you've completed the rewrite per `rewrite_needed`'s `fix` (and all `retain` items preserved verbatim).
Artifact name: `anti_defensive_report.json` (if `--output` is given).
Save location: the caller's current directory or the `--output` path.
Verification: `python3 -c "import json;d=json.load(open('<output>'));assert d['method']=='pattern+context-classifier'"` passes.

## References

Detection rules (`DEFENSIVE_PATTERNS`), statistical-context judgment (`LEGIT_CONTEXT`), and the hedge lexicon (`HEDGE_LEXICON`) are built into `scripts/anti_defensive.py`; no external reference file needed.

## Chain Position

This skill handles "defensive tone", alongside ai-humanizer (which handles "AI tone"); after rewriting, feed it back to latex-formatter for re-check, and finally tex-cleaner closes out.
