---
name: session-handoff
description: >-
  Compress a long in-flight session into a cold-start handoff doc so a fresh
  agent (or a future-you, or a teammate) can pick up with zero context: goal,
  done, next, gotchas, key files, one-page cheat sheet. Use when the user asks
  for a handoff / session handoff / write the current state for the next person
  / cold-start pickup / context compression / knowledge transfer. Do NOT use for
  long-term memory across projects (use memory-architect) or for final deliverable
  reports (this is an internal relay, not a finished doc).
license: Apache-2.0
compatibility: Pure local Markdown generation; offline, no network, no credentials; default dry-run.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: meta
  pattern: script
  tier: standard
  verified-date: "2026-09-20"
---

# Session Handoff (Long-Session Cold-Start Handoff)

Compress a half-finished long session into a handoff doc that **the next agent
can pick up with zero context**. Adapted from mattpocock/skills' `handoff`
concept, trimmed to an offline Markdown generator + a "one-page cheat sheet"
skeleton.

Core judgment: **the handoff receiver's biggest cost isn't reading code—it's
"guessing where you got to, what's stuck, which pitfalls to avoid."** This skill
makes these three things explicit: `next steps (ordered)`, `known pitfalls /
don't repeat`, `key file paths`.

> Red lines: default dry-run prints preview; `--write` saves; zero network, zero
> credentials.

## Input Checklist

| Input | Required | Notes |
|---|---|---|
| Goal | yes | Original intent (why this work started) |
| Done | yes | What was done, how far |
| Next steps | yes | Ordered TODOs |
| Known pitfalls | strongly recommended | Pitfalls hit / detours not to repeat |
| Key files | recommended | `--file` can be repeated with paths |
| Run/verify method | recommended | How the receiver runs it, how to verify |

Structured input can also go via `--input handoff.json` (fields:
title/done/next/gotchas/files/repo/verify/blocker), takes priority over same-name
CLI args.

## Pre-flight Checks

1. Are "next steps" **executable in order** (not empty words like "continue")?
2. Are "known pitfalls" specific enough to avoid (not "be careful not to err")?
3. Do key files give **paths** rather than "some file"?

## Workflow

```bash
# 1. Dry run: preview handoff doc
python3 scripts/make_handoff.py --title "P1 Domain Fix" --goal "Fix three-way domain inconsistency" \
  --done "git mv 5 skills; build 143→145" --next "Add CHANGELOG; run validate" \
  --gotcha "Python r''' in heredoc collides with shell EOF" --file skills/ --repo awesome-skillkit

# 2. Write to disk
python3 scripts/make_handoff.py ... --write -o handoff.md

# 3. Via JSON structured input
python3 scripts/make_handoff.py --input handoff.json --write -o handoff.md
```

## Delivery Criteria

- Six sections complete: goal / done / next steps / known pitfalls / key files / one-page cheat sheet
- "Next steps" item-by-item executable, numbered
- Receiver reading only this md can say: which repo, how to run, what's stuck now, what pitfalls to avoid

## Failure Handling Table

| Symptom | Root Cause | Action |
|---|---|---|
| All sections [TBD] | No info fed | Feed at least goal/done/next |
| JSON input not working | Field name typo | Align per references/handoff-fields.md |
| Handoff doc too thin | "Next steps" are empty words | Change to verb-led ordered steps |
| Receiver still confused | Key files lack paths | `--file` with absolute/repo-relative paths |

## References

- JSON field documentation: [references/handoff-fields.md](references/handoff-fields.md)

## Pipeline Position

- Upstream: any half-finished agent session
- Downstream: `memory-architect` (when this experience should be distilled into long-term memory)
