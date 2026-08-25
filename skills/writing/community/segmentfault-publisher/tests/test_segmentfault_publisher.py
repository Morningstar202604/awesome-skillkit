#!/usr/bin/env python3
"""tests for segmentfault_publisher.py — 纯函数测试，不发网络请求。"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import segmentfault_publisher as s  # noqa: E402


class SegmentFaultPublishTests(unittest.TestCase):
    def test_dry_run_guard(self):
        self.assertFalse(s.dry_run_guard(False))
        self.assertTrue(s.dry_run_guard(True))

    def test_build_article_payload(self):
        payload = s.build_article_payload(
            "Test", "Content", "Summary", "tag1,tag2", "cover.png"
        )
        self.assertEqual(payload["title"], "Test")
        self.assertEqual(payload["content"], "Content")
        self.assertEqual(payload["summary"], "Summary")
        self.assertEqual(payload["tags"], ["tag1", "tag2"])
        self.assertEqual(payload["cover_image"], "cover.png")

    def test_parse_sf_success(self):
        raw = b'{"code": 0, "data": {"article_id": "123"}}'
        out = s.parse_sf_response(raw)
        self.assertEqual(out["data"]["article_id"], "123")

    def test_parse_sf_error(self):
        raw = b'{"code": 400, "message": "bad"}'
        with self.assertRaises(s.SfAPIError) as cm:
            s.parse_sf_response(raw)
        self.assertEqual(cm.exception.code, 400)


if __name__ == "__main__":
    unittest.main()
