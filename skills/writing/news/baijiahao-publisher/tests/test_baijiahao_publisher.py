#!/usr/bin/env python3
"""tests for baijiahao_publisher.py — 纯函数测试，不发网络请求。"""

import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import baijiahao_publisher as b  # noqa: E402


class BaijiahaoPublishTests(unittest.TestCase):
    def test_dry_run_guard(self):
        self.assertFalse(b.dry_run_guard(False))
        self.assertTrue(b.dry_run_guard(True))

    def test_parse_bjh_success(self):
        raw = b'{"errno": 0, "data": {"article_id": "123"}}'
        out = b.parse_bjh_response(raw)
        self.assertEqual(out["data"]["article_id"], "123")

    def test_parse_bjh_error(self):
        raw = b'{"errno": 400, "errmsg": "bad"}'
        with self.assertRaises(b.BaijiahaoAPIError) as cm:
            b.parse_bjh_response(raw)
        self.assertEqual(cm.exception.code, 400)

    def test_get_token_missing(self):
        with mock.patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(SystemExit):
                b.get_access_token(mock.Mock())


if __name__ == "__main__":
    unittest.main()
