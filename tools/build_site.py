#!/usr/bin/env python3
"""build_site.py — 生成静态展示站点 site/（数据 + 可下载副本）。

产出:
  site/data/site.json         站点数据（meta / domains / skills / packs / chains）
  site/skills/<relpath>       SKILL.md 副本，供站点内直接下载（不依赖 raw 服务）
  site/packs/<id>.zip         场景包 zip 副本，Release 附件缺失时的站内镜像

设计约束（与仓库既有口径保持一致）:
  - 技能枚举复用 build.py 的口径：packs/*/pack.json 的技能名 + 目录名同名 SKILL.md
  - Zero third-party deps：仅标准库，CI 无需 pip install
  - 相对路径：所有下载链接用相对路径，站点迁到任何子路径/平台都能用

用法:
  python3 tools/build_site.py
  python3 tools/build_site.py --out site --no-zip
  python3 tools/build_site.py --github-repo MS33834/awesome-skillkit
"""
import argparse
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent
SKILLS_DIR = SCRIPT_DIR / "skills"
DEFAULT_GITHUB = "MS33834/awesome-skillkit"
DEFAULT_GITCODE = "badhope/awesome-skillkit"


def parse_frontmatter(text: str) -> dict:
    """极简 frontmatter 解析（只需 name/description/license/compatibility/metadata）。"""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end].strip("\n")
    data: dict = {}
    current = None
    for line in block.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        indented = line[:1].isspace()
        if indented and current:
            m = re.match(r"\s+([A-Za-z_-]+):\s*(.*)", line)
            if m:
                data[current][m.group(1)] = _strip_quotes(m.group(2))
            continue
        m = re.match(r"([A-Za-z_-]+):\s*(.*)", line)
        if not m:
            continue
        key, value = m.group(1), _strip_quotes(m.group(2))
        if value == "":
            data[key] = {}
            current = key
        else:
            data[key] = value
            current = None
    return data


def _strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def find_skill_dir(name: str) -> Path | None:
    hits = [p.parent for p in SKILLS_DIR.glob(f"**/{name}/SKILL.md")
            if p.parent.name == name]
    return hits[0] if hits else None


