---
name: docx-template-fill
description: >-
  Fill an existing Word template's {{placeholders}} with JSON data, optionally
  append a review note, and keep the original template untouched. Use when the
  user asks to fill a Word template / populate a docx / batch-generate contracts,
  reports, or notices / fill template / merge data into document / comment
  review. Do NOT use for generating a brand-new document from scratch (use
  docx-writer), spreadsheets, or slide decks.
license: Apache-2.0
compatibility: Requires python3 + python-docx (pip install python-docx); degrades to "print placeholder list only" when missing
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: office-productivity
  pattern: script
  tier: standard
  verified-date: "2026-09-20"
---

# DOCX Template Fill (Word Template Filling and Annotations)

Fill `{{placeholders}}` in an **existing** Word template with JSON data, and
optionally append a revision comment. Core judgment: use this skill only when
**the template already exists and only data is missing**; to create a document
from nothing, use `docx-writer`.

> Red lines (SKILL-STANDARD-v2): default **dry-run** only prints what would be
> filled, no file written; add `--apply` to write to a new file, **source
> template is never modified**; zero network, zero copying.

## Input Checklist

| Input | Required | Notes |
|---|---|---|
| Template .docx | yes | Contains `{{name}}`-style placeholders |
| Data JSON | yes | Keys match placeholder names exactly; missing keys are left blank and warned |
| Output filename | required with apply | Defaults to `filled.docx` |
| Comment author/text | no | `--note-author` / `--note-text` |

When inputs are missing, ask all at once: template path + data file path +
whether to add a comment.

## Pre-flight Checks

1. Does `python3 -c "import docx"` work? If not → prompt `pip install
   python-docx`, or run `--list-only` first to see placeholders (list-only also
   needs docx parsing; without docx the script degrades to printing data keys).
2. Are placeholders all UPPER_SNAKE_CASE (`EMP_NAME`) or lowercase (`emp_name`)?
   JSON keys must **exactly match**.

## Workflow

```bash
# 1. Dry run: see what will be filled and which placeholders lack data
python3 scripts/fill_template.py --template assets/sample-template.docx --data assets/sample-data.json

# 2. Real write (output to new file, template untouched)
python3 scripts/fill_template.py --template assets/sample-template.docx --data assets/sample-data.json \
  --apply -o ./out.docx

# 3. Add a revision comment
python3 scripts/fill_template.py --template assets/sample-template.docx --data assets/sample-data.json \
  --apply -o ./out.docx --note-author Reviewer Zhang --note-text "Please recheck the amount in item 3"

# 4. List placeholders only
python3 scripts/fill_template.py --template assets/sample-template.docx --data assets/sample-data.json --list-only
```

Batch scenario: the script handles one template per invocation. For one
template + N data files → in bash:
`for f in data/*.json; do python3 scripts/fill_template.py --template tpl.docx \
  --data "$f" --apply -o "out/$(basename "${f%.json}").docx"; done`.

## Delivery Criteria

- Every placeholder is either filled or explicitly listed in `[NOTICE]`
- Source template md5 is unchanged before/after (verify with `md5sum`)
- Output file opens in Word/WPS without style breakage (paragraph styles preserved, not rebuilt)

## Failure Handling Table

| Symptom | Root Cause | Action |
|---|---|---|
| `[DEGRADE] python-docx not installed` | Dependency missing | `pip install python-docx` then rerun |
| Placeholders not replaced | JSON key case/spelling differs from `{{}}` | Align key names; verify with `--list-only` |
| Table cells not filled | Placeholder is inside a table | Script already covers `doc.tables`; confirm placeholder is in cell text |
| Output won't open in Word | Source template is corrupt or not a real docx | Use another valid .docx as template |
| Wants real Word comment objects | This skill degrades to footnote-style comment paragraph | Requires hand-editing docx parts (OXML), out of scope |

## References

- Placeholder naming and degradation policy: [references/fill-rules.md](references/fill-rules.md)

## Pipeline Position

- Upstream: `docx-writer` (generates the draft template)
- Downstream: `pdf-pipeline` (docx → pdf final)
