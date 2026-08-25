#!/usr/bin/env python3
"""tests for static_blog_deploy.py — 纯函数测试，不发网络请求。"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import static_blog_deploy as s  # noqa: E402


class StaticBlogDeployTests(unittest.TestCase):
    def test_dry_run_guard(self):
        self.assertFalse(s.dry_run_guard(False))
        self.assertTrue(s.dry_run_guard(True))

    def test_run_cmd_dry_run(self):
        # dry-run 模式下不实际运行命令
        rc = s.run_cmd(["echo", "test"], execute=False)
        self.assertEqual(rc, 0)

    def test_run_cmd_execute(self):
        # 实际执行简单命令
        rc = s.run_cmd([sys.executable, "-c", "print('ok')"], execute=True)
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
