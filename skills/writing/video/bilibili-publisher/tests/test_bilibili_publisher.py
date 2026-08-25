#!/usr/bin/env python3
"""tests for bilibili_publisher.py — 纯函数测试，不发网络请求。"""

import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import bilibili_publisher as b  # noqa: E402


class BilibiliPublishTests(unittest.TestCase):
    def test_dry_run_guard(self):
        self.assertFalse(b.dry_run_guard(False))
        self.assertTrue(b.dry_run_guard(True))

    def test_parse_bili_success(self):
        raw = b'{"code": 0, "data": {"bvid": "BV123"}}'
        out = b.parse_bili_response(raw)
        self.assertEqual(out["data"]["bvid"], "BV123")

    def test_parse_bili_error(self):
        raw = b'{"code": 400, "message": "bad"}'
        with self.assertRaises(b.BiliAPIError) as cm:
            b.parse_bili_response(raw)
        self.assertEqual(cm.exception.code, 400)

    def test_get_credentials_missing(self):
        with mock.patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(SystemExit):
                b.get_official_credentials(mock.Mock())


if __name__ == "__main__":
    unittest.main()
