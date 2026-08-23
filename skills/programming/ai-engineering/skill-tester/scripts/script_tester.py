#!/usr/bin/env python3
"""
Script Tester - syntax, import, and runtime testing for a skill's Python scripts.

For each scripts/*.py in the target skill:
  * AST-based syntax validation
  * Import analysis (flags non-stdlib dependencies)
  * Controlled `--help` execution with timeout protection

Usage:
    python script_tester.py <skill_path> [--timeout 30] [--json]

Exit codes: 0 = all scripts passed, 1 = at least one failure.

Stdlib only. Python 3.8+.
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

try:  # 3.10+
    STDLIB_MODULES = frozenset(sys.stdlib_module_names)
except AttributeError:  # pragma: no cover - fallback for older runtimes
    import sysconfig
    _exts = (".py", ".pyd", ".so")
    STDLIB_MODULES = frozenset(
        p.stem.split(".")[0]
        for p in sysconfig.get_paths()["stdlib"] and Path(sysconfig.get_paths()["stdlib"]).glob("*")
        if p.suffix in _exts or p.is_dir()
    )


class ScriptTester:
    """Test all Python scripts inside one skill directory."""

    def __init__(self, skill_path: Path, timeout: int = 30, verbose: bool = False):
        self.skill_path = Path(skill_path)
        self.timeout = timeout
        self.verbose = verbose
        self.results: List[Dict[str, Any]] = []

    # ------------------------------------------------------------
    # static analysis
    # ------------------------------------------------------------

    @staticmethod
    def check_syntax(path: Path) -> Optional[str]:
        """Return None when syntax is valid, else an error message."""
        import ast
        try:
            source = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            return f"unreadable: {exc}"
        try:
            ast.parse(source)
        except SyntaxError as exc:
            return f"syntax error: {exc.msg} (line {exc.lineno})"
        return None

    @staticmethod
    def analyze_imports(path: Path) -> List[str]:
        """Return top-level modules imported that are NOT stdlib."""
        import ast
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        except (OSError, SyntaxError):
            return []
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                imported.add(node.module.split(".")[0])
        local_siblings = {p.stem for p in path.parent.glob("*.py")}
        external = sorted(m for m in imported
                          if m not in STDLIB_MODULES and m not in ("app",)
                          and m not in local_siblings)
        return external

    # ------------------------------------------------------------
    # runtime checks
    # ------------------------------------------------------------

    def run_help(self, script: Path) -> Dict[str, Any]:
        started = time.time()
        try:
            proc = subprocess.run(
                [sys.executable, str(Path(script).resolve()), "--help"],
                capture_output=True, text=True, timeout=self.timeout,
                cwd=str(script.parent),
            )
        except subprocess.TimeoutExpired:
            return {"passed": False,
                    "message": f"--help timed out after {self.timeout}s"}
        except OSError as exc:
            return {"passed": False, "message": f"failed to launch: {exc}"}
        elapsed = round(time.time() - started, 2)
        ok = proc.returncode == 0 and len((proc.stdout or "").strip()) > 20
        msg = (f"--help OK ({elapsed}s)"
               if ok else
               f"--help exit={proc.returncode} stdout_len={len(proc.stdout or '')}")
        return {"passed": ok, "message": msg}

    # ------------------------------------------------------------
    # entry point
    # ------------------------------------------------------------

    def test_all(self) -> Dict[str, Any]:
        scripts_dir = self.skill_path / "scripts"
        py_files = sorted(scripts_dir.glob("*.py")) if scripts_dir.is_dir() else []

        if not py_files:
            self.results.append({
                "script": None,
                "checks": {
                    "scripts_found": {"passed": False,
                                      "message": "no scripts/*.py found"},
                },
                "passed": False,
            })

        for py in py_files:
            checks: Dict[str, Any] = {}

            syntax_error = self.check_syntax(py)
            checks["syntax"] = {
                "passed": syntax_error is None,
                "message": "valid Python syntax" if syntax_error is None else syntax_error,
            }

            external = self.analyze_imports(py)
            checks["imports"] = {
                "passed": len(external) == 0,
                "message": ("stdlib-only imports"
                            if not external else
                            f"external dependencies: {', '.join(external)}"),
            }
            # external deps are advisory, not fatal (documented deps allowed)
            if external:
                checks["imports"]["advisory"] = True

            help_result = self.run_help(py)
            checks["help_runtime"] = help_result

            passed = all(c["passed"] for c in checks.values())
            self.results.append({"script": py.name, "checks": checks, "passed": passed})
            if self.verbose:
                status = "PASS" if passed else "FAIL"
                print(f"  [{status}] {py.name}")

        total = len(self.results)
        passed_count = sum(1 for r in self.results if r["passed"])
        return {
            "skill_path": str(self.skill_path).replace("\\\\", "/"),
            "total_scripts": total,
            "passed_scripts": passed_count,
            "all_passed": passed_count == total,
            "results": self.results,
        }


def print_report(report: Dict[str, Any]) -> None:
    print("=== SCRIPT TESTER ===")
    print(f"Skill: {report['skill_path']}")
    print(f"Scripts: {report['passed_scripts']}/{report['total_scripts']} passed")
    print()
    for result in report["results"]:
        name = result.get("script") or "(none)"
        mark = "+" if result["passed"] else "x"
        print(f"  [{mark}] {name}")
        for check_name, check in result["checks"].items():
            symbol = "+" if check["passed"] else "x"
            advisory = " (advisory)" if check.get("advisory") else ""
            print(f"      [{symbol}] {check['message']}{advisory} ({check_name})")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Test a skill's Python scripts: syntax, imports, runtime."
    )
    parser.add_argument("skill_path", help="Path to the skill directory")
    parser.add_argument("--timeout", type=int, default=30,
                        help="Per-script execution timeout in seconds (default: 30)")
    parser.add_argument("--json", action="store_true", dest="as_json",
                        help="Emit machine-readable JSON")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)

    skill_path = Path(args.skill_path)
    if not skill_path.is_dir():
        msg = f"error: skill path is not a directory: {skill_path}"
        print(json.dumps({"error": msg}) if args.as_json else msg, file=sys.stderr)
        return 1

    tester = ScriptTester(skill_path, timeout=args.timeout, verbose=args.verbose)
    report = tester.test_all()

    if args.as_json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)

    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
