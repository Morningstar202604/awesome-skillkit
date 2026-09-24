---
name: skill-tester
description: "Validate, test, and score the quality of skills within the claude-skills ecosystem. Comprehensive meta-skill: structure validation, Python script testing (syntax + imports + runtime + output format), multi-dimensional quality scoring with letter grades and tier classification (BASIC/STANDARD/POWERFUL). Use when authoring a new skill, auditing existing skills for tier promotion, setting up pre-commit hooks for skill quality, integrating skill QA into CI, testing a skill, checking whether a skill is compliant, or grading a skill. Do NOT use for fixing the skills it audits (this skill only audits and scores)."
license: Apache-2.0
compatibility: Pure prompt-based; may read project structure via Bash.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: ai-engineering
  pattern: single-task
  tier: expert
  verified-date: "2026-09-09"
---

# Skill Tester

Use four tools to validate, test, and score the quality of a skill directory (structure validation, script testing, quality scoring, security scoring), all runnable directly from the repo root.

> **Scope note**: this skill's tier line-count thresholds measure *legacy* skills. When authoring *new* skills, `engineering/write-a-skill` (SKILL.md around 100 lines or fewer, the Matt Pocock principle) is the binding standard — do not pad a new skill just to meet this skill's tier floor.

## Input Checklist

| Input | Required | Description |
|---|---|---|
| Path of the skill to audit | Yes | A skill directory in the repo, e.g. `skills/programming/api/api-design-reviewer` |
| Target minimum score | No | `quality_scorer.py --minimum-score`; CI commonly uses 75 |
| Target tier | No | `skill_validator.py --tier BASIC\|STANDARD\|POWERFUL`; if omitted, inferred from SKILL.md line count |
| Include security scoring? | No | Add `--include-security` (or run `security_scorer.py` separately) |

When inputs are missing, ask for them all at once: "Please provide: (1) the path of the skill directory to audit; (2) target minimum score (default 75 if blank); (3) whether security scoring is needed."

## Pre-flight Checks

Run each item; if any fails → handle the fix and STOP:

```bash
# 1. Python 3 is available
python3 --version
# Expected: Python 3.8+. Failure → install Python 3 and retry.

# 2. The four tool scripts exist
ls skills/programming/ai-engineering/skill-tester/scripts/{skill_validator,script_tester,quality_scorer,security_scorer}.py
# Expected: four .py filenames. Failure → confirm you're running from the repo root; still missing → STOP and report the repo is incomplete.

# 3. The target skill directory exists and contains SKILL.md
cat skills/programming/ai-engineering/skill-tester/examples/good-skill/SKILL.md > /dev/null && echo OK
# Expected: OK. Failure → confirm the correct path with the user, then STOP.
```

## Workflow

Run all commands from the **repo root**.

### Step 1: Structure validation

```bash
python3 skills/programming/ai-engineering/skill-tester/scripts/skill_validator.py skills/programming/ai-engineering/skill-tester/examples/good-skill --json
```

- **Action**: validate frontmatter, required sections, tier line-count floor, directory structure (README/scripts/references), and that scripts are stdlib-only.
- **Expected**: exit code 0; `compliance_level` in the JSON is not `FAIL`.
- **On failure**: non-zero exit code → read the `passed:false` entries in the JSON `checks{}`, report each to the user (this skill only audits, it does not fix), STOP.

### Step 2: Script testing

```bash
python3 skills/programming/ai-engineering/skill-tester/scripts/script_tester.py skills/programming/ai-engineering/skill-tester/examples/good-skill --json
```

- **Action**: for each Python script in the skill, do an AST syntax check, import analysis (flag external dependencies), controlled run (default 30s timeout, adjustable via `--timeout`), `--help` verification, and compare sample output against `expected_outputs/`.
- **Expected**: all scripts PASS, no timeout/import failures.
- **On failure**: timeout → rerun once with `--timeout 60`; an import failure → the script pulled in a non-stdlib dependency, a repo-policy violation, report as FAIL.

