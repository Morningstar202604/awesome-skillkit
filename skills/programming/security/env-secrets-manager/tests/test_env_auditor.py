#!/usr/bin/env python3
"""
env_auditor.py unit tests (stdlib unittest, no dependencies).

    python3 tests/test_env_auditor.py           # run all
    python3 -m pytest tests/test_env_auditor.py # via pytest

Builds a throwaway fixture repo per test; asserts detection, severity,
redaction, and hygiene checks.
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from env_auditor import EnvAuditor, is_probably_secret_value, redact  # noqa: E402


def make_repo(files: dict) -> Path:
    tmp = tempfile.TemporaryDirectory()
    root = Path(tmp.name)
    for name, content in files.items():
        p = root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    _tmpdirs.append(tmp)
    return root


_tmpdirs = []


class TestRedaction(unittest.TestCase):
    def test_long_value_redacted(self):
        self.assertEqual(redact("ghp_" + "a" * 36), "ghp_...(40 chars)")

    def test_short_value_masked(self):
        self.assertEqual(redact("short"), "***")

    def test_report_never_contains_full_secret(self):
        secret = "ghp_" + "b" * 36
        root = make_repo({"app.py": f"GITHUB_TOKEN = '{secret}'\n"})
        report = EnvAuditor(root).run()
        dumped = json.dumps(report)
        self.assertNotIn(secret, dumped)


class TestDetection(unittest.TestCase):
    def test_github_token_critical(self):
        root = make_repo({"a.py": "T = 'ghp_" + "c" * 36 + "'\n"})
        report = EnvAuditor(root).run()
        ids = [f["id"] for f in report["findings"]]
        self.assertIn("github_token", ids)

    def test_aws_key_critical(self):
        root = make_repo({"conf.txt": "key=AKIAFAKE0123456789AB\n"})
        report = EnvAuditor(root).run()
        self.assertIn("aws_access_key", [f["id"] for f in report["findings"]])

    def test_placeholder_not_flagged(self):
        root = make_repo({".gitignore": ".env\n", ".env": "API_KEY=your_api_key_here\n"})
        report = EnvAuditor(root).run()
        self.assertEqual(report["summary"]["high"], 0)

    def test_code_expression_not_flagged(self):
        root = make_repo({"s.js": "const token = process.env.AUTH_TOKEN;\n"})
        report = EnvAuditor(root).run()
        self.assertEqual(report["summary"]["high"], 0)


class TestHygiene(unittest.TestCase):
    def test_env_without_gitignore_flagged_high(self):
        root = make_repo({".env": "APP_ENV=dev\n"})
        report = EnvAuditor(root).run()
        self.assertIn("env_not_gitignored", [f["id"] for f in report["findings"]])

    def test_drift_detected_low(self):
        root = make_repo({
            ".env": "A=1\nB=2\n",
            ".env.example": "A=\n",
        })
        report = EnvAuditor(root).run()
        drift = [f for f in report["findings"] if f["id"] == "env_example_drift"]
        self.assertTrue(drift and "B" in drift[0]["message"])

    def test_rotation_date_low_finding(self):
        root = make_repo({
            ".gitignore": ".env\n",
            ".env": "API_KEY=sk-FakeKey0123456789abcdef1234\n",
            ".env.example": "API_KEY=your_api_key_here\n",
        })
        report = EnvAuditor(root).run()
        self.assertIn("no_rotation_date", [f["id"] for f in report["findings"]])


class TestHelpers(unittest.TestCase):
    def test_probably_secret_rejects_substitution(self):
        self.assertFalse(is_probably_secret_value("${DB_PASS}"))

    def test_cli_json_runs(self):
        root = make_repo({".gitignore": ".env\n", ".env": "APP_ENV=dev\n"})
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "env_auditor.py"), str(root), "--json"],
            capture_output=True, text=True, timeout=60,
        )
        payload = json.loads(proc.stdout)
        self.assertIn("summary", payload)
        self.assertEqual(proc.returncode, 0)


if __name__ == "__main__":
    import atexit
    atexit.register(lambda: [t.cleanup() for t in _tmpdirs])
    unittest.main(verbosity=2)
