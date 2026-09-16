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

覆盖 Jest、Pytest、JUnit 与 Vitest 的测试驱动开发：生成测试、分析覆盖率缺口，用一个 CLI 驱动红-绿-重构循环。

---

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 源码 / 需求 | 是 | 源码文件、`req.json`，或一条功能需求描述。 |
| 目标框架 | 否 | `jest` \| `pytest` \| `junit` \| `vitest` \| `mocha`（可自动检测）。 |
| 覆盖率报告 | 否 | LCOV / JSON / XML 路径，缺口分析用。 |
| 覆盖率阈值 | 否 | 百分比（默认 `80`）。 |
| 阶段（工作流） | 否 | `red` \| `green` \| `refactor`。 |

必需输入缺失时，只问一次：

> 请提供：① 待测源码或需求描述；② 目标测试框架（Jest/Pytest/JUnit/Vitest/Mocha）。
> 其余采用默认值：coverage-threshold=80%、phase 由工作流自动推进。

## 前置自检

```bash
# 1. 入口脚本存在？
test -f scripts/tdd_cli.py || { echo "ERROR: scripts/tdd_cli.py missing"; exit 1; }
# 2. Python 可用？
command -v python3 >/dev/null 2>&1 || { echo "ERROR: python3 not found"; exit 1; }
# 3. 若提供了覆盖率报告，确认文件存在：
test -z "$REPORT" || test -f "$REPORT" || { echo "ERROR: report $REPORT not found"; exit 1; }
```

## 统一 CLI（`scripts/tdd_cli.py`）

所有库模块都经一个入口调用（退出码：`0` = 正常，`2` = 输入错误，`1` = 内部错误）：

```bash
python scripts/tdd_cli.py workflow --requirement "实现用户登录"            # 红-绿-重构循环 + 阶段指引
python scripts/tdd_cli.py detect --file src/service.py                  # 语言/框架/测试模式检测
python scripts/tdd_cli.py gen-tests --requirements req.json --framework pytest   # 需求 → 测试用例
python scripts/tdd_cli.py fixtures --mode boundary --type int           # 边界值/边缘场景/mock 数据
python scripts/tdd_cli.py coverage --report coverage.xml --threshold 80 # 覆盖率摘要/缺口/建议
python scripts/tdd_cli.py metrics --source src/a.py --test tests/test_a.py      # 质量 metrics
python scripts/tdd_cli.py stub --framework pytest --name test_login     # 测试骨架渲染
```

`format_detector` / `framework_adapter` / `output_formatter` 经 `detect` / `stub` / `coverage --format text` 间接暴露；也可作为库 `import`（无独立 `__main__`，不要直接执行）。

## 工作流

### 步骤 1：检测语言与框架

```bash
python scripts/tdd_cli.py detect --file src/service.py
```

预期：输出检测到的语言、测试框架与既有测试模式。若失败：扩展名不受支持 → 显式指定 `--framework`。

### 步骤 2：从代码 / 需求生成测试

```bash
# 从源码文件生成
python scripts/test_generator.py --input math_utils.py --framework pytest
# 经 CLI 从需求 JSON 生成
python scripts/tdd_cli.py gen-tests --requirements req.json --framework pytest
```

预期：产出测试骨架，覆盖正常路径、错误场景、边界场景。若失败：输出为空 → 检查 `--framework` 取值，确认输入可解析。

### 步骤 3：分析覆盖率缺口

```bash
python scripts/coverage_analyzer.py --report lcov.info --threshold 80
# 或经 CLI
python scripts/tdd_cli.py coverage --report coverage.xml --threshold 80
```

预期：按优先级输出缺口，标注 P0（关键，如未覆盖的错误路径）/ P1（核心分支）/ P2（工具函数），并给出达到阈值的建议。若失败：报告格式不受支持 → 先转成 LCOV/JSON/XML。

### 步骤 4：驱动红-绿-重构

