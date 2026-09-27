#!/usr/bin/env python3
"""export-platforms.py — 把 teams/ + skills/ 导出为 4 个宿主的原生安装包。

输出（位于 dist/ 下，只重建本脚本自己的 4 个子目录，不动 export-agents.py 的产物）：
  dist/opencode/.opencode/{agents,skills}/     OpenCode 项目级包
  dist/claude/.claude/{agents,skills}/         Claude Code 项目级包
  dist/cursor/{.cursor-plugin,agents,skills}/  Cursor Plugin 包
  dist/gemini/{gemini-extension.json,GEMINI.md,commands,skills}

平台契约（来源，2026-09 抓取）：
  OpenCode   opencode.ai/docs/agents — .opencode/agents/*.md，文件名即 agent 名，
             必填 description，mode: subagent|all，permission: {edit/bash: allow|deny}
  Claude Code docs.anthropic.com/claude-code/sub-agents — .claude/agents/*.md，
             必填 name + description，可选 tools / disallowedTools / model
  Cursor     cursor.com/docs/plugins — .cursor-plugin/plugin.json 仅需 name，
             agents/skills/commands/rules 按插件根默认目录自动发现
  Gemini CLI github.com/google-gemini/gemini-cli — gemini-extension.json
             (name/version/contextFileName) + GEMINI.md + commands/*.toml
             (prompt 多行字符串 + {{args}} 注入)

仅依赖标准库 + PyYAML。用法：python3 export-platforms.py
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent
DIST = REPO / "dist"
VERSION = "1.0.0"
PLUGIN_NAME = "expert-teams"
CLAUDE_TOOLS_MAP = {"write": "Write", "edit": "Edit", "bash": "Bash", "read": "Read"}


def load_split_frontmatter():
    """文件名带连字符无法直接 import，用 importlib 复用 export-agents.py 的解析器。"""
    spec = importlib.util.spec_from_file_location(
        "export_agents_mod", REPO / "export-agents.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.split_frontmatter


split_frontmatter = load_split_frontmatter()


def collect_agents() -> list[dict]:
    """全部 agent：219 个团队成员 + project-director。"""
    out: list[dict] = []
    for team_dir in sorted((REPO / "teams").iterdir()):
        agents_dir = team_dir / "agents"
        if not team_dir.is_dir() or not agents_dir.is_dir():
            continue
        for path in sorted(agents_dir.glob("*.md")):
            out.append(_load_agent(path, team_dir.name))
    director = REPO / "project-director.md"
    if director.is_file():
        out.append(_load_agent(director, ""))
    return out


def _load_agent(path: Path, team: str) -> dict:
    meta, body = split_frontmatter(path.read_text(encoding="utf-8"))
    return {"id": path.stem, "team": team, "meta": meta, "body": body}


def collect_skills() -> list[tuple[str, Path]]:
    """全部 skill（通用 + 团队），按名称去重并保持唯一性。"""
    seen: dict[str, Path] = {}
    roots = [REPO / "skills"] + [
        p / "skills" for p in sorted((REPO / "teams").iterdir()) if p.is_dir()
    ]
    for root in roots:
        if not root.is_dir():
            continue
        for d in sorted(root.iterdir()):
            if d.is_dir() and not d.name.startswith("."):
                if d.name in seen:
                    raise SystemExit(f"[冲突] skill 名重复：{d.name}")
                seen[d.name] = d
    return sorted(seen.items())


def render_frontmatter(meta: dict) -> str:
    body = yaml.safe_dump(
        meta,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
        width=10**6,
    ).rstrip()
    return f"---\n{body}\n---\n\n"


def readonly_tools(meta: dict) -> dict:
    tools = meta.get("tools")
    return tools if isinstance(tools, dict) else {}


def opencode_meta(agent: dict) -> dict:
    meta = agent["meta"]
    out: dict = {"description": str(meta.get("description") or agent["id"])}
    out["mode"] = "all" if agent["id"] == "project-director" else "subagent"
    if meta.get("temperature") is not None:
        out["temperature"] = meta["temperature"]
    tools = readonly_tools(meta)
    permission = {}
    if tools.get("write") is False or tools.get("edit") is False:
        permission["edit"] = "deny"
    if tools.get("bash") is False:
        permission["bash"] = "deny"
    if permission:
        out["permission"] = permission
    return out


def claude_meta(agent: dict) -> dict:
    meta = agent["meta"]
    out: dict = {
        "name": agent["id"],
        "description": str(meta.get("description") or agent["id"]),
    }
    tools = readonly_tools(meta)
    denied = [
        claude_tool
        for key, claude_tool in CLAUDE_TOOLS_MAP.items()
        if tools.get(key) is False
    ]
    if denied:
        out["disallowedTools"] = ", ".join(denied)
    if meta.get("temperature") is not None:
        out["temperature"] = meta["temperature"]
    return out


def export_opencode(agents: list[dict], skills: list[tuple[str, Path]]) -> None:
    root = DIST / "opencode" / ".opencode"
    agents_dir = root / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    for agent in agents:
        text = render_frontmatter(opencode_meta(agent)) + agent["body"].strip() + "\n"
        (agents_dir / f"{agent['id']}.md").write_text(text, encoding="utf-8")
    skills_dir = root / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    for name, src in skills:
        shutil.copytree(src, skills_dir / name, dirs_exist_ok=True)


def export_claude(agents: list[dict], skills: list[tuple[str, Path]]) -> None:
    root = DIST / "claude" / ".claude"
    agents_dir = root / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    for agent in agents:
        text = render_frontmatter(claude_meta(agent)) + agent["body"].strip() + "\n"
        (agents_dir / f"{agent['id']}.md").write_text(text, encoding="utf-8")
    skills_dir = root / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    for name, src in skills:
        shutil.copytree(src, skills_dir / name, dirs_exist_ok=True)


def export_cursor(agents: list[dict], skills: list[tuple[str, Path]]) -> None:
    root = DIST / "cursor"
    manifest = root / ".cursor-plugin"
    manifest.mkdir(parents=True, exist_ok=True)
    # 契约：Cursor Plugin manifest 仅必需 name，组件按插件根默认目录自动发现
    (manifest / "plugin.json").write_text(
        json.dumps(
            {
                "name": PLUGIN_NAME,
                "version": VERSION,
                "description": "18 支 AI 专家团队 / 220 agents / 100 skills，平台中立源格式导出",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    agents_dir = root / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    for agent in agents:
        # Cursor 沿用平台中立 frontmatter（description/tools/temperature）
        meta = {k: v for k, v in agent["meta"].items() if v is not None}
        text = render_frontmatter(meta) + agent["body"].strip() + "\n"
        (agents_dir / f"{agent['id']}.md").write_text(text, encoding="utf-8")
    skills_dir = root / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    for name, src in skills:
        shutil.copytree(src, skills_dir / name, dirs_exist_ok=True)


def toml_string(text: str) -> str:
    """转成可放进 TOML 多行基本字符串（\"\"\"）的内容：先转义反斜杠再转义引号。"""
    return text.replace("\\", "\\\\").replace('"', '\\"')


