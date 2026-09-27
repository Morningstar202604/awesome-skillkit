"""R1/R2/R3/R5：团队有效性与一致性门禁（effectiveness.py 单元测试 + 真实仓库断言）。"""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parent.parent
# 子目录迁入 awesome-skillkit 后，从仓库根运行 unittest 时需把子树根加入
# sys.path，才能找到同目录的 effectiveness.py
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import effectiveness  # RED：模块未实现时报 ImportError


def make_fixture(tmp: str) -> Path:
    """构造一个通过全部 effectiveness 检查的最小仓库。"""
    root = Path(tmp)
    (root / "teams" / "demo-team" / "agents").mkdir(parents=True)
    (root / "teams" / "demo-team" / "skills" / "demo-skill").mkdir(parents=True)
    (root / "skills" / "gen-skill").mkdir(parents=True)

    (root / "README.md").write_text(
        '# x\n<img src="badge/Agents-2_experts" />\n<img src="badge/Skills-2" />\n',
        encoding="utf-8",
    )
    (root / "SKILLS_INDEX.md").write_text(
        "# idx\n`gen-skill`\n`demo-skill`\n", encoding="utf-8"
    )
    (root / "project-director.md").write_text(
        "| kw | scene | route |\n|---|---|---|\n| demo | Demo | `teams/demo-team/agents/demo-team-lead` |\n",
        encoding="utf-8",
    )
    (root / "orchestration-protocol.md").write_text("# protocol\n", encoding="utf-8")
    (root / "teams" / "demo-team" / "TEAM.md").write_text(
        "## 成员架构（2 人）\n\n| 角色 | Agent ID |\n|---|---|\n"
        "| lead | `demo-team-lead` |\n| qa | `demo-qa` |\n",
        encoding="utf-8",
    )
    (root / "teams" / "demo-team" / "agents" / "demo-team-lead.md").write_text(
        "---\ndescription: lead\n---\n# lead\n见 orchestration-protocol.md。\n成员：`demo-qa`。\n",
        encoding="utf-8",
    )
    (root / "teams" / "demo-team" / "agents" / "demo-qa.md").write_text(
        "---\ndescription: qa\ntools: { write: false, edit: false }\n---\n# qa\n只读审核，不改交付物。\n",
        encoding="utf-8",
    )
    (root / "teams" / "demo-team" / "skills" / "demo-skill" / "SKILL.md").write_text(
        "---\nname: demo-skill\ndescription: d\n---\nbody\n", encoding="utf-8"
    )
    (root / "skills" / "gen-skill" / "SKILL.md").write_text(
        "---\nname: gen-skill\ndescription: d\n---\nbody\n", encoding="utf-8"
    )
    return root


class FixtureCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = make_fixture(self.tmp)
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        patcher = mock.patch.object(
            effectiveness, "EXPECTED_TEAM_AGENTS", {"demo-team": 2}
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def errors(self):
        return effectiveness.check_all(self.root)


class TestBaseline(FixtureCase):
    def test_valid_fixture_has_no_errors(self):
        self.assertEqual(self.errors(), [])

    def test_missing_member_in_team_md(self):
        team_md = self.root / "teams" / "demo-team" / "TEAM.md"
        team_md.write_text(
            team_md.read_text(encoding="utf-8").replace("| qa | `demo-qa` |\n", ""),
            encoding="utf-8",
        )
        joined = "\n".join(self.errors())
        self.assertIn("demo-qa", joined, "TEAM.md 缺成员行未被发现")

    def test_lead_not_referencing_protocol(self):
        lead = self.root / "teams" / "demo-team" / "agents" / "demo-team-lead.md"
        lead.write_text(
            lead.read_text(encoding="utf-8").replace(
                "orchestration-protocol.md", "别的东西"
            ),
            encoding="utf-8",
        )
        joined = "\n".join(self.errors())
        self.assertIn("orchestration-protocol", joined, "lead 未引用编排协议未被发现")

    def test_readonly_claim_without_tools(self):
        qa = self.root / "teams" / "demo-team" / "agents" / "demo-qa.md"
        qa.write_text(
            qa.read_text(encoding="utf-8").replace(
                "tools: { write: false, edit: false }\n", ""
            ),
            encoding="utf-8",
        )
        joined = "\n".join(self.errors())
        self.assertIn("demo-qa", joined, "声称只读却无 tools 约束未被发现")

    def test_stale_route_target(self):
        pd = self.root / "project-director.md"
        pd.write_text(
            pd.read_text(encoding="utf-8").replace("demo-team-lead", "ghost-lead"),
            encoding="utf-8",
        )
        joined = "\n".join(self.errors())
        self.assertIn("ghost-lead", joined, "路由幽灵目标未被发现")

    def test_skills_index_gap(self):
        idx = self.root / "SKILLS_INDEX.md"
        idx.write_text(
            idx.read_text(encoding="utf-8").replace("`demo-skill`\n", ""),
            encoding="utf-8",
        )
        joined = "\n".join(self.errors())
        self.assertIn("demo-skill", joined, "SKILLS_INDEX 漏登记未被发现")

    def test_readme_badge_drift(self):
        rd = self.root / "README.md"
        rd.write_text(
            rd.read_text(encoding="utf-8").replace("Agents-2_", "Agents-99_"),
            encoding="utf-8",
        )
        joined = "\n".join(self.errors())
        self.assertIn("README", joined, "README 徽章数字漂移未被发现")


class TestRealRepo(unittest.TestCase):
    """真实仓库全量断言（S1.2 / S2.1 / S3.1 的 GREEN 形态）。"""

    def test_real_repo_passes(self):
        errs = effectiveness.check_all(REPO)
        self.assertEqual(errs, [], "真实仓库未通过有效性门禁:\n" + "\n".join(errs))


if __name__ == "__main__":
    unittest.main()
