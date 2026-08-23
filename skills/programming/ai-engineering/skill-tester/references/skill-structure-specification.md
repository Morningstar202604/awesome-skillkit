# Skill Structure Specification

**Version:** 1.1 · **Enforced by:** `scripts/skill_validator.py`

## Required Files

| File | Requirement |
|------|-------------|
| `SKILL.md` | Must exist; YAML frontmatter with at least `name:` and `description:`; line count per tier table below |
| `README.md` | Must exist; usage-oriented content |

## Required Directories by Tier

| Tier | Required | Recommended |
|------|----------|-------------|
| BASIC | `scripts/` | `assets/`, `references/` |
| STANDARD | `scripts/`, `assets/`, `references/` | `expected_outputs/` |
| POWERFUL | `scripts/`, `assets/`, `references/`, `expected_outputs/` | — |

## Script Requirements

Every `scripts/*.py` must:

1. Parse with `ast` (valid Python syntax).
2. Use only the standard library, or declare external deps in its docstring
   (`script_tester.py --json` reports non-stdlib imports as advisory).
3. Accept `--help` and exit 0 within the timeout.
4. Prefer argparse with help text on every argument.

## SKILL.md Line Minimums (legacy tier table)

| Tier | Minimum lines |
|------|---------------|
| BASIC | 100 |
| STANDARD | 200 |
| POWERFUL | 300 |

> **Scope note:** these minimums measure *legacy* skills in the upstream
> repository. When authoring *new* skills, follow the write-a-skill doctrine
> instead (SKILL.md under ~100 lines); do not pad to satisfy this table.

## Compliance Scoring

`overall_score = passed_checks / total_checks × 100`

| Level | Score |
|-------|-------|
| EXCELLENT | ≥ 95 |
| GOOD | ≥ 80 |
| FAIR | ≥ 60 |
| POOR | < 60 |

Exit code 0 requires score ≥ 80 and zero errors — suitable as a CI gate.
