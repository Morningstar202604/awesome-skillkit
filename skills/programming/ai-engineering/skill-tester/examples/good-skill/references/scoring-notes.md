# How the scorer grades (author-side quick reference)

quality_scorer.py's four dimensions each weigh 25%. This file records the checkpoints per dimension,
so when writing a new skill you can self-check against it and avoid trial and error.

## Documentation (40% SKILL.md + 25% README + 20% references + 15% other)

- SKILL.md depth: line count (300 lines = full marks), complete frontmatter, number of code blocks (4 = full marks).
- README: character-count tiers (<200 chars only scores 45, ≥1000 chars scores 95)—so the README
  should have real content, not a one-line placeholder.
- references/: ≥2 files totaling ≥2000 chars scores 90—design notes and cheat sheets all count.

## Code Quality (script quality)

- Scripts averaging too thin in LOC lose points (avg <100 LOC marked "Scripts are thin").
- Every script must support both --json and human-readable output.
- Scripts must have a __main__ guard, --help, and be stdlib-only.

## Completeness

- scripts/ count, tests/ automated-test directory, assets/ sample data,
  expected_outputs/ golden output, references/ docs—all five categories are checked.

## Usability

- Existence of a Quick Start / Usage section, and whether the examples are copy-paste runnable.

## Exit-code semantics (CI view)

| Script | All pass | Problem found |
|---|---|---|
| skill_validator.py | 0 | 1 |
| script_tester.py | 0 | 1 |
| quality_scorer.py --minimum-score N | 0 | 2 (score below N) |
| audit_skills.py | 0 | 1 (only with --fail-under) |

This is why the docs point their examples at good-skill: it guarantees the example commands exit 0,
so readers copy-pasting won't get tripped up by an "expected failure".
