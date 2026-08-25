#!/usr/bin/env python3
"""tests for toutiao_publisher.py — 纯函数测试，不发网络请求。"""

import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import toutiao_publisher as t  # noqa: E402


class ToutiaoPublishTests(unittest.TestCase):
    def test_dry_run_guard(self):
        self.assertFalse(t.dry_run_guard(False))
        self.assertTrue(t.dry_run_guard(True))

    def test_parse_toutiao_success(self):
        raw = b'{"code": 0, "data": {"article_id": "123"}}'
        out = t.parse_toutiao_response(raw)
        self.assertEqual(out["data"]["article_id"], "123")

    def test_parse_toutiao_error(self):
        raw = b'{"code": 400, "msg": "bad"}'
        with self.assertRaises(t.ToutiaoAPIError) as cm:
            t.parse_toutiao_response(raw)
        self.assertEqual(cm.exception.code, 400)

    def test_get_token_missing(self):
        with mock.patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(SystemExit):
                t.get_official_token(mock.Mock())

    def test_get_web_cookie_missing(self):
        with mock.patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(SystemExit):
                t.get_web_cookie(mock.Mock())


if __name__ == "__main__":
    unittest.main()
