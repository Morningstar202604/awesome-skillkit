---
name: skill-linter
description: >-
  Check a single SKILL.md or a whole skills directory against the awesome-skillkit
  spec and print a PASS/WARN/FAIL report with an explicit fix line per problem:
  frontmatter blocks, name/directory sync, description routing, the ten-section
  skeleton, line count, CJK body ratio, reference existence, and failure-table
  depth. Use when the user asks to lint a skill / validate skill spec / check if
  my skill is compliant / skill validation / skill compliance check. Do NOT use
  for creating a new skill (that is skill-author) or for grading documentation
  quality beyond spec compliance.
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

# Skill Linter (Skill Spec Validation)

Eight static checks on SKILL.md, turning "is this skill compliant" into one exit
code: returns 1 when there's a FAIL, can hang directly in CI or pre-commit.
Only reports and gives fixes, **doesn't modify files for you**.

Boundary with same-pack skills: `skill-author` generates from scratch,
`skill-finder` searches and assembles; this skill only judges spec compliance.

> **Known script/repo drift (read before trusting FAIL output).** This repo's
> SKILL.md files were refactored to **English** headings and English prose, but
> the shipped `scripts/lint_skill.py` still hard-codes the **Chinese** names of
> the six mandatory H2 sections and a Chinese-body CJK ratio. Consequences on a
> correctly English skill:
> - `BODY-SECTS` reports 6 spurious FAILs (it looks for the Chinese H2 names,
>   not the English `## Input Checklist` / `## Pre-flight Checks` / `## Workflow`
>   / `## Delivery Criteria` / `## Failure Handling Table` / `## References`).
> - `FAIL-TABLE` reports 1 spurious FAIL (it looks for the Chinese heading).
> - `LANG-CJK` reports a WARN (English body has ~0 CJK ratio).
> These are **code mismatches, not skill defects**. Until the script's section
> map and language check are flipped to English, judge a skill by the English
> headings listed in the table below, and treat the 6–7 `BODY-SECTS`/`FAIL-TABLE`
> FAILs and the `LANG-CJK` WARN as expected noise. The exact Chinese strings the
> script greps for are printed in its own `FIX:` lines when you run it. This
> SKILL.md documents the intended (English) spec; fixing the script is a separate
> code change.

## Input Checklist

| Input | Required | Default | Notes |
|---|---|---|---|
| Check target | yes | — | `SKILL.md` path / single skill directory / parent directory containing multiple skills |
| Output format | no | text | add `--json` for machine-readable report |
| Show PASS details? | no | only WARN+FAIL | add `--verbose` to print all eight conclusions |

When required input is missing, ask all at once:

> Please provide: 1) path to check (can be a directory like
> `skills/meta/skill-linter`, or directly `SKILL.md`). Optionally: 2) whether you
> need JSON output (default no); 3) whether you need to see passing checks
> (default no).

## Pre-flight Checks

Run each in order; any failure → follow action, then STOP:

```bash
# 1. Python 3 available
python3 --version
# Expected: Python 3.8+. Failure → install Python 3 then retry; this script uses no third-party libraries.

# 2. Script exists
ls skills/meta/skill-linter/scripts/lint_skill.py
# Expected: prints that path. Failure → confirm you're at repo root, paths use repo-relative.

# 3. Target path exists
ls <target path>
# Expected: lists files or directory. Failure → script exits code 2 and prints "path not found"; confirm path with user then STOP.
```

## Workflow

### Step 1: Single Skill Health Check

```bash
python3 skills/meta/skill-linter/scripts/lint_skill.py .   # single skill self-check (run inside skill directory): expected RESULT: PASS, exit code 0
```

- **Action**: `python3 skills/meta/skill-linter/scripts/lint_skill.py <skill directory> --verbose`
- **Expected**: eight `PASS/WARN/FAIL` lines + last line `RESULT: PASS`; exit code 0.
- **If it fails**: last line `RESULT: FAIL` or exit code 1 → read `FIX:` lines
  one by one, fix files per guidance; **must rerun on the same target until 0
  FAIL before it counts as done**.

### Step 2: Directory Tree Batch Check

- **Action**: `python3 skills/meta/skill-linter/scripts/lint_skill.py skills/ > lint-report.txt`
- **Expected**: report lists all skills in repo, last line gives
  `skills: N  FAIL: X  WARN: Y`; exit code 0 when X=0.
- **If it fails**: exit code 2 and reports "no SKILL.md found" → wrong target
  path, or no skills under the passed directory; verify with `ls <target>`.

### Step 3: CI Gate Integration

- **Action**: Use exit code as criterion, run only on changed skill directories:
  ```bash
  for d in $changed_skill_dirs; do
#     python3 skills/meta/skill-linter/scripts/lint_skill.py "$d" --json > /dev/null || exit 1
  done
  ```
- **Expected**: any skill with FAIL makes this step exit non-zero, CI fails.
- **If it fails**: entries in `--json` output `skills[].findings[]` with
  `level == "FAIL"` are gate-blocking reasons; print them as PR comments.

### Step 4: Interpret Report

- **Action**: Attribute by check item; `FAIL` must fix, `WARN` at author's
  judgment.
- **Expected**: every non-PASS item has a corresponding `FIX:` line.
- **If it fails**: no `FIX:` line → script defect; record target path and check
  item name to feedback to `skill-author` maintainers, don't silently ignore.

## Check Items and Judgment Rules

