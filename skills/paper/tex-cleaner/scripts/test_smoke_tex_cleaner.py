# -*- coding: utf-8 -*-
r"""Strong smoke test for tex-cleaner (SOTA: comment stripping + package map + assets).

真输入 + 真断言：验证转义/verbatim 感知的注释剥离、命令→宏包未用检测、资源清单与存在性核对。
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SP = Path(__file__).resolve().parent
SCRIPT = SP / "tex_cleaner.py"
spec = importlib.util.spec_from_file_location("tex_cleaner", SCRIPT)
tc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tc)

DRAFT = r"""
\documentclass{article}
\usepackage{graphicx}
\usepackage{booktabs}
\begin{document}
Text with trailing comment % drop this
% Whole line comment dropped
Keep 100\% literal
\begin{verbatim}
not a comment % stays
\end{verbatim}
\input{extra}
\includegraphics{fig1}
\ref{missing}
\end{document}
"""


def test_comment_stripping_is_escape_and_verbatim_aware():
    cleaned, stats = tc.strip_comments(DRAFT)
    assert stats["removed_comments"] == 2, stats        # 行尾 + 整行；verbatim 内不算
    assert stats["full_line_comments_removed"] == 1, stats
    assert "drop this" not in cleaned
    assert "Whole line comment dropped" not in cleaned
    assert r"100\%" in cleaned, "escaped percent must survive"
    assert "not a comment % stays" in cleaned, "verbatim percent must survive"


def test_unused_package_detection_via_command_map():
    unused = tc.find_unused_packages(DRAFT)
    assert "booktabs" in unused, unused                # 装了但 toprule/midrule 未出现
    assert "graphicx" not in unused, unused            # includegraphics 出现 → 在用
    assert "amsmath" not in tc.NEVER_UNUSED


def test_asset_manifest_and_existence():
    with tempfile.TemporaryDirectory() as d:
        base = Path(d)
        (base / "extra.tex").write_text("% x")
        (base / "fig1.pdf").write_bytes(b"%PDF-1.4")
        m = tc.collect_assets(DRAFT, base)
        assert m["groups"]["inputs"] == ["extra.tex"], m
        assert m["groups"]["figures"] == ["fig1"], m
        assert m["missing"] == [], m


def test_missing_assets_reported():
    with tempfile.TemporaryDirectory() as d:
        m = tc.collect_assets(DRAFT, Path(d))
        assert "fig1" in m["missing"], m


def test_clean_flag_without_output_errors():
    """--clean 单独使用必须报错（不再静默无操作）。"""
    with tempfile.TemporaryDirectory() as d:
        fp = Path(d, "d.tex")
        fp.write_text(DRAFT, encoding="utf-8")
        r = subprocess.run([sys.executable, str(SCRIPT), "--input", str(fp), "--clean"],
                           capture_output=True, text=True, timeout=60)
        assert r.returncode == 1, r
        assert "--output" in json.loads(r.stdout)["error"]


def test_clean_writes_new_file_and_leaves_input_untouched():
    with tempfile.TemporaryDirectory() as d:
        fp = Path(d, "d.tex")
        fp.write_text(DRAFT, encoding="utf-8")
        outp = Path(d, "clean.tex")
        r = subprocess.run([sys.executable, str(SCRIPT), "--input", str(fp),
                            "--clean", "--output", str(outp)],
                           capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, r.stderr
        d2 = json.loads(r.stdout)
        assert d2["cleaned_to"] == str(outp)
        assert "cleaned_text" not in d2, "cleaned text must not leak into report"
        assert fp.read_text(encoding="utf-8") == DRAFT, "input file must be unchanged"
        assert outp.exists() and "drop this" not in outp.read_text(encoding="utf-8")


def test_missing_input_rc1():
    r = subprocess.run([sys.executable, str(SCRIPT), "--input", "/no/such.tex"],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 1
    assert json.loads(r.stdout)["status"] == "error"


def test_clean_doc_is_arxiv_ready():
    with tempfile.TemporaryDirectory() as d:
        fp = Path(d, "ok.tex")
        fp.write_text("\\begin{document}\nAll good.\n\\end{document}\n", encoding="utf-8")
        r = subprocess.run([sys.executable, str(SCRIPT), "--input", str(fp)],
                           capture_output=True, text=True, timeout=60)
        o = json.loads(r.stdout)
        assert o["arxiv_ready"] is True, o
        assert o["status"] == "clean"