def collect(github_repo: str, gitcode_repo: str, dist_dir: Path) -> dict:
    manifest = json.loads((SCRIPT_DIR / "manifest.json").read_text(encoding="utf-8"))
    chains_doc = json.loads((SKILLS_DIR / "skill_chains.json").read_text(encoding="utf-8"))
    version = manifest.get("version", "0.0.0")

    # 1) packs → 技能名 → 目录（与 build.py 同口径）
    pack_files = sorted((SCRIPT_DIR / "packs").glob("*/pack.json"))
    skill_dirs: dict[str, Path] = {}
    pack_skill_names: dict[str, list[str]] = {}
    for pack_json in pack_files:
        pack = json.loads(pack_json.read_text(encoding="utf-8"))
        names = []
        for skill in pack.get("skills", []):
            name = skill.get("name")
            if not name:
                continue
            names.append(name)
            if name not in skill_dirs:
                found = find_skill_dir(name)
                if found:
                    skill_dirs[name] = found
        pack_skill_names[pack_json.parent.name] = names

    # 2) 技能卡片
    skills = []
    for name in sorted(skill_dirs):
        skill_dir = skill_dirs[name]
        rel = skill_dir.relative_to(SKILLS_DIR).as_posix()
        domain = rel.split("/")[0]
        text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        meta = fm.get("metadata") or {}
        desc = fm.get("description", "") or ""
        skills.append({
            "name": name,
            "domain": domain,
            "path": f"skills/{rel}",                 # 站点内相对路径（目录）
            "file": f"skills/{rel}/SKILL.md",        # 站点内 SKILL.md 副本
            "desc": desc,
            "license": fm.get("license", ""),
            "compatibility": fm.get("compatibility", ""),
            "version": meta.get("version", ""),
            "tier": meta.get("tier", ""),
            "pattern": meta.get("pattern", ""),
            "verified": meta.get("verified-date", ""),
            "repo_file": f"skills/{rel}/SKILL.md",   # 仓库内路径（拼 raw 用）
            "packs": sorted(p for p, names in pack_skill_names.items() if name in names),
        })

    # 3) 场景包
    packs = []
    for pack in manifest.get("packs", []):
        pid = pack.get("id")
        zip_name = f"{pid}.zip"
        packs.append({
            "id": pid,
            "name": pack.get("name", pid),
            "name_zh": pack.get("name_zh", ""),
            "desc": pack.get("description", ""),
            "desc_zh": pack.get("description_zh", ""),
            "size_kb": pack.get("size_kb", 0),
            "n_skills": len(pack.get("skills", [])),
            "skills": [s.get("name") for s in pack.get("skills", [])],
            "local_url": f"packs/{zip_name}",
            # GitHub：附件直链（发版时由 release 流程上传 28 个 zip 到 Release 资产）
            "release_github": (f"https://github.com/{github_repo}/releases/download/"
                               f"v{version}/{zip_name}"),
            # GitCode：API 不支持上传 Release 附件（attach_files 405/404），
            # 故指向 Release 页面——该 URL 只要 Release 存在就一定有效，
            # 避免给访客一个 404 的死链。真正下载走 local_url 站内镜像。
            "release_gitcode": f"https://gitcode.com/{gitcode_repo}/releases/tag/v{version}",
            "dist_exists": (dist_dir / zip_name).is_file(),
        })

    # 4) 域与链条
    domains = []
    for domain_id, info in sorted(chains_doc.get("domains", {}).items()):
        chain_map = info.get("chains", {}) or {}
        domains.append({
            "id": domain_id,
            "label": domain_id,
            "entry": info.get("entry") or "",
            "n_skills": len(info.get("skills", []) or []),
            "n_chains": len(chain_map),
            "chains": [{"name": k, "steps": v} for k, v in sorted(chain_map.items())],
        })

    gh_raw = f"https://raw.githubusercontent.com/{github_repo}/main"
    gc_raw = f"https://gitcode.com/{gitcode_repo}/raw/main"
    for s in skills:
        s["raw_github"] = f"{gh_raw}/{s['repo_file']}"
        s["raw_gitcode"] = f"{gc_raw}/{s['repo_file']}"

    return {
        "meta": {
            "hub": manifest.get("hub", "awesome-skillkit"),
            "version": version,
            "updated": manifest.get("updated", ""),
            "desc": manifest.get("description", ""),
            "desc_zh": manifest.get("description_zh", ""),
            "n_skills": len(skills),
            # 磁盘 SKILL.md 总数：含 sample-skill 等不入包模板，与 README 徽章口径一致
            "n_skills_on_disk": len(list(SKILLS_DIR.rglob("SKILL.md"))),
            "n_packs": len(packs),
            "n_domains": len(domains),
            "n_chains": sum(d["n_chains"] for d in domains),
            "github": {"repo": github_repo, "url": f"https://github.com/{github_repo}",
                       "raw": gh_raw},
            "gitcode": {"repo": gitcode_repo, "url": f"https://gitcode.com/{gitcode_repo}",
                        "raw": gc_raw},
        },
        "domains": domains,
        "skills": skills,
        "packs": packs,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="生成 awesome-skillkit 静态站点数据")
    parser.add_argument("--out", default=str(SCRIPT_DIR / "site"), help="站点输出目录")
    parser.add_argument("--dist", default=str(SCRIPT_DIR / "dist"), help="zip 产物目录")
    parser.add_argument("--github-repo", default=DEFAULT_GITHUB)
    parser.add_argument("--gitcode-repo", default=DEFAULT_GITCODE)
    parser.add_argument("--no-zip", action="store_true", help="跳过 zip 副本复制")
    parser.add_argument("--no-skill-copy", action="store_true", help="跳过 SKILL.md 副本复制")
    args = parser.parse_args(argv[1:])

    out_dir = Path(args.out)
    dist_dir = Path(args.dist)
    data = collect(args.github_repo, args.gitcode_repo, dist_dir)

    (out_dir / "data").mkdir(parents=True, exist_ok=True)
    (out_dir / "data" / "site.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")

    # SKILL.md 副本
    copied = 0
    if not args.no_skill_copy:
        for skill in data["skills"]:
            src = SCRIPT_DIR / skill["repo_file"]
            dst = out_dir / skill["file"]
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
            copied += 1

    # zip 副本（站内镜像）
    zips = 0
    if not args.no_zip:
        pack_dir = out_dir / "packs"
        pack_dir.mkdir(parents=True, exist_ok=True)
        for pack in data["packs"]:
            src = dist_dir / f"{pack['id']}.zip"
            if src.is_file():
                (pack_dir / f"{pack['id']}.zip").write_bytes(src.read_bytes())
                zips += 1
        _all = dist_dir / "_all.zip"
        if _all.is_file():
            (pack_dir / "_all.zip").write_bytes(_all.read_bytes())
            zips += 1

    m = data["meta"]
    print(f"site.json: {m['n_skills']} skills / {m['n_packs']} packs / "
          f"{m['n_domains']} domains / {m['n_chains']} chains (v{m['version']})")
    print(f"SKILL.md copies: {copied} | zip copies: {zips} -> {out_dir}")
    missing = [p["id"] for p in data["packs"] if not p["dist_exists"]]
    if missing:
        print(f"WARN: dist 缺少 zip: {missing}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
