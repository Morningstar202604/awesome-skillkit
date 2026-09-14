#!/usr/bin/env python3
"""code-generator 单元测试"""
import sys
import os
import json
import subprocess
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from code_generator import (
    match_template, render_template, extract_context,
    generate_l1, generate_l2, generate_code
)
from project_analyzer import detect_tech_stack, analyze_project


TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "references" / "templates"


def _py_compiles(code: str) -> bool:
    """把代码写进临时目录做 py_compile（dry-run，不落产物到仓库）"""
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "rendered_module.py"
        f.write_text(code, encoding="utf-8")
        return subprocess.run(
            [sys.executable, "-m", "py_compile", str(f)],
            capture_output=True,
        ).returncode == 0


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


def test_templates_render():
    """测试 references/templates 下 4 个 Jinja2 模板能渲染出语法正确的代码"""
    try:
        from jinja2 import Environment, FileSystemLoader, StrictUndefined
    except ImportError:
        print("⚠ test_templates_render: skipped（未安装 jinja2）")
        return

    if not TEMPLATE_DIR.is_dir():
        raise AssertionError(f"模板目录不存在: {TEMPLATE_DIR}")

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
    )

    # 上下文口径与 code_generator.extract_context() 完全一致
    plan = {
        "intent_type": "implement",
        "slots": [{"name": "target", "value": "product", "evidence": "verified"}],
        "source_layer": "L1",
    }
    base = extract_context(plan, {"tech_stack": {"primary": "python/fastapi"}})

    fastapi_code = env.get_template("python_fastapi_crud.py.j2").render(**base)
    assert "class Product(BaseModel)" in fastapi_code or "class Product(" in fastapi_code
    assert '@router.get("/{product_id}"' in fastapi_code, "路径参数花括号被吞掉"
    assert _py_compiles(fastapi_code), "python_fastapi_crud 渲染产物语法错误"

    ts_code = env.get_template("typescript_express_crud.ts.j2").render(**base)
    assert "export class ProductService" in ts_code
    assert "productRouter.get('/'" in ts_code
    assert ts_code.count("{") == ts_code.count("}"), "TS 花括号不配对"

    fix_code = env.get_template("fix_runtime.py.j2").render(
        target="auth",
        module="service",
        function_name="login",
        params="self, username: str, password: str",
        return_type="Optional[Token]",
        root_cause="user 为 None 时直接访问 .email",
        fix_description="登录前增加空值 guard clause",
        original_problem="Token(user.email, user.id) 抛 AttributeError",
        guard_condition="user is None",
        guard_warning="Login failed: user not found",
        default_return="None",
        main_logic="if not self.verify_password(password, user.password_hash):\n        return None",
        result="Token(user.email, user.id)",
    )
    assert "def login(self, username: str, password: str) -> Optional[Token]:" in fix_code
    assert _py_compiles(fix_code), "fix_runtime 渲染产物语法错误"

    test_code = env.get_template("test_stub.py.j2").render(
        module_path="src.product.service",
        ClassName="ProductService",
        test_name="find_by_id",
        given="仓储中不存在该 id",
        when="调用 find_by_id(999)",
        then="返回 None",
        constructor_params="",
        method_name="find_by_id",
        method_params="999",
        expected="None",
        Exception="TypeError",
        edge_params="",
        edge_case="缺少必填参数",
        error_scenario="非法输入不应抛异常",
    )
    assert "class TestProductService:" in test_code
    assert "def test_find_by_id_happy_path(self):" in test_code
    assert _py_compiles(test_code), "test_stub 渲染产物语法错误"

    print("✓ test_templates_render: 4 个模板渲染产物均通过语法检查")


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
    test_templates_render()
    test_project_analyzer()
    print("\n全部 8 个测试通过 ✓")
