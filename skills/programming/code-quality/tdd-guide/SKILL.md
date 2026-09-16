---
name: tdd-guide
description: >-
  Test-driven development skill for writing unit tests, generating test fixtures
  and mocks, analyzing coverage gaps, and guiding red-green-refactor workflows
  across Jest, Pytest, JUnit, Vitest, and Mocha. Use when the user asks to write
  tests, improve test coverage, practice TDD, generate mocks or stubs, run the
  red-green-refactor cycle, or mentions testing frameworks like Jest, pytest, or
  JUnit. 当用户要求 写测试 / TDD / 先写测试再写实现 / 提升测试覆盖率 / 生成 mock
  时使用。 Do NOT use for skipping the red-green-refactor cycle.
license: Apache-2.0
compatibility: Pure prompt-based; the bundled scripts require Python 3.10+. May read project structure via Bash.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: code-quality
  pattern: workflow
  tier: powerful
  verified-date: "2026-09-09"
---

# TDD Guide

Test-driven development across Jest, Pytest, JUnit, and Vitest: generate tests,
analyze coverage gaps, and drive red-green-refactor cycles through one CLI.

---

## Inputs

| Input | Required | Notes |
|-------|----------|-------|
| Source / requirement | Yes | A source file, a `req.json`, or a feature requirement string. |
| Target framework | No | `jest` \| `pytest` \| `junit` \| `vitest` \| `mocha` (auto-detected). |
| Coverage report | No | LCOV / JSON / XML path for gap analysis. |
| Coverage threshold | No | Percent (default `80`). |
| Phase (workflow) | No | `red` \| `green` \| `refactor`. |

If a required input is missing, ask once:

> 请提供：① 待测源码或需求描述；② 目标测试框架（Jest/Pytest/JUnit/Vitest/Mocha）。
> 其余采用默认值：coverage-threshold=80%、phase 由工作流自动推进。

## Pre-flight Self-check

```bash
# 1. Entry-point script present?
test -f scripts/tdd_cli.py || { echo "ERROR: scripts/tdd_cli.py missing"; exit 1; }
# 2. Python available?
command -v python3 >/dev/null 2>&1 || { echo "ERROR: python3 not found"; exit 1; }
# 3. If a coverage report was supplied, it exists:
test -z "$REPORT" || test -f "$REPORT" || { echo "ERROR: report $REPORT not found"; exit 1; }
```

## Unified CLI (`scripts/tdd_cli.py`)

All library modules are reachable through one entry point (exit codes:
`0` = ok, `2` = bad input, `1` = internal error):

```bash
python scripts/tdd_cli.py workflow --requirement "实现用户登录"            # 红-绿-重构循环 + 阶段指引
python scripts/tdd_cli.py detect --file src/service.py                  # 语言/框架/测试模式检测
python scripts/tdd_cli.py gen-tests --requirements req.json --framework pytest   # 需求 → 测试用例
python scripts/tdd_cli.py fixtures --mode boundary --type int           # 边界值/边缘场景/mock 数据
python scripts/tdd_cli.py coverage --report coverage.xml --threshold 80 # 覆盖率摘要/缺口/建议
python scripts/tdd_cli.py metrics --source src/a.py --test tests/test_a.py      # 质量 metrics
python scripts/tdd_cli.py stub --framework pytest --name test_login     # 测试骨架渲染
```

`format_detector` / `framework_adapter` / `output_formatter` are exposed
indirectly via `detect` / `stub` / `coverage --format text`; they may also be
`import`ed as libraries (no standalone `__main__`, do not execute directly).

## Workflow

### Step 1: Detect language & framework

```bash
python scripts/tdd_cli.py detect --file src/service.py
```

Expected: prints detected language, test framework, and existing test pattern.
If failed: unsupported extension → specify `--framework` explicitly.

### Step 2: Generate tests from code / requirement

```bash
# From a source file
python scripts/test_generator.py --input math_utils.py --framework pytest
# From a requirement JSON via the CLI
python scripts/tdd_cli.py gen-tests --requirements req.json --framework pytest
```

Expected: emitted test stubs covering happy path, error cases, edge cases.
If failed: empty output → check `--framework` value and that the input parses.

### Step 3: Analyze coverage gaps

```bash
python scripts/coverage_analyzer.py --report lcov.info --threshold 80
# or via the CLI
python scripts/tdd_cli.py coverage --report coverage.xml --threshold 80
```

Expected: prioritized gaps tagged P0 (critical, e.g. uncovered error paths) /
P1 (core-branch) / P2 (utility), with a recommendation to reach the threshold.
If failed: unsupported report format → convert to LCOV/JSON/XML first.

### Step 4: Drive red-green-refactor

```bash
python scripts/tdd_cli.py workflow --requirement "<feature>"   # start cycle, get phase guidance
python scripts/tdd_workflow.py --phase red   --test test_auth.py   # write failing test
python scripts/tdd_workflow.py --phase green --test test_auth.py   # implement minimally
python scripts/tdd_cli.py metrics --source src/a.py --test tests/test_a.py  # verify
```

