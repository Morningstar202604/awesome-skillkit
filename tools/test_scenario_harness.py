# -*- coding: utf-8 -*-
r"""Behavior-lock tests for tools/scenario_harness.py (AQG row 2).

核心 helper 的契约先行锁定（RED -> GREEN）：
  1) parse_flags: 从 argparse --help 文本抽出旗标（含取值/choices/required）。
  2) required_from_error: 从 argparse 报错里解析缺哪些必填参数 / 合法 choices。
  3) value_for_flag: 按旗标名 + 域场景银行解析出「场景真实值」。
  4) iter_resolve: 给定一个故意缺参的脚本，迭代补参直到跑通（用真实脚本演练）。
  5) gate_prompt_output: prompt 型技能输出质量门（空/拒答/占位/过短 → fail）。
  6) load_llm_candidates: models.json -> 稳定候选顺序（key 不落日志）。
"""
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("scenario_harness", HERE / "scenario_harness.py")
sh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sh)


HELP_TEXT = """usage: demo.py [-h] --topic TOPIC [--style {ieee,acm}] [--n N] [--out OUT]

options:
  -h, --help            show this help message and exit
  --topic TOPIC         paper topic (required)
  --style {ieee,acm}    output style (default: ieee)
  --n N                 number of runs (default: 5)
  --out OUT             output file
"""


def test_parse_flags_extracts_flags_choices_and_required():
    flags = sh.parse_flags(HELP_TEXT)
    names = {f.name for f in flags}
    assert {"--topic", "--style", "--n", "--out"} <= names, names
    style = [f for f in flags if f.name == "--style"][0]
    assert style.choices == ["ieee", "acm"], style
    topic = [f for f in flags if f.name == "--topic"][0]
    assert topic.takes_value is True
    out = [f for f in flags if f.name == "--out"][0]
    assert out.takes_value is True and out.choices == []


def test_required_from_error_parses_argparse_missing_args():
    err = "usage: demo.py [-h] --topic TOPIC\n咩: error: the following arguments are required: --topic, --n-runs"
    assert sh.required_from_error(err) == ["--topic", "--n-runs"]


def test_required_from_error_parses_invalid_choice():
    err = "demo.py: error: argument --style: invalid choice: 'xxx' (choose from 'ieee', 'acm')"
    got = sh.required_from_error(err)
    assert got == [], got  # invalid choice 不是缺参，由 invalid_choice_from_error 处理
    assert sh.invalid_choice_from_error(err) == ("--style", ["ieee", "acm"])


def test_value_for_flag_uses_domain_bank_not_junk():
    # 读文件类旗标 → 场景文件路径（由调用方建好）
    v = sh.value_for_flag("--data", "paper/pub-plotter", files={"data.json": "{}"})
    assert v.endswith(".json"), v  # 命名是实现细节，扩展名才是契约
    # 输出类旗标 → 给出可写路径
    v2 = sh.value_for_flag("--output", "paper/pub-plotter", files={}, out_dir="TMP")
    assert "TMP" in v2 and "." in Path(v2).name, v2
    # 计数类 → 正整数
    assert str(sh.value_for_flag("--n-runs", "x/y", files={})).isdigit()
    # 主题类 → 非空场景文案（不是占位符）
    v3 = sh.value_for_flag("--topic", "paper/experiment-runner", files={})
    assert v3 and "TODO" not in v3.upper() and len(v3) > 8, v3


def test_iter_resolve_repairs_a_real_missing_arg_script(tmp_path):
    """真实演练：一个要求 --topic 的脚本，空参跑 → 报错 → 迭代补参 → 成功。"""
    demo = tmp_path / "demo.py"
    demo.write_text(
        "import argparse,sys,json\n"
        "ap=argparse.ArgumentParser()\n"
        "ap.add_argument('--topic',required=True)\n"
        "ap.add_argument('--n',type=int,default=2)\n"
        "a=ap.parse_args()\n"
        "print(json.dumps({'status':'success','topic':a.topic,'n':a.n}))\n",
        encoding="utf-8")
    res = sh.run_script_skill(str(demo), "paper/experiment-runner",
                              out_dir=str(tmp_path / "art"), overrides=None, max_attempts=4)
    assert res["rc"] == 0, res
    assert res["verdict"] == "pass", res
    o = json.loads(res["stdout"])
    assert o["status"] == "success" and o["n"] == 2


def test_gate_prompt_output_rejects_refusal_placeholder_and_short():
    ok = "好的，这是三个候选研究方向……" + "论证" * 200
    assert sh.gate_prompt_output(ok, min_chars=200, must_contain=[]) == []
    assert any("长度" in f for f in sh.gate_prompt_output("太短", min_chars=200, must_contain=[]))
    assert any("拒答" in f for f in
               sh.gate_prompt_output("作为AI我无法完成这个请求。" + "字" * 300,
                                     min_chars=200, must_contain=[]))
    assert any("占位" in f for f in
               sh.gate_prompt_output("第一部分 TODO 待补全。" + "字" * 300,
                                     min_chars=200, must_contain=[]))
    assert any("缺少" in f for f in
               sh.gate_prompt_output("很长很长" * 200, min_chars=10,
                                     must_contain=["voice-profile.json"]))


def test_load_llm_candidates_orders_filters_and_redacts(tmp_path):
    mj = tmp_path / "models.json"
    mj.write_text(json.dumps([
        {"id": "agnes-3.0-flash", "vendor": "agnes-api", "url": "https://a/v1", "apiKey": "sk-a"},
        {"id": "hcnsec-x", "vendor": "hcnsec", "url": "https://h/v1", "apiKey": "sk-h"},
        {"id": "agnes-2.5-flash", "vendor": "agnes-api", "url": "https://b/v1", "apiKey": "sk-b"},
    ], ensure_ascii=False), encoding="utf-8")
    cands = sh.load_llm_candidates(str(mj))
    names = [c["name"] for c in cands]
    assert names == ["agnes-2.5-flash", "agnes-3.0-flash"], names  # 排序 + hcnsec 被剔除
    blob = json.dumps({"names": [c["name"] for c in cands],
                       "urls": [c["base_url"] for c in cands]})
    assert "sk-a" not in blob and "sk-b" not in blob  # key 不进可序列化元数据
    # 文件缺失 + 无 env → 空候选（harness 会跳过 prompt 层而不是假装能跑）
    assert sh.load_llm_candidates(str(tmp_path / "nope.json")) == []


if __name__ == "__main__":
    sys.exit(__import__("pytest").main([__file__, "-q"]))
