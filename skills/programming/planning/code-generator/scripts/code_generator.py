#!/usr/bin/env python3
"""code_generator.py — 两层代码生成引擎（L1 模板 + L2 LLM）

接收 code-intent-planner 的任务计划，生成可运行的代码文件。
"""
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from project_analyzer import analyze_project


# ── L1 模板库 ───────────────────────────────────────────────

PYTHON_FASTAPI_CRUD = {
    "src/{{target}}/models.py": """\
\"\"\"{{target}} 数据模型\"\"\"
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class {{Model}}Create(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class {{Model}}Update(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None


class {{Model}}Base(BaseModel):
    name: str
    description: Optional[str] = None


class {{Model}}({{Model}}Base):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
""",
    "src/{{target}}/service.py": """\
\"\"\"{{target}} 服务层\"\"\"
from datetime import datetime
from typing import List, Optional
from .models import {{Model}}, {{Model}}Create, {{Model}}Update


class {{Service}}:
    def __init__(self):
        self._storage: List[{{Model}}] = []
        self._next_id = 1

    def create(self, data: {{Model}}Create) -> {{Model}}:
        model = {{Model}}(
            id=self._next_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            **data.model_dump()
        )
        self._storage.append(model)
        self._next_id += 1
        return model

    def find_all(self) -> List[{{Model}}]:
        return self._storage

    def find_by_id(self, item_id: int) -> Optional[{{Model}}]:
        for item in self._storage:
            if item.id == item_id:
                return item
        return None

    def update(self, item_id: int, data: {{Model}}Update) -> Optional[{{Model}}]:
        for i, item in enumerate(self._storage):
            if item.id == item_id:
                updated_data = item.model_dump()
                updated_data.update(data.model_dump(exclude_unset=True))
                updated_data['updated_at'] = datetime.now()
                self._storage[i] = {{Model}}(**updated_data)
                return self._storage[i]
        return None

    def delete(self, item_id: int) -> bool:
        for i, item in enumerate(self._storage):
            if item.id == item_id:
                self._storage.pop(i)
                return True
        return False
""",
    "src/{{target}}/api.py": """\
\"\"\"{{target}} API 路由\"\"\"
from fastapi import APIRouter, HTTPException
from typing import List
from .service import {{Service}}
from .models import {{Model}}, {{Model}}Create, {{Model}}Update

router = APIRouter(prefix="/{{target}}", tags=["{{target}}"])
service = {{Service}}()


@router.get("/", response_model=List[{{Model}}])
async def list_{{target}}():
    return service.find_all()


@router.get("/{{id_param}}", response_model={{Model}})
async def get_{{target}}({{id_param}}: int):
    item = service.find_by_id({{id_param}})
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return item


@router.post("/", response_model={{Model}})
async def create_{{target}}(data: {{Model}}Create):
    return service.create(data)


@router.put("/{{id_param}}", response_model={{Model}})
async def update_{{target}}({{id_param}}: int, data: {{Model}}Update):
    item = service.update({{id_param}}, data)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return item


@router.delete("/{{id_param}}", status_code=204)
async def delete_{{target}}({{id_param}}: int):
    if not service.delete({{id_param}}):
        raise HTTPException(status_code=404, detail="Not found")
""",
}


FIX_RUNTIME_PYTHON = {
    "src/{{target}}/{{module}}.py": """\
\"\"\"
Fixed: {{fix_description}}

Root cause: {{root_cause}}
Before: {{original_problem}}
\"\"\"
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def {{function_name}}({{params}}) -> {{return_type}}:
    \"\"\"
    Fixed version of {{function_name}}.
    
    Fix: {{fix_description}}
    \"\"\"
    # Guard clause for edge case
    if {{guard_condition}}:
        logger.warning("{{guard_warning}}")
        return {{default_return}}
    
    # Main logic
    {{main_logic}}
    
    return {{result}}
""",
}


