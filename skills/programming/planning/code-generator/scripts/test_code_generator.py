#!/usr/bin/env python3
"""code-generator 单元测试"""
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from code_generator import (
    match_template, render_template, extract_context,
    generate_l1, generate_l2, generate_code
)
from project_analyzer import detect_tech_stack, analyze_project


def test_match_template():
    """测试模板匹配"""
    # Python FastAPI CRUD
    tpl = match_template("implement", "python/fastapi", "auth")
    assert tpl is not None
    assert "src/auth/models.py" in tpl or "{{target}}" in str(tpl)
    print("✓ test_match_template: Python FastAPI CRUD")

    # Fix runtime
    tpl = match_template("fix", "python/fastapi", "auth")
    assert tpl is not None
    print("✓ test_match_template: Fix runtime")

    # No match
    tpl = match_template("unknown", "unknown", "test")
    assert tpl is None
    print("✓ test_match_template: No match returns None")


def test_render_template():
    """测试模板渲染"""
    template = {"src/{{target}}/test.py": "print('Hello {{name}}')"}
    context = {"target": "auth", "name": "World"}
    rendered = render_template(template, context)
    
    assert "src/auth/test.py" in rendered, f"keys: {list(rendered.keys())}"
    assert "Hello World" in rendered["src/auth/test.py"]
    print("✓ test_render_template")


def test_extract_context():
    """测试上下文提取"""
    plan = {
        "intent_type": "implement",
        "slots": [
            {"name": "target", "value": "user", "evidence": "verified"},
            {"name": "scope", "value": "crud", "evidence": "provisional"},
            {"name": "tech_stack", "value": "python/fastapi", "evidence": "verified"},
        ],
        "sub_tasks": [{"id": "T1", "description": "Create model", "priority": "P0"}],
        "source_layer": "L1",
    }
    project_info = {
        "tech_stack": {"primary": "python/fastapi"},
        "existing_modules": ["auth", "users"],
    }
    
    context = extract_context(plan, project_info)
    assert context["target"] == "user"
    assert context["Model"] == "User"
    assert context["Service"] == "UserService"
    assert context["tech_stack"] == "python/fastapi"
    print("✓ test_extract_context")


def test_generate_l1():
    """测试 L1 生成"""
    plan = {
        "intent_type": "implement",
        "slots": [
            {"name": "target", "value": "product", "evidence": "verified"},
        ],
        "source_layer": "L1",
    }
    project_info = {
        "tech_stack": {"primary": "python/fastapi"},
        "existing_modules": [],
    }
    
    result = generate_l1(plan, project_info)
    assert result["status"] == "success"
    assert result["layer"] == "L1"
    assert "src/product/models.py" in result["files"]
    assert "src/product/service.py" in result["files"]
    assert "src/product/api.py" in result["files"]
    print("✓ test_generate_l1")


def test_generate_l2():
    """测试 L2 生成（Mock）"""
    plan = {
        "intent_type": "implement",
        "slots": [
            {"name": "target", "value": "order", "evidence": "verified"},
        ],
        "source_layer": "L2",
    }
    project_info = {
        "tech_stack": {"primary": "python/fastapi"},
        "existing_modules": [],
    }
    
    result = generate_l2(plan, project_info)
    assert result["status"] == "success"
    assert result["layer"] == "L2"
    assert "src/order/models.py" in result["files"]
    print("✓ test_generate_l2")


def test_generate_code_pipeline():
    """测试完整流水线"""
    plan = {
        "intent_type": "implement",
        "confidence": 0.9,
        "source_layer": "L1",
        "description": "实现商品模块",
        "slots": [
            {"name": "target", "value": "product", "evidence": "verified"},
            {"name": "scope", "value": "crud", "evidence": "provisional"},
            {"name": "tech_stack", "value": "python/fastapi", "evidence": "verified"},
        ],
        "sub_tasks": [
            {"id": "T1", "description": "设计数据模型", "priority": "P0"},
            {"id": "T2", "description": "实现服务层", "priority": "P0"},
            {"id": "T3", "description": "实现 API", "priority": "P1"},
        ],
    }
    
    result = generate_code(plan, use_mock=True)
    assert result["status"] == "success"
    assert result["layer"] == "L1"
    assert "files" in result
    assert "report" in result
    assert "已生成文件" in result["report"]
    print("✓ test_generate_code_pipeline")


def test_project_analyzer():
    """测试项目分析器"""
    info = analyze_project(".")
    assert "tech_stack" in info
    assert "directory_structure" in info
    assert "existing_modules" in info
    print(f"✓ test_project_analyzer: {info['tech_stack']['primary']}")


if __name__ == "__main__":
    test_match_template()
    test_render_template()
    test_extract_context()
    test_generate_l1()
    test_generate_l2()
    test_generate_code_pipeline()
    test_project_analyzer()
    print("\n全部 7 个测试通过 ✓")
