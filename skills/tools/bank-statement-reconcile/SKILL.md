---
name: bank-statement-reconcile
description: >-
  Reconcile a bank/credit-card statement CSV against a billing/expense CSV:
  match transactions by amount + month + optional counterparty, then hand the
  human three lists (matched / only-in-statement / only-in-billing). Use when
  the user asks to reconcile statements / match transactions / find missing
  entries / bank statement vs billing / transaction reconciliation / account
  matching. Do NOT use for importing from a bank account (no network/credentials
  here) or for accounting journal entries (this is matching, not bookkeeping).
license: Apache-2.0
compatibility: Pure local CSV; no network, no bank connection; default dry-run; matching is heuristic (amount + month + counterparty), unmatched items require human review.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: tools
  pattern: script
  tier: standard
  verified-date: "2026-09-20"
---

# Bank Statement Reconcile (Statement vs Billing Reconciliation)

Match a "bank statement CSV" line-by-line against a "billing/expense CSV" and
give you three lists: **matched, in-statement-only, in-billing-only**. It
solves month-end reconciliation: "which entry was missed, which amount doesn't
match"—pure mechanical work; manually matching 500 entries will drive anyone
crazy.

> Red lines: pure local CSV, **no bank connection, no network, no credentials**;
> default dry-run only prints summary, `--write` writes the JSON report; matching
> is heuristic (amount + same month + optional counterparty name), **unmatched
> items must be human-reviewed**.

## Input Checklist

| Input | Required | Notes |
|---|---|---|
| Statement CSV | yes | Bank/card-exported transactions |
| Billing CSV | yes | Your ledger / expenses |
| Amount column name | no | Default `amount`, auto-detects "amount/amt" |
| Date column name | no | Default `date`, auto-detects "date" |
| Counterparty column name | no | Only participates in matching if passed (improves precision) |

Both CSVs' column names should ideally align; if not, use `--amount-col`/`--date-col`.

## Pre-flight Checks

1. Are the two CSVs' **amount units consistent** (both yuan / same decimal places)?
   Unify first if not.
2. Can **date format** be normalized? Script supports `YYYY-MM-DD` / `YYYY/MM/DD` /
   `MM/DD/YYYY`; convert other formats to `YYYY-MM-DD` in the CSV first.
3. Is there a "counterparty" column? If yes, pass `--party-col` for more accurate
   matching; otherwise amount+month only.

## Workflow

```bash
# 1. Dry run: see match rate + unmatched examples
python3 scripts/reconcile.py --statement assets/sample-statement.csv --billing assets/sample-billing.csv

# 2. Specify column names + write JSON report
python3 scripts/reconcile.py --statement assets/sample-statement.csv --billing assets/sample-billing.csv \
  --amount-col amount --date-col date --party-col counterparty \
  --write -o ./reconcile.json

# 3. Export the two unmatched lists to CSV for human review
python3 -c "
import json, csv
r = json.load(open('reconcile.json'))
for key, out in [('unmatched_statement','only_in_statement.csv'),
                 ('unmatched_billing','only_in_billing.csv')]:
    rows = [item['row'] for item in r.get(key, [])]
    with open(out, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ['row'])
        w.writeheader(); w.writerows(rows)
    print(out, '->', len(rows), 'rows')
"
```

Match rate < 90% is normal (means quite a few missed/differences); review
`unmatched_*` lists line by line.

## Delivery Criteria

- Three lists complete: `matched` / `unmatched_statement` / `unmatched_billing`
- `match_rate` computable (matched / row count of the larger side)
- Unmatched items carry original rows for direct human review

## Failure Handling Table

| Symptom | Root Cause | Action |
|---|---|---|
| `cannot locate amount/date columns` | Column name auto-detect failed | Specify `--amount-col`/`--date-col` explicitly |
| Match rate 0% | Amount units / date format inconsistent | Unify units and date format first |
| Lots of "statement unmatched" | Billing missed entries | Normal; fill in one by one |
| Same-amount multiple entries confused | No counterparty column passed | Add `--party-col` to disambiguate |
| Wants "auto bookkeeping" | Out of scope | This skill only matches; booking is a human/accounting action |

## References

- Matching strategy and column name conventions: [references/reconcile-rules.md](references/reconcile-rules.md)

## Pipeline Position

- Upstream: statement CSV exported from bank app / web (download locally first)
- Downstream: human fills `unmatched_*` into ledger; or feed to `invoice-organizer` to build a register
