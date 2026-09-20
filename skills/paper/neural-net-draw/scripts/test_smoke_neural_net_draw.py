# -*- coding: utf-8 -*-
"""Strong smoke test for neural-net-draw (SOTA typed-blocks).

真输入 + 真断言：验证 per-neuron 兼容 + typed-blocks 新能力 + 未知类型报错。
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SP = Path(__file__).resolve().parent
SCRIPT = SP / "neural_net_draw.py"
spec = importlib.util.spec_from_file_location("nn_draw", SCRIPT)
nnd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nnd)


def test_parse_bare_widths_default_fc():
    """旧式纯宽度列表默认按全连接(fc)解析。"""
    out = nnd._parse_layers("784,512,10")
    assert out == [(784, "fc"), (512, "fc"), (10, "fc")], out


def test_parse_typed_layers():
    """带类型解析，且类型必须合法。"""
    out = nnd._parse_layers("784:input,64:conv,64:pool,128:linear,10:output")
    assert out == [(784, "input"), (64, "conv"), (64, "pool"),
                   (128, "linear"), (10, "output")], out


def test_unknown_type_raises():
    """未知类型必须抛 ValueError（不再静默当全连接）。"""
    try:
        nnd._parse_layers("10:bogus")
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_per_neuron_method_and_height_cap():
    """纯宽度 → per-neuron；层宽极大时层高层高封顶 3.0cm。"""
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "net.tex")
        r = nnd.draw_nn("784,512,256,10,1", output=out)
        assert r["method"] == "per-neuron", r
        txt = Path(out).read_text(encoding="utf-8")
        assert txt.count("\\begin{tikzpicture}") == 1
        assert txt.count("\\end{tikzpicture}") == 1
        # 层高封顶：784 节点层不得再出现 470cm 这种失控高度
        assert "470.4cm" not in txt, "height cap not applied"
        assert "neuron" in txt


def test_typed_blocks_method_and_blocks():
    """带类型 → typed-blocks，输出含 nnblock 与层类型缩写。"""
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "net.tex")
        r = nnd.draw_nn("784:input,64:conv,64:pool,128:linear,10:output", output=out)
        assert r["method"] == "typed-blocks", r
        assert r["layers"] == ["784:input", "64:conv", "64:pool",
                               "128:linear", "10:output"], r
        txt = Path(out).read_text(encoding="utf-8")
        assert "nnblock" in txt
        assert "conv" in txt and "pool" in txt and "linear" in txt
        assert txt.count("\\begin{tikzpicture}") == 1


def test_param_estimate_only_fc_layers():
    """参数量估算仅计全连接/linear 相邻层；conv 等计 0。"""
    est = nnd._estimate_params([(784, "fc"), (512, "fc"), (256, "fc")])
    assert est.startswith("~")  # 有估算值
    # 全 conv → 估算为 0（不建模核尺寸）
    est2 = nnd._estimate_params([(64, "conv"), (64, "conv")])
    assert est2 == "0", est2


def test_cli_end_to_end():
    """CLI 冒烟：带类型 + 输出文件实际落盘。"""
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "net.tex")
        p = subprocess.run(
            [sys.executable, str(SCRIPT),
             "--layers", "512:residual,256:attention,10:output",
             "--output", out],
            capture_output=True, text=True, timeout=60,
        )
        assert p.returncode == 0, p.stderr
        d2 = json.loads(p.stdout)
        assert d2["method"] == "typed-blocks"
        assert Path(out).exists() and Path(out).stat().st_size > 0
