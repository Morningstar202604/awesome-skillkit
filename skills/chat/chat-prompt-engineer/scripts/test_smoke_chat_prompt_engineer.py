"""Smoke tests for chat-prompt-engineer's prompt_audit.py (heuristic audit)."""
import importlib.util
import json
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "prompt_audit.py"
spec = importlib.util.spec_from_file_location("chat_prompt_audit", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

FULL_TASK_PROMPT = (
    "你是一名面向新手的AI工具教程编辑。读者是第一次接触豆包的普通用户，"
    "用途是公众号教程栏目。请把下面的功能清单改写成适合新手阅读的入门指南。"
    "要求：字数控制在800字以内；禁止出现'赋能''抓手'等黑话；"
    "每句话必须有信息量，删掉任何一句后意思不完整即为不合格。"
    "输出为分点清单，结构：一句话定义→核心概念→常见误区。"
)

SPARSE_TASK_PROMPT = "帮我写个东西。"

FULL_AGENT_PROMPT = (
    "# 人设\n你是一位资深的阅读顾问，语气亲切。\n"
    "# 能力与流程\n1. 分析用户读过的书，提取偏好；第一步先反问未提供的书名。\n"
    "# 约束\n禁止推荐未正式出版的书籍；不得评价政治立场。\n"
    "# 输出格式\n每次最多推荐3本书，含推荐理由。\n"
    "# 边界处理\n超出知识范围时主动反问；不确定时不编造。\n"
)

SPARSE_AGENT_PROMPT = "# 人设\n你是一个诗人。\n"


def test_task_mode_full_prompt_hits_all_five():
    result = mod.audit_task(FULL_TASK_PROMPT)
    assert all(result.values()), f"missing: {[k for k, v in result.items() if not v]}"


def test_task_mode_sparse_prompt_reports_missing():
    result = mod.audit_task(SPARSE_TASK_PROMPT)
    missing = [k for k, v in result.items() if not v]
    assert len(missing) >= 3, f"expected >=3 missing, got {missing}"


def test_agent_mode_full_prompt_hits_all_five():
    result = mod.audit_agent(FULL_AGENT_PROMPT)
    assert all(result.values()), f"missing: {[k for k, v in result.items() if not v]}"


def test_agent_mode_sparse_prompt_reports_missing():
    result = mod.audit_agent(SPARSE_AGENT_PROMPT)
    missing = [k for k, v in result.items() if not v]
    assert len(missing) >= 3, f"expected >=3 missing, got {missing}"


def test_main_exit_codes_and_json(capsys):
    assert mod.main(["--prompt", FULL_TASK_PROMPT]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["score"] == "5/5" and payload["missing"] == []
    assert mod.main(["--prompt", SPARSE_AGENT_PROMPT, "--mode", "agent"]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["mode"] == "agent" and payload["missing"]


def test_main_empty_prompt_errors(capsys):
    assert mod.main(["--prompt", "  "]) == 2
    assert "error" in capsys.readouterr().out