### Step 3: Quality scoring

```bash
python3 skills/programming/ai-engineering/skill-tester/scripts/quality_scorer.py skills/programming/ai-engineering/skill-tester/examples/good-skill --json --detailed --minimum-score 75
```

- **Action**: score across four dimensions (Documentation / Code Quality / Completeness / Usability, 25% each), outputting a 0-100 score, an A-F grade, a tier recommendation, and an `improvement_roadmap`.
- **Expected**: exit code 0 (score ≥ 75).
- **On failure**: non-zero exit code → list improvement items top-down per the `improvement_roadmap` (report only; do not edit on the user's behalf).

### Step 4: Security scoring (optional)

```bash
python3 skills/programming/ai-engineering/skill-tester/scripts/security_scorer.py skills/programming/ai-engineering/skill-tester/examples/good-skill --json
```

- **Action**: score the scripts' security posture (0-100).
- **Expected**: output the JSON `overall_score`.
- **On failure**: use `--verbose` to see item-by-item findings and report them verbatim.

### Step 5: Summary verdict

- **Action**: aggregate the three/four results and report to the user. For repo-wide batch audits use `scripts/audit_skills.py` (in this skill's scripts/; `quality_scorer.py` in parent-directory + `--batch` mode also works).
- **Expected**: all three green before calling it "passes" — never report a partial pass if any step failed.

## Parameter Cheat Sheet

| Parameter | Values | Description |
|---|---|---|
| `--tier` | BASIC / STANDARD / POWERFUL | Target tier to validate (default inferred from SKILL.md line count) |
| `--timeout` | seconds (default 30) | Per-script run timeout for script_tester |
| `--minimum-score` | 0-100 (default no floor) | quality_scorer exits non-zero below this value; used as a CI gate |
| `--include-security` | boolean | quality_scorer adds the security dimension |
| `--batch` | boolean | quality_scorer batch mode; pass the parent directory as skill_path |
| `--json` | boolean | supported by all tools; machine-readable output |

## Failure Handling Table

| Symptom / error code | Cause | Action |
|---|---|---|
| script_tester timeout | A script ran over 30s | Rerun with `--timeout 60`; still timing out → report as failure |
| import failures | External dependencies detected | Repo policy is stdlib-only; report FAIL, do not fix |
| tier misjudged | Line count/LOC doesn't match the tier table | Cross-check the tier matrix (see references); new skills are exempt under write-a-skill |
| validator reports missing README | The skill directory has no README.md | Report the deduction; the skill author fills it in |
| `FileNotFoundError` | Not running from the repo root | `cd` to the repo root; use repo-relative paths |

## Delivery Criteria

- Definition of success: steps 1-3 all return exit code 0 (four all-zero when security scoring is included).
- Artifact: an in-conversation report suffices; for archival, save as `skill-audit-<skill-name>-<YYYYMMDD>.json` (concatenating each tool's `--json` output), placed outside the repo or where the user specifies.
- Completeness verification: the report includes each tool's `overall_score` and FAIL details; no "partial pass" wording anywhere.

## References

- `references/skill-structure-specification.md` — the structure spec the validator implements; read when interpreting Step 1 FAIL items.
- `references/tier-requirements-matrix.md` — tier vs. line count/LOC mapping; read on Step 1 tier disputes.
- `references/quality-scoring-rubric.md` — the four-dimension scoring details; read when explaining deductions to the user.

## CI Integration

```yaml
# GitHub Actions: gate changed skills (replace $skill with each changed skill directory; the three full commands are in the workflow above)
- name: "validate-changed-skills"
  run: |
    for skill in $changed_skills; do
      skill_validator "$skill" --json
      script_tester "$skill"
      quality_scorer "$skill" --minimum-score 75
    done
```

Pre-commit hook: run the validator on staged skill directories; a non-zero exit blocks the commit.

Batch-audit the entire skill repo (including security scoring):

```bash
python3 scripts/audit_skills.py assets --json   # run from inside the skill directory; the bundled sample skills live under assets/
```
