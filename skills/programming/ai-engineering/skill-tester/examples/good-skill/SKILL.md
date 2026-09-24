---
name: good-skill
description: "Minimal reference sample of a compliant skill — demonstrates what a skill that passes all validations looks like. Referenced and used as a comparison benchmark by the skill-tester documentation."
---

# good-skill — Minimal Compliant-Skill Sample

## overview

good-skill is a minimal skill sample that is **deliberately made fully compliant**, answering one question:
"What is the smallest shape of a skill that passes all of skill-tester's checks?"

It is used as a pair with `assets/sample-skill/` (the deliberately flawed negative example):

| Comparison item | good-skill (this sample) | sample-skill (negative example) |
|---|---|---|
| Validator verdict | All pass, exit code 0 | Multiple FAILs, non-zero exit code |
| Script `__main__` guard | Present | Missing |
| Quick-start section | Present (quick start) | Missing |
| Purpose | Positive model: write along with it | Negative model: practice reading FAILs |

## quick start

Run the bundled script directly inside the skill directory (standard-library only):

```bash
python3 scripts/hello_stats.py 1,2,3.5,4 --json
```

Expected output is a JSON blob containing the six statistics `count/mean/median/min/max/stddev`,
with exit code 0. Human-readable format (the default):

```bash
python3 scripts/hello_stats.py 1,2,3.5,4
```

## usage

### Arguments

| Argument | Required | Description |
|---|---|---|
| `numbers` | Yes | A comma-separated string of numbers, e.g. `1,2,3.5` |
| `--json` | No | Output JSON instead of a table |

### When input is missing

The script returns exit code 2 and prints a readable error for empty input or invalid numbers — this is the
demonstration of a "well-formed script's" error handling: **even a failure should say what to do next**.

### Running from the repo root

When this skill is referenced by skill-tester, commands are run from inside this skill's directory;
if run from the repo root, the path is
`skills/programming/ai-engineering/skill-tester/examples/good-skill`.

## Built-in verification

- [ ] `python3 scripts/hello_stats.py 1,2,3 --json` exit code 0, JSON contains `stats.mean`
- [ ] `python3 scripts/hello_stats.py abc` exit code 2, stderr hints at example usage
- [ ] `python3 scripts/hello_stats.py --help` prints the argument help

## Failure handling

| Symptom | Action |
|---|---|
| `No such file or directory` | Confirm you're running inside the good-skill directory, or use the full repo-root path |
| `invalid literal for float` | The numbers argument has a non-numeric item; check the comma-separated segments |

## Red lines

1. **Do not treat good-skill as a functional skill** — it only does statistical demos; for real needs, use the corresponding domain skill.
2. **Do not delete the comparison relationship** — the positive/negative pairing of this sample with sample-skill is part of skill-tester's teaching.

## references

The correspondence between the three structure classes the validator cares about and this sample:

### Script discipline (scripts/)

- Standard library only: `argparse/json/sys` — any third-party import is flagged by script_tester as a
  repo-policy violation.
- Every script has an `if __name__ == "__main__":` guard: no side effects when imported.
- Supports `--help`: provided automatically by argparse; this is the minimum bar for "a script describing itself".
- Supports `--json`: machine-readable output is a prerequisite for CI integration; human-readable output is a prerequisite for troubleshooting — both must exist (the Code Quality dimension of quality_scorer checks this).
- Error paths: invalid arguments → exit code 2 + a readable stderr hint; success paths → exit code 0.

### Documentation discipline (SKILL.md)

- frontmatter must have `name` and `description`, consistent with the directory name.
- Sections present: overview / usage / quick start / built-in verification / failure handling / red lines —
  the Documentation and Usability dimensions of quality_scorer score these item by item.
- Meets line-count thresholds: the validator infers tier from line count (BASIC ≥100 / STANDARD ≥200 / POWERFUL ≥300);
  this sample is written to BASIC.
- Example commands are copy-runnable: every bash example in the docs uses a real bundled path.

### Directory discipline

- `README.md` exists (a hard validator requirement).
- `scripts/` has at least one script (BASIC).
- `references/` is optional (WARN-level); this sample substitutes this section for it.
