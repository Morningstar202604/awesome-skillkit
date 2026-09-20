#!/usr/bin/env python3
"""
make_handoff.py — 把一段长会话的上下文压成一份"下一个 agent 能冷启动接手"的
交接文档（Markdown）。你喂入：目标、已做、下一步、坑、关键文件；它产出结构化
handoff.md。纯本地、离线，默认 dry-run。

设计红线：默认 dry-run 打印预览；--write 才落盘；零网络。
"""
import argparse
import json
import os
import sys
from datetime import date

TEMPLATE = """# Handoff — {title}

> 生成：{date} · 作者 agent：{author} · 目的：让**另一个** agent 无上下文接手

## 1. 目标（原始意图）
{goal}

## 2. 已完成
{done}

## 3. 下一步（按序）
{next}

## 4. 已知坑 / 不要重蹈
{gotchas}

## 5. 关键文件与路径
{files}

## 6. 给接手 agent 的一页纸速记
- 仓库/项目：{repo}
- 运行/验证方式：{verify}
- 当前卡点：{blocker}
"""


def collect(ap: argparse.Namespace) -> dict:
    goal = ap.goal or "[待填：原始目标]"
    # 从 JSON 读结构化输入（可选，优先级更高）
    data = {}
    if ap.input:
        with open(ap.input, "r", encoding="utf-8") as f:
            data = json.load(f)
    done = data.get("done") or ([ap.done] if ap.done else ["[待填]"])
    nxt = data.get("next") or ([ap.next] if ap.next else ["[待填]"])
    got = data.get("gotchas") or ([ap.gotcha] if ap.gotcha else ["[待填]"])

    def lst(items):
        return "\n".join(f"- {x}" for x in items) if items else "- [待填]"

    files_txt = "\n".join(f"- `{p}`" for p in (ap.file or [])) or "- [待填]"

    return {
        "title": data.get("title", ap.title or "Session"),
        "date": str(date.today()),
        "author": data.get("author", ap.author or "agent"),
        "goal": data.get("goal", goal),
        "done": lst(done),
        "next": lst(nxt),
        "gotchas": lst(got),
        "files": files_txt,
        "repo": data.get("repo", ap.repo or "[repo]"),
        "verify": data.get("verify", ap.verify or "[how to run / verify]"),
        "blocker": data.get("blocker", ap.blocker or "[none / describe current stuck point]"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Build a cold-start handoff doc (offline, dry-run by default)")
    ap.add_argument("--title", default="Session")
    ap.add_argument("--goal", default="")
    ap.add_argument("--done", default="")
    ap.add_argument("--next", default="")
    ap.add_argument("--gotcha", default="")
    ap.add_argument("--file", action="append", default=[], help="key file path (repeatable)")
    ap.add_argument("--repo", default="")
    ap.add_argument("--verify", default="")
    ap.add_argument("--blocker", default="")
    ap.add_argument("--author", default="agent")
    ap.add_argument("--input", default="", help="optional JSON with structured fields (overrides flags)")
    ap.add_argument("-o", "--out", default="handoff.md")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    fields = collect(args)
    doc = TEMPLATE.format(**fields)

    print(doc)
    print("--- preview above ---")
    if args.write:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(doc)
        print(f"[WRITE] {args.out}")
    else:
        print(f"[DRY-RUN] not written. Re-run with --write -o {args.out!r} to save.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