def export_gemini(
    agents: list[dict], skills: list[tuple[str, Path]], teams: list[str]
) -> None:
    root = DIST / "gemini"
    root.mkdir(parents=True, exist_ok=True)
    (root / "gemini-extension.json").write_text(
        json.dumps(
            {
                "name": PLUGIN_NAME,
                "version": VERSION,
                "description": "18 支 AI 专家团队：/命令 调团队 lead，按 orchestration-protocol 编排",
                "contextFileName": "GEMINI.md",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "GEMINI.md").write_text(build_gemini_context(teams), encoding="utf-8")

    commands = root / "commands"
    commands.mkdir(parents=True, exist_ok=True)
    leads = {a["team"]: a for a in agents if a["id"].endswith("team-lead")}
    for team in teams:
        lead = leads.get(team)
        if lead is None:
            raise SystemExit(f"[缺失] 团队 {team} 无 team-lead，无法生成 command")
        prompt = "{{args}}\n\n" + lead["body"].strip()
        desc = (
            str(lead["meta"].get("description") or f"{team} team lead")
            .replace("\\", "\\\\")
            .replace('"', '\\"')
        )
        text = f'description = "{desc}"\nprompt = """\n{toml_string(prompt)}\n"""\n'
        (commands / f"{team}.toml").write_text(text, encoding="utf-8")

    skills_dir = root / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    for name, src in skills:
        shutil.copytree(src, skills_dir / name, dirs_exist_ok=True)


def build_gemini_context(teams: list[str]) -> str:
    lines = [
        "# AI Expert Teams（Gemini CLI 扩展上下文）",
        "",
        "本扩展由 `export-platforms.py` 从平台中立源格式导出。",
        "",
        "## 用法",
        "",
        "- 用 `/<team-name> <任务>` 调起对应团队的 team-lead（如 `/marketing-team 做个 618 方案`）。",
        "- lead 按 `{{args}}` 接收任务，负责拆解、派单、门禁与交接。",
        "",
        "## 编排纪律",
        "",
        "所有 lead 统一遵循仓库根目录 `orchestration-protocol.md`：",
        "质量门禁（H 级不交付）、回炉≤2 次、断路切换、四块交接、技能回退。",
        "",
        "## 团队路由",
        "",
        "| 命令 | 团队 |",
        "| --- | --- |",
    ]
    lines += [f"| `/{t}` | {t} |" for t in teams]
    lines += [
        "",
        "## Skills",
        "",
        f"{len(teams)} 支团队的 skills 已随包导出至 `skills/`，按需读取对应 SKILL.md。",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    agents = collect_agents()
    skills = collect_skills()
    teams = sorted({a["team"] for a in agents if a["team"]})

    for sub in ("opencode", "claude", "cursor", "gemini"):
        target = DIST / sub
        if target.exists():
            shutil.rmtree(target)

    export_opencode(agents, skills)
    export_claude(agents, skills)
    export_cursor(agents, skills)
    export_gemini(agents, skills, teams)

    print(
        f"导出完成：{len(agents)} 个 agent / {len(skills)} 个 skill / {len(teams)} 支团队"
    )
    for sub in ("opencode", "claude", "cursor", "gemini"):
        print(f"  dist/{sub}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
