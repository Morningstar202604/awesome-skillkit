---
name: code-generator
description: "两层代码生成（L1 模板引擎 + L2 LLM），把结构化计划转为可运行代码。支持 Python FastAPI、TypeScript Express、Go Gin 的 CRUD 模板与项目分析。何时使用：需把 code-intent-planner 产出的计划落为实际代码文件时。触发场景（中/英）：生成代码 / 按计划写实现 / 把方案变成代码 / generate code / implement from plan / turn plan into code。排除项：不审查或调试已有代码（仅从计划生成）。"
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

把 code-intent-planner 的任务计划转化为可运行代码文件。两层架构：L1 模板引擎（快，覆盖常见模式） + L2 LLM 生成（灵活，处理复杂逻辑）。

## 输入清单

| 输入 | 必需 | 说明 | 来源 |
|------|------|------|------|
| plan_json | 是 | code-intent-planner 输出的完整 JSON | code-intent-planner |
| project_root | 否 | 项目根目录 | 自动探测 |
| output_dir | 否 | 代码输出目录 | 当前工作目录 |
| session_id | 否 | 会话标识（跨轮复用） | auto-generated |
| dry_run | 否 | 只输出计划不写入文件 | false |

缺失时询问模板：「请提供：① code-intent-planner 输出的 JSON（或 plan 文件路径）。项目目录自动探测。」

## 前置自检

```bash
# 1. plan 来源可读
test -f "$PLAN_JSON" && echo "OK plan present" || echo "NEED plan_json"
# 2. 项目根可探测（任一群存在即视为命中）
for f in package.json pyproject.toml go.mod Cargo.toml pom.xml build.gradle requirements.txt; do
  ls "$project_root/$f" >/dev/null 2>&1 && echo "tech=$f" && break
done
# 3. 模板库存在
test -d references/templates && echo "OK templates present"
```

- 预期：plan 文件存在；项目根至少命中一个配置文件或标 `unknown`；模板库存在。
- 若失败：plan 缺失 → STOP，回到输入清单索取；模板库缺失 → STOP，回报技能未完整分发。

## 两层架构

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

**模式匹配规则**（按优先级）：① 技术栈→语言/框架决定模板语言；② 意图类型→决定代码结构；③ 槽位 target→决定文件名与模块名；④ 项目已有代码→决定风格一致性。

### L2 LLM 生成（灵活，支持复杂逻辑）

触发条件（满足任一）：① L1 无匹配模板；② 任务描述含「自定义/特殊/复杂」；③ 项目有独特架构约定；④ L1 生成代码通过编译/格式检查失败。

**上下文注入**（每次 L2 调用前必读）：项目技术栈（package.json / pyproject.toml 等）、现有代码风格（读取 2-3 个代表性文件）、已有模块结构（目录树）、关键依赖版本。

## 工作流

### 步骤 1：项目上下文分析

- 动作：探测技术栈、目录结构（前 3 层）、关键配置文件、2-3 个代码风格样本。
- 预期输出：
```json
{
  "tech_stack": "python/fastapi",
  "directory_structure": ["src/models/", "src/services/", "src/api/"],
  "code_style_samples": ["..."],
  "existing_modules": ["auth", "users", "orders"]
}
```
- 若失败：无配置文件 → `tech_stack` 标 `unknown`，继续（L2 时再读样本）；目录不可读 → STOP 回报权限问题。

### 步骤 2：L1 模板匹配

按以下顺序尝试匹配：

| 优先级 | 检查项 | 命中后动作 |
|--------|--------|-----------|
| 1 | intent_type + tech_stack 组合 | 加载对应模板 |
| 2 | sub_tasks 关键词 | 微调模板参数 |
| 3 | project 已有代码风格 | 自适应格式 |
| 4 | 默认 fallback | 生成基础骨架 |

- 动作：按优先级加载 `references/templates/` 下对应 `.j2`，无命中转 L2。
- 预期：命中则拿到模板；否则进入 L2。
- 若失败：模板渲染变量缺失 → 检查 plan 的 slots 是否齐全（name/tech_stack/target）。

### 步骤 3：代码生成

**L1 模式（模板填充）：**
```python
def generate_from_template(template, context):
    """用 context 中的变量填充 Jinja2 模板"""
    return template.render(
        module_name=context["target"],
        tech_stack=context["tech_stack"],
        tasks=context["sub_tasks"],
        constraints=context["constraints"],
        project_style=context["code_style_samples"],
    )
```

**L2 模式（LLM 生成）：**
```python
def generate_with_llm(plan, project_context):
    """调用 LLM，注入完整项目上下文"""
    prompt = build_generation_prompt(plan, project_context)
    return parse_code_output(call_llm(prompt, temperature=0.2))
```

