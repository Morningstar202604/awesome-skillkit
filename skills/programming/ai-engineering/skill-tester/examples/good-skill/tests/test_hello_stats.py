#!/usr/bin/env python3
"""hello_stats 的自动化测试（unittest，纯标准库）。

运行：python3 -m unittest discover tests -v
"""

import io
import json
import os
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import hello_stats  # noqa: E402


class TestParseNumbers(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(hello_stats.parse_numbers("1, 2,3.5"), [1.0, 2.0, 3.5])

    def test_newline_separated(self):
        self.assertEqual(hello_stats.parse_numbers("1\n2"), [1.0, 2.0])

    def test_rejects_garbage(self):
        with self.assertRaises(ValueError):
            hello_stats.parse_numbers("abc")

    def test_rejects_empty(self):
        with self.assertRaises(ValueError):
            hello_stats.parse_numbers(" , ,")


class TestComputeStats(unittest.TestCase):
    def test_known_values(self):
        s = hello_stats.compute_stats([1.0, 2.0, 3.0, 4.0])
        self.assertEqual(s["count"], 4)
        self.assertAlmostEqual(s["mean"], 2.5)
        self.assertAlmostEqual(s["median"], 2.5)
        self.assertAlmostEqual(s["min"], 1.0)
        self.assertAlmostEqual(s["max"], 4.0)

    def test_percentiles(self):
        s = hello_stats.compute_stats(list(range(1, 101)), pcts=(90,))
        self.assertAlmostEqual(s["p90"], 90.1)

    def test_percentile_out_of_range(self):
        with self.assertRaises(ValueError):
            hello_stats.percentile([1.0], 150)


class TestCli(unittest.TestCase):
    def run_cli(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = hello_stats.main(argv)
        return rc, out.getvalue(), err.getvalue()

    def test_json_mode(self):
        rc, out, _ = self.run_cli(["1,2,3.5,4", "--json"])
        self.assertEqual(rc, 0)
        payload = json.loads(out)
        self.assertEqual(payload["stats"]["count"], 4)

    def test_table_mode(self):
        rc, out, _ = self.run_cli(["1,2,3.5,4"])
        self.assertEqual(rc, 0)
        self.assertIn("mean", out)

    def test_bad_input_exit_code(self):
        rc, _, err = self.run_cli(["abc"])
        self.assertEqual(rc, 2)
        self.assertIn("error:", err)

    def test_missing_args_exit_code(self):
        rc, _, err = self.run_cli([])
        self.assertEqual(rc, 2)
        self.assertIn("缺少 numbers", err)

    def test_help_lists_flags(self):
        with self.assertRaises(SystemExit) as ctx:
            with redirect_stdout(io.StringIO()):
                hello_stats.main(["--help"])
        self.assertEqual(ctx.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