TEST_STUB_PYTHON = {
    "tests/test_{{module}}.py": """\
import pytest
from {{module_path}} import {{ClassName}}


class Test{{ClassName}}:
    def test_{{test_name}}_happy_path(self):
        \"\"\"Given: {{given}}
        When: {{when}}
        Then: {{then}}\"\"\"
        obj = {{ClassName}}({{constructor_params}})
        result = obj.{{method_name}}({{method_params}})
        assert result == {{expected}}
    
    def test_{{test_name}}_edge_case(self):
        \"\"\"Edge case: {{edge_case}}\"\"\"
        with pytest.raises({{Exception}}):
            {{ClassName}}({{edge_params}}).{{method_name}}()
    
    def test_{{test_name}}_error_handling(self):
        \"\"\"Error handling: {{error_scenario}}\"\"\"
        obj = {{ClassName}}({{constructor_params}})
        result = obj.{{method_name}}({{method_params}})
        assert result is not None
""",
}


TEMPLATES = {
    "implement.python_fastapi_crud": PYTHON_FASTAPI_CRUD,
    "fix.runtime": FIX_RUNTIME_PYTHON,
    "test.coverage": TEST_STUB_PYTHON,
}


# ── 模板匹配器 ───────────────────────────────────────────────

def match_template(intent_type: str, tech_stack: str, target: str) -> Optional[Dict]:
    """根据 intent_type + tech_stack 匹配模板"""
    stack_key = tech_stack.replace("/", "_") if tech_stack != "unknown" else "default"
    
    # 精确匹配
    key = f"{intent_type}.{stack_key}"
    if key in TEMPLATES:
        return TEMPLATES[key]
    
    # 模糊匹配
    key = f"{intent_type}.default"
    if key in TEMPLATES:
        return TEMPLATES[key]
    
    # 按意图类型匹配通用模板
    if intent_type == "fix":
        return FIX_RUNTIME_PYTHON
    elif intent_type == "test":
        return TEST_STUB_PYTHON
    elif intent_type == "implement" and stack_key.startswith("python"):
        return PYTHON_FASTAPI_CRUD
    
    return None


# ── 模板渲染器 ───────────────────────────────────────────────

def render_template(template: Dict, context: Dict[str, Any]) -> Dict[str, str]:
    """渲染模板，返回 {file_path: content}"""
    rendered = {}
    
    for file_path, content in template.items():
        # 替换文件路径中的占位符
        for key, value in context.items():
            placeholder = "{{" + key + "}}"
            file_path = file_path.replace(placeholder, str(value))
            file_path = file_path.replace("{" + key + "}", str(value))
        
        # 替换内容中的占位符
        for key, value in context.items():
            placeholder = "{{" + key + "}}"
            content = content.replace(placeholder, str(value))
            content = content.replace("{" + key + "}", str(value))
        
        rendered[file_path] = content
    
    return rendered


# ── 上下文提取器 ───────────────────────────────────────────────

def extract_context(plan: Dict, project_info: Dict) -> Dict[str, Any]:
    """从 plan 和项目信息中提取模板上下文"""
    intent_type = plan.get("intent_type", "implement")
    slots = plan.get("slots", [])
    tasks = plan.get("sub_tasks", [])
    
    # 提取槽位（plan 中的优先于项目探测）
    slot_dict = {s["name"]: s["value"] for s in slots}
    target = slot_dict.get("target", "module")
    scope = slot_dict.get("scope", "")
    
    # tech_stack: plan 中指定则用 plan 的，否则用项目探测的
    if "tech_stack" in slot_dict and slot_dict["tech_stack"]:
        tech_stack = slot_dict["tech_stack"]
    else:
        tech_stack = project_info.get("tech_stack", {}).get("primary", "unknown")
    
    context = {
        "target": target,
        "Model": target.capitalize(),
        "Service": target.capitalize() + "Service",
        "tech_stack": tech_stack,
        "id_param": f"{target[:-1] if target.endswith('s') else target}_id",
    }
    
    if plan.get("source_layer") == "L2":
        context["code_samples"] = project_info.get("code_style_samples", [])[:2]
        context["existing_modules"] = project_info.get("existing_modules", [])
    
    return context


# ── L1 生成器 ───────────────────────────────────────────────

def generate_l1(plan: Dict, project_info: Dict) -> Dict[str, Any]:
    """L1: 模板匹配 + 渲染"""
    intent_type = plan.get("intent_type", "implement")
    
    # tech_stack: plan 中的 slots 优先，其次项目探测
    slots = plan.get("slots", [])
    slot_dict = {s["name"]: s["value"] for s in slots}
    if "tech_stack" in slot_dict and slot_dict["tech_stack"]:
        tech_stack = slot_dict["tech_stack"]
    else:
        tech_stack = project_info.get("tech_stack", {}).get("primary", "unknown")
    
    template = match_template(intent_type, tech_stack, plan.get("slots", []))
    if not template:
        return {"status": "no_template", "intent_type": intent_type, "tech_stack": tech_stack}
    
    context = extract_context(plan, project_info)
    rendered = render_template(template, context)
    
    return {
        "status": "success",
        "layer": "L1",
        "intent_type": intent_type,
        "files": rendered,
        "context": context,
    }


