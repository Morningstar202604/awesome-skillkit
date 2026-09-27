#!/usr/bin/env python3
"""
export-agents.py — 将仓库中的 markdown agent 定义导出为平台中立的通用格式。

输出（全部位于仓库根目录 dist/ 下，每次运行清空重建）：
  dist/agents.json                      结构化 JSON 导出
  dist/teams/<team>/<agent-id>.txt      每个 agent 一份纯文本 system prompt
  dist/system-prompts/<team>-team.md   每个团队一份汇总 system prompt

仅依赖标准库 + PyYAML。用法：python3 export-agents.py
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent
TEAMS_DIR = REPO_ROOT / "teams"
COMMON_SKILLS_DIR = REPO_ROOT / "skills"
DIST_DIR = REPO_ROOT / "dist"


# --------------------------------------------------------------------------- #
# 解析 markdown agent 文件
# --------------------------------------------------------------------------- #
def split_frontmatter(text: str) -> tuple[dict, str]:
    """把带 YAML frontmatter 的 markdown 拆成 (meta_dict, body_str)。

    文件必须以 --- 开头；找不到 frontmatter 时返回 ({}, 原文)。
    """
    if not text.startswith("---"):
        return {}, text

    # 找第二个独占一行的 ---
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return {}, text

    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        return {}, text

    fm_text = "".join(lines[1:end_idx])
    body = "".join(lines[end_idx + 1 :])

    try:
        meta = yaml.safe_load(fm_text) or {}
    except yaml.YAMLError as exc:
        print(f"  [警告] frontmatter 解析失败，按空 meta 处理：{exc}", file=sys.stderr)
        meta = {}
    if not isinstance(meta, dict):
        meta = {}

    return meta, body.strip("\n")


def extract_title(body: str) -> str:
    """从正文第一个 '# ' 标题提取标题文本（去掉 '# ' 前缀）。"""
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return ""


def derive_role(title: str) -> str:
    """从标题派生角色名：取 ' - ' 前半段；没有则留空。"""
    if not title:
        return ""
    # 形如「选题策略师 - 严选题」→ 角色 = 选题策略师
    if " - " in title:
        return title.split(" - ", 1)[0].strip()
    return ""


def tools_to_readable(tools: dict) -> str:
    """把 tools 字典转成人类可读的工具约束描述。"""
    if not isinstance(tools, dict) or not tools:
        return ""

    denied, granted = [], []
    for name, enabled in tools.items():
        if enabled is False:
            denied.append(str(name))
        elif enabled is True:
            granted.append(str(name))
        else:
            # 非布尔值（如嵌套权限块），原样描述
            granted.append(f"{name}={enabled}")

    parts = []
    readonly = set(denied) >= {"write", "edit"}
    if readonly:
        parts.append("只读模式")
    if denied:
        parts.append("禁止 " + "、".join(denied))
    if granted:
        parts.append("允许 " + "、".join(granted))
    return "；".join(parts) if parts else ""


# --------------------------------------------------------------------------- #
# 单个 agent 的纯文本 system prompt
# --------------------------------------------------------------------------- #
def build_system_prompt_text(meta: dict, body: str, title: str) -> str:
    """生成可直接粘贴进任意 agent 平台的纯文本 system prompt。"""
    chunks: list[str] = [title, ""]

    description = meta.get("description")
    if description:
        chunks.append(f"角色描述：{description}")

    temperature = meta.get("temperature")
    if temperature is not None:
        chunks.append(f"温度设定：{temperature}（建议值，具体取决于所用平台）")

    tools = meta.get("tools")
    if isinstance(tools, dict) and tools:
        readable = tools_to_readable(tools)
        if readable:
            chunks.append(f"工具约束建议：{readable}")

    chunks.append("")
    chunks.append("---")
    chunks.append("")
    chunks.append(body.strip())

    return "\n".join(chunks).rstrip() + "\n"


# --------------------------------------------------------------------------- #
# TEAM.md 要点提取
# --------------------------------------------------------------------------- #
def extract_team_intro(team_md_path: Path) -> str:
    """从 TEAM.md 提取团队定位要点：场景行 + 团队定位小节 + 成员规模。"""
    if not team_md_path.exists():
        return ""

    text = team_md_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    picked: list[str] = []

    # 1) 开头的 > 场景：... 引用行
    for line in lines[:5]:
        if line.strip().startswith(">"):
            picked.append(line.strip().lstrip("> ").strip())
            break

    # 2) ## 团队定位 小节内容（到下一个 ## 为止）
    section = _extract_section(lines, "团队定位")
    if section:
        picked.append("**团队定位**")
        picked.extend(section)

    # 3) 成员架构标题里的人数
    m = re.search(r"##\s*成员架构（?\s*(\d+)\s*人）?", text)
    if m:
        picked.append(f"**成员规模**：共 {m.group(1)} 名专家。")

    # 4) Workflow 对照表头要点（可选）
    wf = _extract_section(lines, "Workflow")
    if wf:
        # 只取表格里的 workflow 名称行，避免整表过长
        wf_names = [
            ln.strip() for ln in wf if ln.strip().startswith("|") and "**W" in ln
        ]
        if wf_names:
            picked.append(
                "**核心 Workflow**："
                + "；".join(re.sub(r"[*|]", "", w).strip() for w in wf_names)
            )

    return "\n\n".join(p for p in picked if p).strip()


def _extract_section(lines: list[str], heading_keyword: str) -> list[str]:
    """提取某个 ## 小节下的正文行（不含标题行本身），直到下一个 ## 。"""
    out: list[str] = []
    inside = False
    for line in lines:
        if line.startswith("## "):
            if inside:
                break
            if heading_keyword in line:
                inside = True
                continue
        elif inside:
            out.append(line.rstrip())
    # 去掉尾部空行
    while out and not out[-1].strip():
        out.pop()
    return out


