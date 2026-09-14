# Jinja2 代码模板库

本目录存放 code-generator 的 L1 代码模板。SKILL.md「代码模式模板库」一节引用的就是这里的文件。

## 用途与所需变量

| 模板文件 | 触发意图 | 渲染产物 | 所需变量 |
|---|---|---|---|
| `python_fastapi_crud.py.j2` | `implement` + `python/fastapi` | 单文件 FastAPI CRUD（pydantic 模型 + 服务层 + Router + app） | `target`, `Model`, `Service`, `tech_stack`, `id_param` |
| `typescript_express_crud.ts.j2` | `implement` + `node/express` | 单文件 Express CRUD（接口类型 + 服务层 + Router） | `target`, `Model`, `Service`, `tech_stack`, `id_param` |
| `fix_runtime.py.j2` | `fix` / `fix.runtime` | 带根因注释的修复版函数 | `module`, `target`, `function_name`, `params`, `return_type`, `root_cause`, `fix_description`, `original_problem`, `guard_condition`, `guard_warning`, `default_return`, `main_logic`, `result` |
| `test_stub.py.j2` | `test` / `test.coverage` | pytest 测试桩（happy path / edge case / error handling） | `module_path`, `ClassName`, `test_name`, `given`, `when`, `then`, `constructor_params`, `method_name`, `method_params`, `expected`, `Exception`, `edge_params`, `edge_case`, `error_scenario` |

### 变量从哪里来

前五个变量由 `scripts/code_generator.py:extract_context()` 产出，取值口径如下（`target` 取自 plan 的 `slots[name=target]`）：

| 变量 | 取值 | 示例（target=product） |
|---|---|---|
| `target` | 槽位 target 原值 | `product` |
| `Model` | `target.capitalize()` | `Product` |
| `Service` | `target.capitalize() + "Service"` | `ProductService` |
| `tech_stack` | slots 或 `project_analyzer` 探测结果 | `python/fastapi` |
| `id_param` | `target` 去尾 s 后 + `_id` | `product_id`（target=users 时为 `user_id`） |

`fix_runtime.py.j2` / `test_stub.py.j2` 的其余变量不在 `extract_context()` 的默认返回里，需要调用方按上面的表格补齐后再 render——变量名与 `code_generator.py` 中 `FIX_RUNTIME_PYTHON` / `TEST_STUB_PYTHON` 的占位符完全一致，不要另起名字。

## 渲染示例

渲染器用 `StrictUndefined`：缺变量直接报错，避免静默产出半渲染代码。

```python
# render_example.py —— 按需修改 context 后运行
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, StrictUndefined

env = Environment(
    loader=FileSystemLoader("references/templates"),
    undefined=StrictUndefined,
    keep_trailing_newline=True,
)

# 1) FastAPI CRUD；TS 模板用同一套变量，把 tech_stack 换成 node/express
ctx = {
    "target": "product",
    "Model": "Product",
    "Service": "ProductService",
    "tech_stack": "python/fastapi",
    "id_param": "product_id",
}
code = env.get_template("python_fastapi_crud.py.j2").render(**ctx)
Path("src/product/impl.py").write_text(code, encoding="utf-8")

# 2) 修复模板
code = env.get_template("fix_runtime.py.j2").render(
    target="auth",
    module="service",
    function_name="login",
    params="self, username: str, password: str",
    return_type="Optional[Token]",
    root_cause="user 为 None 时直接访问 .email",
    fix_description="登录前增加空值 guard clause",
    original_problem="return Token(user.email, user.id) 抛出 AttributeError",
    guard_condition="user is None",
    guard_warning="Login failed: user not found",
    default_return="None",
    main_logic="if not self.verify_password(password, user.password_hash):\n        return None",
    result="Token(user.email, user.id)",
)

# 3) 测试桩模板
code = env.get_template("test_stub.py.j2").render(
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
```

## 渲染后校验

渲染结果必须先过语法检查再写入目标文件（对应 SKILL.md 步骤 4）：

```bash
python3 -m py_compile <渲染产物>.py          # python_fastapi_crud / fix_runtime / test_stub
python3 -m pytest --collect-only -q <测试桩>.py
npx tsc --noEmit --strict <渲染产物>.ts      # typescript_express_crud
```

## 与 scripts/code_generator.py 的关系

`code_generator.py` 为了零外部依赖（不 require jinja2），把 L1 模板以 Python 字典形式内联在 `PYTHON_FASTAPI_CRUD` / `FIX_RUNTIME_PYTHON` / `TEST_STUB_PYTHON` 中；本目录是同一批模板的可读版本，作用是：改模板前在这里核对结构、用上面的命令验证渲染结果，改完同步回脚本内的字典。两处变量名必须保持一致，改一处就要改另一处。