# ── L2 生成器（Mock） ───────────────────────────────────────

def generate_l2(plan: Dict, project_info: Dict) -> Dict[str, Any]:
    """L2: LLM 生成（Mock 版本）"""
    intent_type = plan.get("intent_type", "implement")
    slots = plan.get("slots", [])
    tasks = plan.get("sub_tasks", [])
    
    slot_dict = {s["name"]: s["value"] for s in slots}
    target = slot_dict.get("target", "auth")
    
    # Mock 生成
    files = _mock_llm_generate(intent_type, target, tasks)
    
    return {
        "status": "success",
        "layer": "L2",
        "intent_type": intent_type,
        "files": files,
    }


def _mock_llm_generate(intent_type: str, target: str, tasks: List[Dict]) -> Dict[str, str]:
    """Mock LLM 生成"""
    model_name = target.capitalize()
    
    if intent_type == "implement":
        return {
            f"src/{target}/models.py": f"""\
\"\"\"{model_name} 数据模型\"\"\"
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class {model_name}Create(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class {model_name}Update(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None


class {model_name}Base(BaseModel):
    name: str
    description: Optional[str] = None


class {model_name}({model_name}Base):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
""",
            f"src/{target}/service.py": f"""\
\"\"\"{model_name} 服务层\"\"\"
from datetime import datetime
from typing import List, Optional
from .models import {model_name}, {model_name}Create, {model_name}Update


class {model_name}Service:
    def __init__(self):
        self._storage: List[{model_name}] = []
        self._next_id = 1

    def create(self, data: {model_name}Create) -> {model_name}:
        model = {model_name}(
            id=self._next_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            **data.model_dump()
        )
        self._storage.append(model)
        self._next_id += 1
        return model

    def find_all(self) -> List[{model_name}]:
        return self._storage

    def find_by_id(self, item_id: int) -> Optional[{model_name}]:
        for item in self._storage:
            if item.id == item_id:
                return item
        return None

    def update(self, item_id: int, data: {model_name}Update) -> Optional[{model_name}]:
        for i, item in enumerate(self._storage):
            if item.id == item_id:
                updated_data = item.model_dump()
                updated_data.update(data.model_dump(exclude_unset=True))
                updated_data['updated_at'] = datetime.now()
                self._storage[i] = {model_name}(**updated_data)
                return self._storage[i]
        return None

    def delete(self, item_id: int) -> bool:
        for i, item in enumerate(self._storage):
            if item.id == item_id:
                self._storage.pop(i)
                return True
        return False
""",
            f"src/{target}/api.py": f"""\
\"\"\"{model_name} API 路由\"\"\"
from fastapi import APIRouter, HTTPException
from typing import List
from .service import {model_name}Service
from .models import {model_name}, {model_name}Create, {model_name}Update

router = APIRouter(prefix="/{target}", tags=["{target}"])
service = {model_name}Service()


@router.get("/", response_model=List[{model_name}])
async def list_{target}():
    return service.find_all()


@router.get("/{{item_id}}", response_model={model_name})
async def get_{target}(item_id: int):
    item = service.find_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return item


@router.post("/", response_model={model_name})
async def create_{target}(data: {model_name}Create):
    return service.create(data)


@router.put("/{{item_id}}", response_model={model_name})
async def update_{target}(item_id: int, data: {model_name}Update):
    item = service.update(item_id, data)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return item


@router.delete("/{{item_id}}", status_code=204)
async def delete_{target}(item_id: int):
    if not service.delete(item_id):
        raise HTTPException(status_code=404, detail="Not found")
""",
        }
    
    return {}


# ── 主流水线 ───────────────────────────────────────────────

