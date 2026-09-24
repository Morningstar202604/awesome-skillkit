# Judgment Criteria and Edge Cases for the Eight Checks

This file is the behavior spec for `scripts/lint_skill.py`: SKILL.md only gives the judgment rules table;
here it gives **implementation details, edge cases, and false-positive troubleshooting**. Read this when
you have questions about a conclusion or want to port the rules elsewhere.

## Table of Contents

- [Check execution order](#check-execution-order)
- [Per-item edge cases](#per-item-edge-cases)
  - [FM-FIELDS](#fm-fields) / [NAME-SYNC](#name-sync) / [DESC-ROUTE](#desc-route)
  - [BODY-SECTS](#body-sects) / [BODY-LINES](#body-lines) / [LANG-CJK](#lang-cjk)
  - [REF-EXISTS](#ref-exists) / [FAIL-TABLE](#fail-table)
- [Exit code semantics](#exit-code-semantics)
- [Extension points for adding new checks](#extension-points-for-adding-new-checks)

## Check execution order

The script runs each `SKILL.md` through these eight checks in this fixed order; they are independent:

```
FM-FIELDS → NAME-SYNC → DESC-ROUTE → BODY-SECTS → BODY-LINES
          → LANG-CJK → REF-EXISTS → FAIL-TABLE
```

Any `FAIL` makes the exit code 1; `WARN` does not affect the exit code. In batch mode, results across skills are aggregated.

## Per-item edge cases

### FM-FIELDS

| Input form | Judgment |
|---|---|
| First line is `---` but no closing `---` | FAIL (`split_frontmatter` returns None) |
| First line is a blank line then `---` | FAIL (line 1 must be exactly `---`) |
| `metadata:` has no indented sub-keys | FAIL (parsed result is an empty dict) |
| `description:` uses a `>` folded block | Pass; multi-line folded into one line before length counting |
| `description` length 39 / 1025 | WARN; only out-of-bounds length is reported |

The parser implements only a minimal YAML subset (scalars / folded blocks / literal blocks / one-level nested maps),
**does not support lists, anchors, or multi-line string concatenation**—skill frontmatter doesn't need them, and shouldn't use them.

### NAME-SYNC

| Input form | Judgment |
|---|---|
| `name: Skill-Linter` | FAIL: contains uppercase |
| `name: skill--linter` | FAIL: consecutive hyphens |
| `name: skill-linter` but directory is `skill_linter` | FAIL: directory name mismatch |
| `name: Video Gen` | FAIL: does not match kebab-case regex |

Directory comparison uses the immediate parent directory name of `SKILL.md`. During batch scanning,
`SKILL.md` under `_common/`, `assets/`, `templates/`, `__pycache__/` is skipped—same-named files in these
locations are examples or shared modules, not the skill itself.

### DESC-ROUTE

- "When to use" prompts: `use when` / `use this` / `when the user` / `use it to` / `triggered when`.
- "Exclusions" prompts: `do not use` / `don't use` / `not for` / `exclude` / `not applicable` / `never use for`.
- Trigger-word counting: take the text after the above "when to use" introducers, truncate at the
  exclusion prompt or sentence end; split on `/`, `,`, `;`, ` or `, ` and `;` fragments
  with whitespace and leading/trailing punctuation stripped are counted only if length >= 2.

Edge cases:

| description fragment | Count |
|---|---|
| `Use when the user asks to generate a video / make a short clip / make a video` | 3 |
| `Use when the user needs to lint a skill / check skill compliance` | 2 |
| `Use when needed.` | 0 (fragment `needed` is only 1 word? — actually counts as 1, missing 4) |
| No recognized "when to use" introducer at all | 0 |

**Known false positive**: if trigger words are written after an introducer like `triggers:` but separated by
enumeration commas in a full sentence, the count will run high (descriptive phrases also counted as trigger words).
The judgment threshold is ">=5" as a floor; running high does not produce a false FAIL, so no additional tightening is done.

### BODY-SECTS

The six required sections are matched by `startswith` on H2 headings, so `## References` also matches `## Reference Materials`.
H2 total >=10 is the recommended value; fewer only triggers WARN.

### BODY-LINES

This counts **total file lines** (including frontmatter and code blocks), not prose word count. Blank lines count.
This coexists with the repo-level validator's 500-line ERROR line (in `validate_skills.py` under the repo root `tools/`):
this script's 220 is a self-discipline line, an early warning to avoid being bounced back at the repo gate after the skill has already bloated.

### LANG-CJK

Strip fenced code blocks → strip all whitespace → count CJK characters with `[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]` →
divide by total remaining characters. Threshold is 0.15.

Edge: pure-English skill bodies score ~0 (always WARN); mixed Chinese-English where Chinese is the narrative body
usually scores above 0.35; existing skills in this repo measure around 0.30-0.55. **This check will definitely false-positive
on code-heavy skills**—in that case, keep the WARN and state the reason in the delivery notes; do not pad Chinese text just to clear the WARN.

### REF-EXISTS

Recognizes two forms: `references/<filename>.md` inside backticks, and list items starting with it.
Existence criterion is that "<skill directory>/<relative path>" is a file.

Edge: placeholder names (common in writing templates or explanatory text like this section) will be treated as real references and report FAIL.
**Fix**: write the form without the `.md` suffix, or put it inside a fenced code block—this check does not look inside fences.

### FAIL-TABLE

Takes lines from `## Failure Handling Table` to the next H2; for each three-column table within, counts lines "starting with `|` and ending with `|`",
subtracting separator rows and the header. Requires >=4 data rows.

Edge: cells written with line breaks (`<br>`) are not counted separately; multiple tables are counted separately and summed.

## Exit code semantics

| Code | Meaning | CI handling |
|---|---|---|
| 0 | No FAIL (WARN may exist) | Pass |
| 1 | FAIL present | Block; print `FIX:` lines as comment |
| 2 | Path does not exist / no SKILL.md found | Treat as configuration error, not skill noncompliance |

## Extension points for adding new checks

Adding a new check takes three steps: write a `check_xxx(skill_dir, meta, body_lines, raw)` function returning
a list of `Finding`s → append it to the check chain in `lint_one()` → add a row to the judgment rules table in SKILL.md.
The `Finding`'s `fix` field **must be non-empty** (except for PASS), otherwise the user sees the problem but not the fix.