```bash
python scripts/tdd_cli.py workflow --requirement "<feature>"   # 启动循环，获取阶段指引
python scripts/tdd_workflow.py --phase red   --test test_auth.py   # 写失败的测试
python scripts/tdd_workflow.py --phase green --test test_auth.py   # 最小化实现
python scripts/tdd_cli.py metrics --source src/a.py --test tests/test_a.py  # 验证
```

预期：每轮循环结束时目标测试全部通过；`metrics` 无回归。若失败：最小实现后测试仍红 → 问题在实现而不在测试；回头重审需求。

## 参数速查表

| 子命令 | 关键参数 | 取值 |
|--------|----------|------|
| `workflow` | `--requirement` | 功能描述字符串 |
| `detect` | `--file` | 源码文件路径 |
| `gen-tests` | `--requirements` / `--framework` | 需求 JSON / jest\|pytest\|junit\|vitest\|mocha |
| `fixtures` | `--mode` / `--type` | boundary\|edge\|mock / int\|float\|str |
| `coverage` | `--report` / `--threshold` | LCOV\|JSON\|XML / 百分比 |
| `metrics` | `--source` / `--test` | 源码 / 测试文件路径 |
| `stub` | `--framework` / `--name` | 框架 / 测试名 |

## 关键工具

| 工具 | 用途 | 用法 |
|------|------|------|
| `test_generator.py` | 从代码/需求生成测试用例 | `python scripts/test_generator.py --input source.py --framework pytest` |
| `coverage_analyzer.py` | 解析并分析覆盖率报告 | `python scripts/coverage_analyzer.py --report lcov.info --threshold 80` |
| `tdd_workflow.py` | 引导红-绿-重构循环 | `python scripts/tdd_workflow.py --phase red --test test_auth.py` |
| `fixture_generator.py` | 生成测试数据与 mock | `python scripts/fixture_generator.py --entity User --count 5` |

其余脚本：`framework_adapter.py`（框架间转换）、`metrics_calculator.py`（质量指标）、`format_detector.py`（检测语言/框架）、`output_formatter.py`（CLI/桌面/CI 输出）。

## 有界自治规则

**停下来问，当：** 验收标准含糊；边界值缺失且需要领域知识；测试数量将超过 50（先给摘要，问优先覆盖哪些区域）；外部依赖无文档；安全敏感逻辑（认证、授权、加密、支付）需要签字确认。

**继续自治，当：** 规格清晰且验收标准带编号；简单 CRUD；API 契约明确（OpenAPI/带类型接口）；纯函数；有既有测试模式可循。

## 红-绿-重构示例

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

### Go — 表驱动

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

## 失败处置表

| 症状 | 原因 | 处置 |
|------|------|------|
| CLI 退出码 `exit 2` | 输入参数错误 | 按参数速查表核对必需参数 |
| 生成的测试为空 | `--framework` 不受支持 | 从 5 个受支持框架中选一个 |
| 覆盖率工具读报告报错 | 格式不受支持 | 先转成 LCOV/JSON/XML |
| 最小实现后测试仍红 | 需求不清晰 | 停下来问用户（有界自治规则） |

## 交付标准

成功 = 生成的测试可编译且覆盖正常/错误/边界路径，且覆盖率报告达到阈值。

- 保存位置：生成的测试存 `tests/`；报告存 `coverage.<fmt>`。
- 核验：跑项目的测试运行器，确认达到阈值（通常 ≥80%）；P0 项优先补测试。
- 测试是脚手架，复杂逻辑需人工复审——本技能不 push、不 commit。

## 参考

- `references/framework-guide.md` — 选适配器模式，或在 Jest/Pytest/JUnit/Vitest/Mocha 之间转换时读。
- `references/tdd-best-practices.md` — 属性测试与变异测试指南、更深的 TDD 模式。
- `references/ci-integration.md` — 把 CLI 接入 CI（覆盖率门禁、JUnit XML 报告）时读。

样例夹具：`assets/sample_coverage_report.lcov`、`assets/sample_input_python.json`、`assets/sample_input_typescript.json`、`assets/expected_output.json`。
