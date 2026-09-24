# Jinja2 Code Template Library

This directory holds the L1 code templates for code-generator. The "code pattern template library" section of SKILL.md references the files here.

## Purpose and required variables

| Template file | Triggering intent | Rendered output | Required variables |
|---|---|---|---|
| `python_fastapi_crud.py.j2` | `implement` + `python/fastapi` | Single-file FastAPI CRUD (pydantic models + service layer + Router + app) | `target`, `Model`, `Service`, `tech_stack`, `id_param` |
| `typescript_express_crud.ts.j2` | `implement` + `node/express` | Single-file Express CRUD (interface types + service layer + Router) | `target`, `Model`, `Service`, `tech_stack`, `id_param` |
| `fix_runtime.py.j2` | `fix` / `fix.runtime` | A fixed function with root-cause comments | `module`, `target`, `function_name`, `params`, `return_type`, `root_cause`, `fix_description`, `original_problem`, `guard_condition`, `guard_warning`, `default_return`, `main_logic`, `result` |
| `test_stub.py.j2` | `test` / `test.coverage` | pytest test stub (happy path / edge case / error handling) | `module_path`, `ClassName`, `test_name`, `given`, `when`, `then`, `constructor_params`, `method_name`, `method_params`, `expected`, `Exception`, `edge_params`, `edge_case`, `error_scenario` |

### Where the variables come from

The first five variables are produced by `scripts/code_generator.py:extract_context()`, with the value conventions as follows (`target` comes from the plan's `slots[name=target]`):

| Variable | Value | Example (target=product) |
|---|---|---|
| `target` | The raw target slot value | `product` |
| `Model` | `target.capitalize()` | `Product` |
| `Service` | `target.capitalize() + "Service"` | `ProductService` |
| `tech_stack` | From slots or `project_analyzer` detection | `python/fastapi` |
| `id_param` | `target` with trailing "s" removed + `_id` | `product_id` (when target=users, `user_id`) |

The remaining variables for `fix_runtime.py.j2` / `test_stub.py.j2` are not in `extract_context()`'s default return; the caller must fill them in per the table above before rendering—the variable names must exactly match the placeholders in `code_generator.py`'s `FIX_RUNTIME_PYTHON` / `TEST_STUB_PYTHON`; do not invent new names.

## Rendering example

The renderer uses `StrictUndefined`: a missing variable errors out directly, avoiding silently half-rendered code.

```python
# render_example.py —— modify the context as needed before running
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, StrictUndefined

env = Environment(
    loader=FileSystemLoader("references/templates"),
    undefined=StrictUndefined,
    keep_trailing_newline=True,
)

# 1) FastAPI CRUD; the TS template uses the same variables, swap tech_stack to node/express
ctx = {
    "target": "product",
    "Model": "Product",
    "Service": "ProductService",
    "tech_stack": "python/fastapi",
    "id_param": "product_id",
}
code = env.get_template("python_fastapi_crud.py.j2").render(**ctx)
Path("src/product/impl.py").write_text(code, encoding="utf-8")

# 2) Fix template
code = env.get_template("fix_runtime.py.j2").render(
    target="auth",
    module="service",
    function_name="login",
    params="self, username: str, password: str",
    return_type="Optional[Token]",
    root_cause=".email accessed directly when user is None",
    fix_description="add a null guard clause before login",
    original_problem="return Token(user.email, user.id) raised AttributeError",
    guard_condition="user is None",
    guard_warning="Login failed: user not found",
    default_return="None",
    main_logic="if not self.verify_password(password, user.password_hash):\n        return None",
    result="Token(user.email, user.id)",
)

# 3) Test stub template
code = env.get_template("test_stub.py.j2").render(
    module_path="src.product.service",
    ClassName="ProductService",
    test_name="find_by_id",
    given="the id does not exist in the repository",
    when="call find_by_id(999)",
    then="return None",
    constructor_params="",
    method_name="find_by_id",
    method_params="999",
    expected="None",
    Exception="TypeError",
    edge_params="",
    edge_case="missing required argument",
    error_scenario="invalid input should not raise",
)
```

## Validation after rendering

The rendered result must pass a syntax check before being written to the target file (corresponding to SKILL.md step 4):

```bash
python3 -m py_compile <rendered output>.py          # python_fastapi_crud / fix_runtime / test_stub
python3 -m pytest --collect-only -q <test stub>.py
npx tsc --noEmit --strict <rendered output>.ts      # typescript_express_crud
```

## Relationship to scripts/code_generator.py

To keep zero external dependencies (without requiring jinja2), `code_generator.py` inlines the L1 templates as Python dicts in `PYTHON_FASTAPI_CRUD` / `FIX_RUNTIME_PYTHON` / `TEST_STUB_PYTHON`; this directory is the readable version of the same templates, for the purpose of: checking the structure here before editing a template, and verifying the render output with the commands above, then syncing changes back to the dicts in the script. The variable names in both places must stay consistent; changing one means changing the other.
