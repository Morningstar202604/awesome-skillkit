---
name: journal-adapt
description: "Adapt a draft to a target venue's submission rules: IEEE / ACM / NeurIPS / ACL / Nature — column-aware page estimate with reference-page accounting, abstract word limit, venue-required sections (incl. NeurIPS/ACL Limitations), banned-phrase screening (e.g. Nature dislikes 'In this paper we' / 'Novel'), citation-style and double-blind checks. Use when the user asks to submit to IEEE / change to Nature style / journal format adaptation / switch conference template / adapt to ACL format / revise a draft for a venue / check banned phrases. Fails with rc=1 when the input file does not exist. Do NOT use for LaTeX template mechanics (use latex-formatter)."
license: Apache-2.0
compatibility: Stdlib only; requires python3; static text checks against per-venue rule tables. Page counts are estimates — always confirm with the official venue template.
metadata:
  version: "2.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-21"
---

# Journal Adapt (SOTA)

Check a draft against the target venue's real submission rules: page count (column-aware), abstract limit, required sections, banned phrases, citation style, double-blind.

> Honest disclosure: page counts are **estimates** — `words_per_page` is a community empirical value under given columns/font size (NeurIPS 1 column ~600 words/page; IEEE/ACM/ACL 2 columns ~950-1000 words/page); **before formal submission you MUST compile with the venue's official template to confirm**. `--template-year` only replaces the year string in the class name; it doesn't guarantee that year's template exists.

## Input Checklist

| Input | Required | Notes |
|------|------|------|
| draft file | yes | `--input draft.tex` (.tex or plain text both work); rc=1 if it doesn't exist |
| target venue | no | `--target ieee_conf`/`acm`/`neurips`/`acl`/`nature` (aliases `ieee`/`nips`/`emnlp`...), default `ieee_conf` |
| template year | no | `--template-year 2026`: replaces the year in class names like `xxx_2025` |
| output path | no | `--output report.json`; default prints to stdout |

When missing, ask everything at once: "Please provide: ① draft file path `--input` ② target venue ③ whether the target-year template has been released ④ whether to save `--output`. Otherwise defaults: target=ieee_conf, JSON to stdout."

## Pre-flight Checks
```bash
python3 --version                          # expect >= 3.8, else error and STOP
test -f scripts/journal_adapt.py && echo OK   # expect OK printed, else script missing STOP
test -f draft.tex && echo SRC_OK            # expect SRC_OK; if missing the script rc=1, STOP first
```
If `python3` is missing -> prompt to install Python >=3.8; if the script is missing -> say the directory is incomplete; if the `--input` file doesn't exist -> rc=1.

## Workflow

### Step 1: Detect Per the Target Venue
```bash
python3 scripts/journal_adapt.py --input draft.tex --target ieee_conf
python3 scripts/journal_adapt.py --input draft.tex --target neurips --template-year 2026
python3 scripts/journal_adapt.py --input draft.tex --target nature --output adapt_report.json
```
Expected: JSON output containing `target`, `class`, `columns`, `score`, `status`, `issues[]`, `words`, `body_words`, `est_pages`, `est_billable_pages`, `page_limit`, `refs_included`, `ref_pages`, `abstract_words`, `abstract_limit`, `ref_style_detected`, `anonymous_ok`, `method`, `notes`.
If it fails: `rc=2` + `unknown target` -> the `--target` value isn't in the rule table; check the value.

### Step 2: Read the Verdict and Revise

- `status == "pass"` (`issues` empty) -> pass.
- `status == "adjust_needed"` -> handle by `issues[].severity` priority (high -> medium -> low):

| type | Meaning | Remedy |
|------|------|------|
| `page_limit` | `est_billable_pages` over the cap (already deducts/includes reference pages) | Trim the body or move proofs to the appendix |
| `missing_abstract` / `abstract_too_long` | Missing abstract / abstract over the venue's limit | Add an abstract; when compressing, cut modifiers not conclusions |
| `missing_section` | Missing a venue-required section (NeurIPS/ACL's Limitations is often missed) | Add the section |
| `banned` | Hit a venue banned phrase (e.g. Nature's "Novel", "In this paper we") | Rewrite into a statement with concrete evidence |
| `ref_style` | Detected citation style doesn't match the venue | Regenerate references with the venue's `.bst`/`.bbx` |
| `anonymity` | An author block / acknowledgements appear in a double-blind venue | Delete authors and acknowledgements in the submission version |

Expected: each issue gives `type`/`severity` and locatable info (the specific banned phrase, missing section, billable pages).
If it fails: still `adjust_needed` after revising -> clear high first, then medium/low.

### Step 3: Archive (Optional)
Expected: the JSON file at `--output` exists and is valid.
If it fails: path not writable -> switch to a writable directory and retry.

## Parameter Quick Reference

| Parameter | Value | Notes |
|------|------|------|
| `--input` | path | Draft file (required) |
| `--target` | ieee_conf / acm / neurips / acl / nature (+ aliases) | Target venue, default ieee_conf |
| `--template-year` | 4-digit year | Replace the class-name year string, e.g. `neurips_2025` -> `neurips_2026` |
| `--output` | path | Results JSON output path |

## Failure Remediation Table

| Symptom / Error Code | Cause | Remedy |
|------------|------|------|
| rc=1, File not found | `--input` doesn't exist | Verify the path and retry |
| rc=2, `unknown target` | Illegal `--target` | Use a venue or alias from the rule table |
| Page estimate doesn't match the template compile result | The estimate is empirical, doesn't include figure/table placeholders | Trust the official template compile result; this tool is early warning only |
| `missing_section` false positive | Section heading localized (written in Chinese or renamed) | Use the English heading the venue requires |
| `anonymity` false positive | Anonymized writing like `\author{Anonymous Submission}` | That writing doesn't trigger it; if still flagged, check for acknowledgements or body mentions of the affiliation |
| Reference format flagged non-compliant | The bib is still the previous style (numbered vs author-year) | Regenerate references with the target venue's style file |

## Delivery Standard

Success: `status == "pass"`, or you've completed revisions per `adjust_needed`'s `issues[]`.
Artifact name: `adapt_report.json` (if `--output` is given).
Save location: the caller's current directory or the `--output` path.
Verification: `python3 -c "import json;d=json.load(open('<output>'));assert d['status'] in ('pass','adjust_needed')"` passes.
Honest rule: `method: "column-aware-estimate"` means page counts are column-aware empirical estimates, not a measured compile.

## References

No external reference files; the venue rule table is built into `scripts/journal_adapt.py`'s `JOURNAL_SPECS` (incl. cls/options/columns/font_size/page_limit/refs_included/words_per_page/abstract_max_words/anonymous/ref_style/required_sections/banned/notes). The page model is in `adapt()`; reference splitting in `_split_bibliography()`.

## Chain Position

Upstream connects to self-reviewer's ready judgment; tone polishing can continue to anti-defensive and ai-humanizer, and finally tex-cleaner closes out the submission package.
