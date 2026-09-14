---
name: code-generator
description: "Two-tier code generation (L1 template engine + L2 LLM) that produces working code from intent plans. Supports Python FastAPI, TypeScript Express, and Go Gin CRUD templates with project analysis. Use when converting a structured plan into actual code files. 当用户要求 生成代码 / 按计划写实现 / 把方案变成代码 时使用。"
license: Apache-2.0
compatibility: Pure prompt-based; may read project structure via Bash.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: planning
  pattern: code-generator
  tier: powerful
  verified-date: "2026-09-09"
---

# Code Generator — 从计划到代码的自动化生成器

将 code-intent-planner 的任务计划转化为可运行的代码文件。
两层架构：L1 模板引擎（快，覆盖常见模式） + L2 LLM 生成（灵活，处理复杂逻辑）。

## 输入清单

| 输入 | 必需 | 说明 | 来源 |
|------|------|------|------|
| plan_json | 是 | code-intent-planner 输出的完整 JSON | code-intent-planner |
| project_root | 否 | 项目根目录 | 自动探测 |
| output_dir | 否 | 代码输出目录 | 当前工作目录 |
| session_id | 否 | 会话标识（跨轮复用） | auto-generated |
| dry_run | 否 | 只输出计划不写入文件 | false |

缺失时询问模板：「请提供：① code-intent-planner 输出的 JSON（或 plan 文件路径）。项目目录自动探测。」

---

## 两两架构

### L1 模板引擎（零 LLM，<50ms）

覆盖常见代码模式，直接填充模板生成代码：

| 意图类型 | 覆盖模式 | 示例 |
|---------|---------|------|
| implement.feature | CRUD model + service + API | 用户注册/登录 |
| implement.api | REST controller + DTO + validation | 订单接口 |
| implement.component | UI component（React/Vue/Svelte） | 登录表单 |
| fix.runtime | Bug fix template + patch | 空指针修复 |
| test.coverage | Test stub generation | 覆盖率补全 |
| refactor | Refactor skeleton + checklist | 模块重构 |

**模式匹配规则**（按优先级）：
1. 技术栈 → 语言/框架决定模板语言
2. 意图类型 → 决定代码结构
3. 槽位 target → 决定文件名和模块名
4. 项目已有代码 → 决定风格一致性

### L2 LLM 生成（灵活，支持复杂逻辑）

触发条件（满足任一）：
1. L1 无匹配模板
2. 任务描述含 "自定义" / "特殊" / "复杂"
3. 项目有独特架构约定（需 LLM 理解上下文）
4. L1 生成代码通过编译/格式检查失败

**上下文注入**（每次 L2 调用前必读）：
- 项目技术栈（package.json / pyproject.toml 等）
- 现有代码风格（读取 2-3 个代表性文件）
- 已有模块结构（目录树）
- 关键依赖版本

---

## 工作流

### 步骤 1：项目上下文分析

```bash
# 自动探测（无需手动配置）
analyze_project() {
  # 技术栈
  detect_tech_stack(project_root)    # → python/express/go/rust
  
  # 目录结构（前 3 层）
  find "$project_root" -maxdepth 3 -type d | head -20
  
  # 关键配置文件
  ls package.json pyproject.toml go.mod Cargo.toml tsconfig.json .eslintrc* 2>/dev/null
  
  # 代码风格样本（读取 2-3 个代表性文件）
  sample_files=$(find . -name "*.py" -o -name "*.ts" -o -name "*.js" | head -3)
  cat $sample_files
}
```

**预期输出：**
```json
{
  "tech_stack": "python/fastapi",
  "directory_structure": ["src/models/", "src/services/", "src/api/"],
  "code_style_samples": ["..."],
  "existing_modules": ["auth", "users", "orders"]
}
```

---

### 步骤 2：L1 模板匹配

按以下顺序尝试匹配：

| 优先级 | 检查项 | 命中后动作 |
|--------|--------|-----------|
| 1 | intent_type + tech_stack 组合 | 加载对应模板 |
| 2 | sub_tasks 关键词 | 微调模板参数 |
| 3 | project 已有代码风格 | 自适应格式 |
| 4 | 默认 fallback | 生成基础骨架 |

**模板加载规则：**
```python
# 伪代码
for pattern in [
    f"{intent_type}.{tech_stack.replace('/', '.')}",  # implement.python.fastapi
    f"{intent_type}.default",                          # implement.default
    "implement.default",                               # 最泛模板
]:
    if template_exists(pattern):
        return load_template(pattern)
```

---

### 步骤 3：代码生成

**L1 模式（模板填充）：**
```python
def generate_from_template(template, context):
    """用 context 中的变量填充 Jinja2 模板"""
    rendered = template.render(
        module_name=context["target"],
        tech_stack=context["tech_stack"],
        tasks=context["sub_tasks"],
        constraints=context["constraints"],
        project_style=context["code_style_samples"]
    )
    return rendered
```

**L2 模式（LLM 生成）：**
```python
def generate_with_llm(plan, project_context):
    """调用 LLM，注入完整项目上下文"""
    prompt = build_generation_prompt(plan, project_context)
    response = call_llm(prompt, temperature=0.2)
    return parse_code_output(response)
```

---

### 步骤 4：代码验证

生成代码后自动验证：