# --------------------------------------------------------------------------- #
# 主流程
# --------------------------------------------------------------------------- #
def collect_common_skills() -> list[str]:
    """顶层 skills/ 目录下的所有通用 skill 名（排序）。"""
    if not COMMON_SKILLS_DIR.exists():
        return []
    return sorted(
        p.name
        for p in COMMON_SKILLS_DIR.iterdir()
        if p.is_dir() and not p.name.startswith(".")
    )


def collect_team_skills(team_dir: Path) -> list[str]:
    team_skills = team_dir / "skills"
    if not team_skills.exists():
        return []
    return sorted(
        p.name
        for p in team_skills.iterdir()
        if p.is_dir() and not p.name.startswith(".")
    )


def process_team(team_dir: Path) -> dict:
    """处理一个团队目录，返回 JSON team 对象，并写出 txt / 团队 md。"""
    team_name = team_dir.name
    agents_dir = team_dir / "agents"
    agent_files = sorted(agents_dir.glob("*.md"), key=lambda p: p.name)

    team_obj = {
        "team": team_name,
        "team_skills": collect_team_skills(team_dir),
        "agents": [],
    }

    # 该团队所有 agent 的纯文本 system prompt，用于汇总 md
    team_sysprompts: list[tuple[str, str]] = []

    teams_out_dir = DIST_DIR / "teams" / team_name
    teams_out_dir.mkdir(parents=True, exist_ok=True)

    for agent_path in agent_files:
        agent_id = agent_path.stem  # 文件名即 agent id
        raw = agent_path.read_text(encoding="utf-8")
        meta, body = split_frontmatter(raw)
        title = extract_title(body)

        agent_obj = {
            "id": agent_id,
            "title": title,
            "role": derive_role(title),
            "description": meta.get("description") or "",
            "temperature": meta.get("temperature"),
            "tools": meta.get("tools"),
            "body": body.strip(),
        }
        team_obj["agents"].append(agent_obj)

        # b. 纯文本 system prompt
        txt = build_system_prompt_text(meta, body, title)
        (teams_out_dir / f"{agent_id}.txt").write_text(txt, encoding="utf-8")
        team_sysprompts.append((agent_id, txt))

    # c. 团队汇总 md
    intro = extract_team_intro(team_dir / "TEAM.md")
    md_parts = [f"# {team_name} 专家团队 - 完整 system prompt 汇总", ""]
    if intro:
        md_parts += [intro, ""]
    md_parts.append(
        "> 以下为该团队全部成员的 system prompt，可整队复制或按需拆分使用。"
    )
    md_parts.append("")

    for agent_id, txt in team_sysprompts:
        md_parts.append(f"## {agent_id}")
        md_parts.append("")
        md_parts.append(txt.rstrip())
        md_parts.append("")
        md_parts.append("")

    sp_out_dir = DIST_DIR / "system-prompts"
    sp_out_dir.mkdir(parents=True, exist_ok=True)
    (sp_out_dir / f"{team_name}-team.md").write_text(
        "\n".join(md_parts).rstrip() + "\n", encoding="utf-8"
    )

    return team_obj


def main() -> int:
    # 幂等：只清理本脚本自己的产物，保留 export-platforms.py 的平台包
    for own in ("teams", "system-prompts"):
        target = DIST_DIR / own
        if target.exists():
            shutil.rmtree(target)
    agents_json = DIST_DIR / "agents.json"
    if agents_json.exists():
        agents_json.unlink()
    DIST_DIR.mkdir(parents=True, exist_ok=True)

    common_skills = collect_common_skills()

    team_dirs = sorted(p for p in TEAMS_DIR.iterdir() if p.is_dir())

    teams_out: list[dict] = []
    total_agents = 0
    for team_dir in team_dirs:
        team_obj = process_team(team_dir)
        teams_out.append(team_obj)
        total_agents += len(team_obj["agents"])
        print(
            f"  [团队] {team_dir.name}: {len(team_obj['agents'])} 个 agent, "
            f"{len(team_obj['team_skills'])} 个团队 skill"
        )

    payload = {
        "version": 1,
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "teams": teams_out,
        "common_skills": common_skills,
    }

    json_path = DIST_DIR / "agents.json"
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print()
    print(
        f"导出完成：{len(teams_out)} 个团队 / {total_agents} 个 agent "
        f"/ {len(common_skills)} 个通用 skill"
    )
    print(f"  JSON:      {json_path.relative_to(REPO_ROOT)}")
    print("  纯文本:    dist/teams/<team>/<agent-id>.txt")
    print("  团队汇总:  dist/system-prompts/<team>-team.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
