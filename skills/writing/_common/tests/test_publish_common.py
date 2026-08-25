#!/usr/bin/env python3
"""test_publish_common.py - 发布公共工具的单元测试。"""

import io
import json
import os
import sys
import unittest
from unittest import mock

# 让测试可直接 import 上级目录（_common）的 publish_common
sys.path.insert(
    0,
    __import__("os").path.dirname(
        __import__("os").path.dirname(__import__("os").path.abspath(__file__))
    ),
)

import publish_common  # noqa: E402


class FakeResponse(io.BytesIO):
    def __init__(self, data, status=200):
        super().__init__(data)
        self.status = status


def _fake_urlopen(response_bytes, *, raise_urllib=None, raise_reason=None):
    if raise_urllib is not None:
        if raise_reason is not None:
            exc = publish_common.urllib.error.URLError(raise_reason)
        else:
            exc = publish_common.urllib.error.HTTPError(
                "url", raise_urllib, "msg", None, None
            )
        raise exc
    return FakeResponse(response_bytes)


class HttpJsonTest(unittest.TestCase):
    def test_get_returns_dict(self):
        with mock.patch.object(
            publish_common.urllib.request,
            "urlopen",
            lambda req, timeout=30: FakeResponse(b'{"ok":1}'),
        ):
            out = publish_common.http_json("http://x/api", timeout=5)
        self.assertEqual(out, {"ok": 1})

    def test_post_serializes_payload_and_headers(self):
        captured = {}

        def fake_urlopen(req, timeout=30):
            captured["req"] = req
            return FakeResponse(b'{"a":2}')

        with mock.patch.object(publish_common.urllib.request, "urlopen", fake_urlopen):
            publish_common.http_json("http://x", payload={"x": 1})
        self.assertEqual(
            captured["req"].data,
            json.dumps({"x": 1}, ensure_ascii=False).encode("utf-8"),
        )
        headers = dict(captured["req"].header_items())
        self.assertEqual(headers.get("Content-type"), "application/json; charset=utf-8")
        self.assertIn("Mozilla", headers.get("User-agent", ""))

    def test_cookie_dict_normalized(self):
        captured = {}

        def fake_urlopen(req, timeout=30):
            captured["req"] = req
            return FakeResponse(b"{}")

        with mock.patch.object(publish_common.urllib.request, "urlopen", fake_urlopen):
            publish_common.http_json("http://x", cookie={"a": "1", "b": "2"})
        self.assertEqual(captured["req"].get_header("Cookie"), "a=1; b=2")

    def test_empty_response_returns_dict(self):
        with mock.patch.object(
            publish_common.urllib.request,
            "urlopen",
            lambda req, timeout=30: FakeResponse(b""),
        ):
            self.assertEqual(publish_common.http_json("http://x"), {})

    def test_raw_returns_bytes(self):
        with mock.patch.object(
            publish_common.urllib.request,
            "urlopen",
            lambda req, timeout=30: FakeResponse(b"raw-bytes"),
        ):
            self.assertEqual(
                publish_common.http_json("http://x", raw=True), b"raw-bytes"
            )

    def test_http_error_wrapped(self):
        with mock.patch.object(
            publish_common.urllib.request,
            "urlopen",
            lambda req, timeout=30: _fake_urlopen(b"", raise_urllib=500),
        ):
            with self.assertRaises(publish_common.PublishError):
                publish_common.http_json("http://x")

    def test_url_error_wrapped(self):
        with mock.patch.object(
            publish_common.urllib.request,
            "urlopen",
            lambda req, timeout=30: _fake_urlopen(
                b"", raise_urllib=0, raise_reason="down"
            ),
        ):
            with self.assertRaises(publish_common.PublishError):
                publish_common.http_json("http://x")


class DryRunGuardTest(unittest.TestCase):
    def test_execute_true(self):
        self.assertTrue(publish_common.dry_run_guard(True))
        self.assertTrue(publish_common.dry_run_guard(True, what="上传"))

    def test_dry_run_false_and_prints(self):
        buf = io.StringIO()
        with mock.patch("sys.stdout", buf):
            result = publish_common.dry_run_guard(False)
        self.assertFalse(result)
        self.assertIn("[DRY-RUN]", buf.getvalue())


class LoadCredentialTest(unittest.TestCase):
    def test_from_env(self):
        with mock.patch.dict("os.environ", {"MY_COOKIE": "secret"}):
            self.assertEqual(
                publish_common.load_credential(env="MY_COOKIE", name="Cookie"), "secret"
            )

    def test_from_file(self):
        with mock.patch("builtins.open", mock.mock_open(read_data="  filetok  \n")):
            with mock.patch("os.path.exists", return_value=True):
                self.assertEqual(
                    publish_common.load_credential(cookie_file="a.json", name="C"),
                    "filetok",
                )

    def test_missing_exits(self):
        with mock.patch.dict("os.environ", {}, clear=True):
            with mock.patch("os.path.exists", return_value=False):
                with self.assertRaises(SystemExit):
                    publish_common.load_credential(env="NOPE", name="C")


class LoadJsonTest(unittest.TestCase):
    def test_load_json_normal(self):
        import tempfile

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            f.write('{"a": 1}')
            f.flush()
            path = f.name
        try:
            self.assertEqual(publish_common.load_json(path), {"a": 1})
        finally:
            os.unlink(path)

    def test_load_json_bom(self):
        import tempfile

        with tempfile.NamedTemporaryFile(mode="wb", suffix=".json", delete=False) as f:
            f.write(b'\xef\xbb\xbf{"b": 2}')
            f.flush()
            path = f.name
        try:
            self.assertEqual(publish_common.load_json(path), {"b": 2})
        finally:
            os.unlink(path)


class DumpJsonTest(unittest.TestCase):
    def test_dump_json_default(self):
        result = publish_common.dump_json({"k": "v"})
        self.assertIn('"k": "v"', result)
        self.assertIn("\n", result)

    def test_dump_json_ascii(self):
        result = publish_common.dump_json({"中": "文"})
        self.assertIn("中", result)
        self.assertNotIn("\\u", result)


if __name__ == "__main__":
    unittest.main()
