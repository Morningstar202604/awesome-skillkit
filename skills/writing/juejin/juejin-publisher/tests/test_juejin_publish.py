#!/usr/bin/env python3
"""tests for juejin_publish.py — 纯函数测试，不发网络请求。"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import juejin_publish as j  # noqa: E402


class JuejinPublishTests(unittest.TestCase):
    def test_payload_markdown_edit_type(self):
        p = j.build_article_payload("T", "# md", "b", "680963777", ["1", "2"])
        self.assertEqual(p["edit_type"], 10)
        self.assertEqual(p["title"], "T")
        self.assertEqual(p["markdown_content"], "# md")
        self.assertEqual(p["tag_ids"], ["1", "2"])
        self.assertEqual(p["category_id"], "680963777")

    def test_publish_payload_adds_article_id(self):
        base = j.build_article_payload("T", "md", "b", "cat", [])
        p = j.build_publish_payload("7140000000000000000", base)
        self.assertEqual(p["article_id"], "7140000000000000000")
        self.assertEqual(p["title"], "T")

    def test_parse_ok(self):
        data = j.parse_juejin_response(b'{"err_no":0,"data":{"article_id":"1"}}')
        self.assertEqual(data["data"]["article_id"], "1")
        data = j.parse_juejin_response(b'{"data":{}}')  # err_no 缺省视为成功
        self.assertIn("data", data)

    def test_parse_raises_on_err_no(self):
        with self.assertRaises(j.JuejinAPIError) as ctx:
            j.parse_juejin_response(b'{"err_no":401,"err_msg":"not login"}')
        self.assertEqual(ctx.exception.err_no, 401)

    def test_cookie_missing_exits(self):
        class Args:
            cookie = ""
            cookie_file = ""

        old = os.environ.get("JUEJIN_COOKIE")
        os.environ.pop("JUEJIN_COOKIE", None)
        try:
            with self.assertRaises(SystemExit):
                j.load_cookie(Args())
        finally:
            if old:
                os.environ["JUEJIN_COOKIE"] = old

    def test_endpoints_are_https_and_marked(self):
        for name, url in j.ENDPOINTS.items():
            self.assertTrue(url.startswith("https://"), name)


if __name__ == "__main__":
    unittest.main()
