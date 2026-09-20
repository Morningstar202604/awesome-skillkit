#!/usr/bin/env python3
"""
reconcile.py — 对账：把「流水 CSV」和「账单 CSV」逐笔匹配，
输出三张清单（匹配成功 / 流水有但账单没有 / 账单有但流水没有）。

设计红线：
- 默认 dry-run：只打印结果摘要，不写文件
- --write 才输出 JSON 对账报告（新文件，源 CSV 不动）
- 纯本地、零网络、零拷贝
- 凭证（如有）走环境变量，不在脚本里写死

匹配策略：
- 主键：金额 + 日期（天级）+ 交易对方（可选）
- 金额相等（±0.01）且日期同月 → 候选；再按对方名归一化后比较
- 未匹配进 unmatched 清单，供人工核对
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
    """归一化到天：YYYY-MM-DD。支持 2026-09-20 / 2026/09/20 / 09/20/2026。"""
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
    ap.add_argument("--statement", required=True, help="流水 CSV")
    ap.add_argument("--billing", required=True, help="账单 CSV")
    ap.add_argument("--amount-col", default="amount", help="金额列名")
    ap.add_argument("--date-col", default="date", help="日期列名")
    ap.add_argument("--party-col", default="", help="交易对方列名（可选，增强匹配）")
    ap.add_argument("-o", "--out", default="reconcile_report.json", help="报告路径（仅 --write 时）")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    if not (os.path.isfile(args.statement) and os.path.isfile(args.billing)):
        print("[ERROR] statement/billing file not found", file=sys.stderr)
        return 2

    stmt = load(args.statement)
    bill = load(args.billing)

    # 列名探测
    amt_s = detect_col(stmt, args.amount_col, "金额", "amount", "amt")
    amt_b = detect_col(bill, args.amount_col, "金额", "amount", "amt")
    date_s = detect_col(stmt, args.date_col, "日期", "date")
    date_b = detect_col(bill, args.date_col, "日期", "date")
    if not (amt_s and amt_b and date_s and date_b):
        print(f"[ERROR] cannot locate amount/date columns "
              f"(amt_s={amt_s}, amt_b={amt_b}, date_s={date_s}, date_b={date_b})", file=sys.stderr)
        return 3
    party_s = detect_col(stmt, args.party_col, "对方", "party", "merchant") if args.party_col else None
    party_b = detect_col(bill, args.party_col, "对方", "party", "merchant") if args.party_col else None

    bill_used = set()
    matched, unmatched_stmt, unmatched_bill = [], [], []

    for i, s in enumerate(stmt):
        s_amt = parse_money(s.get(amt_s, ""))
        s_date = parse_date(s.get(date_s, ""))[:7]  # 月到 YYYY-MM
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

    print("=== 对账摘要 ===")
    print(f"  流水 {total_stmt} 笔 / 账单 {total_bill} 笔")
    print(f"  匹配 {len(matched)} / 流水未匹配 {len(unmatched_stmt)} / 账单未匹配 {len(unmatched_bill)}")
    print(f"  匹配率 {match_rate:.1%}")
    if unmatched_stmt:
        print(f"  流水未匹配示例: {json.dumps(unmatched_stmt[0]['row'], ensure_ascii=False)[:120]}")
    if unmatched_bill:
        print(f"  账单未匹配示例: {json.dumps(unmatched_bill[0]['row'], ensure_ascii=False)[:120]}")

    if args.write:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n[WRITE] 报告 -> {args.out}")
    else:
        print(f"\n[DRY-RUN] 未写文件。加 --write -o {args.out!r} 落 JSON 报告。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
