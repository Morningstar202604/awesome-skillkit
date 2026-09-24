---
name: skill-finder
description: >-
  Search this repository's skills by keyword, work out which scene pack a set of
  skills belongs to (or suggest an ad-hoc combo with ordering), and print
  repo-wide statistics — all read from the real manifest.json and SKILL.md
  files, never a hardcoded list. Use when the user asks to find a skill / search
  skills / which skill does X / list repo stats / skill lookup / skill discovery.
  Do NOT use for lint compliance (that is skill-linter) or for writing a new
  skill (skill-author).
license: Apache-2.0
compatibility: Requires python3 (stdlib only); run from the repository root.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: meta
  pattern: single-task
  tier: standard
  verified-date: "2026-09-17"
---

# Skill Finder (Skill Search and Assembly)

Three subcommands solve three things: **find a usable skill** (`search`),
**confirm whether several skills form a pack** (`pack`), **see the repo's
inventory** (`stats`). All data is read live from `manifest.json` and
`skills/**/SKILL.md`; there are no hardcoded skill names in the script.

Boundary with same-pack skills: `skill-author` generates, `skill-linter` checks
compliance; this skill only does search, assembly, and stats, doesn't modify any
file.

## Input Checklist

| Input | Required | Default | Notes |
|---|---|---|---|
| Subcommand | yes | — | one of `search` / `pack` / `stats` |
| Keywords | required for `search` | — | spaces separate multiple words, any hit scores |
| Skill name list | required for `pack` | — | one or more skill names |
| Output format | no | text | add `--json` for machine-readable result |
| Result count | no | 10 | `search --top N` |
| category filter | no | all | `search --category meta` |

When inputs are missing, ask all at once:

> Please provide: 1) what you're looking for (one sentence is enough, I'll
> extract keywords); or 2) which combination of skills to confirm; or 3) see
> repo stats directly. Optionally tell me: whether you need JSON output (default
> no).

## Pre-flight Checks

Run each in order; any failure → follow action, then STOP:

```bash
# 1. Python 3 available
python3 --version
# Expected: Python 3.8+. Failure → install Python 3 then retry; this script uses no third-party libraries.

# 2. Script exists and is in repo
ls skills/meta/skill-finder/scripts/find_skill.py
# Expected: prints that path. Failure → confirm you're at repo root, paths use repo-relative.

# 3. manifest.json readable (data source for search and stats)
python3 -c "import json;print(json.load(open('manifest.json'))['version'])"
# Expected: prints version number (e.g. 0.16.1). Failure → script exits code 2 and reports manifest.json not found; STOP and report repo incomplete.
```

## Workflow

### Step 1: Search by Keyword

- **Action**: `python3 skills/meta/skill-finder/scripts/find_skill.py search <keywords>`
- **Expected**: prints hit skill count and top N, each with score, skill name,
  owning pack, one-line intro, repo-relative path.
- **If it fails**: last line says "no hits" → try shorter or more generic words
  (`PDF` → `pdf`, `video generation` → `video`); or use `stats` to see category
  distribution then search by category.

### Step 2: Assembly Check

- **Action**: `python3 skills/meta/skill-finder/scripts/find_skill.py pack <skill names...>`
- **Expected**: if they belong to an existing pack, prints pack id, Chinese name,
  total skill count, and suggests using the pack directly; otherwise prints the
  temporary combo's execution order and dependency notes.
- **If it fails**: output `⚠ the following skills not on disk, ignored` → first
  use `search` to confirm correct spelling of skill names (this repo uses
  kebab-case, no spaces); exit code 2 when all names wrong.

### Step 3: Repo Stats

- **Action**: `python3 skills/meta/skill-finder/scripts/find_skill.py stats`
- **Expected**: prints skill count, pack count, script-bearing skill count,
  distribution bar chart by category and tier; orphan skills or dangling
  references explicitly listed if any.
