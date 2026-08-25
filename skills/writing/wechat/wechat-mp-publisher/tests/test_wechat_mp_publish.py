#!/usr/bin/env python3
"""tests for wechat_mp_publish.py — 纯函数测试，不发网络请求。"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import wechat_mp_publish as w  # noqa: E402


class WechatPublishTests(unittest.TestCase):
    def test_token_url_contains_params(self):
        url = w.build_token_url("wx123", "sec456")
        self.assertIn("grant_type=client_credential", url)
        self.assertIn("appid=wx123", url)
        self.assertIn("secret=sec456", url)
        self.assertTrue(url.startswith("https://api.weixin.qq.com/cgi-bin/token"))

    def test_draft_payload_shape(self):
        p = w.build_draft_payload(
            "标题", "<p>正文</p>", "THUMB", author="a", digest="d"
        )
        self.assertEqual(p["articles"][0]["title"], "标题")
        self.assertEqual(p["articles"][0]["content"], "<p>正文</p>")
        self.assertEqual(p["articles"][0]["thumb_media_id"], "THUMB")
        self.assertEqual(len(p["articles"]), 1)

    def test_parse_response_ok_and_errcode_none(self):
        self.assertEqual(
            w.parse_wechat_response(b'{"access_token":"x"}'), {"access_token": "x"}
        )
        self.assertEqual(
            w.parse_wechat_response(b'{"media_id":"m"}'), {"media_id": "m"}
        )

    def test_parse_response_raises_on_errcode(self):
        with self.assertRaises(w.WechatAPIError) as ctx:
            w.parse_wechat_response(b'{"errcode":40001,"errmsg":"invalid credential"}')
        self.assertEqual(ctx.exception.errcode, 40001)

    def test_multipart_body_format(self):
        body, ctype = w.multipart_body("media", "a.jpg", b"\xff\xd8jpeg", "image/jpeg")
        self.assertIn("multipart/form-data; boundary=----skillkit", ctype)
        self.assertIn(b'name="media"; filename="a.jpg"', body)
        self.assertIn(b"\xff\xd8jpeg", body)
        self.assertTrue(body.endswith(b"--\r\n"))
        boundary = ctype.split("=")[1].encode()
        self.assertIn(b"--" + boundary, body)

    def test_dry_run_is_default(self):
        """不带 --execute 时 dry_run_guard 必须返回 False（不发送）。"""
        self.assertFalse(w.dry_run_guard(False))

    def test_execute_flag_allows_send(self):
        self.assertTrue(w.dry_run_guard(True))


if __name__ == "__main__":
    unittest.main()
