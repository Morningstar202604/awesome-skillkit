"""R4/R6：平台导出产物结构断言（先写为 RED，实现 export-platforms.py 后转 GREEN）。"""

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

import tomllib
import yaml

REPO = Path(__file__).resolve().parent.parent
DIST = REPO / "dist"
TEAM_COUNT = 18
AGENT_COUNT = 220  # 219 团队成员 + project-director
SKILL_COUNT = 100
PLUGIN_NAME_RE = re.compile(r"^[a-z0-9]+([.-][a-z0-9]+)*$")


def run_export() -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "export-platforms.py"],
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
        timeout=300,
    )


def frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    lines = text.split("\n")
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return {}
    try:
        return yaml.safe_load("\n".join(lines[1:end])) or {}
    except yaml.YAMLError:
        return {}


class TestExportPlatforms(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proc = run_export()

    def test_export_succeeds(self):
        self.assertEqual(
            self.proc.returncode,
            0,
            f"export-platforms.py failed:\n{self.proc.stdout}\n{self.proc.stderr}",
        )

    def test_opencode_package(self):
        agents = sorted((DIST / "opencode" / ".opencode" / "agents").glob("*.md"))
        self.assertEqual(len(agents), AGENT_COUNT, "OpenCode agent 数量不符")
        for p in agents:
            fm = frontmatter(p.read_text(encoding="utf-8"))
            self.assertIn("description", fm, f"{p.name} 缺 description")
            self.assertIn("mode", fm, f"{p.name} 缺 mode")
            self.assertIn(fm["mode"], ("subagent", "all"), f"{p.name} mode 非法")
        skills = [
            d
            for d in (DIST / "opencode" / ".opencode" / "skills").iterdir()
            if d.is_dir()
        ]
        self.assertEqual(len(skills), SKILL_COUNT, "OpenCode skill 数量不符")

    def test_claude_package(self):
        agents = sorted((DIST / "claude" / ".claude" / "agents").glob("*.md"))
        self.assertEqual(len(agents), AGENT_COUNT, "Claude agent 数量不符")
        names = set()
        for p in agents:
            fm = frontmatter(p.read_text(encoding="utf-8"))
            self.assertIn("name", fm, f"{p.name} 缺 name（Claude Code 必需）")
            self.assertIn(
                "description", fm, f"{p.name} 缺 description（Claude Code 必需）"
            )
            self.assertEqual(fm["name"], p.stem, f"{p.name} name 与文件名不一致")
            names.add(fm["name"])
        self.assertEqual(
            len(names), AGENT_COUNT, "Claude agent name 存在重复（同名只加载一个）"
        )
        skills = [
            d for d in (DIST / "claude" / ".claude" / "skills").iterdir() if d.is_dir()
        ]
        self.assertEqual(len(skills), SKILL_COUNT, "Claude skill 数量不符")

    def test_claude_readonly_mapping(self):
        sample = DIST / "claude" / ".claude" / "agents" / "core-architect.md"
        self.assertTrue(sample.exists(), "缺少只读角色 core-architect 导出")
        fm = frontmatter(sample.read_text(encoding="utf-8"))
        tools = str(fm.get("disallowedTools", ""))
        self.assertIn("Write", tools, "只读角色未禁用 Write")

    def test_cursor_package(self):
        root = DIST / "cursor"
        manifest = root / ".cursor-plugin" / "plugin.json"
        self.assertTrue(manifest.exists(), "缺 .cursor-plugin/plugin.json")
        data = json.loads(manifest.read_text(encoding="utf-8"))
        self.assertRegex(data["name"], PLUGIN_NAME_RE)
        self.assertEqual(
            len(list((root / "agents").glob("*.md"))),
            AGENT_COUNT,
            "Cursor agent 数量不符",
        )
        self.assertEqual(
            len([d for d in (root / "skills").iterdir() if d.is_dir()]), SKILL_COUNT
        )

    def test_gemini_package(self):
        root = DIST / "gemini"
        ext = json.loads((root / "gemini-extension.json").read_text(encoding="utf-8"))
        for key in ("name", "version", "contextFileName"):
            self.assertIn(key, ext, f"gemini-extension.json 缺 {key}")
        self.assertTrue(
            (root / "GEMINI.md").read_text(encoding="utf-8").strip(), "GEMINI.md 为空"
        )
        tomls = list((root / "commands").glob("*.toml"))
        self.assertEqual(len(tomls), TEAM_COUNT, "Gemini 命令数应等于团队数")
        for p in tomls:
            text = p.read_text(encoding="utf-8")
            self.assertIn('prompt = """', text, f"{p.name} 缺多行 prompt")
            self.assertIn("{{args}}", text, f"{p.name} 缺 {{args}} 注入点")

    def test_gemini_toml_semantic_parse(self):
        for p in sorted((DIST / "gemini" / "commands").glob("*.toml")):
            data = tomllib.loads(p.read_text(encoding="utf-8"))
            prompt = data.get("prompt", "")
            self.assertTrue(data.get("description"), f"{p.name} 缺 description")
            self.assertIn("{{args}}", prompt, f"{p.name} prompt 无 {{args}}")
            self.assertGreater(len(prompt), 500, f"{p.name} prompt 内容疑似截断")

    def test_agent_names_consistent_across_platforms(self):
        roots = {
            "claude": DIST / "claude" / ".claude" / "agents",
            "opencode": DIST / "opencode" / ".opencode" / "agents",
            "cursor": DIST / "cursor" / "agents",
        }
        sets = {k: {p.stem for p in v.glob("*.md")} for k, v in roots.items()}
        for k, names in sets.items():
            self.assertEqual(len(names), AGENT_COUNT, f"{k} agent 数量不符")
        self.assertEqual(
            sets["claude"], sets["opencode"], "claude/opencode agent 名单漂移"
        )
        self.assertEqual(sets["claude"], sets["cursor"], "claude/cursor agent 名单漂移")

    def test_cursor_frontmatter_contract(self):
        source_tools = {}
        for p in (REPO / "teams").rglob("*.md"):
            if p.parent.name == "agents":
                source_tools.setdefault(
                    p.stem, frontmatter(p.read_text(encoding="utf-8"))
                )
        for p in sorted((DIST / "cursor" / "agents").glob("*.md")):
            fm = frontmatter(p.read_text(encoding="utf-8"))
            self.assertTrue(fm.get("description"), f"{p.name} 缺 description")
            src = source_tools.get(p.stem, {})
            if src.get("tools"):
                self.assertEqual(
                    fm.get("tools"), src["tools"], f"{p.name} tools 与源不一致"
                )
            else:
                self.assertNotIn("tools", fm, f"{p.name} 源未声明 tools 却被注入")


class TestExistingGates(unittest.TestCase):
    """既有三道门禁保持绿色（回归网）。"""

    def test_verify_py(self):
        proc = subprocess.run(
            [sys.executable, "verify.py"],
            cwd=REPO,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
            timeout=300,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_export_agents_py(self):
        proc = subprocess.run(
            [sys.executable, "export-agents.py"],
            cwd=REPO,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
            timeout=300,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
