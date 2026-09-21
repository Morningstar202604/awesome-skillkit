---
name: code-generator
description: "两层代码生成（L1 脚本模板引擎 + L2 agent 生成），把结构化计划转为可运行代码。L1 脚本覆盖 Python FastAPI CRUD、Bug 修复骨架、测试桩三类；L2 复杂逻辑由 agent 按项目上下文生成。何时使用：已有一份结构化实现计划、需要落成可运行代码文件时。触发场景（中/英）：生成代码 / 按计划写实现 / 把方案变成代码 / 生成 CRUD 脚手架 / generate code / implement from plan / turn plan into code。排除项：不审查或调试已有代码，不制定实现计划（交给 code-intent-planner）。"
license: Apache-2.0
compatibility: Pure Python 3.8+ stdlib（脚本零依赖）；L2 生成由运行技能的 agent 承担，无需 API key。
metadata:
  version: "1.1"
  author: awesome-skillkit
  category: planning
  pattern: code-generator
  tier: powerful
  verified-date: "2026-09-21"
---

# Code Generator — 从计划到代码的自动化生成器

把 code-intent-planner 的任务计划转化为可运行代码文件。两层架构：**L1 脚本模板引擎**（快，覆盖常见模式） + **L2 agent 生成**（灵活，处理复杂逻辑）。

## 适用决策表

| 情况 | 用不用本技能 | 走哪层 |
|------|------------|--------|
| plan 是 Python FastAPI 的 CRUD 实现 | ✅ L1 脚本直出 | `code_generator.py --plan ... --format json` |
| plan 是 bug 修复 / 测试桩 | ✅ L1 脚本出骨架 | 同上（`fix`/`test` 意图） |
| TypeScript/Go 的 CRUD | ⚠️ 脚本 L1 不覆盖，agent 按 .j2 模板手工渲染 | `references/templates/typescript_express_crud.ts.j2` |
| 自定义/复杂业务逻辑 | ⚠️ L2 由 agent 生成（见诚实声明） | agent 按「L2 生成纪律」执行 |
| 还没有实现计划 | ❌ 先走 code-intent-planner | — |
| 审查/调试已有代码 | ❌ 超范围 | — |

## 诚实声明（先读，本节与脚本实际行为逐条对齐）

- **L2 在脚本里是 Mock**。`code_generator.py` 的 L2 路径（`generate_l2`）不做任何 LLM 调用：对 `implement` 意图恒返回一份 FastAPI CRUD 脚手架，其他意图返回空。`--no-mock` 参数只是标记位，**不存在真实 LLM 后端**。真正的"LLM 生成"由运行本技能的 agent（你）执行——脚本的角色是 L1 加速器 + 结构化报告器。
- **脚本不做代码验证**。返回 JSON 里 `validation` 字段恒为 `"skip (mock mode)"`；`py_compile`/`tsc`/`black` 等检查由 agent 在文件落盘后自行执行（工作流步骤 4），报告里的"✓ 已生成"只代表"内容已产出"，**不代表可用**。
- **脚本不读 `references/templates/` 下的 .j2 文件**。脚本用内置内存模板（3 族）；.j2 文件是给 agent 与测试做 Jinja2 渲染的参考材料（4 个），两套体系不要混淆。
- **脚手架 ≠ 产品**。L1 产出的 service 层是内存 list 存储、无鉴权、无持久化——它是起点不是终点，交付前必须按项目真实需求改造（见暗知识 1）。

## 输入清单

| 输入 | 必需 | 说明 | 来源 |
|------|------|------|------|
| plan_json | 是 | code-intent-planner 输出的完整 JSON（文件路径或内联 JSON） | code-intent-planner |
| project_root | 否 | 项目根目录 | 自动探测 |
| output | 否 | 报告输出文件路径（markdown/json 报告落盘） | — |
| output_dir | 否 | 代码文件输出目录（仅 `--format json` 且非 dry-run 时写代码文件） | 默认当前目录 |
| dry_run | 否 | 只输出报告不写入任何文件 | false |

缺失时询问模板：「请提供：① code-intent-planner 输出的 JSON（或 plan 文件路径）。项目目录自动探测。」

## 前置自检

```bash
# 1. plan 来源可读
test -f "$PLAN_JSON" && echo "OK plan present" || echo "NEED plan_json"
# 2. 项目根可探测（任一存在即命中）
for f in package.json pyproject.toml go.mod Cargo.toml requirements.txt; do
  test -f "$project_root/$f" && echo "tech=$f" && break
done
# 3. 脚本与模板库在位
test -f scripts/code_generator.py && test -d references/templates && echo "OK skill complete"
```

