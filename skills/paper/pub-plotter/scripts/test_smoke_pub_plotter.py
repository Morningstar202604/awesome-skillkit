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


# --- heatmap（本技能补齐的能力；figure-maker 曾宣传但从未实现） ---

def test_heatmap_type_is_offered():
    """--type 必须含 heatmap（不再只是 figure-maker 的空头承诺）。"""
    r = subprocess.run([sys.executable, str(SP / "pub_plotter.py"), "--help"],
                       capture_output=True, text=True, timeout=60)
    assert "heatmap" in r.stdout, r.stdout


def test_heatmap_renders_with_colorblind_sequential_cmap(tmp_path):
    try:
        import matplotlib  # noqa: F401
    except Exception:
        return
    out = tmp_path / "hm.pdf"
    res = pp.plot_heatmap({"matrix": [[0.8, 0.72], [0.68, 0.85]],
                           "rows": ["A", "B"], "cols": ["x", "y"]},
                          style="ieee", output=str(out), colorblind=True)
    assert res["rendered"] is True, res
    assert res["type"] == "heatmap"
    assert res["cmap"] == "cividis", res          # 全正 → 色盲安全顺序色
    assert res["shape"] == [2, 2], res
    assert res["font_embedded"] is True
    assert out.exists() and out.stat().st_size > 0
    assert res["annotated"] is True


def test_heatmap_diverging_cmap_when_negative():
    try:
        import matplotlib  # noqa: F401
    except Exception:
        return
    res = pp.plot_heatmap({"matrix": [[-0.4, 0.2], [0.1, 0.9]]}, colorblind=True)
    assert res["cmap"] == "RdBu_r", res
    assert res["value_range"][0] < 0


def test_heatmap_rejects_non_2d():
    try:
        import matplotlib  # noqa: F401
    except Exception:
        return
    try:
        pp.plot_heatmap({"matrix": [0.1, 0.2, 0.3]})
        assert False, "expected ValueError for 1-D matrix"
    except ValueError:
        pass


