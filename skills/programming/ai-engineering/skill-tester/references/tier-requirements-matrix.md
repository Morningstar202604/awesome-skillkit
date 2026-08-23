# Tier Requirements Matrix

**Version:** 1.1 · **Used by:** `scripts/skill_validator.py`, `scripts/quality_scorer.py`

## Tier Definitions

| Tier | SKILL.md lines | Scripts LOC | CLI surface |
|------|----------------|-------------|-------------|
| BASIC | ≥ 100 | 100–300 | basic argparse |
| STANDARD | ≥ 200 | 300–500 | subcommands, JSON + text output |
| POWERFUL | ≥ 300 | 500–800 | multiple modes, CI integration |

## Directory Requirements

See `skill-structure-specification.md`. In short: POWERFUL requires all four
directories (`scripts/`, `assets/`, `references/`, `expected_outputs/`);
STANDARD requires three; BASIC requires `scripts/` only.

## Quality Gate Thresholds

| Context | Gate |
|---------|------|
| CI pre-merge | `quality_scorer.py <skill> --minimum-score 75` exits 0 |
| Tier promotion to POWERFUL | overall ≥ 85 and no dimension below 70 |
| With `--include-security` | POWERFUL requires Security ≥ 70; STANDARD ≥ 50 |

## Letter Grades

A+ ≥ 95 · A ≥ 90 · A- ≥ 85 · B+ ≥ 80 · B ≥ 75 · B- ≥ 70 · C+ ≥ 65 ·
C ≥ 60 · C- ≥ 55 · D ≥ 50 · F < 50

## Scope Note

Line-count minimums apply to *legacy* skills inherited from upstream. New
skills follow the write-a-skill doctrine (small SKILL.md, references carry
the depth); never pad a new skill to satisfy this matrix.
