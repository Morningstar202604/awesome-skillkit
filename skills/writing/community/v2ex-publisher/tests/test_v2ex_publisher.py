#!/usr/bin/env python3
"""tests for v2ex_publisher.py — 纯函数测试，不发网络请求。"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import v2ex_publisher as v  # noqa: E402


class V2exPublishTests(unittest.TestCase):
    def test_dry_run_guard(self):
        self.assertFalse(v.dry_run_guard(False))
        self.assertTrue(v.dry_run_guard(True))

    def test_build_topic_payload(self):
        payload = v.build_topic_payload("Test", "Content", 123)
        self.assertEqual(payload["title"], "Test")
        self.assertEqual(payload["content"], "Content")
        self.assertEqual(payload["node_id"], "123")

    def test_parse_v2ex_success(self):
        raw = b'{"status": "ok", "topic_id": 123}'
        out = v.parse_v2ex_response(raw)
        self.assertEqual(out["topic_id"], 123)

    def test_parse_v2ex_error(self):
        raw = b'{"status": "error", "code": 400, "message": "bad"}'
        with self.assertRaises(v.V2exAPIError) as cm:
            v.parse_v2ex_response(raw)
        self.assertEqual(cm.exception.code, 400)


if __name__ == "__main__":
    unittest.main()
