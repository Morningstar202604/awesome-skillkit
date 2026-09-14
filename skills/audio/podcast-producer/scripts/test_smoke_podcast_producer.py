"""Smoke tests for podcast-producer's script_lint.py."""
import importlib.util
import json
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "script_lint.py"
spec = importlib.util.spec_from_file_location("podcast_script_lint", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

CLEAN = """# 开场

HOST: 欢迎回来，这里是游荡者频道。今天我们聊一个反常识的事：AI 写脚本比人快，但人写的更耐听。

# 主体

HOST: 先说现象。过去一年，播客自动生成的工具从三个涨到了三十个。
GUEST: 这个数字其实还保守了，仅开源生态里就有几十个 TTS 方案。

# 收尾

HOST: 相关链接都在 shownotes，下期聊声音克隆的伦理边界。
"""

DIRTY = """## 脚本

[停顿] HOST: 欢迎收听**本期节目**（笑），今天我们聊 [音乐起] AI。
GUEST: 是啊，这个话题我深有体会（详见下期预告），内容请看这里 https://example.com `code` 笔记。
HOST: 说到这里我补充一句，这个观点其实来自去年的一场发布会，当时很多团队都在演示自己的端到端方案，现场效果非常震撼，但是事后大家发现落地远比演示复杂，这里面的差距值得每一个从业者认真思考和研究。
"""


def test_clean_script_passes():
    report = mod.lint(CLEAN, dialogue=True)
    assert report["status"] == "clean", report["violations"]


def test_dirty_script_catches_all_rules():
    report = mod.lint(DIRTY, dialogue=True)
    rules = set(report["rules"])
    assert "stage_direction" in rules
    assert "bracketed_aside" in rules
    assert "markdown_debris" in rules
    assert "overlong_line" in rules


def test_dialogue_mode_flags_missing_label():
    report = mod.lint("没有标签的一行话。\n", dialogue=True)
    rules = set(report["rules"])
    assert "speaker_label" in rules


def test_headings_are_allowed():
    report = mod.lint("# 纯标题行\n\nHOST: 正文。\n", dialogue=True)
    assert report["status"] == "clean"


def test_main_exit_codes(capsys):
    assert mod.main(["--text", CLEAN, "--dialogue"]) == 0
    clean_payload = json.loads(capsys.readouterr().out)
    assert clean_payload["status"] == "clean"
    assert mod.main(["--text", DIRTY, "--dialogue"]) == 1
    dirty_payload = json.loads(capsys.readouterr().out)
    assert dirty_payload["count"] > 0