| Check Item | Rule (what counts as pass) | What's reported on fail | Suggested Fix |
|---|---|---|---|
| `FM-FIELDS` | Frontmatter starts/ends with `---` and parses, contains name/description/license/metadata four blocks; description length 40-1024 | Missing item FAIL, length out of range WARN | Add fields per `skill-template.md` |
| `NAME-SYNC` | `name` byte-identical to directory name, all lowercase, matches `^[a-z0-9]+(-[a-z0-9]+)*$` | FAIL | Rename either name or directory, they must match |
| `DESC-ROUTE` | description contains `Use when` (or "when user/when to use/trigger") and `Do NOT` (or "exclude/not applicable"), and trigger words >=5 | FAIL, reports actual trigger word count | Add English trigger phrases separated by `/` after the guidance |
| `BODY-SECTS` | Six mandatory H2s present (Input Checklist/Pre-flight Checks/Workflow/Delivery Criteria/Failure Handling Table/References); total H2 count 10 recommended | Missing mandatory item FAIL; total <10 WARN | Add sections per skeleton |
| `BODY-LINES` | Total lines < 220 | WARN | Move domain knowledge into `references/` |
| `LANG-EN` | After stripping fenced code blocks, narrative prose contains no CJK characters (this repo standard is English-only). The shipped script still runs the legacy `LANG-CJK` rule (flags CJK ratio < 0.15 as a WARN) | WARN when narrative prose contains CJK characters; the legacy low-CJK WARN on a correctly English skill is expected and non-blocking | Write all narrative prose in English; dismiss the legacy low-CJK WARN until the script's language check is flipped (tracked code change, not a SKILL.md fix) |
| `REF-EXISTS` | Every `references/<filename>.md` in body actually exists in the skill directory | Broken link FAIL | Create file or remove reference |
| `FAIL-TABLE` | `## Failure Handling Table` data rows >= 4 (excluding header and separator rows) | FAIL, reports actual row count | Add real failure scenarios and original error messages |

Trigger word counting basis: take the fragment after `Use when` / "when user" /
"trigger", cut at exclusion or sentence end, split by `/`, comma, or `or`;
fragments length >=2 count.

## Parameter Quick Reference

| Parameter | Values | Notes |
|---|---|---|
| `<target>` | file or directory path | positional; SKILL.md, skill directory, or parent directory all OK |
| `--json` | boolean | output JSON containing `skills[].findings[]` and `summary` |
| `--verbose` | boolean | text mode also prints PASS lines, eight total |
| Exit code | 0 / 1 / 2 | 0 no FAIL; 1 has FAIL; 2 path doesn't exist or no SKILL.md found |

## Failure Handling Table

| Symptom/Error Code | Cause | Action |
|---|---|---|
| Exit code 2 + "path not found" | target wrong or not in current working directory | verify path with `ls`; inside repo always use repo-relative |
| Exit code 2 + "no SKILL.md found" | target directory truly has no skills | confirm whether you wrote a layer above the skill directory; rerun once with `--verbose` to locate |
| `FM-FIELDS` all red | file first line isn't `---`, or YAML indentation broken | Replace frontmatter with first 15 lines of `skill-template.md` |
| `NAME-SYNC` reports directory mismatch | skill renamed but only changed directory or field | Unify one: suggest changing directory name (reference paths update accordingly) |
| `LANG-CJK` reports ratio too low | body is English (this repo standard) or almost all code | Expected: this repo ships English prose, so the legacy low-CJK WARN is non-blocking — keep it in delivery notes and move on; only act on narrative prose that contains CJK characters |
| `REF-EXISTS` reports broken link | referenced reference doc not yet created | Create `references/<name>.md`, or remove that line from `## References` |
| `FAIL-TABLE` row count insufficient | only wrote header or two generic lines | Add to 4+, each with original error and specific action |
| Report conflicts with repo gate `validate_skills.py` | Different check sets (repo gate checks pack consistency and 500-line hard limit) | Repo gate is the merge criterion; this skill is the skill-level self-discipline line; run both |

## Delivery Criteria

- Success definition: target skill has 0 `FAIL`; batch mode `RESULT: PASS`.
- Artifacts: default report to stdout; when archiving, redirect to
  `lint-report-<YYYYMMDD>.txt`, or `--json` output to
  `lint-report-<YYYYMMDD>.json`.
- Location: outside repo or user-specified path; don't pollute skill directory
  (only skill's own files under `skills/**`).
- Integrity verification: report last line must contain `skills:` / `FAIL:` /
  `WARN:` three counts; missing one means output was truncated.

## Relationship to Repo Gate

This skill is the **skill-level self-discipline line**; the repo-level validator
under repo root `tools/` is the **merge gate**. Different check sets, run both:

| Dimension | This skill (skill-linter) | Repo-level validator |
|---|---|---|
| Line limit | 220 lines reports WARN | 500 lines reports ERROR |
| Check granularity | Single skill, offline self-test | Whole repo + pack ↔ disk consistency |
| Trigger word count | Yes (>=5) | Only checks trigger guidance presence |
| Skeleton sections | Checks six mandatory H2s | Doesn't check |
| Output | PASS/WARN/FAIL + FIX lines | `[ OK ]` / `[ERR ]` table |

When conclusions conflict, repo gate is the merge criterion; this skill's value is
giving finer fix hints and a stricter line-count self-discipline line **before
submission**.

## Common Errors

| Symptom | Cause | Action |
|---|---|---|
| NAME-SYNC FAIL and directory name shows empty | target written as `.` without resolving | Pass specific skill directory, or upgrade to fixed script version |
| BODY-SECTS WARN missing 1 H2 | only wrote six mandatory sections | Add optional sections like parameter quick reference / common errors |
| DESC-ROUTE FAIL trigger words insufficient | description missing Use when list | Add ≥5 trigger words and Do NOT exclusions |

## References

- `references/check-rules.md` — complete judgment criteria and edge cases for
  eight checks (including false-positive troubleshooting); read when in doubt
  about a conclusion.
- `references/sources-and-methodology.md` — methodology source and originality
  statement; read when asked "where do rules come from".
