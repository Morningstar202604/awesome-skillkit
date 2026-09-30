#!/usr/bin/env python3
"""skill_router.py — decide WHICH skills (if any) a task needs, in milliseconds.

Indexes every installed SKILL.md's frontmatter (name / description /
description_zh), builds a deterministic TF-IDF-ish term index (English words
+ CJK bigrams), scores the task against it, and prints a ranked verdict:

  USE SKILLS     -> ranked candidates with matched terms
  NO SKILL NEEDED-> top score below threshold; work normally

Deterministic, offline, stdlib only. No embeddings, no network — the same
task always yields the same ranking, so agents can rely on it.

Usage:
  python3 skill_router.py "<task text>" --skills-dir <dir> [--top 5] [--json]
  python3 skill_router.py "<task text>"                 # auto-detect skills dir
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]{1,}")
CJK_RUN_RE = re.compile(r"[\u4e00-\u9fff]+")

AUTO_DETECT_CANDIDATES = [
    Path(__file__).resolve().parents[2],          # repo layout: skills/meta/skill-router
    Path.home() / ".zcode" / "skills",
    Path.home() / ".workbuddy" / "skills",
    Path.home() / ".claude" / "skills",
    Path.home() / ".config" / "opencode" / "skill",
]


def terms_of(text: str) -> list[str]:
    """English words (len>=2) + CJK bigrams (strong) + CJK unigrams (weak)."""
    out = [w.lower() for w in WORD_RE.findall(text)]
    for run in CJK_RUN_RE.findall(text):
        if len(run) == 1:
            out.append(run)
        else:
            out.extend(run[i : i + 2] for i in range(len(run) - 1))
            out.extend(f"~{ch}" for ch in run)  # weak unigram marker
    return out


def fold_description(lines: list[str], key: str) -> str:
    """Minimal frontmatter reader: value of a top-level key (block or inline)."""
    try:
        i = next(k for k, ln in enumerate(lines) if ln.startswith(f"{key}:"))
    except StopIteration:
        return ""
    j = i + 1
    buf = []
    while j < len(lines) and lines[j].startswith("  "):
        buf.append(lines[j].strip())
        j += 1
    if buf:
        return " ".join(buf)
    inline = lines[i].split(":", 1)[1].strip()
    return inline.strip("\"'")


def build_index(skills_dir: Path) -> dict:
    index: dict[str, dict] = {}
    df: dict[str, int] = {}
    for md in sorted(skills_dir.rglob("SKILL.md")):
        parts = md.parts
        if any(x in parts for x in ("_common", "templates", "examples", "skills-backup-20260929")):
            continue
        if md.parent.name.startswith("sample-"):
            continue
        lines = md.read_text(encoding="utf-8", errors="ignore").splitlines()
        name = md.parent.name
        desc = fold_description(lines, "description")
        desc_zh = fold_description(lines, "description_zh")
        if not desc:
            continue
        name_terms = set(name.split("-"))
        desc_terms = set(terms_of(desc)) | set(terms_of(desc_zh))
        # skill terms = what this skill can be found by
        skill_terms = (name_terms | desc_terms) - {name}
        index[name] = {
            "dir": str(md.parent),
            "name_terms": name_terms,
            "terms": skill_terms,
        }
        for t in skill_terms:
            df[t] = df.get(t, 0) + 1
    n_docs = max(len(index), 1)
    # smoothed IDF (sklearn-style): stable from a 1-skill dir to a 400-skill library
    weights = {t: math.log((1 + n_docs) / (1 + c)) + 1.0 for t, c in df.items()}
    for name in index:
        index[name]["weighted"] = {
            # weak CJK unigrams get 0.25x so 审 still connects to 审查/评审
            t: (weights.get(t, 0.1) * (0.15 if t.startswith("~") else 1.0))
            for t in index[name]["terms"]
        }
    return {"skills": index, "weights": weights, "n": n_docs}


MIN_USE = 8.0   # score >= this AND >=2 strong term hits -> USE SKILLS
MIN_WEAK = 8.0  # score >= this -> WEAK MATCH (scan the SKILL.md yourself)


def route(task: str, index: dict, top: int = 5, min_use: float | None = None,
          min_weak: float | None = None) -> dict:
    task_terms = set(terms_of(task))
    if not task_terms:
        return {"verdict": "NO SKILL NEEDED", "reason": "empty/unrecognized task", "results": []}
    scored = []
    for name, rec in index["skills"].items():
        hits = task_terms & rec["weighted"].keys()
        if not hits:
            continue
        score = sum(rec["weighted"][t] for t in hits)
        name_hits = len(hits & rec["name_terms"])
        score += name_hits * 1.5
        strong_hits = sum(1 for t in hits if not t.startswith("~"))
        scored.append(
            {
                "skill": name,
                "score": round(score, 2),
                "matched": sorted(t.lstrip("~") for t in hits)[:8],
                "dir": rec["dir"],
                "_strong": strong_hits,
            }
        )
    scored.sort(key=lambda x: -x["score"])
    results = scored[:top]
    top = results[0] if results else None
    use_at = MIN_USE if min_use is None else min_use
    weak_at = MIN_WEAK if min_weak is None else min_weak
    if top and top["score"] >= use_at and top["_strong"] >= 2:
        verdict = "USE SKILLS"
    elif top and top["score"] >= weak_at:
        verdict = "WEAK MATCH — scan the candidate's SKILL.md before relying on it"
    else:
        verdict = "NO SKILL NEEDED"
    for r in results:
        r.pop("_strong", None)
    return {"verdict": verdict, "task_terms": len(task_terms), "results": results}


def detect_skills_dir(explicit: str | None) -> Path:
    if explicit:
        p = Path(explicit)
        if not p.is_dir():
            sys.exit(f"error: --skills-dir not a directory: {p}")
        return p
    for c in AUTO_DETECT_CANDIDATES:
        if c.is_dir() and any(c.rglob("SKILL.md")):
            return c
    sys.exit("error: no skills directory found — pass --skills-dir")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Decide which skills a task needs (deterministic, offline)")
    ap.add_argument("task", help="the task text, quoted")
    ap.add_argument("--skills-dir", default="", help="skills directory (default: auto-detect)")
    ap.add_argument("--top", type=int, default=5, help="max candidates to show (default 5)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--min-use", type=float, default=None,
                    help="USE threshold override (defaults are tuned for 400+ skill libraries)")
    ap.add_argument("--min-weak", type=float, default=None, help="WEAK threshold override")
    args = ap.parse_args(argv[1:])

    sdir = detect_skills_dir(args.skills_dir)
    index = build_index(sdir)
    result = route(args.task, index, args.top, args.min_use, args.min_weak)

    if args.json:
        result["skills_dir"] = str(sdir)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    print(f"task   : {args.task}")
    print(f"skills : {sdir}  ({index['n']} indexed)")
    print(f"verdict: {result['verdict']}")
    for r in result["results"]:
        print(f"  {r['score']:>6.2f}  {r['skill']:<38} 命中: {'/'.join(r['matched'][:5])}")
    if result["verdict"] == "NO SKILL NEEDED":
        print("  → 没有可信命中：正常干活，不套技能。")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
