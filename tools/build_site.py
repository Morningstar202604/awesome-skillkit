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
  python3 tools/build_site.py --github-repo x33834/awesome-skillkit
"""
import argparse
import hashlib
import json
import zipfile
import os
import re
import sys
from pathlib import Path


def write_text_lf(path: Path, text: str) -> None:
    """LF + 原子写：构建中途失败不会把已提交的站点文件截断成半截。"""
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    os.replace(tmp, path)

SCRIPT_DIR = Path(__file__).resolve().parent.parent
SKILLS_DIR = SCRIPT_DIR / "skills"
DEFAULT_GITHUB = "x33834/awesome-skillkit"
DEFAULT_GITCODE = "badhope/awesome-skillkit"
DEFAULT_GITEE = "badhope/awesome-skillkit"

# tools/ 内共享模块（脚本方式运行时 tools/ 已在 sys.path[0]；显式插入防被当包导入）
sys.path.insert(0, str(SCRIPT_DIR / "tools"))
from taxonomy_check import check_taxonomy  # noqa: E402


def parse_frontmatter(text: str) -> dict:
    """极简 frontmatter 解析（只需 name/description/license/compatibility/metadata）。

    支持 `>` / `|` 块标量（description 的常见写法）。历史 bug：原实现把 `>-`
    原样当值，导致 83 个技能卡片描述显示为 ">"、中文关键词（如"公众号"）搜不到。
    """
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    lines = text[3:end].strip("\n").splitlines()
    data: dict = {}
    parent = None  # 形如 `metadata:` 的父键（其子键再缩进一层）
    i = 0
    while i < len(lines):
        line = lines[i]
        i += 1
        if not line.strip() or line.strip().startswith("#"):
            continue
        if line[:1].isspace():
            m = re.match(r"\s+([A-Za-z_-]+):\s*(.*)", line)
            if m and parent and isinstance(data.get(parent), dict):
                data[parent][m.group(1)] = _strip_quotes(m.group(2))
            continue
        parent = None
        m = re.match(r"([A-Za-z_-]+):\s*(.*)", line)
        if not m:
            continue
        key, value = m.group(1), _strip_quotes(m.group(2))
        if value in (">", ">-", ">+", "|", "|-", "|+"):
            # 块标量：吃掉后续所有缩进行；`>` 折叠为空格，`|` 保留换行
            sep = " " if value.startswith(">") else "\n"
            buf = []
            while i < len(lines) and (lines[i][:1].isspace() or not lines[i].strip()):
                if lines[i].strip():
                    buf.append(lines[i].strip())
                i += 1
            data[key] = _strip_quotes(sep.join(buf))
        elif value == "":
            data[key] = {}
            parent = key
        else:
            data[key] = value
    return data


def _strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


_SKILL_INDEX: dict[str, Path] | None = None


def _build_skill_index() -> dict[str, Path]:
    """一次性遍历 skills 树建立 技能名 → 目录 索引。

    之前 find_skill_dir 对每个技能各做一次递归 glob（skills 树文件多时
    单次可达秒级，153 个技能累计数分钟，导致 build_site 超时/卡死）。
    这里只遍历一次，后续查找 O(1)。
    """
    index: dict[str, Path] = {}
    for p in SKILLS_DIR.glob("**/SKILL.md"):
        index.setdefault(p.parent.name, p.parent)
    return index


def find_skill_dir(name: str) -> Path | None:
    global _SKILL_INDEX
    if _SKILL_INDEX is None:
        _SKILL_INDEX = _build_skill_index()
    return _SKILL_INDEX.get(name)


def collect(github_repo: str, gitcode_repo: str, gitee_repo: str,
            dist_dir: Path) -> dict:
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
            # 中文描述：frontmatter `description_zh`（中文检索与卡片展示用；
            # 全仓技能已补齐，见 docs/TAXONOMY-V2.md §5 中文检索）
            "desc_zh": fm.get("description_zh", "") or "",
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
            "sha256": pack.get("sha256", ""),  # 站内镜像复制前的防呆基准（见 main）
            "n_skills": len(pack.get("skills", [])),
            "skills": [s.get("name") for s in pack.get("skills", [])],
            "local_url": f"packs/{zip_name}",
            # GitHub：附件直链（发版时由 release 流程上传 dist/*.zip 到 Release 资产，
            # 见 docs/DEPLOY-SITE.md §5）
            "release_github": (f"https://github.com/{github_repo}/releases/download/"
                               f"v{version}/{zip_name}"),
            # GitCode：API 不支持上传 Release 附件（attach_files 405/404），
            # 故指向 Release 页面——该 URL 只要 Release 存在就一定有效，
            # 避免给访客一个 404 的死链。真正下载走 local_url 站内镜像。
            "release_gitcode": f"https://gitcode.com/{gitcode_repo}/releases/tag/v{version}",
            # Gitee：Release API 支持 attach_files 上传附件，附件直链与 GitHub 同构
            # （/releases/download/{tag}/{filename}）——发版后已逐个实测可达。
            "release_gitee": (f"https://gitee.com/{gitee_repo}/releases/download/"
                              f"v{version}/{zip_name}"),
            "dist_exists": (dist_dir / zip_name).is_file(),
        })

    # 4) 域与链条
    taxonomy = json.loads((SCRIPT_DIR / "taxonomy.json").read_text(encoding="utf-8"))
    domain_labels: dict = taxonomy.get("domain_labels", {})
    domains = []
    for domain_id, info in sorted(chains_doc.get("domains", {}).items()):
        chain_map = info.get("chains", {}) or {}
        domains.append({
            "id": domain_id,
            "label": domain_id,
            "label_zh": domain_labels.get(domain_id, domain_id),
            "entry": info.get("entry") or "",
            # n_skills：链域声明口径（chains 视图用，允许跨物理目录声明）
            "n_skills": len(info.get("skills", []) or []),
            # n_packed：站点实装口径（挂在 skills/<域>/ 下、且入包的技能数）——
            # 导航 chip 计数用它，保证「chip 数字 == 点进去的卡片数」
            "n_packed": sum(1 for s in skills if s["domain"] == domain_id),
            "n_chains": len(chain_map),
            "chains": [{"name": k, "steps": v} for k, v in sorted(chain_map.items())],
        })

    # 4b) 场景库（taxonomy.json）：站点一级导航；
    # 技能按能力域归组、包按使用场景归组（两者允许不同——用户找包看场景，找技能看能力）
    groups = []
    for g in taxonomy.get("groups", []):
        gid = g.get("id")
        g_domains = list(g.get("domains", []) or [])
        g_packs = list(g.get("packs", []) or [])
        groups.append({
            "id": gid,
            "label": g.get("label", gid),
            "label_en": g.get("label_en", ""),
            "emoji": g.get("emoji", ""),
            "desc": g.get("desc", ""),
            "domains": g_domains,
            "packs": g_packs,
            "n_packs": len(g_packs),
            "n_skills": sum(1 for s in skills if s["domain"] in g_domains),
        })

    gh_raw = f"https://raw.githubusercontent.com/{github_repo}/main"
    gc_raw = f"https://gitcode.com/{gitcode_repo}/raw/main"
    for s in skills:
        s["raw_github"] = f"{gh_raw}/{s['repo_file']}"
        s["raw_gitcode"] = f"{gc_raw}/{s['repo_file']}"

    # 专家团实装统计（首页双主线卡片用；数据源：expert-teams/ 子树，口径与
    # expert-teams/verify.py 一致：团队=teams/* 目录数，专家=teams/*/agents/*.md，
    # 技能=通用 skills/ + 团队 teams/*/skills/ 下 SKILL.md 总数）
    et_root = SCRIPT_DIR / "expert-teams"
    et_teams = (
        sorted(d for d in (et_root / "teams").iterdir() if d.is_dir())
        if (et_root / "teams").is_dir()
        else []
    )
    n_et_agents = sum(len(list((t / "agents").glob("*.md"))) for t in et_teams)
    n_et_skills = len(list((et_root / "skills").rglob("SKILL.md"))) + sum(
        len(list((t / "skills").rglob("SKILL.md"))) for t in et_teams
    )

    return {
        "meta": {
            "hub": manifest.get("hub", "awesome-skillkit"),
            "version": version,
            "updated": manifest.get("updated", ""),
            "desc": manifest.get("description", ""),
            "desc_zh": manifest.get("description_zh", ""),
            "n_skills": len(skills),
            # 磁盘 SKILL.md 总数：含 good-skill / sample-skill 等不入包夹具；
            # README 徽章与站点标题用的是 n_skills，此值仅供 diff 参考
            "n_skills_on_disk": len(list(SKILLS_DIR.rglob("SKILL.md"))),
            "n_packs": len(packs),
            "n_domains": len(domains),
            "n_groups": len(groups),
            "n_chains": sum(d["n_chains"] for d in domains),
            # 专家团（第二条产品线）
            "n_et_teams": len(et_teams),
            "n_et_agents": n_et_agents,
            "n_et_skills": n_et_skills,
            "github": {"repo": github_repo, "url": f"https://github.com/{github_repo}",
                       "raw": gh_raw},
            "gitcode": {"repo": gitcode_repo, "url": f"https://gitcode.com/{gitcode_repo}",
                        "raw": gc_raw},
            "gitee": {"repo": gitee_repo, "url": f"https://gitee.com/{gitee_repo}"},
        },
        "domains": domains,
        "groups": groups,
        "skills": skills,
        "packs": packs,
    }


# index.html 里静态计数锚点。锚点缺失 = 页面结构已变，fail-closed 报错，
# 避免计数再次静默漂移（历史上曾长期显示 153/36/18/62）。
INDEX_COUNT_ANCHORS = (
    (r"— \d+ Skills & \d+ Scene Packs",
     "— {n_skills} Skills & {n_packs} Scene Packs"),
    (r"\d+ curated SKILL\.md files and \d+ scene packs \(zips\) for AI coding tools, "
     r"across \d+ domains and \d+ skill chains",
     "{n_skills} curated SKILL.md files and {n_packs} scene packs (zips) for AI coding "
     "tools, across {n_domains} domains and {n_chains} skill chains"),
    (r"\d+ skills · \d+ scene packs · \d+ domains · \d+ skill chains",
     "{n_skills} skills · {n_packs} scene packs · {n_domains} domains · {n_chains} skill chains"),
    (r"\d+ 个场景包", "{n_packs} 个场景包"),
    # 首页双主线卡片（产品线 A/B）：计数与 site.json meta 同源，防静默漂移
    (r"\d+ 个场景包 · \d+ 个技能",
     "{n_packs} 个场景包 · {n_skills} 个技能"),
    (r"\d+ 大场景库", "{n_groups} 大场景库"),
    (r"\d+ 支团队 · \d+ 位专家 · \d+ 个技能",
     "{n_et_teams} 支团队 · {n_et_agents} 位专家 · {n_et_skills} 个技能"),
)


def inject_index_counts(out_dir: Path, meta: dict) -> int:
    """把 index.html 的静态计数改写为与 site.json meta 同源；重复运行幂等。"""
    page = out_dir / "index.html"
    if not page.is_file():
        print(f"WARN: {page} 不存在，跳过计数注入", file=sys.stderr)
        return 0
    text = page.read_text(encoding="utf-8")
    missing = []
    for pattern, repl in INDEX_COUNT_ANCHORS:
        text, n = re.subn(pattern, repl.format(**meta), text)
        if n == 0:
            missing.append(pattern)
    if missing:
        raise SystemExit(
            "index.html 计数锚点缺失（页面结构已变？）: " + " | ".join(missing)
        )
    write_text_lf(page, text)
    return len(INDEX_COUNT_ANCHORS)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="生成 awesome-skillkit 静态站点数据")
    parser.add_argument("--out", default=str(SCRIPT_DIR / "site"), help="站点输出目录")
    parser.add_argument("--dist", default=str(SCRIPT_DIR / "dist"), help="zip 产物目录")
    parser.add_argument("--github-repo", default=DEFAULT_GITHUB)
    parser.add_argument("--gitcode-repo", default=DEFAULT_GITCODE)
    parser.add_argument("--gitee-repo", default=DEFAULT_GITEE)
    parser.add_argument("--no-zip", action="store_true", help="跳过 zip 副本复制")
    parser.add_argument("--no-skill-copy", action="store_true", help="跳过 SKILL.md 副本复制")
    args = parser.parse_args(argv[1:])

    # 构建前先过 taxonomy 覆盖校验（与 CI 门禁同一函数，口径唯一）
    tax_errors = check_taxonomy(SCRIPT_DIR)
    if tax_errors:
        raise SystemExit(
            "taxonomy.json 覆盖校验失败（先修数据再构建）:\n  - "
            + "\n  - ".join(tax_errors)
        )

    out_dir = Path(args.out)
    dist_dir = Path(args.dist)
    data = collect(args.github_repo, args.gitcode_repo, args.gitee_repo, dist_dir)

    (out_dir / "data").mkdir(parents=True, exist_ok=True)
    write_text_lf(out_dir / "data" / "site.json",
                  json.dumps(data, ensure_ascii=False, indent=1))
    inject_index_counts(out_dir, data["meta"])

    # SKILL.md 副本
    copied = 0
    if not args.no_skill_copy:
        for skill in data["skills"]:
            src = SCRIPT_DIR / skill["repo_file"]
            dst = out_dir / skill["file"]
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
            copied += 1

    # 单技能 zip（市场级：每个技能一个独立压缩包，整文件夹含 scripts/references；
    # 写作发布器家族复用 _common，随包附带保证解压即用）
    skill_zips = 0
    if not args.no_skill_copy:
        sz_dir = out_dir / "skills-zip"
        sz_dir.mkdir(parents=True, exist_ok=True)
        for skill in data["skills"]:
            src = (SCRIPT_DIR / skill["repo_file"]).parent  # repo_file 指向 SKILL.md，取技能目录
            zp = sz_dir / f"{skill['name']}.zip"
            with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as zf:
                for f in sorted(src.rglob("*")):
                    if f.is_dir() or "__pycache__" in f.parts or f.suffix == ".pyc":
                        continue
                    zf.writestr(f"{skill['name']}/{f.relative_to(src).as_posix()}",
                                f.read_bytes())
            skill_zips += 1

    # zip 副本（站内镜像）
    zips = 0
    if not args.no_zip:
        pack_dir = out_dir / "packs"
        pack_dir.mkdir(parents=True, exist_ok=True)
        # 防呆：dist 是本地构建产物，可能过期（历史事故：3 个包的后续更新一直没进
        # 已提交的 site/packs）。摘要与 manifest 不一致时拒绝覆盖、fail-closed——
        # 先跑 python3 build.py 再构建站点，别让旧包把已提交镜像改坏。
        stale = []
        for pack in data["packs"]:
            src = dist_dir / f"{pack['id']}.zip"
            if not src.is_file():
                continue
            want = pack.get("sha256") or ""
            got = hashlib.sha256(src.read_bytes()).hexdigest()
            if want and got != want:
                stale.append(f"{pack['id']}（dist={got[:12]}… manifest={want[:12]}…）")
                continue
            (pack_dir / f"{pack['id']}.zip").write_bytes(src.read_bytes())
            zips += 1
        if stale:
            raise SystemExit(
                "dist 与 manifest 摘要不一致（dist 过期？先跑 python3 build.py）:\n  - "
                + "\n  - ".join(stale)
            )
        _all = dist_dir / "_all.zip"
        if _all.is_file():
            (pack_dir / "_all.zip").write_bytes(_all.read_bytes())
            zips += 1

    # 全局规则（安装后 1 分钟配置）随站点分发，保证官网链接可达
    gr = SCRIPT_DIR / "GLOBAL-RULES.md"
    if gr.is_file():
        write_text_lf(out_dir / "GLOBAL-RULES.md", gr.read_text(encoding="utf-8"))

    # 专家团子页（源：expert-teams/site/index.html，由 expert-teams/build-site.py
    # 从子树实装数据生成；此处只做站点内同步，不做二次加工）
    et_page = SCRIPT_DIR / "expert-teams" / "site" / "index.html"
    if et_page.is_file():
        write_text_lf(out_dir / "expert-teams.html", et_page.read_text(encoding="utf-8"))
        print(f"expert-teams page -> {out_dir / 'expert-teams.html'}")
    else:
        print(
            "WARN: expert-teams/site/index.html 不存在，跳过专家团子页",
            file=sys.stderr,
        )

    # 专家团安装包（源：expert-teams/dist/zips/，由 expert-teams/export-platforms.py 生成）。
    # 提交进 site/downloads/：GitCode Pages 直接从 main 的 /site 目录部署，
    # 不提交 = 镜像站下载按钮全部失效（与 site/packs/*.zip 同理）。
    et_zips = sorted((SCRIPT_DIR / "expert-teams" / "dist" / "zips").glob("*.zip"))
    if et_zips:
        dl_dir = out_dir / "downloads"
        dl_dir.mkdir(parents=True, exist_ok=True)
        for z in et_zips:
            (dl_dir / z.name).write_bytes(z.read_bytes())
        print(f"expert-teams downloads -> {dl_dir} ({len(et_zips)} zips)")
    else:
        print(
            "WARN: expert-teams/dist/zips 不存在（先跑 expert-teams/export-platforms.py），"
            "跳过安装包同步（已提交的 site/downloads 原样保留）",
            file=sys.stderr,
        )

    m = data["meta"]
    print(f"site.json: {m['n_skills']} skills / {m['n_packs']} packs / "
          f"{m['n_domains']} domains / {m['n_groups']} groups / "
          f"{m['n_chains']} chains (v{m['version']})")
    print(f"SKILL.md copies: {copied} | zip copies: {zips} | skill zips: {skill_zips} -> {out_dir}")
    missing = [p["id"] for p in data["packs"] if not p["dist_exists"]]
    if missing:
        print(f"WARN: dist 缺少 zip: {missing}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