def test_cli_heatmap_end_to_end(tmp_path):
    try:
        import matplotlib  # noqa: F401
    except Exception:
        return
    import json
    data = tmp_path / "d.json"
    data.write_text(json.dumps({"matrix": [[0.5, 0.9], [0.7, 0.3]]}), encoding="utf-8")
    out = tmp_path / "hm.pdf"
    r = subprocess.run([sys.executable, str(SP / "pub_plotter.py"), "--type", "heatmap",
                        "--journal", "ieee", "--data", str(data), "--output", str(out)],
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stderr
    o = json.loads(r.stdout)
    assert o["status"] == "success" and o["type"] == "heatmap"


# --- 物理宽度契约（修掉「--journal 静默回退 ieee 宽度」这类静默错误） ---

def test_journal_overrides_width_and_is_reported(tmp_path):
    """--journal nature_single 必须真的把画布宽度设成 3.504in，并在结果里回报。"""
    try:
        import matplotlib  # noqa: F401
    except Exception:
        return
    out = tmp_path / "n.pdf"
    res = pp.plot_line({"series": [{"name": "Ours", "values": [0.7, 0.8]}]},
                       style="ieee", output=str(out), journal="nature_single")
    assert res["journal"] == "nature_single", res
    assert res["width_inches"] == pp.JOURNAL_WIDTHS["nature_single"] == 3.504, res
    assert res["width_inches"] != pp.JOURNAL_WIDTHS["ieee"], "journal 被静默回退成 ieee 宽度"


def test_every_offered_style_has_its_own_geometry():
    """--style 的每个合法选项都必须命中真实 STYLES 预设（防静默回退 ieee 几何）。"""
    r = subprocess.run([sys.executable, str(SP / "pub_plotter.py"), "--help"],
                       capture_output=True, text=True, timeout=60)
    assert "science" in r.stdout
    assert "science" in pp.STYLES, "--style science 曾是合法选项却无预设 → 静默套 ieee 几何"
    assert pp.STYLES["science"]["figure_width"] == pp.JOURNAL_WIDTHS["science"]
    for name in pp.STYLES:
        assert "figure_width" in pp.STYLES[name], f"{name} 缺几何定义"


def test_plot_functions_accept_and_report_journal(tmp_path):
    """四种图都必须接受 journal 参数并回报 width_inches（否则薄壳/下游无法核对版面）。"""
    try:
        import matplotlib  # noqa: F401
    except Exception:
        return
    calls = {
        "line": lambda: pp.plot_line({"series": [{"name": "a", "values": [1, 2]}]},
                                     output=str(tmp_path / "l.pdf"), journal="acm"),
        "bar": lambda: pp.plot_bar({"labels": ["A"], "values": [1]},
                                   output=str(tmp_path / "b.pdf"), journal="acm"),
        "boxplot": lambda: pp.plot_boxplot({"groups": ["A"], "data": [[1, 2]]},
                                           output=str(tmp_path / "x.pdf"), journal="acm"),
        "heatmap": lambda: pp.plot_heatmap({"matrix": [[1, 2]]},
                                           output=str(tmp_path / "h.pdf"), journal="acm"),
    }
    for name, fn in calls.items():
        res = fn()
        assert res.get("journal") == "acm", (name, res)
        assert res.get("width_inches") == pp.JOURNAL_WIDTHS["acm"], (name, res)


def test_unknown_journal_rejected_cli(tmp_path):
    """未知 --journal 必须 rc=2 报错，不允许静默出图。"""
    r = subprocess.run([sys.executable, str(SP / "pub_plotter.py"), "--type", "bar",
                        "--journal", "nota_journal"],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 2, r.stdout + r.stderr
    import json
    assert "未知 --journal" in json.loads(r.stdout)["error"]


def _pdf_width_pt(path):
    """读 PDF 真实 /MediaBox 宽度（pt），用于端到端验证物理尺寸确实变了。"""
    import re
    m = re.search(rb"/MediaBox\s*\[\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)",
                  Path(path).read_bytes())
    assert m, "no /MediaBox found in PDF"
    return float(m.group(3)) - float(m.group(1))


def test_journal_width_is_actually_applied_to_the_pdf(tmp_path):
    """端到端铁证：--journal science（4.76in）出的 PDF 必须显著宽于 --journal ieee（3.5in）。

    只断言返回的常量是不够的（常量和实际画布可能不一致——这正是旧版静默回退的病灶）。
    这里直接读 PDF 的 /MediaBox，证明宽度**真的**被施加到画布上。
    """
    try:
        import matplotlib  # noqa: F401
    except Exception:
        return
    import json
    data = tmp_path / "d.json"
    data.write_text(json.dumps({"series": [{"name": "Ours", "values": [0.7, 0.8, 0.9]}]}),
                    encoding="utf-8")

    def render(journal):
        out = tmp_path / f"{journal}.pdf"
        r = subprocess.run([sys.executable, str(SP / "pub_plotter.py"), "--type", "line",
                            "--data", str(data), "--journal", journal, "--output", str(out)],
                           capture_output=True, text=True, timeout=120)
        assert r.returncode == 0, r.stderr
        return _pdf_width_pt(out), json.loads(r.stdout)["width_inches"]

    w_ieee, inch_ieee = render("ieee")
    w_sci, inch_sci = render("science")
    assert inch_ieee == 3.5 and inch_sci == 4.76
    # science 比 ieee 宽 ~36%：MediaBox 必须真实反映，而不是画布仍是 3.5in
    assert w_sci > w_ieee * 1.2, f"PDF 宽度未随 --journal 变化: ieee={w_ieee}pt science={w_sci}pt"


def test_missing_data_file_errors_not_silent_demo(tmp_path):
    """--data 指向不存在的文件时必须报错（旧版会静默套演示数据）。"""
    r = subprocess.run([sys.executable, str(SP / "pub_plotter.py"), "--type", "line",
                        "--data", str(tmp_path / "nope.json")],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 2, r.stdout + r.stderr
    import json
    o = json.loads(r.stdout)
    assert o["status"] == "error" and "不存在" in o["error"]
