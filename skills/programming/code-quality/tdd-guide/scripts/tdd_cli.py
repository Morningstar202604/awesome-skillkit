#!/usr/bin/env python3
"""tdd_cli.py -- unified CLI entry point for tdd-guide.

Exposes the library modules under scripts/ (tdd_workflow / format_detector /
test_generator / fixture_generator / coverage_analyzer / metrics_calculator /
framework_adapter / output_formatter) as a single command line, callable directly
by orchestrators, agents, and humans.

Usage:
  python tdd_cli.py workflow --requirement "implement user login"
  python tdd_cli.py detect --file src/service.py
  python tdd_cli.py gen-tests --requirements req.json --framework pytest
  python tdd_cli.py fixtures --mode boundary --type int --constraints '{"min":1,"max":10}'
  python tdd_cli.py coverage --report coverage.xml --threshold 80
  python tdd_cli.py metrics --source src/a.py --test tests/test_a.py
  python tdd_cli.py stub --framework pytest --language python --name test_login

Exit codes: 0 success / 2 input error (missing file, invalid JSON, etc.) / 1 internal error
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
        raise FileNotFoundError(f"File not found: {p}")
    return p.read_text(encoding="utf-8")


def _read_json(path: str):
    raw = _read_text(path).strip()
    if not raw:
        raise ValueError(f"JSON file is empty: {path}")
    return json.loads(raw)


def _require(value, message: str):
    if not value:
        raise ValueError(message)
    return value


def cmd_workflow(args) -> int:
    """TDD workflow: start the red-green-refactor loop and provide phase guidance."""
    from tdd_workflow import TDDWorkflow

    wf = TDDWorkflow()
    cycle = wf.start_cycle(_require(args.requirement.strip(), "--requirement must not be empty"))
    result = {"cycle": cycle, "guidance": wf.get_phase_guidance()}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_detect(args) -> int:
    """Detect language / framework / test pattern."""
    from format_detector import FormatDetector

    if args.file:
        code = _read_text(args.file)
    else:
        code = _require((args.code or "").strip(), "must provide either --file or --code")
    if not code.strip():
        raise ValueError("input code is empty")

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
    """Generate test cases and a test scaffold from a requirements JSON."""
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
        print(f"Written: {args.out}", file=sys.stderr)
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_fixtures(args) -> int:
    """Boundary value / edge case / mock data generation."""
    from fixture_generator import FixtureGenerator

    gen = FixtureGenerator(seed=args.seed)
    if args.mode == "boundary":
        data = gen.generate_boundary_values(args.type, args.constraints)
    elif args.mode == "edge":
        data = gen.generate_edge_cases(
            _require(args.scenario and args.scenario.strip(), "--mode edge requires --scenario"),
            args.context)
    else:  # mock
        data = gen.generate_mock_data(_read_json(args.schema), count=args.count)
    print(json.dumps(data, ensure_ascii=False, indent=2, default=str))
    return 0


def cmd_coverage(args) -> int:
    """Parse a coverage report and output summary / gaps / recommendations."""
    from coverage_analyzer import CoverageAnalyzer
    from output_formatter import OutputFormatter

    content = _read_text(args.report)
    if not content.strip():
        raise ValueError(f"Coverage report is empty: {args.report}")
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
    """Source/test code quality metrics."""
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
    """Render a test scaffold for the framework (imports + test function + optional suite wrapper)."""
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
        description="tdd-guide unified CLI entry point (covers all 8 library modules)")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("workflow", help="start the TDD loop and get phase guidance")
    p.add_argument("--requirement", required=True, help="requirement description")
    p.set_defaults(func=cmd_workflow)

    p = sub.add_parser("detect", help="detect language / test framework / test pattern")
    p.add_argument("--file", help="source file path")
    p.add_argument("--code", help="inline source text (mutually exclusive with --file)")
    p.set_defaults(func=cmd_detect)

    p = sub.add_parser("gen-tests", help="generate test cases from a requirements JSON")
    p.add_argument("--requirements", required=True, help="requirements JSON file")
    p.add_argument("--framework", choices=FRAMEWORKS, default="pytest")
    p.add_argument("--language", default="python")
    p.add_argument("--type", choices=TEST_TYPES, default="unit")
    p.add_argument("--module", help="module name for which to also generate a test file scaffold")
    p.add_argument("--out", help="write to file (default prints to stdout)")
    p.set_defaults(func=cmd_gen_tests)

    p = sub.add_parser("fixtures", help="boundary values / edge cases / mock data")
    p.add_argument("--mode", choices=["boundary", "edge", "mock"], required=True)
    p.add_argument("--type", default="int", help="data type in boundary mode")
    p.add_argument("--constraints", help="boundary constraints JSON (inline)")
    p.add_argument("--scenario", help="edge scenario description")
    p.add_argument("--context", help="edge context JSON (inline)")
    p.add_argument("--schema", help="schema JSON file for mock mode")
    p.add_argument("--count", type=int, default=1, help="number of mock items to generate")
    p.add_argument("--seed", type=int, help="random seed")
    p.set_defaults(func=cmd_fixtures)

    p = sub.add_parser("coverage", help="parse a coverage report (lcov/json/xml)")
    p.add_argument("--report", required=True, help="coverage report file")
    p.add_argument("--threshold", type=float, default=80.0, help="gap threshold")
    p.add_argument("--coverage-format", help="force the report format (default auto-detect)")
    p.add_argument("--format", choices=["json", "text"], default="json")
    p.set_defaults(func=cmd_coverage)

    p = sub.add_parser("metrics", help="source/test quality metrics")
    p.add_argument("--source", required=True, help="source file")
    p.add_argument("--test", required=True, help="test file")
    p.add_argument("--format", choices=["json", "text"], default="json")
    p.set_defaults(func=cmd_metrics)

    p = sub.add_parser("stub", help="render test scaffold code")
    p.add_argument("--framework", choices=ADAPTER_FRAMEWORKS, default="pytest")
    p.add_argument("--language", choices=ADAPTER_LANGUAGES, default="python")
    p.add_argument("--name", required=True, help="test function name")
    p.add_argument("--body", nargs="*", help="test function body (multiple segments allowed)")
    p.add_argument("--suite", help="optional suite wrapper name")
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
    except Exception as e:  # noqa: BLE001 -- unified catch-all at the CLI boundary
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
