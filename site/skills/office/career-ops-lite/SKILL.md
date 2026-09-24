---
name: career-ops-lite
description: >-
  Score a job posting against your resume (per-requirement A-F grades + a 0-5
  holistic score), then draft a tailored cover-letter block and a tracker entry.
  Offline, human-in-the-loop: it evaluates and drafts, it never submits. Use
  when the user asks to evaluate a job posting / should I apply / job match /
  tailor resume / career pipeline / track applications / ATS fit / cover letter
  draft. Do NOT use for scraping job portals or auto-applying (out of scope +
  compliance); this is scoring + drafting only.
license: Apache-2.0
compatibility: Plain text + Python offline; no network, no Playwright; scoring is heuristic word matching, final judgment stays with the human
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: office
  pattern: script
  tier: standard
  verified-date: "2026-09-20"
---

# Career Ops Lite (Job Evaluation + Tailoring + Tracking)

Score a JD text against your resume bullet points into **per-requirement A-F
grades + a 0-5 total + a decision recommendation**, then produce a tailored
cover-letter snippet and a tracker entry. Adapted from santifer/career-ops (MIT)
with its "evaluate first, don't spray-and-pray" philosophy, trimmed to a
**fully offline version that never touches recruiter-site logins**.

Core judgment: the biggest value of a job-search system isn't "help you
apply"—it's "help you **don't apply blindly**". Evaluate first, tailor second,
track third; the human stays in the loop throughout—**never auto-submits an
application**.

> Red lines: dry-run by default only prints scores; `--write` writes the JSON
> report; zero network, zero credentials; no application is ever sent.

## Input Checklist

| Input | Required | Notes |
|---|---|---|
| JD text file | yes | Job description (plain text/.md) |
| Resume bullet file | yes | Your skills/experience bullets |
| Weights JSON | no | Override the five-dimension weights |

## Pre-flight Checks

1. Can resume bullets be **word-matched**? (Scoring is **heuristic word-level**,
   not LLM semantics—keywords must line up: if the JD says "React", your resume
   must also say "React".)
2. Is there a level signal (junior/mid/senior/staff) in the JD? If not,
   `level_fit` defaults to neutral 0.4.
3. `comp_band` / `domain_match` / `stability` all **default to 0.5**; you must
   supply human-estimated values and rerun.

## Workflow

```bash
# 1. Dry run: scoring + per-requirement A-F
python3 scripts/job_scorer.py --jd ./jd.txt --resume ./me.txt

# 2. Override weights (weight match higher)
python3 scripts/job_scorer.py --jd ./jd.txt --resume ./me.txt \
  --weights ./config/weights.json

# 3. Write JSON report (feed to tracker / Notion / human review)
python3 scripts/job_scorer.py --jd ./jd.txt --resume ./me.txt \
  --write -o ./report.json
```

Only recommend applying when `score_5 >= 4` (career-ops' "filter, not
spray-and-pray" principle); skip outright when < 3.

## Delivery Criteria

- Every requirement has an A-F grade + a readable explanation (script output)
- Five-dimension weights are overridable and recomputable
- JSON report contains `requirements`/`grade_counts`/`dimension_scores`/`score_5`/`verdict`
- **No auto-application action is ever produced**

## Failure Handling Table

| Symptom | Root Cause | Action |
|---|---|---|
| All grades C/F | Resume keywords don't match JD wording | Align terminology (JD says "Go", you wrote "golang") |
| Level not detected | JD doesn't state level | Fill in manually, or add level words to the JD text |
| comp/domain/stability all 0.5 | Default values | Estimate manually, write into `--weights` or edit JSON |
| Weights JSON errors | Malformed format | Use `config/weights.example.json` as template |
| Wants "auto-apply" | Out of scope + compliance risk | This skill only evaluates/tailors; submission is human |

## References

- Scoring dimensions and weights explanation: [references/scoring.md](references/scoring.md)
- Weights template: [config/weights.example.json](config/weights.example.json)

## Pipeline Position

- Upstream: `resume-tailor` (tailor resume bullets first, then feed in)
- Downstream: `meeting-notes` / manual tracker (archive the JSON report into the pipeline)
