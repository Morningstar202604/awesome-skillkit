# Reconciliation matching rules

## Matching key
- Amounts equal (within ±0.01)
- Same month (dates normalized to `YYYY-MM`)
- Optional: counterparties equal after normalization (lowercase + strip whitespace/punctuation)

## Column-name auto-detection
- Amount: `amount` / `amt`
- Date: `date`
- Party: `party` / `merchant` (must be passed explicitly via `--party-col`)

## Date formats
Supports `YYYY-MM-DD` / `YYYY/MM/DD` / `MM/DD/YYYY`; convert anything else to `YYYY-MM-DD` in the CSV first.

## Match rate
`matched / max(transaction rows, statement rows)`; below 90% is normal (there are omissions/discrepancies) — check the `unmatched_*` lists.

## Boundaries
- Purely heuristic; **unmatched items must be reviewed by a human**
- Does not connect to banks, make network calls, or use credentials
- Same-amount multi-entry ambiguity -> add `--party-col`
