# -*- coding: utf-8 -*-
r"""Strong smoke test for figure-maker (DEPRECATED shim → pub-plotter).

真输入 + 真断言：验证薄壳确实委托 pub-plotter、heatmap 从「unsupported」变为真实渲染、
弃用标记存在、缺数据时报错而非静默演示。
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SP = Path(__file__).resolve().parent
SCRIPT = SP / "figure_maker.py"
spec = importlib.util.spec_from_file_location("figure_maker", SCRIPT)
fm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fm)

PUB = (SP / fm.PURPLE).resolve()


def _run(args):
    return subprocess.run([sys.executable, str(SCRIPT)] + args,
                          capture_output=True, text=True, timeout=120)


def test_pub_plotter_target_exists():
    """委托目标必须在（否则薄壳只是空壳）。"""
    assert PUB.exists(), f"delegation target missing: {PUB}"
    assert PUB.name == "pub_plotter.py"


def test_load_pub_plotter_module():
    mod, target = fm._load_pub_plotter()
    assert mod is not None, f"failed to load {target}"
    assert hasattr(mod, "plot_heatmap"), "pub-plotter lacks plot_heatmap (superset broken)"
    assert hasattr(mod, "JOURNAL_WIDTHS") and hasattr(mod, "STYLES")


def test_dispatch_table_covers_all_types():
    assert set(fm._DISPATCH) == {"line", "bar", "boxplot", "heatmap"}


def test_output_is_flagged_deprecated():
    try:
        import matplotlib  # noqa: F401
    except Exception:
        return
    with tempfile.TemporaryDirectory() as d:
        data = Path(d, "d.json")
        data.write_text(json.dumps({"labels": ["A", "B"], "values": [0.8, 0.9]}), encoding="utf-8")
        out = Path(d, "f.pdf")
        r = _run(["--data", str(data), "--type", "bar", "--output", str(out)])
        assert r.returncode == 0, r.stderr
        o = json.loads(r.stdout)
        assert o["deprecated"] is True, o
        assert o["superseded_by"] == "pub-plotter", o
        assert "deprecation_note" in o
        assert o["rendered"] is True and o["font_embedded"] is True, o
        assert out.exists() and out.stat().st_size > 0


def test_heatmap_now_actually_renders():
    """v1 的 heatmap 永远 unsupported；现在必须真实出图。"""
    try:
        import matplotlib  # noqa: F401
    except Exception:
        return
    with tempfile.TemporaryDirectory() as d:
        data = Path(d, "d.json")
        data.write_text(json.dumps({"matrix": [[0.1, 0.5], [0.7, 0.9]]}), encoding="utf-8")
        out = Path(d, "hm.pdf")
        r = _run(["--data", str(data), "--type", "heatmap", "--output", str(out)])
        assert r.returncode == 0, r.stderr
        o = json.loads(r.stdout)
        assert o.get("status") != "unsupported", o
        assert o["type"] == "heatmap" and o["rendered"] is True, o
        assert out.exists() and out.stat().st_size > 0


def test_passes_through_journal_flag():
    """--journal 必须真正覆盖物理宽度（旧版会悄悄回退 ieee 宽度）。"""
    try:
        import matplotlib  # noqa: F401
    except Exception:
        return
    with tempfile.TemporaryDirectory() as d:
        data = Path(d, "d.json")
        data.write_text(json.dumps({"labels": ["A"], "values": [0.5]}), encoding="utf-8")
        r = _run(["--data", str(data), "--type", "bar", "--journal", "nature_single",
                  "--output", str(Path(d, "n.pdf"))])
        assert r.returncode == 0, r.stderr
        o = json.loads(r.stdout)
        assert o["journal"] == "nature_single", o
        assert o["width_inches"] == 3.504, o   # 真·Nature 单栏宽度，不再回退 3.5


def test_bad_journal_rejected():
    r = _run(["--type", "bar", "--journal", "nota_journal"])
    assert r.returncode == 2, r
    o = json.loads(r.stdout)
    assert "未知 --journal" in o["error"] and o["deprecated"] is True


def test_missing_data_errors_not_silent():
    """v1 会静默用演示数据；现在必须报错。"""
    r = _run(["--data", "/no/such/file.json", "--type", "bar"])
    assert r.returncode == 2, r
    assert json.loads(r.stdout)["status"] == "error"


def test_bad_data_shape_errors_not_traceback():
    """非法数据（heatmap 非二维阵）必须返回干净 JSON + rc=2，而不是抛 traceback。"""
    try:
        import matplotlib  # noqa: F401
    except Exception:
        return
    with tempfile.TemporaryDirectory() as d:
        data = Path(d, "d.json")
        data.write_text(json.dumps({"matrix": [0.1, 0.2, 0.3]}), encoding="utf-8")
        r = _run(["--data", str(data), "--type", "heatmap"])
        assert r.returncode == 2, r.stdout + r.stderr
        assert "Traceback" not in (r.stdout + r.stderr), r.stderr
        o = json.loads(r.stdout)
        assert o["status"] == "error" and o["deprecated"] is True


def test_delegated_output_is_superset_of_legacy():
    """薄壳产物必须带上 pub-plotter 的出版级字段（证明真委托而非自带旧实现）。"""
    try:
        import matplotlib  # noqa: F401
    except Exception:
        return
    with tempfile.TemporaryDirectory() as d:
        data = Path(d, "d.json")
        data.write_text(json.dumps({"series": [{"name": "Ours", "values": [0.7, 0.8]}]}),
                        encoding="utf-8")
        r = _run(["--data", str(data), "--type", "line", "--output", str(Path(d, "l.pdf"))])
        assert r.returncode == 0, r.stderr
        o = json.loads(r.stdout)
        assert o["font_embedded"] is True and o["colorblind_safe"] is True, o
        assert "width_inches" in o, o


def test_help_mentions_deprecated():
    r = _run(["--help"])
    assert r.returncode == 0
    assert "DEPRECATED" in r.stdout.upper()
