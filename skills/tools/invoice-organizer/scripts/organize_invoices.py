#!/usr/bin/env python3
"""
organize_invoices.py — 把一堆发票/收据文件按 月份/类别 归档，
并生成台账 CSV（文件名, 月份, 类别, 来源）。

设计红线：
- 默认 dry-run：只打印"会怎么分"，不动任何文件
- --apply 才真移动（用 shutil.move；源目录清空，目标目录保留原结构）
- 不删任何文件（可手动回滚）
- 凭证 / 网络无关（纯本地文件系统 + CSV）

类别识别：
- 默认从文件名推断：含 "餐饮/餐"/"coffee"→餐饮；含 "打车/出租/taxi"→交通；
  含 "酒店/住宿/hotel"→住宿；含 "办公/文具/耗材"→办公；含 "话费/流量/网"→通讯；
  含 "报销" 或 "发票"→发票；否则"未分类"
- 也可传 --map-json 走自定义映射（正则→类别）
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
    (re.compile(r"(餐饮|餐费|coffee|咖啡|food)", re.I), "餐饮"),
    (re.compile(r"(打车|出租|taxi|滴滴|uber)", re.I), "交通"),
    (re.compile(r"(酒店|住宿|hotel)", re.I), "住宿"),
    (re.compile(r"(办公|文具|耗材|打印|paper)", re.I), "办公"),
    (re.compile(r"(话费|流量|网络|宽带|网费)", re.I), "通讯"),
    (re.compile(r"(报销|发票|invoice|receipt|ticket)", re.I), "发票"),
]


def categorize(filename: str, rules) -> str:
    for pat, label in rules:
        if pat.search(filename):
            return label
    return "未分类"


def guess_month(filename: str, fallback_year: int) -> str:
    """从文件名找 YYYY-MM / YYYYMM / YYYY.MM；找不到用当前月。"""
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
