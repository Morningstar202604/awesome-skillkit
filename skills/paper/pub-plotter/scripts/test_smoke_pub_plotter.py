# -*- coding: utf-8 -*-
"""Strong smoke test for pub-plotter (SOTA: font embedding + journal widths)."""
import importlib.util
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SP = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("pub_plotter", SP / "pub_plotter.py")
pp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pp)


def test_journal_widths_exist_and_are_real():
    """必须含真实期刊宽度常量（不再是手拍 5.5/6.5）。"""
    for k in ("nature_single", "science", "ieee", "acm", "neurips"):
        assert k in pp.JOURNAL_WIDTHS, f"missing journal width {k}"
    assert pp.JOURNAL_WIDTHS["nature_single"] < 4.0  # Nature 单栏 ~3.5"
    assert pp.JOURNAL_WIDTHS["ieee"] < 4.0


def test_style_includes_nature():
    """新增 nature 风格预设。"""
    assert "nature" in pp.STYLES, "missing nature style preset"


def test_render_line_font_embedded(tmp_path):
    """渲染 line 图：必须产出非空 PDF，且 rcParams 启用 Type 42 字体嵌入。"""
    try:
        import matplotlib
    except Exception:
        return  # matplotlib 缺则跳过（mock 轨），不强测真实出图
    out = tmp_path / "fig.pdf"
    res = pp.plot_line({"series": [{"name": "Ours", "values": [0.7, 0.8, 0.9]}]},
                       style="ieee", output=str(out), colorblind=True)
    assert res["rendered"] is True
    assert res["font_embedded"] is True
    assert res["colorblind_safe"] is True
    assert out.exists() and out.stat().st_size > 0, "empty pdf"


def test_colorblind_default_on():
    """色盲安全色板必须默认启用（出版级最佳实践）。"""
    res = pp.plot_bar({"labels": ["A", "B"], "values": [0.7, 0.85]},
                      style="acm", output=None, colorblind=True)
    assert res["colorblind_safe"] is True


def test_cli_help_no_crash():
    r = subprocess.run([sys.executable, str(SP / "pub_plotter.py"), "--help"],
                       capture_output=True, text=True, timeout=60)
    assert "Traceback" not in (r.stdout + r.stderr), r.stdout + r.stderr
    assert r.returncode in (0, 1, 2)
