# Hermetic self-test for skill_router.py: builds a tiny fake skills tree,
# checks ranking, verdicts, and determinism. No network, no repo dependency
# (the CLI smoke test runs against a generated temp tree too).
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import skill_router

SKILL_A = """---
name: backup-scheduler
description: >-
  Schedule recurring crontab backup jobs and preview next fire times.
  Use when the user asks 定时备份 / crontab / 计划任务 / schedule a daily job.
  Do NOT use for one-off commands.
---
# Backup Scheduler
"""

SKILL_B = """---
name: wechat-publisher
description: >-
  Publish articles to WeChat official account platforms. Use when the user
  asks 发文章 / 公众号发布 / publish to WeChat. Do NOT use for scheduling.
---
# WeChat Publisher
"""


class SkillRouterTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        for name, body in [("backup-scheduler", SKILL_A), ("wechat-publisher", SKILL_B)]:
            d = self.tmp / name
            d.mkdir()
            (d / "SKILL.md").write_text(body, encoding="utf-8")
        self.index = skill_router.build_index(self.tmp)

    def test_relevant_task_ranks_matching_skill_first_with_use_verdict(self):
        r = skill_router.route(
            "每天凌晨用 crontab 自动备份数据库目录并生成计划任务，预览下次执行时间",
            self.index, top=3, min_use=4.0, min_weak=3.0,
        )
        self.assertEqual(r["verdict"], "USE SKILLS")
        self.assertEqual(r["results"][0]["skill"], "backup-scheduler")

    def test_unrelated_task_yields_no_skill_needed(self):
        r = skill_router.route("你好", self.index, top=3)
        self.assertEqual(r["verdict"], "NO SKILL NEEDED")
        self.assertEqual(r["results"], [])

    def test_router_is_deterministic(self):
        task = "每天凌晨用 crontab 自动备份数据库目录并生成计划任务"
        self.assertEqual(
            skill_router.route(task, self.index), skill_router.route(task, self.index)
        )

    def test_index_ignores_sample_and_common_dirs(self):
        d = self.tmp / "sample-skill"
        d.mkdir()
        (d / "SKILL.md").write_text(
            "---\nname: sample-skill\ndescription: crontab backup\n---\n", encoding="utf-8"
        )
        idx = skill_router.build_index(self.tmp)
        self.assertNotIn("sample-skill", idx["skills"])


class CliSmokeTest(unittest.TestCase):
    def test_cli_json_against_generated_tree(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td) / "backup-scheduler"
            d.mkdir()
            (d / "SKILL.md").write_text(SKILL_A, encoding="utf-8")
            script = Path(skill_router.__file__)
            completed = subprocess.run(
                [
                    sys.executable, str(script),
                    "每天凌晨用 crontab 自动备份数据库目录并生成计划任务",
                    "--skills-dir", td, "--json", "--min-use", "4.0", "--min-weak", "3.0",
                ],
                capture_output=True, text=True, timeout=60,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            out = json.loads(completed.stdout)
            self.assertEqual(out["verdict"], "USE SKILLS")
            self.assertEqual(out["results"][0]["skill"], "backup-scheduler")


if __name__ == "__main__":
    unittest.main()


class BenchmarkGateTest(unittest.TestCase):
    """Accuracy regression gate: pinned to the repo's real skill library."""

    def test_benchmark_accuracy_floor(self):
        repo = Path(__file__).resolve().parents[4]
        bench = Path(skill_router.__file__).parent / "benchmark.py"
        sys.path.insert(0, str(bench.parent))
        import benchmark  # noqa: PLC0415
        cases = json.loads((bench.parent / "benchmark_tasks.json").read_text(encoding="utf-8"))["cases"]
        index = skill_router.build_index(repo / "skills")
        top3 = use = fp = 0
        for c in cases:
            r = skill_router.route(c["task"], index, top=3)
            got = [x["skill"] for x in r["results"]]
            if c.get("none"):
                if r["verdict"] == "USE SKILLS":
                    fp += 1
            else:
                use += 1
                if exp := set(c["expect"]):
                    if exp & set(got):
                        top3 += 1
        self.assertGreaterEqual(top3 / max(use, 1), 0.90, "top3 accuracy regressed below 90%")
        self.assertEqual(fp, 0, "false-positive USE verdicts on none-tasks")
