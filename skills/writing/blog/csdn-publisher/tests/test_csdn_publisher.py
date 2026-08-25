#!/usr/bin/env python3
"""tests for csdn_publisher.py — 纯函数测试，不发网络请求。"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import csdn_publisher as c  # noqa: E402


class CsdnPublishTests(unittest.TestCase):
    def test_payload_structure(self):
        payload = c.build_article_payload(
            "Test Title",
            "# Hello\nContent",
            "Brief content",
            "123",
            ["tag1", "tag2"],
            "https://example.com/cover.png",
        )
        self.assertEqual(payload["title"], "Test Title")
        self.assertEqual(payload["markdown_content"], "# Hello\nContent")
        self.assertEqual(payload["brief"], "Brief content")
        self.assertEqual(payload["category_id"], "123")
        self.assertEqual(payload["tags"], ["tag1", "tag2"])
        self.assertEqual(payload["cover_image"], "https://example.com/cover.png")
        self.assertEqual(payload["is_original"], 1)

    def test_publish_payload(self):
        article = {"title": "T", "markdown_content": "M"}
        out = c.build_publish_payload("789", article)
        self.assertEqual(out["article_id"], "789")
        self.assertEqual(out["title"], "T")

    def test_parse_success(self):
        raw = b'{"code": 0, "data": {"article_id": "123"}}'
        out = c.parse_csdn_response(raw)
        self.assertEqual(out["data"]["article_id"], "123")

    def test_parse_error(self):
        raw = b'{"code": 400, "msg": "bad request"}'
        with self.assertRaises(c.CsdnAPIError) as cm:
            c.parse_csdn_response(raw)
        self.assertEqual(cm.exception.code, 400)

    def test_dry_run_guard(self):
        self.assertFalse(c.dry_run_guard(False))
        self.assertTrue(c.dry_run_guard(True))


if __name__ == "__main__":
    unittest.main()