- 预期：plan 存在；项目根至少命中一个配置文件或标 `unknown`；脚本与模板库在位。
- 若失败：plan 缺失 → STOP 回到输入清单索取；技能文件不全 → STOP 回报未完整分发。

## L1 真实覆盖表（脚本内置 3 族，与代码逐一对应）

| 意图类型 | 脚本键 | 产出文件 | 说明 |
|---------|--------|---------|------|
| implement + python/fastapi | `implement.python_fastapi_crud` | `src/{target}/models.py` + `service.py` + `api.py` | Pydantic v2 模型 + 内存存储 service + FastAPI 路由 |
| fix（任意技术栈，实际产出 Python） | `fix.runtime` | `src/{target}/{module}.py` | guard-clause 修复骨架，槽位需填 function_name/params/root_cause 等 |
| test（任意技术栈，实际产出 Python） | `test.coverage` | `tests/test_{module}.py` | pytest 测试桩，槽位需填 module_path/ClassName/method 等 |

- 匹配顺序：精确键 `{intent}.{tech_stack.replace('/','_')}` → `{intent}.default` → 意图兜底（fix→修复骨架，test→测试桩，implement+python*→CRUD）→ 无匹配返回 `no_template`。
- TypeScript Express 的 CRUD 由 agent 用 `references/templates/typescript_express_crud.ts.j2` 渲染（需 Jinja2，或按占位符手工替换）。
- 渲染机制是**朴素占位符替换**（`{{key}}` 与 `{key}` 都替换），不是 Jinja2——模板里不要用控制流语法。

## 工作流

### 步骤 1：项目上下文分析

```bash
python3 scripts/code_generator.py --project <project_root> --format json --dry-run
```

- 动作：脚本调用 project_analyzer 探测技术栈与目录结构；agent 另读 2-3 个代表性代码文件确认风格（缩进/命名/导入习惯）。
- 预期：JSON 含 `tech_stack`、`files`、`context`。
- 若失败：无配置文件 → `tech_stack` 标 `unknown` 继续；目录不可读 → STOP 回报权限。

### 步骤 2：L1 模板生成（脚本）

```bash
# 生成报告（markdown，不写代码）
python3 scripts/code_generator.py --plan plan.json --project . --format markdown
# 落盘代码 + JSON 报告
python3 scripts/code_generator.py --plan plan.json --format json --output report.json --output-dir .
```

- 预期：`status:"success"` 且 `files` 含 3 个文件（CRUD 情形）；`no_template` → 转 L2。
- 若失败：plan 缺 slots 的 `target` → 模板渲染退化为 `module`，先补 plan 再跑。

### 步骤 3：L2 agent 生成（L1 未覆盖时）

agent 按以下纪律生成，不依赖脚本的 mock L2：

1. 注入上下文：技术栈配置、2-3 个风格样本、目录树、关键依赖版本；
2. 先写测试桩或接口签名，再填实现（与 tdd-guide 的 RED→GREEN 对齐）；
3. 产出必须通过步骤 4 验证才允许落盘交付；
4. 失败重试上限 2 次，仍失败则列入"需人工介入"清单，不许静默降级为脚手架。

### 步骤 4：代码验证（agent 执行，脚本不做）

| 验证项 | 方法 | 失败处理 |
|--------|------|---------|
| 语法 | `python -m py_compile` / `tsc --noEmit` | 修正或重生成 |
| 格式 | `black --check` / `prettier --check` / `go fmt` | 自动格式化后复验 |
| 导入 | `pyflakes` / `eslint` | 修复后复验 |
| 冒烟 | 生成的测试桩跑 `pytest --collect-only` | 收集失败=桩不可用，回 L2 |

- 预期：全部通过才宣布交付；任何一项失败都写进进度报告的"验证失败"节。

### 步骤 5：测试桩生成（真实可调）

tdd-guide 技能（位于技能库 code-quality 域）的 test_generator.py 真实存在，路径以 tdd-guide 技能目录为基准：

```bash
python "<tdd-guide>/scripts/test_generator.py" \
  --source src/auth/service.py \
  --framework pytest \
  --output tests/test_auth_service.py
```

- 若失败：tdd-guide 未安装 → 跳过并标注，不阻断主流程。

### 步骤 6：进度报告

脚本 markdown 模式自动产出（含已生成文件清单与行数）；agent 追加两类信息：**验证结果**（步骤 4）与**待改造项**（见暗知识 1 的清单）。报告里"已生成"与"验证通过"是两个不同状态，不许合并表述。

