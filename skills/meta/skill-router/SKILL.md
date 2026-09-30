---
name: skill-router
description: >-
  Decide WHICH installed skills (if any) a task needs, in milliseconds, before
  work starts. Indexes all SKILL.md descriptions (Chinese + English) into a
  deterministic TF-IDF term index and scores the task against it — ranked
  candidates, matched terms, and a USE / WEAK / NO-SKILL verdict. Use when
  starting any professional task and unsure which skill fits, when choosing
  between several similar skills, when the skill-first rule says "check for a
  matching skill", or when the user asks 技能路由 / 用哪个技能 / 判断要不要用技能 /
  which skill should I use / route this task to skills. Do NOT use for writing
  new skills (use skill-author), auditing skill quality (use skill-linter), or
  as an embedding/vector service — it is lexical matching, deterministic and
  offline.
description_zh: "任务一开始就判断：该用哪些已安装技能、各打几分、要不要用。确定性离线词法匹配，毫秒级出结果。"
license: Apache-2.0
compatibility: "Python 3.8+ stdlib only; offline; auto-detects the skills directory (repo layout or ~/.zcode, ~/.workbuddy, ~/.claude, ~/.config/opencode)."
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: meta
  pattern: single-task
  tier: standard
  verified-date: "2026-09-30"
---

# Skill Router (task → which skills, or none)

Answers one question at task start: **which installed skills does this task
need — or none?** It is the local, deterministic cousin of hosted
classification services: no embeddings, no network, same input always yields
the same ranking, so an agent can act on it without re-judging.

## Input Checklist

- The task text (one sentence is enough; quote it on the command line).
- Which skills directory to judge against. Auto-detected in order: repo
  layout (`skills/` two levels up from this script), then `~/.zcode/skills`,
  `~/.workbuddy/skills`, `~/.claude/skills`, `~/.config/opencode/skill`.
  Otherwise pass it explicitly.
- (Optional) `--top N`, `--json`.

## Pre-flight Checks

```bash
python3 scripts/skill_router.py --help
```

Expected: usage text, exit 0. The router indexes only directories that contain
a SKILL.md with a non-empty `description`; it ignores `_common`, `templates`,
`examples`, `sample-*`, and install backups.

## Workflow

1. **Ask the router** (one command, milliseconds):

   ```bash
   python3 scripts/skill_router.py "<task text>" --skills-dir <skills 目录>
   ```

2. **Read the verdict**, then act on exactly one of three branches:
   - `USE SKILLS` → the ranked candidates are the working set. Load the top
     skill's SKILL.md and follow the skill-first rule for handoffs.
   - `WEAK MATCH — scan the candidate's SKILL.md before relying on it` → open
     the candidate's description yourself; if it genuinely fits, use it and
     say so; if not, proceed without skills.
   - `NO SKILL NEEDED` → work normally. Do not force-fit a skill.
3. **Between phases** (writing → publishing, data → charting, draft → audit),
   run the router again on the new sub-task — phase transitions are where
   skill handoffs happen.

## Delivery Criteria

- A verdict line (`USE SKILLS` / `WEAK MATCH` / `NO SKILL NEEDED`) plus a
  ranked list with scores and matched terms — or the explicit statement that
  no skill was needed and why.
- When a skill is adopted, its own SKILL.md governs the work; the router only
  performs routing.

## Failure Handling Table

| Symptom | Cause | Handling |
|---|---|---|
| `error: no skills directory found` | no SKILL.md under any auto-detect path | pass `--skills-dir` explicitly |
| Top scores are all tiny on a task you know has a match | the task text and skill descriptions share no lexical terms (paraphrase) | rephrase with the domain's own words, or scan descriptions manually |
| A wrong skill ranks first | lexical overlap is misleading (e.g. shared generic terms) | treat the router as a shortlist generator — the SKILL.md's own Do-NOT line decides |
| Same task, different hosts, different scores | different skills installed per host | expected: the router judges what is installed |

## References

- `scripts/skill_router.py` — the router (index + score + verdict)
- The skill-first global rule (repo `GLOBAL-RULES.md`) — where to plug this
  into your host's instruction file
