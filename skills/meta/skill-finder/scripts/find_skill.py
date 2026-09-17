#!/usr/bin/env python3
"""find_skill.py — 在本仓库内检索技能、装配技能组合、输出仓库统计。

三个子命令：

  search <关键词> [--json] [--top N] [--category C]
      在本仓 manifest.json 的 pack 描述与所有 SKILL.md 的 name / description /
      正文里检索，按相关度排序。权重：名称命中 5 / description 命中 3 / 正文命中 1，
      名称前缀命中额外 +3。输出技能名、所属包、一行简介与路径。

  pack <技能名...> [--json]
      给定若干技能名，返回它们共同所属的包；若无共同包，则建议一个临时组合，
      列出各自的 category / tier / 是否带脚本，并给出顺序建议。

  stats [--json]
      输出仓库统计：技能数、包数、按 category 分布、孤儿技能（在盘上但不在任何 pack）。

数据全部来自真实文件（manifest.json + skills/**/SKILL.md），无任何硬编码技能列表。
仅用标准库。

用法：
  python3 find_skill.py search 视频
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

#: 仓库根 = 本脚本上溯三级（scripts/ -> skill-finder/ -> meta/ -> skills/ -> root）
ROOT = Path(__file__).resolve().parents[4]

# 相关度权重
W_NAME = 5
W_NAME_PREFIX = 3
W_DESC = 3
W_BODY = 1
W_PACK_DESC = 2

CJK_RE = re.compile(r"[\u4e00-\u9fff]")
FENCE_RE = re.compile(r"^\s*```")
H1_RE = re.compile(r"^#\s+(.+?)\s*$")


# ---------------------------------------------------------------- 数据加载


def load_manifest(root=ROOT):
    """读 manifest.json；失败抛 FileNotFoundError（不静默返回空）。"""
    p = root / "manifest.json"
    if not p.is_file():
        raise FileNotFoundError(f"未找到 manifest.json：{p}")
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
    """取正文首个非标题、非空、非代码的段落，作为一行简介。"""
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
        return text[:80] + ("…" if len(text) > 80 else "")
    return ""


def load_skills(root=ROOT):
    """扫描 skills/**/SKILL.md，返回技能记录列表。

    跳过 _common / assets / templates / __pycache__ 下的同名文件。
    """
    skip = {"_common", "assets", "templates", "__pycache__"}
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
    """技能名 -> 所属包列表、包简介。"""
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


# ---------------------------------------------------------------- 检索


def score_skill(rec, terms, manifest, skill_packs, pack_of):
    """给单个技能打分，返回 (分数, 命中明细)。"""
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
            hits.append(f"名称:{t}")
        if tl in desc:
            score += W_DESC
            hits.append(f"描述:{t}")
        for pid in skill_packs.get(rec["name"], []):
            blob = " ".join(str(pack_of[pid].get(k, "")) for k in
                            ("name", "name_zh", "description", "description_zh")).lower()
            if tl in blob:
                score += W_PACK_DESC
                hits.append(f"包:{pack_of[pid].get('name_zh') or pid}")
                break
        if tl in body:
            score += W_BODY
            hits.append(f"正文:{t}")
    return score, hits


def cmd_search(args):
    manifest = load_manifest()
    skills = load_skills()
    skill_packs, pack_of = build_index(manifest, skills)

    terms = [t for t in re.split(r"[\s,]+", args.keyword) if t]
    if not terms:
        print("关键词为空", file=sys.stderr)
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
        print(f"未命中：{args.keyword!r}。可试 `stats` 看全仓分布，或换更短的词。")
        return 1

    print(f"检索 {args.keyword!r} —— 命中 {len(scored)} 个技能，显示前 {len(top)} 个：\n")
    for sc, hits, r in top:
        packs = ", ".join(pack_of[p].get("name_zh") or p for p in skill_packs.get(r["name"], []))
        print(f"[{sc:>3}分] {r['name']}")
        print(f"        所属包: {packs or '（不属于任何包）'}")
        print(f"        简介  : {r['summary'] or r['title']}")
        print(f"        路径  : {r['path']}")
    return 0


# ---------------------------------------------------------------- 装配


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
        print(f"没有任何技能在盘上：{', '.join(missing)}", file=sys.stderr)
        return 2

    # 共同所属的包 = 每个技能所属包的交集
    sets = [set(skill_packs.get(nm, [])) for nm in wanted]
    common = set.intersection(*sets) if sets else set()

    # 顺序建议：编排/编排器类优先，带脚本的其次，其余按名称稳定排序
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
        print(f"⚠ 以下技能不在盘上，已忽略：{', '.join(missing)}\n")

    if common:
        print(f"这些技能同属 {len(common)} 个现成包：")
        for pid in sorted(common):
            p = pack_of[pid]
            print(f"  - {pid}（{p.get('name_zh') or p.get('name')}）"
                  f"  共 {len(p.get('skills', []))} 个技能")
        print("\n建议直接使用现有包，无需临时组合。\n")
    else:
        print("没有共同所属的现成包 —— 建议组成临时组合：\n")

    if len(wanted) < 2 and not common:
        print("（只给了 1 个技能，无顺序可排。）\n")

    print("执行顺序建议（编排/流水线类优先，其次带脚本者，最后纯提示型）：")
    for i, nm in enumerate(ordered, 1):
        r = by_name[nm]
        flag = "带脚本" if r["has_scripts"] else "纯提示"
        print(f"  {i}. {nm:<32} [{r['category'] or '未标注'}/{r['tier'] or '未标注'}] {flag}")
    print("\n依赖与顺序说明：")
    for nm in ordered:
        r = by_name[nm]
        deps = "scripts/ 已随包提供" if r["has_scripts"] else "无外部依赖（纯提示型）"
        print(f"  - {nm}: {deps}")
    print("\n注意：本仓库约定技能自包含、不做跨技能硬依赖；以上顺序是编排建议，"
          "不是运行时依赖，任一技能单独使用也应成立。")
    return 0


# ---------------------------------------------------------------- 统计


def cmd_stats(args):
    manifest = load_manifest()
    skills = load_skills()
    skill_packs, pack_of = build_index(manifest, skills)
    packs = manifest.get("packs", [])

    cat_counter = Counter(r["category"] or "（未标注）" for r in skills)
    tier_counter = Counter(r["tier"] or "（未标注）" for r in skills)
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

    print(f"仓库            : {payload['hub']}  (manifest {payload['manifest_version']}, "
          f"更新于 {payload['updated']})")
    print(f"技能数（盘上）  : {payload['skills_on_disk']}")
    print(f"场景包数        : {payload['packs']}")
    print(f"包引用的技能名  : {payload['skills_referenced_by_packs']}")
    print(f"含脚本的技能    : {payload['skills_with_scripts']}")
    print(f"\n按 category 分布（{len(cat_counter)} 类）：")
    for k, v in sorted(cat_counter.items(), key=lambda kv: (-kv[1], kv[0])):
        bar = "█" * min(v, 40)
        print(f"  {k:<26} {v:>3}  {bar}")
    print(f"\n按 tier 分布：")
    for k, v in sorted(tier_counter.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"  {k:<26} {v:>3}")
    if orphans:
        print(f"\n⚠ 孤儿技能（盘上有、不属于任何包）{len(orphans)} 个：")
        for nm in orphans:
            print(f"  - {nm}")
    if dangling:
        print(f"\n⚠ 包引用了盘上不存在的技能 {len(dangling)} 个：")
        for nm in dangling:
            print(f"  - {nm}")
    if not orphans and not dangling:
        print("\n包 ↔ 磁盘一致：无孤儿、无悬空引用。")
    return 0


# ---------------------------------------------------------------- 入口


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="find_skill.py",
        description="在本仓库检索技能、装配技能组合、输出仓库统计（数据来自真实文件）。",
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_search = sub.add_parser("search", help="按关键词检索技能")
    p_search.add_argument("keyword", help="关键词，空格可分隔多个（任一命中即计分）")
    p_search.add_argument("--json", action="store_true", help="输出 JSON")
    p_search.add_argument("--top", type=int, default=10, help="最多显示几条（默认 10）")
    p_search.add_argument("--category", default="", help="只在该 category 内检索")
    p_search.set_defaults(func=cmd_search)

    p_pack = sub.add_parser("pack", help="查共同所属的包，或建议临时组合")
    p_pack.add_argument("names", nargs="+", help="技能名，可给多个")
    p_pack.add_argument("--json", action="store_true", help="输出 JSON")
    p_pack.set_defaults(func=cmd_pack)

    p_stats = sub.add_parser("stats", help="输出仓库统计")
    p_stats.add_argument("--json", action="store_true", help="输出 JSON")
    p_stats.set_defaults(func=cmd_stats)

    args = ap.parse_args(argv)
    try:
        return args.func(args)
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
