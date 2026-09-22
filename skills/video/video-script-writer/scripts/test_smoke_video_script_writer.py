"""Smoke tests per SKILL-STANDARD-v2 G7: CLI contract stays runnable.

--help exercises argparse wiring without touching the network or filesystem.
"""
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "script_writer.py"


def test_help_contract():
    r = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, r.stderr
    assert "usage" in (r.stdout + r.stderr).lower()


SP = Path(__file__).resolve().parent  # noqa: E305
import json  # noqa: E402
import importlib.util  # noqa: E402

# --- 强测试：LLM 双轨（真模型/模板兜底诚实标注）+ 退出码契约 ---

def _run(args, env=None):
    import subprocess, sys, os
    e = dict(os.environ)
    for k in ("SKILLKIT_LLM_URL", "SKILLKIT_LLM_KEY", "SKILLKIT_LLM_MODEL"):
        e.pop(k, None)  # 测试基线：无网关 → 模板轨
    if env:
        e.update(env)
    return subprocess.run([sys.executable, str(SP / "script_writer.py")] + args,
                          capture_output=True, text=True, timeout=120, env=e)


def test_template_track_honest_source(tmp_path):
    """env 未配网关 → 台词必须是模板轨且如实标注 source=template。"""
    r = _run(["--concept", "宝宝测评手机", "--type", "tutorial"])
    assert r.returncode == 0, r.stderr
    o = json.loads(r.stdout)
    assert o["dialogue_source"] == "template", o.get("dialogue_source")
    assert all(s["dialogue_source"] == "template" for s in o["scenes"])


def test_llm_track_when_gateway_configured(tmp_path, monkeypatch):
    """配了网关 → 走真模型写台词（monkeypatch llm_chat 模拟网关返回）。"""
    spec = importlib.util.spec_from_file_location("sw2", SP / "script_writer.py")
    sw = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sw)
    monkeypatch.setattr(sw, "llm_chat", lambda messages, timeout=60: json.dumps(
        {"lines": [{"role": "intro", "dialogue": "3 步搞定手机测评，第 2 步 90% 的人做错"},
                   {"role": "steps", "dialogue": "先跑分，再测温，最后对比续航数据"},
                   {"role": "outro", "dialogue": "关注看下期拆机"}]}))
    res = sw.generate_script("宝宝测评手机", "tutorial", 30, use_llm=True)
    assert res["dialogue_source"] == "llm", res.get("dialogue_source")
    assert "90%" in res["scenes"][0]["dialogue"]
    assert all(s["dialogue_source"] == "llm" for s in res["scenes"])


def test_llm_failure_falls_back_with_note(tmp_path, monkeypatch):
    """网关炸了 → 自动落回模板，llm_note 说明原因，绝不冒充成功。"""
    spec = importlib.util.spec_from_file_location("sw3", SP / "script_writer.py")
    sw = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sw)

    def boom(messages, timeout=60):
        raise TimeoutError("gateway timeout")
    monkeypatch.setattr(sw, "llm_chat", boom)
    res = sw.generate_script("概念", "short", 15, use_llm=True)
    assert res["dialogue_source"] == "template", res
    assert res["llm_note"] and "TimeoutError" in res["llm_note"], res.get("llm_note")


def test_bad_json_input_rejected():
    r = _run(["--concept", "x", "--json-input", "{not json"])
    assert r.returncode == 2, r
    assert json.loads(r.stdout)["status"] == "error"


def test_llm_parse_tolerates_code_fence(monkeypatch):
    """LLM 回复带 ```json 围栏/前后废话也能解析。"""
    spec = importlib.util.spec_from_file_location("sw4", SP / "script_writer.py")
    sw = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sw)
    raw = '好的，这是台词：\n```json\n{"lines": [{"role": "hook", "dialogue": "3 秒抓住眼球"}]}\n```\n希望有帮助'
    assert sw._parse_json_loose(raw)["lines"][0]["role"] == "hook"


def test_duration_invariants_no_zero_second_scene():
    """时长不变量（回归测试）：每场 ≥1s；各场之和 == total_duration；
    平台截断与小目标抬升都必须写进 duration_note，不静默改用户输入。"""
    spec = importlib.util.spec_from_file_location("sw5", SP / "script_writer.py")
    sw = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sw)
    for vt in ("talking_character", "meme", "tutorial", "vlog", "short"):
        for d in range(1, 61):
            r = sw.generate_script("C", vt, d, "douyin", use_llm=False)
            durs = [s["duration_sec"] for s in r["scenes"]]
            assert min(durs) >= 1, (vt, d, durs)
            assert sum(durs) == r["total_duration"], (vt, d, durs)
    # 平台截断：120s 抖音 → 60s，且如实记录
    r = sw.generate_script("C", "talking_character", 120, "douyin", use_llm=False)
    assert r["total_duration"] == 60 and r["requested_duration"] == 120
    assert r["duration_note"] and "截断" in r["duration_note"]
    # 目标小于场景数：抬升到场景数，且如实记录
    r2 = sw.generate_script("C", "talking_character", 3, "douyin", use_llm=False)
    assert r2["total_duration"] == 4 and min(
        s["duration_sec"] for s in r2["scenes"]) == 1
    assert r2["duration_note"] and "抬升" in r2["duration_note"]
    # caption 合规核对字段在场
    assert r2["caption_check"]["ok"] is True and r2["caption_check"]["limit"] == 50
