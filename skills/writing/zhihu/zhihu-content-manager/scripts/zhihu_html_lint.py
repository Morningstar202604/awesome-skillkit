#!/usr/bin/env python3
"""zhihu_html_lint.py - 知乎正文 HTML 预发布静态检查。

依据本技能 SKILL.md 沉淀的平台规则，对将要发布到知乎的 HTML 做
离线静态检查。只读文件，不联网，天然 dry-run。

检查项：
  E001 bare-img        裸 <img>（必须用 <figure> 包裹，否则被过滤）
  E002 table-tag       <table>（Draft.js 编辑器无法清除）
  E003 empty-paragraph 空段落 <p></p>（会被剥离，应用 <br data-text="true"/> 方案）
  E004 unescaped-code  <code> 块内未转义的尖括号（会被当标签吃掉）
  E005 mojibake        Latin-1 连续字符（UTF-8 被错误解码的乱码特征）
  W001 strong-tag      使用了 <strong>（知乎约定用 <b>）
  I001 missing-pid     多数段落缺 data-pid（粘贴后编辑器会补齐，仅提示）

用法：
  python zhihu_html_lint.py article.html [--json] [--strict]

退出码：0 = 无 error；1 = 存在 error（--strict 时 warning 也算失败）。
"""

from __future__ import annotations

import argparse
import json
import re

MOJIBAKE_RE = re.compile(r"[\u00c0-\u00ff]{2,}")
CODE_BLOCK_RE = re.compile(r"<code>(.*?)</code>", re.S | re.I)
EMPTY_P_RE = re.compile(r"<p(?:\s[^>]*)?>\s*(?:&nbsp;)?\s*</p>", re.I)
P_TAG_RE = re.compile(r"<p(\s[^>]*)?>", re.I)
FIGURE_RE = re.compile(r"<figure\b.*?</figure>", re.S | re.I)
IMG_RE = re.compile(r"<img\b", re.I)
STRONG_RE = re.compile(r"</?strong\b", re.I)
CODE_ESCAPE_HINT = re.compile(r"<[a-zA-Z/][^&]*")


def _line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def lint(html: str):
    findings = []

    def add(code, severity, message, pos):
        findings.append({"code": code, "severity": severity,
                         "line": _line_of(html, pos), "message": message})

    figures = [(m.start(), m.end()) for m in FIGURE_RE.finditer(html)]
    for m in IMG_RE.finditer(html):
        if not any(s <= m.start() < e for s, e in figures):
            add("E001", "error",
                "裸 <img> 标签会被知乎过滤，必须用 <figure data-size=\"normal\"> 包裹",
                m.start())

    for m in re.finditer(r"<table\b", html, re.I):
        add("E002", "error", "<table> 无法被 Draft.js 编辑器清除，请改用列表或删除",
            m.start())

    for m in EMPTY_P_RE.finditer(html):
        add("E003", "warning",
            "空段落会被 Draft.js 剥离；段落间距请用 "
            "<p data-pid=\"...\"><br data-text=\"true\"/></p>",
            m.start())

    for m in CODE_BLOCK_RE.finditer(html):
        body = m.group(1)
        if "&lt;" not in body and "&gt;" not in body:
            bad = CODE_ESCAPE_HINT.search(body)
            if bad:
                add("E004", "error",
                    "<code> 块内疑似未转义尖括号（%r...），必须写作 &lt; / &gt;"
                    % (bad.group(0)[:20],),
                    m.start(1) + bad.start())

    for m in MOJIBAKE_RE.finditer(html):
        add("E005", "error",
            "检测到 Latin-1 乱码特征 %r（UTF-8 被错误解码），禁止发布"
            % (m.group(0)[:12],),
            m.start())

    for m in STRONG_RE.finditer(html):
        add("W001", "warning", "知乎编辑器约定用 <b> 加粗，<strong> 可能不生效",
            m.start())

    p_total = p_missing = 0
    first_missing = None
    for m in P_TAG_RE.finditer(html):
        attrs = m.group(1) or ""
        if "data-pid" not in attrs:
            p_missing += 1
            if first_missing is None:
                first_missing = m.start()
        p_total += 1
    if p_total and p_missing / p_total > 0.5 and first_missing is not None:
        add("I001", "info",
            "%d/%d 个 <p> 缺少 data-pid（粘贴注入后编辑器会自动补齐，可忽略）"
            % (p_missing, p_total),
            first_missing)

    return findings


def main(argv=None):
    ap = argparse.ArgumentParser(description="知乎正文 HTML 预发布检查")
    ap.add_argument("html_file", help="待检查的 HTML 文件")
    ap.add_argument("--json", action="store_true", help="以 JSON 输出报告")
    ap.add_argument("--strict", action="store_true",
                    help="warning 也视为失败")
    args = ap.parse_args(argv)

    with open(args.html_file, encoding="utf-8") as fh:
        findings = lint(fh.read())

    errors = [f for f in findings if f["severity"] == "error"]
    warnings = [f for f in findings if f["severity"] == "warning"]

    if args.json:
        print(json.dumps({"errors": len(errors), "warnings": len(warnings),
                          "findings": findings}, ensure_ascii=False, indent=2))
    else:
        if not findings:
            print("PASS: 未发现问题")
        for f in findings:
            print("%s:%d [%s] %s" % (args.html_file, f["line"],
                                     f["code"], f["message"]))
        status = "PASS" if not errors else "FAIL"
        print("%s: %d errors, %d warnings" % (status, len(errors), len(warnings)))

    failed = bool(errors) or (args.strict and bool(warnings))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
