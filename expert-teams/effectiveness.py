#!/usr/bin/env python3
"""团队有效性与跨文档一致性门禁（平台中立，纯标准库 + PyYAML）。

check_all(base) 返回错误消息列表（空 = 通过）。由 verify.py 第 7 节调用，
也可独立用于单元测试。所有检查均为双向一致性：磁盘实装 ↔ 文档声明。
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

# 团队规模唯一口径（verify.py §4 与此共用；新增/删除团队必须同步此表）
EXPECTED_TEAM_AGENTS = {
    "academic-paper-team": 19,
    "fullstack-web-team": 19,
    "math-modeling-team": 9,
    "software-dev-team": 12,
    "visual-design-team": 14,
    "content-writing-team": 14,
    "video-production-team": 14,
    "data-analysis-team": 12,
    "marketing-team": 12,
    "ecommerce-ops-team": 12,
    "product-team": 12,
    "finance-team": 10,
    "hr-team": 10,
    "legal-compliance-team": 10,
    "translation-team": 10,
    "education-training-team": 10,
    "audio-podcast-team": 10,
    "game-design-team": 10,
}

PROTOCOL_FILE = "orchestration-protocol.md"
READONLY_CLAIMS = (
    "只读不改",
    "只读审核",
    "只读收口",
    "只读不写",
    "只读专家",
    "只读模式",
    "不改代码",
)
ROUTE_RE = re.compile(r"`teams/([a-z0-9-]+)/agents/([a-z0-9-]+)`")
MEMBER_COUNT_RE = re.compile(r"成员架构（?\s*(\d+)\s*人）?")
TABLE_ID_RE = re.compile(r"\|\s*`([a-z0-9][a-z0-9-]{2,})`\s*\|")
BADGE_AGENTS_RE = re.compile(r"Agents-(\d+)")
BADGE_SKILLS_RE = re.compile(r"Skills-(\d+)")


def _split_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    lines = text.split("\n")
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return {}, text
    try:
        meta = yaml.safe_load("\n".join(lines[1:end])) or {}
    except yaml.YAMLError:
        meta = {}
    if not isinstance(meta, dict):
        meta = {}
    return meta, "\n".join(lines[end + 1 :])


def _teams_dir(base: Path) -> Path:
    return base / "teams"


def _team_names(base: Path) -> list[str]:
    tdir = _teams_dir(base)
    if not tdir.is_dir():
        return []
    return sorted(p.name for p in tdir.iterdir() if p.is_dir())


def _agent_stems(base: Path, team: str) -> set[str]:
    adir = _teams_dir(base) / team / "agents"
    if not adir.is_dir():
        return set()
    return {p.stem for p in adir.glob("*.md")}


def _skill_dirs(base: Path) -> set[str]:
    out: set[str] = set()
    for root in [base / "skills"] + [
        _teams_dir(base) / t / "skills" for t in _team_names(base)
    ]:
        if root.is_dir():
            out |= {p.name for p in root.iterdir() if p.is_dir()}
    return out


def check_all(base: Path | str) -> list[str]:
    base = Path(base)
    errors: list[str] = []
    errors += _check_routing(base)
    errors += _check_team_membership(base)
    errors += _check_lead_reachability(base)
    errors += _check_skills_index(base)
    errors += _check_readme_badges(base)
    errors += _check_readonly_claims(base)
    errors += _check_protocol_adoption(base)
    errors += _check_expected_table(base)
    return errors


def _check_routing(base: Path) -> list[str]:
    """R1：project-director 路由表 ↔ 实际 lead 文件（双向）。"""
    errors: list[str] = []
    pd = base / "project-director.md"
    if not pd.is_file():
        return ["[路由] project-director.md 不存在"]
    text = pd.read_text(encoding="utf-8")
    routes = ROUTE_RE.findall(text)
    routed_teams = set()
    for team, agent in routes:
        routed_teams.add(team)
        if not (_teams_dir(base) / team / "agents" / f"{agent}.md").is_file():
            errors.append(f"[路由] 幽灵目标 teams/{team}/agents/{agent}.md 不存在")
    for team in _team_names(base):
        if team not in routed_teams:
            errors.append(f"[路由] 团队 {team} 未出现在 project-director 路由表")
    return errors


def _check_team_membership(base: Path) -> list[str]:
    """R1：TEAM.md 成员表 ↔ agents/ 目录（双向）+ 每团队恰有一个 team-lead。"""
    errors: list[str] = []
    for team in _team_names(base):
        team_md = _teams_dir(base) / team / "TEAM.md"
        stems = _agent_stems(base, team)
        if not stems:
            errors.append(f"[成员] {team} 无 agents/*.md")
            continue
        leads = [s for s in stems if s.endswith("team-lead")]
        if len(leads) != 1:
            errors.append(f"[成员] {team} 的 team-lead 数量为 {len(leads)}（应为 1）")
        if not team_md.is_file():
            errors.append(f"[成员] {team} 缺 TEAM.md")
            continue
        team_text = team_md.read_text(encoding="utf-8")
        m = MEMBER_COUNT_RE.search(team_text)
        if not m:
            errors.append(f"[成员] {team} TEAM.md 缺「成员架构（N 人）」标题")
        elif int(m.group(1)) != len(stems):
            errors.append(f"[成员] {team} 标题人数 {m.group(1)} ≠ 磁盘 {len(stems)}")
        table_ids = set(TABLE_ID_RE.findall(team_text))
        table_ids = {i for i in table_ids if "/" not in i}
        for stem in sorted(stems - table_ids):
            errors.append(f"[成员] {team}: 成员 {stem} 未登记进 TEAM.md 成员表")
        for ghost in sorted(table_ids - stems):
            errors.append(
                f"[成员] {team}: TEAM.md 成员表含幽灵成员 {ghost}（磁盘无此文件）"
            )
    return errors


def _check_lead_reachability(base: Path) -> list[str]:
    """R1：lead 正文必须提到每个成员（可调度），lead 成员表不得有幽灵。"""
    errors: list[str] = []
    for team in _team_names(base):
        stems = _agent_stems(base, team)
        leads = [s for s in stems if s.endswith("team-lead")]
        if len(leads) != 1:
            continue  # 由 _check_team_membership 报
        lead_path = _teams_dir(base) / team / "agents" / f"{leads[0]}.md"
        body = lead_path.read_text(encoding="utf-8")
        for member in sorted(stems - {leads[0]}):
            if member not in body:
                errors.append(
                    f"[调度] {team}: lead 正文未提及成员 {member}（无法被派发）"
                )
        for ghost in sorted(set(TABLE_ID_RE.findall(body)) - stems):
            errors.append(
                f"[调度] {team}: lead 成员表含幽灵成员 {ghost}（磁盘无此文件）"
            )
    return errors


def _check_skills_index(base: Path) -> list[str]:
    """R1：SKILLS_INDEX.md ↔ 实际 skills 目录（双向）。"""
    errors: list[str] = []
    idx = base / "SKILLS_INDEX.md"
    actual = _skill_dirs(base)
    if not idx.is_file():
        return ["[技能索引] SKILLS_INDEX.md 不存在"]
    listed = set(
        re.findall(r"`([a-z0-9][a-z0-9-]{2,})`", idx.read_text(encoding="utf-8"))
    )
    for name in sorted(actual - listed):
        errors.append(f"[技能索引] skill {name} 未登记进 SKILLS_INDEX.md")
    for ghost in sorted(listed - actual):
        errors.append(
            f"[技能索引] SKILLS_INDEX.md 含幽灵 skill {ghost}（磁盘无此目录）"
        )
    return errors


def _check_readme_badges(base: Path) -> list[str]:
    """R1：README 徽章数字 ↔ 实装（专家=团队 agent 数，技能=全部 skill 目录数）。"""
    errors: list[str] = []
    readme = base / "README.md"
    if not readme.is_file():
        return ["[README] README.md 不存在"]
    text = readme.read_text(encoding="utf-8")
    actual_agents = sum(len(_agent_stems(base, t)) for t in _team_names(base))
    actual_skills = len(_skill_dirs(base))
    m = BADGE_AGENTS_RE.search(text)
    if not m:
        errors.append("[README] 未找到 Agents-N 徽章")
    elif int(m.group(1)) != actual_agents:
        errors.append(f"[README] 徽章 Agents-{m.group(1)} ≠ 实装 {actual_agents}")
    m = BADGE_SKILLS_RE.search(text)
    if not m:
        errors.append("[README] 未找到 Skills-N 徽章")
    elif int(m.group(1)) != actual_skills:
        errors.append(f"[README] 徽章 Skills-{m.group(1)} ≠ 实装 {actual_skills}")
    return errors


def _check_readonly_claims(base: Path) -> list[str]:
    """R3：正文声称只读的成员（lead/director 除外）必须带 tools.write/edit=false。"""
    errors: list[str] = []
    files = [base / "project-director.md"]
    for team in _team_names(base):
        adir = _teams_dir(base) / team / "agents"
        if adir.is_dir():
            files += sorted(adir.glob("*.md"))
    for path in files:
        if not path.is_file():
            continue
        stem = path.stem
        if stem == "project-director" or stem.endswith("team-lead"):
            continue
        text = path.read_text(encoding="utf-8")
        if not any(k in text for k in READONLY_CLAIMS):
            continue
        meta, _ = _split_frontmatter(text)
        tools = meta.get("tools")
        if not (
            isinstance(tools, dict)
            and tools.get("write") is False
            and tools.get("edit") is False
        ):
            errors.append(
                f"[只读] {stem} 正文声称只读，但 frontmatter 缺 tools.write/edit=false"
            )
    return errors


def _check_protocol_adoption(base: Path) -> list[str]:
    """R2：每个 team-lead 必须引用共享编排协议。"""
    errors: list[str] = []
    if not (base / PROTOCOL_FILE).is_file():
        errors.append(f"[编排协议] 根目录缺 {PROTOCOL_FILE}")
    for team in _team_names(base):
        stems = _agent_stems(base, team)
        leads = [s for s in stems if s.endswith("team-lead")]
        if len(leads) != 1:
            continue
        body = (_teams_dir(base) / team / "agents" / f"{leads[0]}.md").read_text(
            encoding="utf-8"
        )
        if PROTOCOL_FILE not in body:
            errors.append(f"[编排协议] {team} lead 未引用 {PROTOCOL_FILE}")
    return errors


def _check_expected_table(base: Path) -> list[str]:
    """R1：EXPECTED_TEAM_AGENTS ↔ teams/ 目录（双向），防新增/删除团队忘同步。"""
    errors: list[str] = []
    actual = set(_team_names(base))
    expected = set(EXPECTED_TEAM_AGENTS)
    for team in sorted(expected - actual):
        errors.append(f"[规模口径] expected 表残留已删除团队 {team}")
    for team in sorted(actual - expected):
        errors.append(f"[规模口径] 新增团队 {team} 未登记进 EXPECTED_TEAM_AGENTS")
    return errors


if __name__ == "__main__":
    import sys

    base = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent
    errs = check_all(base)
    for e in errs:
        print(f"  ❌ {e}")
    if errs:
        raise SystemExit(1)
    print("  ✅ 团队有效性检查通过")
