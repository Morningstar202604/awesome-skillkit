#!/usr/bin/env python3
"""
make_handoff.py — compress a long session's context into a handoff doc (Markdown)
that lets the NEXT agent cold-start and take over. You feed it: the goal, what's
done, next steps, gotchas, and key files; it produces a structured handoff.md.
Fully local and offline; dry-run by default.

Hard rules: default dry-run prints a preview; --write writes to disk; zero network.
"""
import argparse
import json
import os
import sys
from datetime import date

TEMPLATE = """# Handoff — {title}

> Generated: {date} · Authoring agent: {author} · Purpose: let **another** agent take over with no prior context

## 1. Goal (original intent)
{goal}

## 2. Done
{done}

## 3. Next steps (in order)
{next}

## 4. Known gotchas / do not repeat
{gotchas}

## 5. Key files and paths
{files}

## 6. One-page briefing for the receiving agent
- Repo/project: {repo}
- How to run / verify: {verify}
- Current blocker: {blocker}
"""


def collect(ap: argparse.Namespace) -> dict:
    goal = ap.goal or "[fill in: original goal]"
    # read structured input from JSON (optional, higher priority)
    data = {}
    if ap.input:
        with open(ap.input, "r", encoding="utf-8") as f:
            data = json.load(f)
    done = data.get("done") or ([ap.done] if ap.done else ["[fill in]"])
    nxt = data.get("next") or ([ap.next] if ap.next else ["[fill in]"])
    got = data.get("gotchas") or ([ap.gotcha] if ap.gotcha else ["[fill in]"])

    def lst(items):
        return "\n".join(f"- {x}" for x in items) if items else "- [fill in]"

    files_txt = "\n".join(f"- `{p}`" for p in (ap.file or [])) or "- [fill in]"

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
