#!/usr/bin/env python3
"""tests for cnblogs-pre-publish-check.py（文件名含连字符，用 importlib 加载）。"""

import importlib.util
import os
import sys
import tempfile
import unittest

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "cnblogs_check",
    os.path.join(_here, "..", "scripts", "cnblogs-pre-publish-check.py"),
)
mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mod)


class CnblogsCheckTests(unittest.TestCase):
    def test_h1_detected(self):
        issues = mod.check_h1("# 标题\n## 二级")
        self.assertEqual(len(issues), 2)  # 问题 + 修复方法

    def test_h2_ok(self):
        self.assertEqual(mod.check_h1("## 二级\n### 三级"), [])

    def test_title_entities(self):
        issues = mod.check_title_entities("标题&quot;x&quot;")
        self.assertTrue(issues)
        self.assertEqual(mod.check_title_entities("正常标题"), [])

    def test_backtick_pairing(self):
        issues = mod.check_backticks("``code\nline\n```")  # 两反引号开头
        self.assertTrue(issues)
        odd = mod.check_backticks("```a\n```x\n```y")  # 三个标记=奇数
        self.assertTrue(any("不成对" in i for i in odd))

    def test_bom_file_still_checked(self):
        """Windows PowerShell 写的 UTF-8 文件带 BOM，h1 检查必须仍然生效。"""
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8-sig", suffix=".md", delete=False
        ) as fh:
            fh.write("# BOM标题\n正文\n")
            path = fh.name
        try:
            passed = mod.run_checks(path, "")
            self.assertFalse(passed)  # h1 必须被拦下
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
