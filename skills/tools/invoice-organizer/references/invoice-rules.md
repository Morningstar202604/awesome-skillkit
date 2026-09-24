# Invoice Archiving Rules

## Default categories (filename regex → category)
| Keyword | Category |
|---|---|
| dining/meal/coffee/food | Dining |
| taxi/ride-hail/uber | Transport |
| hotel/lodging | Lodging |
| office/stationery/supplies/print/paper | Office |
| phone/data/network/broadband | Telecom |
| reimbursement/invoice/receipt/ticket | Invoice |
| other | Uncategorized |

## Month
- Filename contains `YYYY-MM` / `YYYYMM` / `YYYY.MM` → by that month
- None → current month

## Undo
`--apply` uses `shutil.move` (no deletion); to undo, drag files from the target directory back to the source.

## Boundaries
- Does not read file content, does no OCR (amount/date rely on filename or human fill-in)
- Move operations **do not delete**, can be manually rolled back
- The ledger CSV contains four columns `file/month/category/source_dir`; be careful not to include sensitive amounts
