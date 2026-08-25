#!/usr/bin/env python3
"""tests for xiaohongshu_publisher.py — 纯函数测试，不发网络请求。"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import xiaohongshu_publisher as x  # noqa: E402


class XiaohongshuPublishTests(unittest.TestCase):
    def test_dry_run_guard(self):
        self.assertFalse(x.dry_run_guard(False))
        self.assertTrue(x.dry_run_guard(True))

    def test_build_note_payload(self):
        payload = x.build_note_payload(
            "Test Title",
            "Content",
            ["tag1", "tag2"],
            ["img1.png", "img2.png"],
            "cover.png",
        )
        self.assertEqual(payload["title"], "Test Title")
        self.assertEqual(payload["content"], "Content")
        self.assertEqual(payload["tags"], ["tag1", "tag2"])
        self.assertEqual(payload["images"], ["img1.png", "img2.png"])
        self.assertEqual(payload["cover_image"], "cover.png")
        self.assertEqual(payload["source"], "web")

    def test_parse_xhs_success(self):
        raw = b'{"code": 0, "data": {"note_id": "123"}}'
        out = x.parse_xhs_response(raw)
        self.assertEqual(out["data"]["note_id"], "123")

    def test_parse_xhs_error(self):
        raw = b'{"code": 400, "msg": "bad"}'
        with self.assertRaises(x.XhsAPIError) as cm:
            x.parse_xhs_response(raw)
        self.assertEqual(cm.exception.code, 400)


if __name__ == "__main__":
    unittest.main()
