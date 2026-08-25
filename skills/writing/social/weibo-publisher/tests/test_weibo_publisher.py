#!/usr/bin/env python3
"""tests for weibo_publisher.py — 纯函数测试，不发网络请求。"""

import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import weibo_publisher as w  # noqa: E402


class WeiboPublishTests(unittest.TestCase):
    def test_official_token_fallback(self):
        with mock.patch.dict("os.environ", {"WEIBO_ACCESS_TOKEN": "test_token"}):
            self.assertEqual(w.get_official_token(mock.Mock()), "test_token")

    def test_official_token_missing(self):
        with mock.patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(SystemExit):
                w.get_official_token(mock.Mock())

    def test_dry_run_guard(self):
        self.assertFalse(w.dry_run_guard(False))
        self.assertTrue(w.dry_run_guard(True))

    def test_parse_official_error(self):
        raw = b'{"error_code": 400, "error": "bad request"}'
        with self.assertRaises(w.WeiboAPIError) as cm:
            w.parse_weibo_official(raw)
        self.assertEqual(cm.exception.code, 400)

    def test_parse_web_error(self):
        raw = b'{"ok": 0, "code": 400, "msg": "bad"}'
        with self.assertRaises(w.WeiboAPIError) as cm:
            w.parse_weibo_web(raw)
        self.assertEqual(cm.exception.code, 400)


if __name__ == "__main__":
    unittest.main()
