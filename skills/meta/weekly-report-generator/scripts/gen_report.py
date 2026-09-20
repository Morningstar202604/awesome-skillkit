#!/usr/bin/env python3
"""
gen_report.py — 从 git log + git diff --stat 拉出本周（或指定天数）的工作，
按固定段落（做了什么 / 卡在哪 / 下周计划）输出周报 Markdown。

设计红线：
- 默认 dry-run 打印周报预览，不落盘
- --write 才写文件（输出到新文件）
- 凭证 / 网络无关（纯本地 git + 文件系统操作）
- 不碰 git remote，不 push
"""
import argparse
import datetime
import json
import os
import re
import subprocess
import sys

TEMPLATE = """# 周报 · {start} ~ {end}

> 生成：{today} · 项目：{repo} · 作者：{author}

## 1. 本周完成

{done}

## 2. 卡点 / 风险

{blockers}

## 3. 下周计划

{next}

---
*由 weekly-report-generator 生成；"卡点"与"下周"默认占位，需人工补。*
"""


def sh(args: list[str], cwd: str) -> str:
    try:
        return subprocess.check_output(args, cwd=cwd, text=True, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def git_commits_since(days: int, cwd: str) -> list[str]:
    """列出 N 天内当前分支的 commit subject（不拉全量历史）。"""
    out = sh(["git", "log", f"--since={days} days ago", "--pretty=%ad | %s | %an",
              "--date=short", "--no-merges"], cwd)
    lines = []
    for raw in out.splitlines():
        parts = raw.split(" | ")
        if len(parts) >= 3:
            lines.append(f"{parts[0]} {parts[2]}: {parts[1]}")
    return lines


def diff_stat(cwd: str) -> dict:
    """最近一次 merge-base..HEAD 的 --stat 文件行数变化（粗略）。"""
    out = sh(["git", "diff", "--stat", "HEAD~3", "HEAD"], cwd)
    return {"raw": out.strip() or "(无 diff stat)"}


def group_by_day(commits: list[str]) -> dict:
    by_day = {}
    for c in commits:
        day = c[:10]
        by_day.setdefault(day, []).append(c)
    return by_day


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate a weekly report from git log (offline, dry-run by default)")
    ap.add_argument("--days", type=int, default=7, help="look-back window in days (default 7)")
    ap.add_argument("--repo", default=".", help="git repo path (default: cwd)")
    ap.add_argument("--author", default="agent", help="author name in report")
    ap.add_argument("--blockers", default="[待填：本周卡点]", help="free-text 卡点")
    ap.add_argument("--next", default="[待填：下周计划]", help="free-text 下周计划")
    ap.add_argument("--input", default="", help="optional JSON with {done, blockers, next}")
    ap.add_argument("-o", "--out", default="weekly-report.md")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    if not os.path.isdir(os.path.join(args.repo, ".git")):
        print(f"[ERROR] {args.repo} is not a git repo", file=sys.stderr)
        return 2

    start = (datetime.date.today() - datetime.timedelta(days=args.days)).isoformat()
    end = datetime.date.today().isoformat()

    commits = git_commits_since(args.days, args.repo)
    grouped = group_by_day(commits)
    stat = diff_stat(args.repo)

    # 人工输入 JSON 优先级最高
    done_blocks: list[str] = []
    blockers = args.blockers
    next_plan = args.next
    if args.input:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                data = json.load(f)
            done_blocks = data.get("done", [])
            blockers = data.get("blockers", blockers)
            next_plan = data.get("next", next_plan)
        except Exception as e:
            print(f"[WARN] --input failed ({e}); using git-derived", file=sys.stderr)

    if not done_blocks:
        done_blocks = [f"- [{d}] {c}" for d, cs in grouped.items() for c in cs] or ["(本周无 commit)"]

    doc = TEMPLATE.format(
        start=start, end=end,
        today=datetime.date.today().isoformat(),
        repo=os.path.basename(os.path.abspath(args.repo)),
        author=args.author,
        done="\n".join(done_blocks),
        blockers=blockers,
        next=next_plan,
    )

    print(doc)
    print(f"--- stats: {len(commits)} commits, {len(grouped)} active days ---")
    print(f"[DRY-RUN] git stat: {stat['raw'][:120]}{'…' if len(stat['raw']) > 120 else ''}")

    if args.write:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(doc)
        print(f"[WRITE] {args.out}")
    else:
        print(f"[DRY-RUN] nothing written. Re-run with --write -o {args.out!r}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
