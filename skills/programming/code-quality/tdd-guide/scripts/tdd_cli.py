#!/usr/bin/env python3
"""tdd_cli.py — tdd-guide 统一 CLI 入口

将 scripts/ 下的库模块（tdd_workflow / format_detector / test_generator /
fixture_generator / coverage_analyzer / metrics_calculator / framework_adapter /
output_formatter）暴露为统一命令行，供编排器、Agent 与人类直接调用。

用法:
  python tdd_cli.py workflow --requirement "实现用户登录"
  python tdd_cli.py detect --file src/service.py
  python tdd_cli.py gen-tests --requirements req.json --framework pytest
  python tdd_cli.py fixtures --mode boundary --type int --constraints '{"min":1,"max":10}'
  python tdd_cli.py coverage --report coverage.xml --threshold 80
  python tdd_cli.py metrics --source src/a.py --test tests/test_a.py
  python tdd_cli.py stub --framework pytest --language python --name test_login

退出码: 0 成功 / 2 输入错误（文件缺失、JSON 非法等）/ 1 内部错误
"""
import argparse
import json
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

FRAMEWORKS = ["jest", "vitest", "pytest", "junit", "mocha"]
ADAPTER_FRAMEWORKS = FRAMEWORKS + ["unittest", "testng", "jasmine"]
ADAPTER_LANGUAGES = ["typescript", "javascript", "python", "java"]
TEST_TYPES = ["unit", "integration", "e2e"]


def _read_text(path: str) -> str:
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"文件不存在: {p}")
    return p.read_text(encoding="utf-8")


def _read_json(path: str):
    raw = _read_text(path).strip()
    if not raw:
        raise ValueError(f"JSON 文件为空: {path}")
    return json.loads(raw)


def _require(value, message: str):
    if not value:
        raise ValueError(message)
    return value


def cmd_workflow(args) -> int:
    """TDD 工作流：启动红-绿-重构循环并给出阶段指引。"""
    from tdd_workflow import TDDWorkflow

    wf = TDDWorkflow()
    cycle = wf.start_cycle(_require(args.requirement.strip(), "--requirement 不能为空"))
    result = {"cycle": cycle, "guidance": wf.get_phase_guidance()}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_detect(args) -> int:
    """语言/框架/测试模式检测。"""
    from format_detector import FormatDetector

    if args.file:
        code = _read_text(args.file)
    else:
        code = _require((args.code or "").strip(), "必须提供 --file 或 --code")
    if not code.strip():
        raise ValueError("输入代码为空")

    det = FormatDetector()
    result = {
        "language": det.detect_language(code),
        "test_framework": det.detect_test_framework(code),
        "test_patterns": det.identify_test_patterns(code),
    }
    if args.file:
        result["suggested_test_file"] = det.suggest_test_file_name(
            args.file, result["test_framework"])
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_gen_tests(args) -> int:
    """从需求 JSON 生成测试用例与测试骨架。"""
    from test_generator import TestFramework, TestGenerator, TestType

    requirements = _read_json(args.requirements)
    gen = TestGenerator(TestFramework(args.framework), args.language)
    cases = gen.generate_from_requirements(requirements, TestType(args.type))

    result = {"framework": args.framework, "language": args.language,
              "test_cases": cases}
    if args.module:
        result["test_file"] = gen.generate_test_file(args.module, cases)
    if args.out:
        Path(args.out).write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"已写入: {args.out}", file=sys.stderr)
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_fixtures(args) -> int:
    """边界值 / 边缘场景 / mock 数据生成。"""
    from fixture_generator import FixtureGenerator

    gen = FixtureGenerator(seed=args.seed)
    if args.mode == "boundary":
        data = gen.generate_boundary_values(args.type, args.constraints)
    elif args.mode == "edge":
        data = gen.generate_edge_cases(
            _require(args.scenario and args.scenario.strip(), "--mode edge 需要 --scenario"),
            args.context)
    else:  # mock
        data = gen.generate_mock_data(_read_json(args.schema), count=args.count)
    print(json.dumps(data, ensure_ascii=False, indent=2, default=str))
    return 0


def cmd_coverage(args) -> int:
    """解析覆盖率报告并输出摘要 / 缺口 / 建议。"""
    from coverage_analyzer import CoverageAnalyzer
    from output_formatter import OutputFormatter

    content = _read_text(args.report)
    if not content.strip():
        raise ValueError(f"覆盖率报告为空: {args.report}")
    analyzer = CoverageAnalyzer()
    fmt = args.coverage_format or analyzer.detect_format(content)
    analyzer.parse_coverage_report(content, fmt)
    summary = analyzer.calculate_summary()

    if args.format == "text":
        out = OutputFormatter()
        print(out.format_coverage_summary(summary, detailed=True))
        print(out.format_recommendations(analyzer.generate_recommendations()))
    else:
        print(json.dumps({
            "detected_format": fmt,
            "summary": summary,
            "gaps": analyzer.identify_gaps(threshold=args.threshold),
            "recommendations": analyzer.generate_recommendations(),
        }, ensure_ascii=False, indent=2, default=str))
    return 0


