#!/usr/bin/env python3
"""taxonomy.json 覆盖校验：站点一级导航（场景库）数据的护栏，fail-closed。

约束：
  - 每个场景包（manifest.json）与每个能力域（skills/skill_chains.json）
    必须且只能归入一个场景库；
  - 引用必须存在（漏登记 / 幽灵 id 都算错）；
  - 组 id 唯一，label / desc 必填。

被两处共用（单一事实源，避免两套口径）：
  - tools/validate_skills.py —— CI 门禁（每 PR 跑）
  - tools/build_site.py      —— 站点构建（产物写进 site/data/site.json）
"""

import json
from pathlib import Path


def check_taxonomy(root: Path) -> list[str]:
    """返回错误信息列表；空列表 = 通过。root 为仓库根目录。"""
    errs: list[str] = []
    tpath = root / "taxonomy.json"
    if not tpath.is_file():
        return ["taxonomy.json not found"]
    try:
        tax = json.loads(tpath.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return [f"taxonomy.json unreadable ({e})"]

    groups = tax.get("groups")
    if not isinstance(groups, list) or not groups:
        return ["taxonomy.json: 'groups' missing/empty"]

    seen_gid: set[str] = set()
    seen_packs: dict[str, str] = {}
    seen_domains: dict[str, str] = {}
    for g in groups:
        if not isinstance(g, dict):
            errs.append("taxonomy.json: group entry is not an object")
            continue
        gid = g.get("id")
        if not isinstance(gid, str) or not gid:
            errs.append("taxonomy.json: group without id")
            continue
        if gid in seen_gid:
            errs.append(f"taxonomy.json: duplicate group id '{gid}'")
        seen_gid.add(gid)
        for key in ("label", "desc"):
            if not isinstance(g.get(key), str) or not g[key]:
                errs.append(f"taxonomy group '{gid}': missing '{key}'")
        packs = g.get("packs", []) or []
        domains = g.get("domains", []) or []
        if not isinstance(packs, list) or not isinstance(domains, list):
            errs.append(f"taxonomy group '{gid}': 'packs'/'domains' must be lists")
            continue
        for pid in packs:
            if pid in seen_packs:
                errs.append(f"pack '{pid}' 同时归入 '{seen_packs[pid]}' 与 '{gid}'（必须唯一）")
            else:
                seen_packs[pid] = gid
        for d in domains:
            if d in seen_domains:
                errs.append(f"domain '{d}' 同时归入 '{seen_domains[d]}' 与 '{gid}'（必须唯一）")
            else:
                seen_domains[d] = gid

    try:
        manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return errs + [f"manifest.json unreadable ({e})"]
    all_packs = {p.get("id") for p in manifest.get("packs", []) if isinstance(p, dict)}

    try:
        chains = json.loads((root / "skills" / "skill_chains.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return errs + [f"skills/skill_chains.json unreadable ({e})"]
    all_domains = set((chains.get("domains") or {}).keys())

    for pid in sorted(all_packs - set(seen_packs)):
        errs.append(f"pack '{pid}' 未归入任何场景库（taxonomy.json 漏登记）")
    for pid in sorted(set(seen_packs) - all_packs):
        errs.append(f"taxonomy.json 引用了不存在的 pack '{pid}'")
    for d in sorted(all_domains - set(seen_domains)):
        errs.append(f"domain '{d}' 未归入任何场景库（taxonomy.json 漏登记）")
    for d in sorted(set(seen_domains) - all_domains):
        errs.append(f"taxonomy.json 引用了不存在的 domain '{d}'")
    return errs


if __name__ == "__main__":  # 可独立运行：python3 tools/taxonomy_check.py
    import sys

    root = Path(__file__).resolve().parent.parent
    errors = check_taxonomy(root)
    for m in errors:
        print(f"ERROR: {m}")
    print(f"taxonomy: {'FAILED' if errors else 'PASSED'}")
    sys.exit(1 if errors else 0)