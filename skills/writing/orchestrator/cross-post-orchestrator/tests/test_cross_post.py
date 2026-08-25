#!/usr/bin/env python3
"""tests for cross_post.py — 纯函数与文件级测试，不发网络请求。"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import cross_post as c  # noqa: E402


def write_manifest(tmp, **overrides):
    m = {
        "title": "测试文章",
        "markdown": "article.md",
        "targets": [
            {"platform": "wechat_mp", "enabled": True},
            {"platform": "juejin", "enabled": True},
            {"platform": "zhihu", "enabled": False},
        ],
    }
    m.update(overrides)
    path = os.path.join(tmp, "post.manifest.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(m, fh)
    return path


class CrossPostTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        with open(os.path.join(self.tmp, "article.md"), "w", encoding="utf-8") as fh:
            fh.write("# hi")

    def test_load_manifest_ok(self):
        path = write_manifest(self.tmp)
        m = c.load_manifest(path)
        self.assertEqual(m["title"], "测试文章")
        self.assertEqual(len(m["targets"]), 3)

    def test_load_manifest_missing_field(self):
        path = os.path.join(self.tmp, "bad.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump({"title": "x"}, fh)
        with self.assertRaises(ValueError):
            c.load_manifest(path)

    def test_unknown_platform_rejected(self):
        path = write_manifest(self.tmp, targets=[{"platform": "mastodon"}])
        with self.assertRaises(ValueError):
            c.load_manifest(path)

    def test_plan_reports_md_missing(self):
        path = write_manifest(self.tmp)
        os.remove(os.path.join(self.tmp, "article.md"))
        plan = c.build_plan(c.load_manifest(path), self.tmp)
        wechat = [p for p in plan if p["platform"] == "wechat_mp"][0]
        self.assertEqual(wechat["status"], "blocked-md-missing")

    def test_plan_respects_enabled_false(self):
        path = write_manifest(self.tmp)
        plan = c.build_plan(c.load_manifest(path), self.tmp)
        zhihu = [p for p in plan if p["platform"] == "zhihu"][0]
        self.assertEqual(zhihu["status"], "skipped")

    def test_readiness_without_creds_is_not_ready(self):
        old = (
            os.environ.pop("WECHAT_MP_APPID", None),
            os.environ.pop("WECHAT_MP_SECRET", None),
        )
        try:
            ready, why = c.check_readiness("wechat_mp", self.tmp)
            self.assertFalse(ready)
            self.assertIn("WECHAT_MP_APPID", why)
        finally:
            if old[0]:
                os.environ["WECHAT_MP_APPID"] = old[0]
            if old[1]:
                os.environ["WECHAT_MP_SECRET"] = old[1]

    def test_ledger_append_and_read(self):
        lf = os.path.join(self.tmp, "ledger.json")
        c.append_ledger(lf, {"platform": "juejin", "title": "t", "status": "ok"})
        c.append_ledger(lf, {"platform": "wechat_mp", "title": "t2", "status": "ok"})
        with open(lf, encoding="utf-8") as fh:
            data = json.load(fh)
        self.assertEqual(len(data), 2)
        self.assertIn("ts", data[0])

    def test_render_plan_table(self):
        out = c.render_plan([{"platform": "juejin", "status": "ready", "detail": "ok"}])
        self.assertIn("juejin", out)
        self.assertIn("ready", out)


if __name__ == "__main__":
    unittest.main()
