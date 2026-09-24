# Methodology sources and design trade-offs

> When to read: when you want to change the application order of renaming rules, adjust conflict strategy, or question "why the log uses JSONL instead of plain text."
> This file does not contain the CLI parameter table (that's in SKILL.md); it only covers design rationale.

## Idea sources (distilled from public methodology; no code copied)

| This script's approach | Idea distilled from |
|--------------|--------------|
| `preview` default / `apply` requires explicit confirmation | The two-phase model of batch ops tools (Terraform `plan`→`apply`, `git clean -n`) |
| Two-phase renaming (temp names first, final names second) | The classic batch-rename algorithm: lift everything out of the original namespace first, then settle uniformly, eliminating circular dependencies at the root |
| Skip conflicts rather than auto-append suffixes | Renaming differs from archiving: after renaming, filenames are for humans; auto-appending `_1` pollutes the naming intent—better to let the human decide |
| JSONL change log + reverse-order undo | Write-ahead log (WAL) idea: record the change intent first, then execute; undo is reverse replay |
| EXIF failure falls back to mtime | Progressive degradation: metadata may be missing, but the user's intent of "sort by capture time" must always be satisfied |

## Key trade-offs

**Why does `{n}` only auto-increment when the template actually uses it?** If it incremented unconditionally, skipped files
(already compliant, or in conflict) would eat a number for nothing, producing gaps like `IMG_001, IMG_003, IMG_007`. The user should see a continuous sequence.

**Why are swaps (a→b, b→a) not allowed through in `_detect_conflicts`?**
Conflict detection is based on "whether the target currently exists," and cannot distinguish "occupied by someone else" from
"about to be freed by another file in the same batch." If allowed through, a mid-failure in phase two would lose files. The current implementation chooses conservatism:
a direct swap is reported as a conflict, driving the user toward a rule that doesn't form a cycle. The script's internal two-phase mechanism still retains robustness against interruption.

**Why is the log format JSONL rather than `old -> new` text?**
Filenames can contain spaces, quotes, newlines, and `->` itself. Parsing delimiter text will inevitably break one day;
JSONL lines are independently parseable, and bad lines can be skipped individually (`--undo` warns on a bad line rather than aborting).

**Why delete rolled-back records from the log after a successful `undo`?**
Otherwise, repeating `undo` would try to roll back the same records again, mistakenly renaming same-named files the user created later.
Retaining unrollbackable records is to keep leftover issues visible.

## Official documentation

- Python `re` (`sub` and backreference syntax): <https://docs.python.org/3/library/re.html>
- Python `str.format` Format Specification Mini-Language (basis for `{n:03d}`): <https://docs.python.org/3/library/string.html#format-specification-mini-language>
- Python `datetime.strftime` (basis for `{date:%Y-%m}`): <https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes>
- Pillow `Image.Exif` (EXIF reading, tag 36867 = DateTimeOriginal): <https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Exif>
- CIPA DC-008 EXIF spec (`DateTimeOriginal` field definition): <https://www.cipa.jp/std/documents/e/DC-008-2012_E.pdf>
- Python `pathlib.Path.rename` (atomic rename within the same filesystem): <https://docs.python.org/3/library/pathlib.html#pathlib.Path.rename>
