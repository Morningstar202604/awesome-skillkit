---
name: invoice-organizer
description: >-
  Sort a pile of loose invoice/receipt/expense files into a month/category tree
  and emit a CSV ledger, so reimbursement filing stops being a mess. Use when
  the user asks to organize receipts / sort invoices / archive reimbursement by
  month / expense ledger / invoice categorization / receipt filing. Do NOT use
  for OCR / reading amounts off images (this works on filenames + an optional
  ledger, not pixels) or for actually submitting a reimbursement (human step).
license: Apache-2.0
compatibility: Pure local filesystem + CSV; no network; default dry-run; move operations are manually reversible.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: tools
  pattern: script
  tier: standard
  verified-date: "2026-09-20"
---

# Invoice Organizer (Invoice/Expense Filing and Ledger)

Archive a pile of loose invoices, receipts, and expense files into a **month/
category** directory tree by **month/category**, and produce a **ledger CSV**.
It solves reimbursement season: "invoices scattered everywhere, can't find them
all, don't match up."

> Red lines: default **dry-run** only prints "how it would be sorted"; `--apply`
> actually moves (source directory empties, target directory keeps); **doesn't
> delete any files**, moves are manually reversible; pure local, no network.

## Input Checklist

| Input | Required | Notes |
|---|---|---|
| Invoice source directory | yes | Scattered invoice files |
| Target root directory | no | Default `organized/` |
| Custom category mapping | no | `--map-json` takes `[[regex, category], ...]` |
| Ledger CSV path | no | Default `ledger.csv`, written only with `--apply` |

## Pre-flight Checks

1. Do filenames contain words that imply category/month? (dining/taxi/hotel/
   phone bill…) If none → files go to "uncategorized"; use `--map-json` to add
   rules.
2. Where does the month come from? If filename contains `YYYY-MM`, use that;
   otherwise use current month.
3. Do these files contain **sensitive amount information**? If so, after
   `--apply` the ledger CSV shouldn't be sent to remote.

## Workflow

```bash
# 1. Dry run: see how it would sort
python3 scripts/organize_invoices.py --src assets/sample-invoices

# 2. Real filing + ledger
python3 scripts/organize_invoices.py --src assets/sample-invoices --dst ./organized \
  --apply --ledger ./organized/ledger.csv

# 3. Custom categories (company's own taxonomy)
python3 scripts/organize_invoices.py --src assets/sample-invoices \
  --map-json ./rules.json --apply
```

`rules.json` example:
```json
[["travel|trip|high-speed|flight", "Travel"], ["cloud|server|domain", "IT"]]
```

## Delivery Criteria

- Archive directory tree: `organized/<YYYY-MM>/<category>/<file>`
- Ledger CSV each row = filename / month / category / source relative path
- Source directory is emptied after `--apply`; all files countable, none lost

## Failure Handling Table

| Symptom | Root Cause | Action |
|---|---|---|
| All go to "uncategorized" | Filenames lack category words | Pass `--map-json` to add regex |
| Months all the same | Filenames lack dates | Add `YYYY-MM` from filename/content, or accept current month |
| Want to move back | Moved wrong | `--apply` is `shutil.move`; manually drag back from target to source |
| Ledger should include amounts | This skill doesn't read file content | Amounts need separate OCR/manual entry |

## References

- Category rules and rollback notes: [references/invoice-rules.md](references/invoice-rules.md)

## Pipeline Position

- Upstream: invoice originals downloaded from phone/email (download to local directory first)
- Downstream: human pastes ledger into reimbursement system (this skill **doesn't auto-submit**, compliance left to human)
