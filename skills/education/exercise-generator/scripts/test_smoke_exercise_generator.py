"""Smoke tests for exercise-generator's exercise_lint.py."""
import importlib.util
import json
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "exercise_lint.py"
spec = importlib.util.spec_from_file_location("exercise_lint", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

GOOD = """# 题库

### Q1 [recall]
题干：用自己的话定义"过拟合"，不抄教材。
参考答案：训练误差持续下降但泛化误差上升的状态；要素：训练/泛化分离、记忆噪声。
评分标准：5 分制——要素各 1 分 + 表述完整 1 分。
常见陷阱：把"训练误差高"当过拟合。
关联：CP2

### Q2 [transfer]
题干：推荐系统把用户看过的都推给用户，这属于什么问题？写出机制层面的理由。
参考答案：过拟合用户历史；要素：泛化失败、多样性坍缩。
评分标准：5 分制——机制判定 3 分 + 理由 2 分。
常见陷阱：只说"不好"不给机制。
关联：CP3
"""

MCQ_BANK = """### Q1 [recall]
题干：过拟合是指？
A. 训练误差高
B. 训练误差低但泛化差
C. 数据太少
D. 学习率太高
参考答案：B
评分标准：5 分制。
常见陷阱：选 A。
关联：CP2
"""

BAD = """### Q1 [apply]
题干：解释一下梯度消失。
关联：CP2

### Q2 [expert]
题干：迁移题。
参考答案：略
评分标准：略
常见陷阱：略
"""


def test_good_bank_passes():
    report = mod.lint(GOOD)
    assert report["status"] == "clean", report["violations"]


def test_mcq_banned_by_default():
    report = mod.lint(MCQ_BANK)
    assert "mcq_banned" in report["rules"]


def test_allow_mcq_flag_disables_rule():
    report = mod.lint(MCQ_BANK, no_mcq=False)
    assert "mcq_banned" not in report["rules"]


def test_bad_bank_reports_fields_and_difficulty():
    report = mod.lint(BAD)
    assert "missing_field" in report["rules"]


def test_main_exit_codes(capsys):
    assert mod.main(["--text", GOOD]) == 0
    clean_payload = json.loads(capsys.readouterr().out)
    assert clean_payload["status"] == "clean"
    assert mod.main(["--text", MCQ_BANK]) == 1
    dirty_payload = json.loads(capsys.readouterr().out)
    assert "mcq_banned" in dirty_payload["rules"]