Expected: every cycle ends with all targeted tests passing; `metrics` shows no
regression. If failed: a test stays red after the minimal implementation → the
implementation, not the test, is at fault; revisit the requirement.

## Parameter Cheat-sheet

| Subcommand | Key flag | Values |
|------------|----------|--------|
| `workflow` | `--requirement` | feature description string |
| `detect` | `--file` | source file path |
| `gen-tests` | `--requirements` / `--framework` | req JSON / jest\|pytest\|junit\|vitest\|mocha |
| `fixtures` | `--mode` / `--type` | boundary\|edge\|mock / int\|float\|str |
| `coverage` | `--report` / `--threshold` | LCOV\|JSON\|XML / percent |
| `metrics` | `--source` / `--test` | source / test paths |
| `stub` | `--framework` / `--name` | framework / test name |

## Key Tools

| Tool | Purpose | Usage |
|------|---------|-------|
| `test_generator.py` | Generate test cases from code/requirements | `python scripts/test_generator.py --input source.py --framework pytest` |
| `coverage_analyzer.py` | Parse and analyze coverage reports | `python scripts/coverage_analyzer.py --report lcov.info --threshold 80` |
| `tdd_workflow.py` | Guide red-green-refactor cycles | `python scripts/tdd_workflow.py --phase red --test test_auth.py` |
| `fixture_generator.py` | Generate test data and mocks | `python scripts/fixture_generator.py --entity User --count 5` |

Additional scripts: `framework_adapter.py` (convert between frameworks),
`metrics_calculator.py` (quality metrics), `format_detector.py` (detect
language/framework), `output_formatter.py` (CLI/desktop/CI output).

## Bounded Autonomy Rules

**Stop and ask when:** ambiguous acceptance criteria; missing boundary values
that need domain knowledge; test count would exceed 50 (present a summary and
ask which areas to prioritize); external dependencies are undocumented;
security-sensitive logic (auth, authz, encryption, payments) needs sign-off.

**Continue autonomously when:** a clear spec with numbered acceptance criteria;
straightforward CRUD; well-defined API contracts (OpenAPI/typed interfaces);
pure functions; existing test patterns to follow.

## Red-Green-Refactor Examples

### TypeScript / Jest

```typescript
describe("Cart", () => {
  describe("addItem", () => {
    it("should add a new item to an empty cart", () => {
      const cart = new Cart();
      cart.addItem({ id: "sku-1", name: "Widget", price: 9.99, qty: 1 });
      expect(cart.items).toHaveLength(1);
      expect(cart.items[0].id).toBe("sku-1");
    });
    it("should throw when quantity is zero or negative", () => {
      const cart = new Cart();
      expect(() => cart.addItem({ id: "sku-1", name: "Widget", price: 9.99, qty: 0 }))
        .toThrow("Quantity must be positive");
    });
  });
});
```

### Python / Pytest

```python
import pytest
from app.pricing import calculate_discount

@pytest.mark.parametrize("subtotal, expected_discount", [
    (50.0, 0.0), (100.0, 5.0), (250.0, 25.0), (500.0, 75.0),
])
def test_calculate_discount(subtotal, expected_discount):
    assert calculate_discount(subtotal) == pytest.approx(expected_discount)
```

### Go — Table-Driven

```go
func TestApplyDiscount(t *testing.T) {
    tests := []struct {
        name     string
        subtotal float64
        want     float64
    }{
        {"no discount below threshold", 50.0, 0.0},
        {"5 percent tier", 100.0, 5.0},
        {"15 percent tier", 500.0, 75.0},
        {"zero subtotal", 0.0, 0.0},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            if got := ApplyDiscount(tt.subtotal); got != tt.want {
                t.Errorf("ApplyDiscount(%v) = %v, want %v", tt.subtotal, got, tt.want)
            }
        })
    }
}
```

## Failure Handling

| Symptom | Cause | Action |
|---------|-------|--------|
| `exit 2` from CLI | bad input argument | re-check required flags per cheat-sheet |
| Empty generated tests | unsupported `--framework` | use one of the 5 supported frameworks |
| Coverage tool errors on report | unsupported format | convert to LCOV/JSON/XML |
| Test stays red after minimal impl | requirement unclear | stop and ask the user (bounded-autonomy rule) |

## Delivery Standard

Success = generated tests that compile and cover happy/error/edge paths, plus a
coverage report meeting the threshold.

- Save location: `tests/` for generated tests; `coverage.<fmt>` for reports.
- Verify: run the project's test runner and confirm the threshold is met
  (typically ≥80%); for P0 items generate tests first.
- Tests are scaffolding requiring human review for complex logic — this skill
  does not push or commit.

## References

- `references/framework-guide.md` — read when choosing adapter patterns or
  converting between Jest/Pytest/JUnit/Vitest/Mocha.
- `references/tdd-best-practices.md` — read for property-based and mutation
  testing guidance and deeper TDD patterns.
- `references/ci-integration.md` — read when wiring the CLI into CI (coverage
  gates, JUnit XML reporting).

Sample fixtures: `assets/sample_coverage_report.lcov`,
`assets/sample_input_python.json`, `assets/sample_input_typescript.json`,
`assets/expected_output.json`.