## 代码生成暗知识（从模板与真实工程里来的坑）

1. **脚手架的三张欠条**：L1 CRUD 脚手架固定有三处必须改造——① `service.py` 是内存 list 存储（重启即丢），要换真实持久层；② 无鉴权/权限检查，`api.py` 的路由裸奔；③ 无分页，`find_all` 在数据量上来后是事故。交付说明里必须列出这三项，把"欠条"显式化。
2. **命名派生链一错全错**：`target` 槽位决定 `Model = target.capitalize()`、`Service = target + "Service"`、`id_param = target 去尾 s + "_id"`。`target` 用复数（如 `orders`）则 Model 变 `Orders`、id_param 变 `order_id`——先用单数模块名再考虑表名复数，或在 plan 的 slots 里显式覆盖。
3. **模板先行的边界**：模板覆盖的是"形状"（分层、命名、路由写法），永远不覆盖业务规则、鉴权、并发控制。判断一个需求能不能走 L1：如果 sub_tasks 里出现"校验库存/风控/通知"这类词，直接 L2。
4. **落盘前必须验证**：报告"✓ 已生成"只是内容产出，py_compile 都过不了的东西落盘会污染项目——agent 的验证步骤（步骤 4）不可跳过，宁可重来。
5. **风格一致性靠样本不靠想象**：L2 生成前读 2-3 个真实文件（缩进、引号、import 排序、异常处理习惯），生成的代码要像"这个项目里的人写的"，不是像教科书。

## 红线

1. **不冒充验证**：没有跑过 py_compile/tsc 的代码，报告里不得出现"验证通过"。
2. **不静默降级**：L2 重试 2 次失败就列入"需人工介入"，不许拿脚手架顶替复杂逻辑交付。
3. **不覆盖已有文件**：目标文件存在时先读取合并（或征得同意），不许直接覆写。
4. **不伪造交付清单**：报告里的"已生成 + 待生成 + 失败"三类计数必须与实际产物一一对应。
5. **不做计划外发挥**：plan 之外的功能不顺手实现；有建议写进报告。

## 失败处置表

| 现象 | 原因 | 处置 |
|------|------|------|
| `no_template` | 意图类型或技术栈不在 3 族覆盖内 | 转 L2（agent 生成）；或按 .j2 模板渲染 |
| 渲染后代码含未替换占位符 | plan slots 缺 `target` 等键 | 补齐 plan 的 slots 再跑 |
| L2 生成代码编译失败 | 逻辑错误/幻觉 | 重试 L2（≤2 次），仍失败列入人工介入 |
| 依赖缺失 | 模板 import 了未安装的包 | 报告列出缺失依赖，征得同意后安装 |
| 文件冲突 | 目标文件已存在 | 先读取现有文件合并，不覆写 |
| `--output` 指向不存在的深层目录 | 路径问题 | 脚本会自动创建父目录；仍失败改用相对路径 |

## 与 tdd-guide 的协作

code-generator 生成代码后，可自动调用 tdd-guide：

```text
code-generator → 生成代码文件 → agent 验证（步骤 4）→ tdd-guide (test_generator.py) → 生成测试桩 → 验证测试桩语法 → 完成报告
```

**TDD 优先模式**（可选）：先生成测试桩（RED）→ 实现代码使测试通过（GREEN）→ 重构（REFACTOR）。启用方式：plan 中含 `tdd: true`。

## 交付标准

- 成功定义：plan 中可生成的 sub_tasks 均产出文件，且**agent 验证**（步骤 4）通过或明确列入"需人工介入"。
- 产物命名：按 plan 的 target 与模块约定（如 `src/{target}/model.py`、`tests/test_{target}_service.py`）。
- 保存位置：代码 → `--output-dir`（默认当前目录）；报告 → `--output`（缺省打印 stdout）。
- 验证完整性：重跑步骤 4 全 ✓；"已生成 + 待生成 + 失败"计数与实际产物一致；脚手架三张欠条写入交付说明。

## 参考

- `references/templates/` — 4 个 Jinja2 模板（agent 渲染用；脚本 L1 用内置内存模板，两套并行）
- `references/patterns.md` — 常见代码模式速查
- `references/gotchas.md` — 生成陷阱与规避
- `references/examples.md` — 真实生成案例
- `scripts/test_code_generator.py` — 8 项单元测试（含 .j2 渲染产物 py_compile 检查），改动脚本后必跑
