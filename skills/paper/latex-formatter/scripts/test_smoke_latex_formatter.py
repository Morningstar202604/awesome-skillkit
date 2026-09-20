# -*- coding: utf-8 -*-
"""Strong smoke test for latex-formatter (SOTA static + cross-file checks).

真输入 + 真断言：验证按名环境配对、未转义字符、跨文件 undefined \\cite、method 诚实标注。
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SP = Path(__file__).resolve().parent
SCRIPT = SP / "latex_formatter.py"
spec = importlib.util.spec_from_file_location("lat_fmt", SCRIPT)
lf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lf)


def test_unbalanced_env_by_name():
    """\\begin/\\end 按名核对（而非简单计数）。"""
    r = lf.format_latex("\\begin{table}\\end{table}\\begin{itemize}", "ieee")
    assert r["status"] == "issues_found", r
    assert any("itemize" in i and "Unbalanced" in i for i in r["issues"]), r["issues"]


def test_raw_chars_flagged():
    """裸 & % # 必须被标记。"""
    r = lf.format_latex("\\section{a & b} \\textbf{x}% raw #", "ieee")
    msgs = " ".join(r["issues"])
    assert "Raw &" in msgs, r["issues"]
    assert "Raw %" in msgs, r["issues"]
    assert "Raw #" in msgs, r["issues"]


def test_undefined_cite_cross_file():
    """给定 .bib 后，\\cite 中无 entry 的 key 必须报 undefined。"""
    tex = "text \\cite{smith2020} \\cite{ghost} \\bibliography{refs}"
    bib = "@article{smith2020,author={S}}\n"
    r = lf.format_latex(tex, "ieee", refs_bib=bib)
    assert any("Undefined \\cite" in i for i in r["issues"]), r["issues"]
    assert "ghost" in " ".join(r["issues"])
    assert "smith2020" not in [i for i in r["issues"] if "Undefined" in i]


def test_cite_without_bibliography_flagged():
    r = lf.format_latex("\\begin{document}\\cite{a}\\end{document}", "ieee")
    assert any("no \\bibliography command" in i for i in r["issues"]), r["issues"]


def test_method_honest_stdlib_fallback():
    """无外部工具时 method 必须如实标 stdlib-fallback。"""
    r = lf.format_latex("\\begin{document}\\section{a}\\end{document}", "ieee")
    assert r["method"] in ("stdlib-fallback", "external-lint"), r["method"]
    assert r["status"] in ("pass", "issues_found"), r


def test_pass_when_clean():
    """干净文档（有 bibliography、环境配对）应 pass。"""
    tex = ("\\begin{document}\\section{A}\\section{B}\\section{C}\n"
           "\\cite{k}\\bibliography{refs}\\end{document}")
    bib = "@article{k,author={A}}\n"
    r = lf.format_latex(tex, "ieee", refs_bib=bib)
    assert r["status"] == "pass", r


def test_cli_error_missing_input():
    """--input 不存在 → rc=1 + error JSON。"""
    p = subprocess.run(
        [sys.executable, str(SCRIPT), "--input", "/no/such/file.tex"],
        capture_output=True, text=True, timeout=60,
    )
    assert p.returncode == 1, p
    d = json.loads(p.stdout)
    assert d["status"] == "error" and "File not found" in d["error"], d


def test_cli_end_to_end_with_refs():
    """CLI + --refs 落盘，跨文件 undefined 检查生效。"""
    with tempfile.TemporaryDirectory() as d:
        texp = Path(d, "draft.tex")
        texp.write_text("\\cite{ok}\\cite{nope}\\bibliography{refs}\\begin{document}\\end{document}")
        bibp = Path(d, "refs.bib")
        bibp.write_text("@article{ok,author={A}}\n")
        outp = Path(d, "out.json")
        p = subprocess.run(
            [sys.executable, str(SCRIPT), "--input", str(texp),
             "--refs", str(bibp), "--output", str(outp)],
            capture_output=True, text=True, timeout=60,
        )
        assert p.returncode == 0, p.stderr
        d2 = json.loads(outp.read_text(encoding="utf-8"))
        assert any("nope" in i for i in d2["issues"]), d2["issues"]
