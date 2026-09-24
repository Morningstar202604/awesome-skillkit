---
name: weekly-report-generator
description: >-
  Auto-draft a weekly report from `git log` + `git diff --stat` over a look-back
  window, structured into the three paragraphs every company expects (done /
  blockers / next week), then let the human fill in the qualitative bits. Use
  when the user asks for a weekly report / daily report / weekly report template
  / auto-write weekly report / status update / sprint summary. Do NOT use for
  monthly business reviews (different scope) or for performance/HR narratives
  (this is a work-log, not a performance doc).
license: Apache-2.0
compatibility: Pure local git operations; no network, no remote; default dry-run; needs python3 + git.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: meta
  pattern: script
  tier: standard
  verified-date: "2026-09-20"
---

# Weekly Report Generator (Weekly Report Auto-Generation)

Pull a week's git activity, auto-fill the "what I did" section, and leave
"blockers / next week" as placeholders for you to fill in manually. It solves:
**the most annoying part of weekly reports isn't writing—it's "can't remember
what I actually did this week."** This skill helps you recall; you only do
qualitative judgment.

> Red lines: pure local git + filesystem; no network, no push; default dry-run,
> `--write` saves.

## Input Checklist

| Input | Required | Notes |
|---|---|---|
| Look-back days | no | Default 7; adjust for biweekly |
| Repo path | no | Default current directory |
| Author name | no | Default `agent` |
| Blockers / next week | no | If not passed, leaves placeholders; can use `--input report.json` structured input |

## Pre-flight Checks

1. Is current directory a git repo? (script checks `.git` exists)
2. Are there commits this week? If not, "what I did" section is empty—normal,
   don't mistake for a bug.
3. Does the company have a fixed weekly report template? Align template section
   names to `done/blockers/next`, or feed via `--input`.

## Workflow

```bash
# 1. Dry run: see auto-filled "what I did" section
python3 scripts/gen_report.py --days 7 --repo ../../.. --author AuthorName   # ../../.. = from skill directory to repo root; write --repo . when running at repo root

# 2. Feed structured input (also writes "blockers/next week")
python3 scripts/gen_report.py --days 7 --input report.json --repo ../../.. --write -o weekly.md

# 3. Biweekly
python3 scripts/gen_report.py --days 14 --repo ../../.. --author AuthorName
```

`report.json` fields (optional):
```json
{
  "done": ["Fixed session drift", "Added 2 security scanners"],
  "blockers": "Dependency approval process slow, blocking P1 launch",
  "next": "Finish e2e scaffold integration into CI"
}
```

## Delivery Criteria

- Three sections complete: what I did (git auto) / blockers (human) / next week (human)
- "What I did" grouped by date, each entry = `date author: subject`
- File can be pasted directly into email / document system

## Failure Handling Table

| Symptom | Root Cause | Action |
|---|---|---|
| `is not a git repo` | Wrong path | Pass `--repo <path>` |
| "What I did" section empty | No commits this week | Normal; increase `--days` or fill manually |
| Sections don't match company template | Section names differ | Use `--input` to feed corresponding fields |
| Author name garbled | git config author inconsistent | Pass `--author` to override |
| Want monthly report | Window too long, too many commits | Change to `--days 30` and trim manually |

## References

- Section conventions and JSON fields: [references/report-fields.md](references/report-fields.md)

## Pipeline Position

- Upstream: daily git work
- Downstream: `meeting-notes` (turn weekly report into team sync minutes)
