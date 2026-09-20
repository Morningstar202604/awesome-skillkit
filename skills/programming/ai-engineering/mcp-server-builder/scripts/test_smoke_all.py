# -*- coding: utf-8 -*-
r"""Auto-generated smoke test for `programming/ai-engineering` (tools/gen_smoke.py).

保守校验：每个脚本 import 无异常 + `python <script> --help` 不抛未捕获异常。
手搓强测试（真输入 + 真断言）应逐步替换本文件。
"""
import importlib.util
import subprocess
import sys

from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
SCRIPTS = sorted(p for p in SCRIPTS_DIR.glob("*.py") if not p.name.startswith("test_"))


def test_all_scripts_import_cleanly():
    assert SCRIPTS, "no scripts found in scripts/"
    for sp in SCRIPTS:
        try:
            spec = importlib.util.spec_from_file_location(sp.stem, sp)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        except Exception as e:
            raise AssertionError(f"{sp.name} import failed: {e}")


def test_all_scripts_help_no_crash():
    assert SCRIPTS
    for sp in SCRIPTS:
        r = subprocess.run(
            [sys.executable, str(sp), "--help"],
            capture_output=True, text=True, timeout=60,
        )
        out = (r.stdout or "") + (r.stderr or "")
        assert "Traceback" not in out, f"{sp.name} --help crashed:\n{out[-800:]}"
        assert r.returncode in (0, 1, 2), f"{sp.name} --help unexpected exit {r.returncode}"