- **If it fails**: no output → check you're at repo root; reports "manifest.json
  not found" → wrong path, STOP.

### Step 4: Chain into Reusable Search Conclusion

- **Action**: feed `search` hit skill names into `pack`, confirm whether they're
  already a pack; if not, organize into a suggestion list for the user in output
  order.
- **Expected**: gives suggestions with all three elements "path + owning pack +
  whether it has scripts".
- **If it fails**: `pack` reports many "not on disk" → skill names were made up
  from memory; return to step 1 to use `search` for accurate names.

## Relevance Algorithm

Scoring uses interpretable weighted term frequency, no vector model; hit = add
points:

| Hit Position | Weight | Notes |
|---|---|---|
| Skill `name` contains keyword | +5 | Name is strongest signal |
| `name` starts with keyword | extra +3 | e.g. `pdf-pipeline` vs `pdf` |
| `description` contains keyword | +3 | Description is routing basis, weight second |
| Owning pack's name/description contains keyword | +2 | Counted once per skill, avoid pack-internal score inflation |
| Body contains keyword | +1 | Weakest signal, fallback only |

Multiple keywords accumulate per word then sort; ties by skill name ascending,
guaranteeing results are **reproducible**.

## Parameter Quick Reference

| Parameter | Values | Notes |
|---|---|---|
| `search <keywords>` | any string, space-separated multi-word | any hit scores |
| `--top N` | integer, default 10 | only affects display count, not total hits |
| `--category C` | category value, e.g. `meta` | filter then search |
| `pack <names...>` | one or more skill names | with 1, only outputs that skill's metadata and ownership |
| `stats` | no params | see `references/repo-map.md` for counting basis |
| `--json` | all three subcommands support | `search` returns `matches[]` and `total_matches` |
| Exit code | 0 / 1 / 2 | 0 success; 1 `search` no hits; 2 param or data source error |

## Failure Handling Table

| Symptom/Error Code | Cause | Action |
|---|---|---|
| `search` reports "no hits" and returns 1 | Keyword too narrow or used English full name | Shorten keyword, try Chinese alias, or `stats` to see category first |
| `⚠ the following skills not on disk, ignored: xxx` | Skill name spelling inaccurate or placeholder name in source | Use `search` for accurate name; placeholder names (like `references/<filename>.md`) aren't skills |
| Exit code 2 + "manifest.json not found" | Not run at repo root | `cd` to repo root then rerun, always use repo-relative paths |
| `search` results have many tied-score skills | Keyword too generic (like "generate") | Add `--category` to narrow, or switch to a more specific action word |
| `stats` reports many orphan skills | Skill on disk but referenced by no pack | Release process issue; report to user and suggest updating `manifest.json` and `packs/*/pack.json` |
| `stats` reports "pack references skill not on disk" | Dangling reference in pack, CI will error | Report list and paths, hand to release process; this skill doesn't fix for you |
| `--json` output truncated | Result redirected to file but process interrupted | Rerun and redirect stdout completely; JSON top level has `total_matches` to verify integrity |

## Delivery Criteria

- Success definition: selected subcommand exit code 0 (`search` no hits returning
  1 is a normal conclusion, not failure).
- Artifacts: default to stdout; when archiving, redirect to
  `skill-search-<keywords>-<YYYYMMDD>.json` (with `--json`) or `.txt`.
- Location: outside repo or user-specified path; don't write into `skills/**`.
- Integrity verification: `search --json` `total_matches` matches `matches`
  length (latter larger when `--top` truncates); `stats` output skill count
  roughly equals `find skills -name SKILL.md` count (difference is skipped
  `assets/` examples).

## References

- `references/repo-map.md` — repo directory map and counting basis (how skill
  count is counted, what's skipped); read when interpreting `stats` numbers or
  can't find a skill.
- `references/sources-and-methodology.md` — methodology source and originality
  statement; read when asked "where do search rules come from".
