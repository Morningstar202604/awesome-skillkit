"""Smoke tests for layout-spec-auditor's spec_audit.py."""
import importlib.util
import json
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "spec_audit.py"
spec = importlib.util.spec_from_file_location("layout_spec_audit", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_exact_size_passes():
    report, code = mod.audit(900, 383, platform="wechat-header")
    assert code == 0 and report["status"] == "pass"


def test_wrong_ratio_fails():
    report, code = mod.audit(900, 500, platform="wechat-header")
    names = {c["check"] for c in report["checks"] if not c["pass"]}
    assert code == 1 and "aspect_ratio" in names


def test_small_resolution_fails():
    report, code = mod.audit(450, 192, platform="wechat-header")
    names = {c["check"] for c in report["checks"] if not c["pass"]}
    assert "resolution" in names and code == 1


def test_ratio_only_platform_uses_expected_ratio():
    # zhihu-header carries a ratio constraint (16:9) with no absolute size
    report, code = mod.audit(1600, 900, platform="zhihu-header")
    assert code == 0 and report["status"] == "pass"
    report, code = mod.audit(1000, 1000, platform="zhihu-header")
    assert code == 1


def test_text_budget_check():
    report, code = mod.audit(1080, 1440, platform="xhs-portrait",
                             text_chars=20, text_budget=12)
    names = {c["check"] for c in report["checks"] if not c["pass"]}
    assert "text_budget" in names and code == 1


def test_expect_custom_target():
    report, code = mod.audit(1200, 511, expect="900x383")
    assert code == 0 and report["status"] == "pass"


def test_unknown_platform_is_usage_error():
    report, code = mod.audit(100, 100, platform="nope")
    assert code == 2 and "error" in report


def test_main_json_output(capsys):
    assert mod.main(["--width", "900", "--height", "383",
                     "--platform", "wechat-header"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "pass"
