#!/usr/bin/env python3
"""tests for generate_cover.py — 纯函数测试，不发网络请求。"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import generate_cover as g  # noqa: E402


class GenerateCoverTests(unittest.TestCase):
    def test_validate_size_ok(self):
        self.assertEqual(g.validate_size("1792x1024"), "1792x1024")
        self.assertEqual(g.validate_size("1024X1024"), "1024x1024")

    def test_validate_size_rejects_non_multiple_of_16(self):
        with self.assertRaises(ValueError):
            g.validate_size("1000x1000")

    def test_validate_size_rejects_bad_ratio(self):
        with self.assertRaises(ValueError):
            g.validate_size("3072x512")  # 6:1 超出 3:1

    def test_validate_size_rejects_pixel_range(self):
        with self.assertRaises(ValueError):
            g.validate_size("16x16")  # 总像素过小
        with self.assertRaises(ValueError):
            g.validate_size("4096x4096")  # 总像素过大

    def test_payload_shape(self):
        p = g.build_generate_payload("a dark tech cover", "1536x1024", "high")
        self.assertEqual(p["model"], "gpt-image-2")
        self.assertEqual(p["params"]["size"], "1536x1024")
        self.assertEqual(p["params"]["n"], 1)

    def test_extract_task_id_shapes(self):
        self.assertEqual(g.extract_task_id({"task_id": "t1"}), "t1")
        self.assertEqual(g.extract_task_id({"data": {"task_id": "t2"}}), "t2")
        self.assertEqual(g.extract_task_id({"data": {"task": {"id": "t3"}}}), "t3")
        with self.assertRaises(ValueError):
            g.extract_task_id({"foo": "bar"})

    def test_poll_should_stop(self):
        stop, url = g.poll_should_stop({"is_final": False})
        self.assertFalse(stop)
        stop, url = g.poll_should_stop(
            {"is_final": True, "state": "success", "result_url": "http://x/a.png"}
        )
        self.assertTrue(stop)
        self.assertEqual(url, "http://x/a.png")
        stop, url = g.poll_should_stop({"is_final": True, "state": "failed"})
        self.assertTrue(stop)
        self.assertIsNone(url)


if __name__ == "__main__":
    unittest.main()
