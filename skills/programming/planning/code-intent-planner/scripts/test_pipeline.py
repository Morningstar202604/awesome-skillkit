#!/usr/bin/env python3
"""code-intent-planner 单元测试"""
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from l1_matcher import match, match_all
from plan_renderer import render_markdown, render_json


def check(name, result, expect_match, expect_type=None, expect_conf=None):
    ok = (result["matched"] == expect_match)
    if expect_type:
        ok = ok and (result["intent_type"] == expect_type)
    if expect_conf is not None:
        ok = ok and (result["confidence"] == expect_conf)
    status = "✓" if ok else "✗"
    print(f"{status} {name}")
    assert ok, f"Failed: {name} got {result}"


def test_l1_match():
    """L1 规则匹配测试"""
    check("fix-bug",        match("帮我修复这个 bug，程序一直 crash"),        True,  "fix",         0.95)
    check("implement",     match("帮我写一个用户登录功能"),                  True,  "implement",   0.88)
    check("plan-cn",       match("这个需求怎么规划"),                         True,  "plan",        0.95)
    check("review",        match("帮我 review 一下这段代码"),                 True,  "review",      0.92)
    check("no-match",      match("今天天气不错"),                             False, None,        0.0)
    check("multi-intent",  match("修复登录 bug 并添加验证码功能"),             True,  "fix",         0.95)
    check("destructive",   match("删除用户表中的所有测试数据"),               True,  "destructive", 0.97)
    check("refactor",      match("重构 auth 模块，提高可读性"),               True,  "refactor",    0.90)
    check("test",          match("给这个模块写单元测试"),                     True,  "test",        0.90)
    check("optimize",      match("优化数据库查询性能"),                       True,  "optimize",    0.85)
    check("migrate",       match("把项目从 Python 3.8 迁移到 3.12"),          True,  "migrate",     0.88)
    check("design",        match("设计一个微服务架构"),                       True,  "design",      0.82)
    check("english-plan",  match("break down this task for me"),              True,  "plan",        0.95)
    check("english-fix",   match("fix the authentication crash"),             True,  "fix",         0.95)
    check("subtype-fix",   match("程序 crash 了"),                            True,  "fix",         0.95)


def test_match_all():
    """多意图检测测试"""
    results = match_all("修复 bug 并添加新功能")
    assert len(results) >= 2, f"期望多意图，得到 {len(results)}"
    types = [r["intent_type"] for r in results]
    assert "fix" in types and "implement" in types
    print("✓ test_match_all: 多意图检测")


def test_plan_renderer():
    """计划渲染测试"""
    intent = {
        "intent_type": "implement",
        "confidence": 0.92,
        "source_layer": "L2",
        "description": "实现用户认证模块",
        "slots": [
            {"name": "target", "value": "auth", "evidence": "verified"},
            {"name": "scope", "value": "login+register", "evidence": "provisional"}
        ],
        "constraints": {"hard": [], "soft": ["use JWT"]},
        "sub_tasks": [
            {"id": "T1", "description": "设计用户数据模型", "depends_on": [], "priority": "P0", "effort": "S", "risk": "low"},
            {"id": "T2", "description": "实现核心逻辑", "depends_on": ["T1"], "priority": "P1", "effort": "M", "risk": "medium"},
        ],
        "critical_path": ["T1", "T2"],
        "parallel_groups": [],
        "solution": "先设计 schema，再实现 model，最后加 API",
        "assumptions": [{"text": "使用 PostgreSQL", "impact": "medium", "evidence": "provisional"}],
        "session_id": "test_123",
    }
    
    md = render_markdown(intent)
    assert "任务计划" in md
    assert "implement" in md
    assert "T1" in md
    assert "PostgreSQL" in md
    print("✓ test_plan_renderer: markdown 渲染")
    
    js = render_json(intent)
    parsed = json.loads(js)
    assert parsed["intent_type"] == "implement"
    print("✓ test_plan_renderer: json 渲染")


def test_pipeline_mock():
    """流水线 Mock 测试"""
    from pipeline import run_pipeline
    
    # 测试 L1 直接命中
    result = run_pipeline("修复登录页面的 crash 问题", use_mock=True)
    assert result["intent_type"] == "fix"
    assert result["source_layer"] == "L1"
    assert result["confidence"] == 0.95
    print("✓ test_pipeline_L1: L1 直接命中")
    
    # 测试 L2 Mock（需要设置 USE_MOCK_LLM）
    import os
    os.environ["USE_MOCK_LLM"] = "true"
    
    # 使用不触发 L1 规则的输入（避免关键词"实现"、"写"等）
    result = run_pipeline("针对用户登录场景，需要设计认证方案并给出实现建议，技术栈 FastAPI", use_mock=True)
    assert result["intent_type"] == "implement"
    assert result["source_layer"] in ("L2", "L3")
    assert "sub_tasks" in result
    print("✓ test_pipeline_L2: L2/L3 流程")


def test_session():
    """Session 跨轮累积测试"""
    from pipeline import run_pipeline, load_session
    import time
    
    session_id = f"test_session_{int(time.time())}"
    
    # 第 1 轮（使用不触发 L1 的输入，强制走 L2/L3）
    r1 = run_pipeline("针对用户认证场景，设计 auth 模块并给出实现建议，技术栈 Python", session_id=session_id, use_mock=True)
    assert "auth" in str(r1.get("slots", []))
    
    # 第 2 轮（跨轮累积）
    r2 = run_pipeline("再加个忘记密码功能", session_id=session_id, use_mock=True)
    session = load_session(session_id)
    assert session is not None
    assert session["turn"] == 2
    print("✓ test_session: 跨轮累积")


if __name__ == "__main__":
    test_l1_match()
    test_match_all()
    test_plan_renderer()
    test_pipeline_mock()
    test_session()
    print("\n全部测试通过 ✓")