| 验证项 | 方法 | 失败处理 |
|--------|------|---------|
| 语法检查 | `python -m py_compile` / `tsc --noEmit` | L2 重新生成 |
| 格式检查 | `black` / `prettier` / `go fmt` | 自动格式化 |
| 导入检查 | `pyflakes` / `eslint --fix` | 修复后重试 |
| 依赖检查 | `pip install -r requirements.txt` | 报告缺失依赖 |

验证通过 → 写入文件
验证失败 → L2 重新生成（最多 2 次）

---

### 步骤 5：测试桩生成

调用 tdd-guide 技能里的 test_generator（路径以 tdd-guide 技能目录为基准，不是本技能目录）：

```bash
# <tdd-guide>/scripts/test_generator.py
python "<tdd-guide>/scripts/test_generator.py" \
  --source src/auth/service.py \
  --framework pytest \
  --output tests/test_auth_service.py
```

---

### 步骤 6：进度报告

```markdown
## 生成报告 — {session_id}

**意图类型：** {intent_type}
**生成时间：** {timestamp}
**生成层：** L1（模板） / L2（LLM）

### 已生成文件（{n} 个）
| 文件 | 行数 | 验证 |
|------|------|------|
| src/auth/model.py | 42 | ✓ 语法OK |
| src/auth/service.py | 87 | ✓ 语法OK |
| tests/test_auth_service.py | 65 | ✓ 语法OK |

### 待生成文件（{m} 个）
| 文件 | 原因 |
|------|------|
| src/auth/api.py | 依赖 src/auth/service.py |
| tests/test_auth_api.py | 依赖 src/auth/api.py |

### 验证失败（{k} 个，需人工介入）
| 文件 | 错误 | 建议 |
|------|------|------|
| src/auth/service.py | import error: no module named 'jwt' | pip install pyjwt |
```

---

## 代码模式模板库

### implement.feature — Python FastAPI CRUD

**模板位置：** `references/templates/python_fastapi_crud.py.j2`

```python
# src/{target}/models.py
from datetime import datetime
from pydantic import BaseModel, Field

class {Model}Create(BaseModel):
    {fields}

class {Model}Update(BaseModel):
    {fields}

class {Model}Base(BaseModel):
    id: int
    {fields}
    created_at: datetime
    updated_at: datetime

class {Model}({Model}Base):
    class Config:
        from_attributes = True
```

### implement.feature — TypeScript Express CRUD

**模板位置：** `references/templates/typescript_express_crud.ts.j2`

```typescript
// src/{target}/{target}.router.ts
import { Router, Request, Response } from 'express';
import { {Service} } from './{target}.service';

const router = Router();
const service = new {Service}();

router.get('/', async (req: Request, res: Response) => {
  const items = await service.findAll();
  res.json(items);
});

// ... POST, GET/:id, PUT/:id, DELETE/:id
```

### fix.runtime — Bug Fix Template

**模板位置：** `references/templates/fix_runtime.py.j2`

```python
# 修复前的代码位置标注
# TODO: Replace with fixed version
# Root cause: {root_cause}
# Fix: {fix_description}

def {function_name}({params}):
    """
    Fixed: {fix_description}
    
    Before:
      {original_problem}
    
    After:
      {fixed_version}
    """
    # Guard clause for edge case
    if {condition}:
        return {default_value}
    
    # Main logic
    return {result}
```

### test.coverage — Test Stub Generator

**模板位置：** `references/templates/test_stub.py.j2`

```python
import pytest
from {module} import {FunctionName}

class Test{FunctionName}:
    def test_{name}_happy_path(self):
        """Given: {given}
        When: {when}
        Then: {then}"""
        result = {function_name}({params})
        assert result == {expected}
    
    def test_{name}_edge_case(self):
        """Edge case: {edge_case}"""
        with pytest.raises({Exception}):
            {function_name}({edge_params})
```

---

## 失败处置表

| 现象 | 原因 | 处置 |
|------|------|------|
| L1 无匹配模板 | 意图类型或技术栈不在模板库 | 升级 L2 |
| L1 生成代码语法错误 | 模板变量填充错误 | 重新渲染，检查 context |
| L2 生成代码编译失败 | LLM 幻觉 / 语法错误 | 重试 L2（最多 2 次） |
| 依赖缺失 | 模板使用了未安装的包 | 报告缺失依赖，建议安装 |
| 风格不一致 | 项目有特定约定 | 读取更多样本文件，调整 L2 prompt |
| 文件冲突 | 目标文件已存在 | 先读取现有文件，合并变更 |

---

## 与 tdd-guide 的协作

code-generator 生成代码后，自动调用 tdd-guide：

```
code-generator
    ↓ 生成代码文件
tdd-guide (test_generator.py)
    ↓ 生成测试桩
code-generator
    ↓ 验证测试桩语法
完成报告
```

**TDD 优先模式**（可选）：
1. 先生成测试桩（RED 阶段）
2. 再实现代码使测试通过（GREEN 阶段）
3. 最后重构（REFACTOR 阶段）

启用方式：`--mode tdd` 或 plan 中含 `tdd: true`

---

## 参考

- references/templates/ —— 代码模板（Jinja2）
- references/patterns.md —— 常见代码模式速查
- references/gotchas.md —— 生成陷阱与规避
- references/examples.md —— 真实生成案例