def cmd_metrics(args) -> int:
    """源码/测试代码质量指标。"""
    from metrics_calculator import MetricsCalculator
    from output_formatter import OutputFormatter

    source = _read_text(args.source)
    test = _read_text(args.test)
    calc = MetricsCalculator()
    calc.calculate_all_metrics(source, test)

    if args.format == "text":
        print(calc.generate_metrics_summary())
    else:
        print(json.dumps(calc.metrics, ensure_ascii=False, indent=2, default=str))
    return 0


def cmd_stub(args) -> int:
    """按框架渲染测试骨架（imports + 测试函数 + 可选 suite 包装）。"""
    from framework_adapter import Framework, FrameworkAdapter, Language

    adapter = FrameworkAdapter(Framework(args.framework), Language(args.language))
    body = "\n".join(args.body) if args.body else ""
    function = adapter.generate_test_function(args.name, body)
    code = adapter.generate_imports() + "\n\n" + function
    if args.suite:
        code = adapter.generate_test_suite_wrapper(args.suite, code)
    print(code)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="tdd-guide 统一 CLI 入口（覆盖全部 8 个库模块）")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("workflow", help="启动 TDD 循环并获取阶段指引")
    p.add_argument("--requirement", required=True, help="需求描述")
    p.set_defaults(func=cmd_workflow)

    p = sub.add_parser("detect", help="检测语言 / 测试框架 / 测试模式")
    p.add_argument("--file", help="源码文件路径")
    p.add_argument("--code", help="内联源码文本（与 --file 二选一）")
    p.set_defaults(func=cmd_detect)

    p = sub.add_parser("gen-tests", help="从需求 JSON 生成测试用例")
    p.add_argument("--requirements", required=True, help="需求 JSON 文件")
    p.add_argument("--framework", choices=FRAMEWORKS, default="pytest")
    p.add_argument("--language", default="python")
    p.add_argument("--type", choices=TEST_TYPES, default="unit")
    p.add_argument("--module", help="同时生成测试文件骨架的模块名")
    p.add_argument("--out", help="写入文件（缺省打印 stdout）")
    p.set_defaults(func=cmd_gen_tests)

    p = sub.add_parser("fixtures", help="边界值 / 边缘场景 / mock 数据")
    p.add_argument("--mode", choices=["boundary", "edge", "mock"], required=True)
    p.add_argument("--type", default="int", help="boundary 模式的数据类型")
    p.add_argument("--constraints", help="boundary 约束 JSON（内联）")
    p.add_argument("--scenario", help="edge 场景描述")
    p.add_argument("--context", help="edge 上下文 JSON（内联）")
    p.add_argument("--schema", help="mock 模式的 schema JSON 文件")
    p.add_argument("--count", type=int, default=1, help="mock 生成条数")
    p.add_argument("--seed", type=int, help="随机种子")
    p.set_defaults(func=cmd_fixtures)

    p = sub.add_parser("coverage", help="解析覆盖率报告（lcov/json/xml）")
    p.add_argument("--report", required=True, help="覆盖率报告文件")
    p.add_argument("--threshold", type=float, default=80.0, help="缺口判定阈值")
    p.add_argument("--coverage-format", help="强制指定报告格式（缺省自动检测）")
    p.add_argument("--format", choices=["json", "text"], default="json")
    p.set_defaults(func=cmd_coverage)

    p = sub.add_parser("metrics", help="源码/测试质量指标")
    p.add_argument("--source", required=True, help="源码文件")
    p.add_argument("--test", required=True, help="测试文件")
    p.add_argument("--format", choices=["json", "text"], default="json")
    p.set_defaults(func=cmd_metrics)

    p = sub.add_parser("stub", help="渲染测试骨架代码")
    p.add_argument("--framework", choices=ADAPTER_FRAMEWORKS, default="pytest")
    p.add_argument("--language", choices=ADAPTER_LANGUAGES, default="python")
    p.add_argument("--name", required=True, help="测试函数名")
    p.add_argument("--body", nargs="*", help="测试函数体（可选多段）")
    p.add_argument("--suite", help="可选 suite 包装名")
    p.set_defaults(func=cmd_stub)

    args = parser.parse_args()
    try:
        if args.func.__name__ == "cmd_fixtures" and getattr(args, "constraints", None):
            args.constraints = json.loads(args.constraints)
        if args.func.__name__ == "cmd_fixtures" and getattr(args, "context", None):
            args.context = json.loads(args.context)
        return args.func(args)
    except (FileNotFoundError, ValueError, json.JSONDecodeError, KeyError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    except Exception as e:  # noqa: BLE001 — CLI 边界统一兜底
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