- 动作：按 L1/L2 路径产出代码字符串。
- 预期：产出对应文件内容，结构与 plan 的 sub_tasks 对应。
- 若失败：L1 渲染异常 → 校验 context；L2 输出非代码 → 重试 L2（最多 2 次）。

### 步骤 4：代码验证

| 验证项 | 方法 | 失败处理 |
|--------|------|---------|
| 语法检查 | `python -m py_compile` / `tsc --noEmit` | L2 重新生成 |
| 格式检查 | `black` / `prettier` / `go fmt` | 自动格式化 |
| 导入检查 | `pyflakes` / `eslint --fix` | 修复后重试 |
| 依赖检查 | `pip install -r requirements.txt` | 报告缺失依赖 |

- 动作：逐项校验，全部通过才写入文件。
- 预期：全部 ✓；任一失败进入对应处理。
- 若失败：连续 2 次 L2 仍失败 → 标记该文件需人工介入（见进度报告）。

### 步骤 5：测试桩生成

调用 tdd-guide 技能的 test_generator（路径以 tdd-guide 技能目录为基准，不是本技能目录）：

```bash
# <tdd-guide>/scripts/test_generator.py
python "<tdd-guide>/scripts/test_generator.py" \
  --source src/auth/service.py \
  --framework pytest \
  --output tests/test_auth_service.py
```

- 动作：为已生成模块生成测试桩。
- 预期：在 `tests/` 下生成对应测试文件。
- 若失败：tdd-guide 未安装 → 跳过此步并标注，不阻断主流程。

### 步骤 6：进度报告

```markdown
## 生成报告 — {session_id}
**意图类型：** {intent_type}  **生成层：** L1 / L2
### 已生成文件（{n} 个）
| 文件 | 行数 | 验证 |
| src/auth/model.py | 42 | ✓ 语法OK |
### 待生成文件（{m} 个）
| 文件 | 原因 |
| src/auth/api.py | 依赖 src/auth/service.py |
### 验证失败（{k} 个，需人工介入）
| 文件 | 错误 | 建议 |
| src/auth/service.py | import error: no module named 'jwt' | pip install pyjwt |
```

## 代码模式模板库

真实模板位于 `references/templates/`（Jinja2，按意图+技术栈命名）：

| 意图类型 | 模板文件 |
|---------|---------|
| implement.feature — Python FastAPI | `references/templates/python_fastapi_crud.py.j2` |
| implement.feature — TypeScript Express | `references/templates/typescript_express_crud.ts.j2` |
| fix.runtime — Bug Fix | `references/templates/fix_runtime.py.j2` |
| test.coverage — Test Stub | `references/templates/test_stub.py.j2` |

示例（`references/templates/python_fastapi_crud.py.j2` 渲染片段）：
```python
# src/{target}/models.py
from datetime import datetime
from pydantic import BaseModel, Field

class {Model}Create(BaseModel):
    {fields}

class {Model}({Model}Base):
    class Config:
        from_attributes = True
```

## 失败处置表

| 现象 | 原因 | 处置 |
|------|------|------|
| L1 无匹配模板 | 意图类型或技术栈不在模板库 | 升级 L2 |
| L1 生成代码语法错误 | 模板变量填充错误 | 重新渲染，检查 context |
| L2 生成代码编译失败 | LLM 幻觉 / 语法错误 | 重试 L2（最多 2 次） |
| 依赖缺失 | 模板使用了未安装的包 | 报告缺失依赖，建议安装 |
| 风格不一致 | 项目有特定约定 | 读取更多样本文件，调整 L2 prompt |
| 文件冲突 | 目标文件已存在 | 先读取现有文件，合并变更 |

## 与 tdd-guide 的协作

code-generator 生成代码后，可自动调用 tdd-guide：

```text
code-generator → 生成代码文件 → tdd-guide (test_generator.py) → 生成测试桩 → 验证测试桩语法 → 完成报告
```

**TDD 优先模式**（可选）：先生成测试桩（RED）→ 实现代码使测试通过（GREEN）→ 重构（REFACTOR）。
启用方式：`--mode tdd` 或 plan 中含 `tdd: true`。

## 交付标准

- 成功定义：所有 plan 中可生成的 sub_tasks 均产出文件，且语法/格式/导入验证通过（或明确列出需人工介入项）。
- 产物命名：按 plan 的 target 与模块约定（如 `src/{target}/model.py`、`src/{target}/service.py`、`tests/test_{target}_service.py`）。
- 保存位置：`output_dir`（默认当前工作目录）。
- 验证完整性：重跑步骤 4 的四项检查全 ✓；对照进度报告确认「已生成 + 待生成 + 失败」三类计数与 plan 一致。

## 参考

- references/templates/ — 代码模板（Jinja2，真实可渲染文件）
- references/patterns.md — 常见代码模式速查
- references/gotchas.md — 生成陷阱与规避
- references/examples.md — 真实生成案例
