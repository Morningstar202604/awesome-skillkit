#!/usr/bin/env python3
"""tests for jianshu_publisher.py — 纯函数测试，不发网络请求。"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import jianshu_publisher as j  # noqa: E402


class JianshuPublishTests(unittest.TestCase):
    def test_payload_structure(self):
        payload = j.build_note_payload(
            "Test Title",
            "# Hello\nContent",
            "Brief content",
            ["tag1", "tag2"],
            "https://example.com/cover.png",
        )
        self.assertEqual(payload["note"]["title"], "Test Title")
        self.assertEqual(payload["note"]["content"], "# Hello\nContent")
        self.assertEqual(payload["note"]["brief"], "Brief content")
        self.assertEqual(payload["note"]["tag_names"], ["tag1", "tag2"])
        self.assertEqual(
            payload["note"]["cover_image"], "https://example.com/cover.png"
        )

    def test_parse_success(self):
        raw = b'{"status": "ok", "data": {"note_id": "123"}}'
        out = j.parse_jianshu_response(raw)
        self.assertEqual(out["data"]["note_id"], "123")

    def test_parse_error(self):
        raw = b'{"status": "error", "code": 400, "message": "bad"}'
        with self.assertRaises(j.JianshuAPIError) as cm:
            j.parse_jianshu_response(raw)
        self.assertEqual(cm.exception.code, 400)

    def test_dry_run_guard(self):
        self.assertFalse(j.dry_run_guard(False))
        self.assertTrue(j.dry_run_guard(True))


if __name__ == "__main__":
    unittest.main()
