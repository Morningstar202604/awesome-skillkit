#!/usr/bin/env python3
"""find_skill.py — search skills in this repo, assemble skill combos, and print repo stats.

Three subcommands:

  search <keyword> [--json] [--top N] [--category C]
      Search the pack descriptions in this repo's manifest.json plus the name /
      description / body of every SKILL.md, ranked by relevance. Weights: name hit
      5 / description hit 3 / body hit 1, name-prefix hit +3. Outputs the skill name,
      its pack, a one-line summary, and the path.

  pack <skill-name...> [--json]
      Given several skill names, return the pack they share; if there is no common
      pack, suggest an ad-hoc combo, list each skill's category / tier / whether it
      ships a script, and give an ordering suggestion.

  stats [--json]
      Print repo statistics: skill count, pack count, distribution by category, and
      orphan skills (on disk but in no pack).

All data comes from real files (manifest.json + skills/**/SKILL.md); no hard-coded
skill lists. Standard library only.

Usage:
  python3 find_skill.py search video
  python3 find_skill.py search pdf --json --top 5
  python3 find_skill.py pack video-generation image-generation
  python3 find_skill.py stats
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

#: repo root = four levels up from this script
#: (scripts/ -> skill-finder/ -> meta/ -> skills/ -> repo root)
ROOT = Path(__file__).resolve().parents[4]

# relevance weights
W_NAME = 5
W_NAME_PREFIX = 3
W_DESC = 3
W_BODY = 1
W_PACK_DESC = 2

CJK_RE = re.compile(r"[\u4e00-\u9fff]")
FENCE_RE = re.compile(r"^\s*```")
H1_RE = re.compile(r"^#\s+(.+?)\s*$")


# ---------------------------------------------------------------- Data loading


def load_manifest(root=ROOT):
    """Read manifest.json; raise FileNotFoundError on failure (never silently return empty)."""
    p = root / "manifest.json"
    if not p.is_file():
        raise FileNotFoundError(f"manifest.json not found: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def split_frontmatter(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[1:i], "\n".join(lines[i + 1:])
    return None, text


def parse_simple_yaml(fm_lines):
    data = {}
    i, n = 0, len(fm_lines)
    while i < n:
        line = fm_lines[i]
        if not line.strip() or line.strip().startswith("#"):
            i += 1
            continue
        m = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):\s*(.*)$", line)
        if not m:
            i += 1
            continue
        key, val = m.group(1), m.group(2).strip()
        if val in ("", ">", ">-", "|", "|-", "|+"):
            block, j = [], i + 1
            while j < n and (fm_lines[j][:1] in (" ", "\t") or not fm_lines[j].strip()):
                block.append(fm_lines[j])
                j += 1
            if val.startswith(">") or val.startswith("|"):
                data[key] = " ".join(s.strip() for s in block if s.strip())
            else:
                sub = {}
                for bl in block:
                    sm = re.match(r"^\s+([A-Za-z][A-Za-z0-9_-]*):\s*(.*)$", bl)
                    if sm:
                        sub[sm.group(1)] = sm.group(2).strip().strip("\"'")
                data[key] = sub
            i = j
        else:
            data[key] = val.strip("\"'")
            i += 1
    return data


def first_paragraph(body):
    """Take the first non-heading, non-empty, non-code paragraph as a one-line summary."""
    in_fence = False
    for line in body.splitlines():
        s = line.strip()
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence or not s:
            continue
        if s.startswith("#") or s.startswith("|") or s.startswith(">"):
            continue
        text = re.sub(r"[*`]", "", s)
        return text[:80] + ("..." if len(text) > 80 else "")
    return ""


def load_skills(root=ROOT):
    """Scan skills/**/SKILL.md; return a list of skill records.

    Skip same-named files under _common / templates / __pycache__.
    Note: `assets/` is **not skipped** — `skills/writing/assets/ai-cover-generator`
    is a real skill referenced by packs; skipping it would make search/assembly
    inconsistent with the manifest. Pure resources under `assets/` (no SKILL.md)
    are not enumerated by this function anyway.
    """
    skip = {"_common", "templates", "__pycache__"}
    records = []
    for md in sorted(root.glob("skills/**/SKILL.md")):
        if any(part in skip for part in md.parts):
            continue
        raw = md.read_text(encoding="utf-8", errors="ignore")
        fm, body = split_frontmatter(raw)
        meta = parse_simple_yaml(fm) if fm else {}
        smeta = meta.get("metadata") if isinstance(meta.get("metadata"), dict) else {}
        h1 = ""
        for line in body.splitlines():
            m = H1_RE.match(line)
            if m and not m.group(1).startswith("#"):
                h1 = m.group(1)
                break
        records.append({
            "name": str(meta.get("name", "") or md.parent.name),
            "description": str(meta.get("description", "") or ""),
            "body": body,
            "path": md.relative_to(root).as_posix(),
            "dir": md.parent.relative_to(root).as_posix(),
            "category": str(smeta.get("category", "") or ""),
            "tier": str(smeta.get("tier", "") or ""),
            "title": h1,
            "summary": first_paragraph(body),
            "has_scripts": (md.parent / "scripts").is_dir(),
            "has_references": (md.parent / "references").is_dir(),
        })
    return records


def build_index(manifest, skills):
    """skill name -> list of owning packs, and a lookup of pack -> pack info."""
    skill_packs = {}
    pack_of = {}
    for pack in manifest.get("packs", []):
        pid = pack.get("id", "")
        pack_of[pid] = pack
        for s in pack.get("skills", []):
            nm = s.get("name", "")
            skill_packs.setdefault(nm, [])
            if pid not in skill_packs[nm]:
                skill_packs[nm].append(pid)
    return skill_packs, pack_of


# ---------------------------------------------------------------- Search


def score_skill(rec, terms, manifest, skill_packs, pack_of):
    """Score a single skill; return (score, hit details)."""
    name = rec["name"].lower()
    desc = rec["description"].lower()
    body = rec["body"].lower()
    score = 0
    hits = []
    for t in terms:
        tl = t.lower()
        if tl in name:
            score += W_NAME
            if name.startswith(tl):
                score += W_NAME_PREFIX
            hits.append(f"name:{t}")
        if tl in desc:
            score += W_DESC
            hits.append(f"desc:{t}")
        for pid in skill_packs.get(rec["name"], []):
            blob = " ".join(str(pack_of[pid].get(k, "")) for k in
                            ("name", "name_zh", "description", "description_zh")).lower()
            if tl in blob:
                score += W_PACK_DESC
                hits.append(f"pack:{pack_of[pid].get('name_zh') or pid}")
                break
        if tl in body:
            score += W_BODY
            hits.append(f"body:{t}")
    return score, hits


def cmd_search(args):
    manifest = load_manifest()
    skills = load_skills()
    skill_packs, pack_of = build_index(manifest, skills)

    terms = [t for t in re.split(r"[\s,]+", args.keyword) if t]
    if not terms:
        print("empty keyword", file=sys.stderr)
        return 2

    scored = []
    for rec in skills:
        if args.category and rec["category"] != args.category:
            continue
        sc, hits = score_skill(rec, terms, manifest, skill_packs, pack_of)
        if sc > 0:
            scored.append((sc, hits, rec))
    scored.sort(key=lambda x: (-x[0], x[2]["name"]))

    top = scored[: args.top] if args.top else scored

    if args.json:
        print(json.dumps({
            "keyword": args.keyword,
            "matches": [
                {
                    "name": r["name"],
                    "packs": skill_packs.get(r["name"], []),
                    "summary": r["summary"] or r["title"],
                    "path": r["path"],
                    "score": sc,
                    "hits": sorted(set(hits)),
                }
                for sc, hits, r in top
            ],
            "total_matches": len(scored),
        }, ensure_ascii=False, indent=2))
        return 0

    if not scored:
        print(f"no match for {args.keyword!r}. Try `stats` to see the repo distribution, or a shorter term.")
        return 1

    print(f"search {args.keyword!r} — {len(scored)} skills matched, showing top {len(top)}:\n")
    for sc, hits, r in top:
        packs = ", ".join(pack_of[p].get("name_zh") or p for p in skill_packs.get(r["name"], []))
        print(f"[{sc:>3} pts] {r['name']}")
        print(f"        pack    : {packs or '(not in any pack)'}")
        print(f"        summary : {r['summary'] or r['title']}")
        print(f"        path    : {r['path']}")
    return 0


# ---------------------------------------------------------------- Assembly


def cmd_pack(args):
    manifest = load_manifest()
    skills = load_skills()
    skill_packs, pack_of = build_index(manifest, skills)
    by_name = {r["name"]: r for r in skills}

    wanted = []
    missing = []
    for nm in args.names:
        if nm in by_name:
            wanted.append(nm)
        else:
            missing.append(nm)

    if not wanted:
        print(f"none of the requested skills are on disk: {', '.join(missing)}", file=sys.stderr)
        return 2

    # the shared pack = the intersection of each skill's owning packs
    sets = [set(skill_packs.get(nm, [])) for nm in wanted]
    common = set.intersection(*sets) if sets else set()

    # ordering suggestion: orchestrator/pipeline/planner first, then script-bearing,
    # the rest in stable name order
    def order_key(nm):
        low = nm
        rank = 0
        if "orchestrator" in low or "pipeline" in low or "planner" in low:
            rank = -2
        elif by_name[nm]["has_scripts"]:
            rank = -1
        return (rank, nm)

    ordered = sorted(wanted, key=order_key)

    payload = {
        "requested": wanted,
        "missing": missing,
        "common_packs": [
            {"id": pid, "name": pack_of[pid].get("name", pid),
             "name_zh": pack_of[pid].get("name_zh", "")}
            for pid in sorted(common)
        ],
        "mode": "existing-pack" if common else "ad-hoc-combo",
        "sequence": [
            {
                "name": nm,
                "category": by_name[nm]["category"],
                "tier": by_name[nm]["tier"],
                "has_scripts": by_name[nm]["has_scripts"],
                "path": by_name[nm]["path"],
            }
            for nm in ordered
        ],
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if missing:
        print(f"warning: the following skills are not on disk and were ignored: {', '.join(missing)}\n")

    if common:
        print(f"these skills share {len(common)} existing pack(s):")
        for pid in sorted(common):
            p = pack_of[pid]
            print(f"  - {pid} ({p.get('name_zh') or p.get('name')})"
                  f"  {len(p.get('skills', []))} skills total")
        print("\nRecommendation: use the existing pack directly; no ad-hoc combo needed.\n")
    else:
        print("no shared existing pack — suggest an ad-hoc combo:\n")

    if len(wanted) < 2 and not common:
        print("(only 1 skill given; nothing to order.)\n")

    print("recommended execution order (orchestrator/pipeline first, then script-bearing, then pure-prompt):")
    for i, nm in enumerate(ordered, 1):
        r = by_name[nm]
        flag = "scripts" if r["has_scripts"] else "pure-prompt"
        print(f"  {i}. {nm:<32} [{r['category'] or 'uncategorized'}/{r['tier'] or 'untiered'}] {flag}")
    print("\ndependencies & ordering note:")
    for nm in ordered:
        r = by_name[nm]
        deps = "scripts/ shipped with the pack" if r["has_scripts"] else "no external deps (pure prompt)"
        print(f"  - {nm}: {deps}")
    print("\nNote: this repo's convention is that skills are self-contained with no hard")
    print("cross-skill dependencies; the order above is an orchestration suggestion, not a runtime")
    print("dependency, and any single skill should stand on its own.")
    return 0


# ---------------------------------------------------------------- Stats


def cmd_stats(args):
    manifest = load_manifest()
    skills = load_skills()
    skill_packs, pack_of = build_index(manifest, skills)
    packs = manifest.get("packs", [])

    cat_counter = Counter(r["category"] or "(uncategorized)" for r in skills)
    tier_counter = Counter(r["tier"] or "(untiered)" for r in skills)
    orphans = sorted(r["name"] for r in skills if not skill_packs.get(r["name"]))
    packed_refs = {s.get("name") for p in packs for s in p.get("skills", [])}
    on_disk = {r["name"] for r in skills}
    dangling = sorted(packed_refs - on_disk)
    with_scripts = sum(1 for r in skills if r["has_scripts"])

    payload = {
        "hub": manifest.get("hub", ""),
        "manifest_version": manifest.get("version", ""),
        "updated": manifest.get("updated", ""),
        "skills_on_disk": len(skills),
        "packs": len(packs),
        "skills_referenced_by_packs": len(packed_refs),
        "skills_with_scripts": with_scripts,
        "by_category": dict(sorted(cat_counter.items(), key=lambda kv: (-kv[1], kv[0]))),
        "by_tier": dict(sorted(tier_counter.items(), key=lambda kv: (-kv[1], kv[0]))),
        "orphan_skills": orphans,
        "pack_references_missing_on_disk": dangling,
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    print(f"repo            : {payload['hub']}  (manifest {payload['manifest_version']}, "
          f"updated {payload['updated']})")
    print(f"skills on disk  : {payload['skills_on_disk']}")
    print(f"scene packs     : {payload['packs']}")
    print(f"skills referenced by packs: {payload['skills_referenced_by_packs']}")
    print(f"skills with scripts: {payload['skills_with_scripts']}")
    print(f"\nby category ({len(cat_counter)} categories):")
    for k, v in sorted(cat_counter.items(), key=lambda kv: (-kv[1], kv[0])):
        bar = "█" * min(v, 40)
        print(f"  {k:<26} {v:>3}  {bar}")
    print(f"\nby tier:")
    for k, v in sorted(tier_counter.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"  {k:<26} {v:>3}")
    if orphans:
        print(f"\nwarning: {len(orphans)} orphan skill(s) (on disk, in no pack):")
        for nm in orphans:
            print(f"  - {nm}")
    if dangling:
        print(f"\nwarning: {len(dangling)} skill(s) referenced by packs but missing on disk:")
        for nm in dangling:
            print(f"  - {nm}")
    if not orphans and not dangling:
        print("\npacks <-> disk consistent: no orphans, no dangling references.")
    return 0


# ---------------------------------------------------------------- Entry point


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="find_skill.py",
        description="Search skills in this repo, assemble combos, and print repo stats (data from real files).",
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_search = sub.add_parser("search", help="search skills by keyword")
    p_search.add_argument("keyword", help="keyword; separate several with spaces (any hit scores)")
    p_search.add_argument("--json", action="store_true", help="output JSON")
    p_search.add_argument("--top", type=int, default=10, help="max results to show (default 10)")
    p_search.add_argument("--category", default="", help="search only within this category")
    p_search.set_defaults(func=cmd_search)

    p_pack = sub.add_parser("pack", help="find the shared pack, or suggest an ad-hoc combo")
    p_pack.add_argument("names", nargs="+", help="skill names; give several")
    p_pack.add_argument("--json", action="store_true", help="output JSON")
    p_pack.set_defaults(func=cmd_pack)

    p_stats = sub.add_parser("stats", help="print repo statistics")
    p_stats.add_argument("--json", action="store_true", help="output JSON")
    p_stats.set_defaults(func=cmd_stats)

    args = ap.parse_args(argv)
    try:
        return args.func(args)
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
