#!/usr/bin/env python3
"""tests for oschina_publisher.py — 纯函数测试，不发网络请求。"""

import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import oschina_publisher as o  # noqa: E402


class OschinaPublishTests(unittest.TestCase):
    def test_dry_run_guard(self):
        self.assertFalse(o.dry_run_guard(False))
        self.assertTrue(o.dry_run_guard(True))

    def test_parse_osc_success(self):
        raw = b'{"errorCode": 0, "data": {"blog_id": "123"}}'
        out = o.parse_osc_response(raw)
        self.assertEqual(out["data"]["blog_id"], "123")

    def test_parse_osc_error(self):
        raw = b'{"errorCode": 400, "errorMessage": "bad"}'
        with self.assertRaises(o.OscAPIError) as cm:
            o.parse_osc_response(raw)
        self.assertEqual(cm.exception.code, 400)

    def test_get_token_missing(self):
        with mock.patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(SystemExit):
                o.get_official_token(mock.Mock())


if __name__ == "__main__":
    unittest.main()
