#!/usr/bin/env python3
"""tests for zhihu_html_lint.py — run with `python -m unittest` or pytest."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from zhihu_html_lint import lint  # noqa: E402


class ZhihuHtmlLintTests(unittest.TestCase):
    def test_clean_html_passes(self):
        html = (
            '<h2>一、背景</h2>'
            '<p data-pid="a1">第一段内容。</p>'
            '<p data-pid="a2"><br data-text="true"/></p>'
            '<figure data-size="normal"><img src="https://pic1.zhimg.com/x.jpg"/></figure>'
        )
        codes = [f["code"] for f in lint(html)]
        self.assertNotIn("E001", codes)
        self.assertNotIn("E002", codes)
        self.assertNotIn("E003", codes)
        self.assertNotIn("E004", codes)
        self.assertNotIn("E005", codes)

    def test_bare_img_detected(self):
        findings = [f for f in lint('<p>x</p><img src="a.jpg"/>')
                    if f["code"] == "E001"]
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["severity"], "error")

    def test_img_inside_figure_ok(self):
        codes = [f["code"] for f in
                 lint('<figure><img src="a.jpg"/></figure>')]
        self.assertNotIn("E001", codes)

    def test_table_detected(self):
        codes = [f["code"] for f in lint("<table><tr><td>1</td></tr></table>")]
        self.assertIn("E002", codes)

    def test_empty_paragraph_warns(self):
        findings = [f for f in lint('<p>a</p><p></p>') if f["code"] == "E003"]
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["severity"], "warning")
        ok = [f for f in lint('<p>a</p><p data-pid="x"><br data-text="true"/></p>')
              if f["code"] == "E003"]
        self.assertEqual(ok, [])

    def test_unescaped_code_block(self):
        codes = [f["code"] for f in lint("<p>c</p><code>#include <stdio.h></code>")]
        self.assertIn("E004", codes)

    def test_escaped_code_block_ok(self):
        codes = [f["code"] for f in lint("<p>c</p><code>&lt;stdio.h&gt;</code>")]
        self.assertNotIn("E004", codes)

    def test_mojibake_detected(self):
        codes = [f["code"] for f in lint("<p>å­¦ä¹ æ¯ä¸ªäººçå¿…ä¿®è¯¾</p>")]
        self.assertIn("E005", codes)

    def test_strong_tag_warns(self):
        findings = [f for f in lint("<p><b>粗体</b></p>") if f["code"] == "W001"]
        self.assertEqual(findings, [])
        findings = [f for f in lint("<p><strong>粗体</strong></p>")
                    if f["code"] == "W001"]
        self.assertEqual(len(findings), 2)  # open + close

    def test_missing_pid_info_only_when_majority(self):
        html = "".join("<p>段落%d</p>" % i for i in range(10))
        codes = [f["code"] for f in lint(html)]
        self.assertIn("I001", codes)
        html_pid = "".join('<p data-pid="%d">段落</p>' % i for i in range(10))
        codes = [f["code"] for f in lint(html_pid)]
        self.assertNotIn("I001", codes)


if __name__ == "__main__":
    unittest.main()