def generate_code(
    plan: Dict[str, Any],
    project_root: Optional[str] = None,
    use_mock: bool = True,
) -> Dict[str, Any]:
    """主生成流水线"""
    
    # 步骤 1：项目上下文分析
    project_info = analyze_project(project_root)
    
    # 注入 plan 中的 slots
    if "slots" in plan:
        project_info["slots"] = plan["slots"]
    
    # 步骤 2：L1 模板匹配
    l1_result = generate_l1(plan, project_info)
    
    if l1_result["status"] == "success":
        result = l1_result
    else:
        if use_mock:
            os.environ["USE_MOCK_LLM"] = "true"
        result = generate_l2(plan, project_info)
    
    # 步骤 3：验证（Mock 模式跳过）
    result["validation"] = {
        "syntax_check": "skip (mock mode)",
        "format_check": "skip (mock mode)",
    }
    
    # 步骤 4：生成报告
    result["report"] = _generate_report(result, project_info)
    
    return result


def _generate_report(result: Dict, project_info: Dict) -> str:
    """生成 Markdown 报告"""
    files = result.get("files", {})
    
    lines = [
        f"# 代码生成报告",
        f"",
        f"**意图类型：** {result.get('intent_type', 'unknown')}",
        f"**生成层：** {result.get('layer', 'unknown')}",
        f"**技术栈：** {project_info.get('tech_stack', {}).get('primary', 'unknown')}",
        f"**生成时间：** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"",
        f"## 已生成文件（{len(files)} 个）",
        f"",
        f"| 文件 | 状态 |",
        f"|------|------|",
    ]
    
    for path, content in files.items():
        lines.append(f"| `{path}` | ✓ 已生成 ({len(content.splitlines())} 行) |")
    
    lines.append(f"")
    lines.append(f"---")
    lines.append(f"*由 code-generator v1.0 生成*")
    
    return "\n".join(lines)


# ── CLI 入口 ───────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Code Generator — 从计划生成代码")
    parser.add_argument("--plan", "-p", help="plan JSON 文件或字符串")
    parser.add_argument("--plan-stdin", action="store_true", help="从 stdin 读取 plan JSON")
    parser.add_argument("--project", "-r", help="项目根目录")
    parser.add_argument("--output", "-o", help="输出目录")
    parser.add_argument("--format", "-f", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--dry-run", action="store_true", help="只输出报告不写文件")
    parser.add_argument("--no-mock", action="store_true", help="使用真实 LLM")
    
    args = parser.parse_args()
    
    # 读取 plan
    plan = None
    if args.plan:
        plan_path = Path(args.plan)
        if plan_path.exists():
            try:
                with open(plan_path, encoding="utf-8") as f:
                    plan = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error: invalid JSON in plan file: {e}", file=sys.stderr)
                return 1
        else:
            try:
                plan = json.loads(args.plan)
            except json.JSONDecodeError:
                print(f"Error: plan file not found and value is not valid JSON: {args.plan}", file=sys.stderr)
                return 1
    elif args.plan_stdin:
        try:
            plan = json.load(sys.stdin)
        except json.JSONDecodeError as e:
            print(f"Error: invalid JSON from stdin: {e}", file=sys.stderr)
            return 1
    else:
        plan = {
            "intent_type": "implement",
            "confidence": 0.9,
            "source_layer": "L1",
            "description": "实现用户认证模块",
            "slots": [
                {"name": "target", "value": "auth", "evidence": "verified"},
                {"name": "scope", "value": "login+register", "evidence": "provisional"},
            ],
            "sub_tasks": [
                {"id": "T1", "description": "设计用户数据模型", "priority": "P0"},
                {"id": "T2", "description": "实现服务层", "priority": "P0"},
                {"id": "T3", "description": "实现 API 接口", "priority": "P1"},
            ],
        }
    
    # 执行生成
    result = generate_code(plan=plan, project_root=args.project, use_mock=not args.no_mock)
    
    # 输出
    if args.format == "markdown":
        output = result.get("report", "")
    else:
        output = json.dumps(result, ensure_ascii=False, indent=2)
    
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"报告已保存到: {args.output}", file=sys.stderr)
    else:
        print(output)
    
    # 写入文件
    if not args.dry_run and args.format == "json":
        files = result.get("files", {})
        output_dir = args.output or "."
        
        for path, content in files.items():
            full_path = Path(output_dir) / path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding="utf-8")
            print(f"✓ 已生成: {full_path}", file=sys.stderr)
    
    return 1 if isinstance(result, dict) and result.get("status") == "error" else 0


if __name__ == "__main__":
    sys.exit(main())
