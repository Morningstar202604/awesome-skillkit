#!/usr/bin/env python3
"""
reconcile.py -- reconciliation: match a "transactions CSV" against a "billing CSV"
row by row, and emit three lists (matched / in-statement-but-not-billing /
in-billing-but-not-statement).

Design guardrails:
- dry-run by default: only print the result summary, do not write files
- --write outputs a JSON reconciliation report (a new file; source CSVs untouched)
- purely local, zero network, zero copying
- credentials (if any) come from environment variables, never hard-coded in the script

Matching strategy:
- key: amount + date (day-level) + counterparty (optional)
- amounts equal (within +/-0.01) and dates in the same month -> candidate; then compare
  after normalizing the counterparty name
- unmatched rows go into the unmatched lists for human review
"""
import argparse
import csv
import json
import os
import re
import sys
from datetime import datetime


def normalize_party(s: str) -> str:
    s = re.sub(r"[\s\-_]+", "", (s or "").lower())
    return s


def parse_money(v: str) -> float:
    v = re.sub(r"[^0-9.\-]", "", (v or ""))
    return float(v) if v else 0.0


def parse_date(v: str) -> str:
    """Normalize to day: YYYY-MM-DD. Supports 2026-09-20 / 2026/09/20 / 09/20/2026."""
    v = (v or "").strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(v, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return v[:10]


def load(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def detect_col(rows: list[dict], *cands: str) -> str | None:
    if not rows:
        return None
    header = rows[0]
    for c in cands:
        for k in header:
            if k.strip().lower() == c.lower():
                return k
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Reconcile two CSV ledgers (offline, dry-run by default)")
    ap.add_argument("--statement", required=True, help="transactions CSV")
    ap.add_argument("--billing", required=True, help="billing CSV")
    ap.add_argument("--amount-col", default="amount", help="amount column name")
    ap.add_argument("--date-col", default="date", help="date column name")
    ap.add_argument("--party-col", default="", help="counterparty column name (optional, improves matching)")
    ap.add_argument("-o", "--out", default="reconcile_report.json", help="report path (only with --write)")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    if not (os.path.isfile(args.statement) and os.path.isfile(args.billing)):
        print("[ERROR] statement/billing file not found", file=sys.stderr)
        return 2

    stmt = load(args.statement)
    bill = load(args.billing)

    # column-name detection
    amt_s = detect_col(stmt, args.amount_col, "amount", "amt")
    amt_b = detect_col(bill, args.amount_col, "amount", "amt")
    date_s = detect_col(stmt, args.date_col, "date")
    date_b = detect_col(bill, args.date_col, "date")
    if not (amt_s and amt_b and date_s and date_b):
        print(f"[ERROR] cannot locate amount/date columns "
              f"(amt_s={amt_s}, amt_b={amt_b}, date_s={date_s}, date_b={date_b})", file=sys.stderr)
        return 3
    party_s = detect_col(stmt, args.party_col, "party", "merchant") if args.party_col else None
    party_b = detect_col(bill, args.party_col, "party", "merchant") if args.party_col else None

    bill_used = set()
    matched, unmatched_stmt, unmatched_bill = [], [], []

    for i, s in enumerate(stmt):
        s_amt = parse_money(s.get(amt_s, ""))
        s_date = parse_date(s.get(date_s, ""))[:7]  # month to YYYY-MM
        s_party = normalize_party(s.get(party_s, "")) if party_s else ""
        best_j = -1
        for j, b in enumerate(bill):
            if j in bill_used:
                continue
            b_amt = parse_money(b.get(amt_b, ""))
            b_date = parse_date(b.get(date_b, ""))[:7]
            if abs(s_amt - b_amt) > 0.01:
                continue
            if s_date and b_date and s_date != b_date:
                continue
            if s_party and normalize_party(b.get(party_b, "")) and s_party != normalize_party(b.get(party_b, "")):
                continue
            best_j = j
            break
        if best_j >= 0:
            bill_used.add(best_j)
            matched.append({"stmt": i, "billing": best_j,
                            "amount": s_amt, "date": s_date})
        else:
            unmatched_stmt.append({"index": i, "row": s})

    for j, b in enumerate(bill):
        if j not in bill_used:
            unmatched_bill.append({"index": j, "row": b})

    total_stmt = len(stmt)
    total_bill = len(bill)
    match_rate = round(len(matched) / max(1, max(total_stmt, total_bill)), 4)

    report = {
        "summary": {
            "statement_rows": total_stmt,
            "billing_rows": total_bill,
            "matched": len(matched),
            "unmatched_statement": len(unmatched_stmt),
            "unmatched_billing": len(unmatched_bill),
            "match_rate": match_rate,
        },
        "matched": matched,
        "unmatched_statement": unmatched_stmt,
        "unmatched_billing": unmatched_bill,
    }

    print("=== Reconciliation summary ===")
    print(f"  statement {total_stmt} rows / billing {total_bill} rows")
    print(f"  matched {len(matched)} / unmatched-in-statement {len(unmatched_stmt)} / unmatched-in-billing {len(unmatched_bill)}")
    print(f"  match rate {match_rate:.1%}")
    if unmatched_stmt:
        print(f"  unmatched-in-statement sample: {json.dumps(unmatched_stmt[0]['row'], ensure_ascii=False)[:120]}")
    if unmatched_bill:
        print(f"  unmatched-in-billing sample: {json.dumps(unmatched_bill[0]['row'], ensure_ascii=False)[:120]}")

    if args.write:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n[WRITE] report -> {args.out}")
    else:
        print(f"\n[DRY-RUN] no file written. Add --write -o {args.out!r} to emit the JSON report.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
