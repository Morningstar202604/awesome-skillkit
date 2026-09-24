#!/usr/bin/env python3
"""
organize_invoices.py -- archive a pile of invoice/receipt files by month/category and
emit a ledger CSV (filename, month, category, source).

Design guardrails:
- dry-run by default: only print "how it would be split", touch no files
- --apply actually moves (via shutil.move; source files moved out, destination keeps the layout)
- never deletes any file (can be rolled back manually)
- no credentials / no network (pure local filesystem + CSV)

Category detection:
- inferred from the filename by default: "coffee"/"meal" -> food; "taxi"/"ride" -> transport;
  "hotel"/"lodging" -> lodging; "office"/"stationery" -> office; "telecom"/"internet" -> telecom;
  "invoice"/"receipt" -> invoice; otherwise "uncategorized"
- you may also pass --map-json for a custom mapping (regex -> category)
"""
import argparse
import csv
import json
import os
import re
import shutil
import sys
from collections import OrderedDict
from datetime import datetime

DEFAULT_RULES = [
    (re.compile(r"(coffee|food|meal|restaurant)", re.I), "food"),
    (re.compile(r"(taxi|uber|ride|cab)", re.I), "transport"),
    (re.compile(r"(hotel|lodging|lodge)", re.I), "lodging"),
    (re.compile(r"(office|stationery|paper|supply)", re.I), "office"),
    (re.compile(r"(telecom|internet|broadband|mobile|phone)", re.I), "telecom"),
    (re.compile(r"(invoice|receipt|ticket|expense|claim)", re.I), "invoice"),
]


def categorize(filename: str, rules) -> str:
    for pat, label in rules:
        if pat.search(filename):
            return label
    return "uncategorized"


def guess_month(filename: str, fallback_year: int) -> str:
    """Find YYYY-MM / YYYYMM / YYYY.MM in the filename; fall back to the current month."""
    m = re.search(r"(20\d{2})[-.\s]?(\d{1,2})?", filename)
    if m:
        y = m.group(1)
        mo = m.group(2) or datetime.now().month
        return f"{y}-{int(mo):02d}"
    return f"{fallback_year}-{datetime.now().month:02d}"


def scan(src: str, rules, fallback_year: int) -> list:
    items = []
    for root, _, files in os.walk(src):
        for f in sorted(files):
            if f.lower().endswith((".json", ".csv", ".md")):
                continue
            month = guess_month(f, fallback_year)
            cat = categorize(f, rules)
            items.append({
                "name": f,
                "rel": os.path.relpath(os.path.join(root, f), src),
                "month": month,
                "category": cat,
            })
    return items


def render_dry(items: list) -> str:
    tree = OrderedDict()
    for it in items:
        tree.setdefault(it["month"], OrderedDict()).setdefault(it["category"], []).append(it["name"])
    out = []
    for month in sorted(tree):
        out.append(f"{month}/")
        for cat, files in tree[month].items():
            out.append(f"  {cat}/")
            for f in files:
                out.append(f"    {f}")
    return "\n".join(out)


def apply(items: list, src: str, dst: str) -> int:
    moved = 0
    for it in items:
        target_dir = os.path.join(dst, it["month"], it["category"])
        os.makedirs(target_dir, exist_ok=True)
        src_path = os.path.join(src, it["rel"])
        if not os.path.exists(src_path):
            print(f"[WARN] missing source: {src_path}", file=sys.stderr)
            continue
        shutil.move(src_path, os.path.join(target_dir, it["name"]))
        moved += 1
    return moved


def write_ledger(items: list, path: str) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["file", "month", "category", "source_dir"])
        for it in items:
            w.writerow([it["name"], it["month"], it["category"], it["rel"]])


def main() -> int:
    ap = argparse.ArgumentParser(description="Organize invoices/receipts into month/category + CSV ledger (dry-run by default)")
    ap.add_argument("--src", required=True, help="directory holding loose invoice files")
    ap.add_argument("--dst", default="organized", help="destination root (created if missing)")
    ap.add_argument("--apply", action="store_true", help="actually move; default is dry-run")
    ap.add_argument("--map-json", default="", help="optional JSON: list of [regex, category]")
    ap.add_argument("--ledger", default="ledger.csv", help="ledger CSV path (only with --apply)")
    args = ap.parse_args()

    if not os.path.isdir(args.src):
        print(f"[ERROR] src not found: {args.src}", file=sys.stderr)
        return 2

    rules = DEFAULT_RULES
    if args.map_json:
        with open(args.map_json, "r", encoding="utf-8") as f:
            custom = json.load(f)
        rules = [(re.compile(p, re.I), c) for p, c in custom] + rules

    items = scan(args.src, rules, fallback_year=datetime.now().year)
    if not items:
        print(f"[OK] no eligible files in {args.src}")
        return 0

    print(f"Files to organize: {len(items)}")
    print(render_dry(items))

    if args.apply:
        moved = apply(items, args.src, args.dst)
        write_ledger(items, args.ledger)
        print(f"\n[APPLY] moved {moved} file(s) into {args.dst}/ ; ledger -> {args.ledger}")
    else:
        print(f"\n[DRY-RUN] no file moved. Re-run with --apply --dst {args.dst!r} to commit; ledger at {args.ledger!r}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
