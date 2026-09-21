# -*- coding: utf-8 -*-
r"""Strong smoke test for arch-diagram (SOTA: valid LaTeX font + valid SVG marker + layouts).

真输入 + 真断言：验证 \sffootnotesize 硬伤已修、SVG marker 有定义、布局与标签转义。
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

SP = Path(__file__).resolve().parent
SCRIPT = SP / "arch_diagram.py"
spec = importlib.util.spec_from_file_location("arch_diagram", SCRIPT)
ad = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ad)


def test_no_invalid_font_command():
    """v1 的 \\sffootnotesize 不是合法 LaTeX 命令，必须已修。"""
    with tempfile.TemporaryDirectory() as d:
        out = Path(d, "a.tex")
        r = ad.generate_tikz_pipeline([("A", None), ("B", None)], str(out))
        txt = out.read_text(encoding="utf-8")
        assert "\\sffootnotesize" not in txt, "invalid LaTeX font command still present"
        assert "\\footnotesize" in txt
        assert r["font_command"] == "\\footnotesize"


def test_svg_marker_is_defined():
    """v1 用了 url(#arrow) 却没有 defs → 箭头不渲染。现在必须有 marker 定义。"""
    with tempfile.TemporaryDirectory() as d:
        out = Path(d, "a.svg")
        r = ad.generate_svg_pipeline([("A", None), ("B", None)], str(out))
        txt = out.read_text(encoding="utf-8")
        assert 'marker-end="url(#arrow)"' in txt
        assert '<marker id="arrow"' in txt, "marker referenced but never defined"
        assert r["has_marker_def"] is True and r["valid_root"] is True


def test_svg_is_wellformed_xml():
    with tempfile.TemporaryDirectory() as d:
        out = Path(d, "a.svg")
        ad.generate_svg_pipeline([("Encoder", None), ("Decoder", None), ("Head", None)], str(out))
        ET.fromstring(out.read_text(encoding="utf-8"))  # 不抛异常即合法


def test_svg_escapes_special_chars():
    with tempfile.TemporaryDirectory() as d:
        out = Path(d, "a.svg")
        ad.generate_svg_pipeline([("A & B", None), ("x < y", None)], str(out))
        txt = out.read_text(encoding="utf-8")
        assert "A &amp; B" in txt and "x &lt; y" in txt, txt
        ET.fromstring(txt)


def test_latex_labels_escaped():
    assert ad.escape_latex("A & B_1 #2 100%") == r"A \& B\_1 \#2 100\%"


def test_layouts_produce_different_geometry():
    row = ad._positions(5, "row", 3)
    wrap = ad._positions(5, "wrap", 3)
    stack = ad._positions(5, "stack", 3)
    assert row == [(0, i) for i in range(5)]
    assert wrap == [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1)]
    assert stack == [(i, 0) for i in range(5)]


def test_block_color_spec_parsing():
    blocks = ad.parse_blocks("Encoder#red, Decoder#blue, Head")
    assert blocks[0] == ("Encoder", "red")
    assert blocks[1] == ("Decoder", "blue")
    assert blocks[2] == ("Head", None)
    # 非法颜色回退 blue，不抛异常
    assert ad.parse_blocks("X#notacolor")[0][1] == "blue"


def test_escaping_flag_reported():
    with tempfile.TemporaryDirectory() as d:
        out = Path(d, "a.tex")
        r = ad.generate_tikz_pipeline([("A&B", None), ("C", None)], str(out))
        assert r["escaped"] is True, r


def test_cli_wrap_tikz_and_svg():
    with tempfile.TemporaryDirectory() as d:
        tex = Path(d, "a.tex")
        r = subprocess.run([sys.executable, str(SCRIPT), "--type", "pipeline",
                            "--blocks", "A,B,C,D,E", "--layout", "wrap", "--per-row", "3",
                            "--output", str(tex)], capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, r.stderr
        o = json.loads(r.stdout)
        assert o["layout"] == "wrap" and o["n_blocks"] == 5
        assert "\\end{tikzpicture}" in tex.read_text(encoding="utf-8")

        svg = Path(d, "a.svg")
        r2 = subprocess.run([sys.executable, str(SCRIPT), "--type", "svg",
                             "--blocks", "A,B", "--output", str(svg)],
                            capture_output=True, text=True, timeout=60)
        assert r2.returncode == 0
        ET.fromstring(svg.read_text(encoding="utf-8"))


def test_nn_mode_notes_neural_net_draw():
    with tempfile.TemporaryDirectory() as d:
        out = Path(d, "nn.tex")
        r = ad.generate_neural_net(["input(4)", "hidden(8)", "output(2)"], str(out))
        assert r["n_layers"] == 3
        assert "neural-net-draw" in r["note"]


def test_defaults_used_when_blocks_empty():
    with tempfile.TemporaryDirectory() as d:
        out = Path(d, "a.tex")
        r = subprocess.run([sys.executable, str(SCRIPT), "--output", str(out)],
                           capture_output=True, text=True, timeout=60)
        assert r.returncode == 0
        assert json.loads(r.stdout)["n_blocks"] == 4
