#!/usr/bin/env python3
"""tests for douban_publisher.py — 纯函数测试，不发网络请求。"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import douban_publisher as d  # noqa: E402


class DoubanPublishTests(unittest.TestCase):
    def test_dry_run_guard(self):
        self.assertFalse(d.dry_run_guard(False))
        self.assertTrue(d.dry_run_guard(True))

    def test_build_note_payload(self):
        payload = d.build_note_payload("Test", "Content", 1)
        self.assertEqual(payload["title"], "Test")
        self.assertEqual(payload["content"], "Content")
        self.assertEqual(payload["privacy"], "1")

    def test_parse_douban_success(self):
        raw = b'{"r": 0, "note_id": "123"}'
        out = d.parse_douban_response(raw)
        self.assertEqual(out["note_id"], "123")

    def test_parse_douban_error(self):
        raw = b'{"r": 1, "msg": "bad"}'
        with self.assertRaises(d.DoubanAPIError) as cm:
            d.parse_douban_response(raw)
        self.assertEqual(cm.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
