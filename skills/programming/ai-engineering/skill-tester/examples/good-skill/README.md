# good-skill

A minimal example of a compliant skill (used as a pair with the negative example in `assets/sample-skill/`).

## What this is

good-skill answers one concrete question: "what is the smallest a skill that passes all skill-tester checks looks like?"
It is referenced by skill-tester's documentation examples as the target for "auditing a compliant skill";
at the same time, it is itself a **runnable writing template**—new skill authors can start by copying this directory.

Comparison:

| Aspect | good-skill (this example) | sample-skill (negative example) |
|---|---|---|
| Validator verdict | All pass, exit code 0 | Multiple FAILs, non-zero exit code |
| Script `__main__` guard | Present | Missing |
| Quick-start section | Present (quick start) | Missing |
| Automated tests | unittest in tests/ | None |
| Purpose | Positive example: write by following it | Negative example: practice reading FAILs |

## Directory structure

```
good-skill/
├── SKILL.md              # main skill doc (frontmatter + sections + runnable examples)
├── README.md             # this file
├── scripts/
│   └── hello_stats.py    # demo script (stdlib only, 150+ lines)
├── tests/
│   └── test_hello_stats.py  # unittest automated tests
├── expected_outputs/
│   └── sample_numbers_stats.json  # golden output (for script_tester comparison)
├── assets/
│   └── sample_numbers.txt   # sample input data
└── references/
    └── notes.md          # design notes
```

## Quick verification

Run from within this directory:

```bash
python3 scripts/hello_stats.py 1,2,3.5,4 --json
python3 -m unittest discover tests
```

The first command outputs stats JSON (exit code 0); the second runs 10 unit tests (all pass).

## Using it as a template

1. Copy this directory to a new skill directory; rename the directory and the frontmatter `name`.
2. Replace `scripts/hello_stats.py` with your real script—keep the five disciplines:
   stdlib-only, `__main__` guard, self-describing `--help`, machine-readable `--json`,
   non-zero exit code on error paths with a readable message.
3. Rewrite each SKILL.md section for your feature; **every example command must be copy-paste runnable**.
4. Self-check with `python3 ../../scripts/skill_validator.py . --json`,
   until `compliance_level` is not FAIL.

## Related docs

- Detailed design notes: [references/notes.md](references/notes.md)
- Line-by-line explanation of the five script disciplines: the references section of [SKILL.md](SKILL.md)
- Negative example: [../../assets/sample-skill/](../../assets/sample-skill/)
