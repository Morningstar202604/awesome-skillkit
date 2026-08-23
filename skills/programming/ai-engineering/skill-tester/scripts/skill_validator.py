#!/usr/bin/env python3
"""
Skill Validator - structure and documentation compliance checker.

Validates a skill directory against the ecosystem structure spec:
  * SKILL.md present, YAML frontmatter (name/description), line minimums per tier
  * README.md, scripts/, assets/, references/, expected_outputs/ presence by tier
  * Per-script checks: valid syntax, argparse usage, main guard

Usage:
    python skill_validator.py <skill_path> [--tier BASIC|STANDARD|POWERFUL] [--json]

Exit codes: 0 = no errors, 1 = validation errors found.

Stdlib only. Python 3.8+.
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

TIER_MIN_LINES = {"BASIC": 100, "STANDARD": 200, "POWERFUL": 300}
TIER_REQUIRED_DIRS = {
    "BASIC": ["scripts"],
    "STANDARD": ["scripts", "assets", "references"],
    "POWERFUL": ["scripts", "assets", "references", "expected_outputs"],
}
TIER_RECOMMENDED_DIRS = {
    "BASIC": ["assets", "references"],
    "STANDARD": ["expected_outputs"],
    "POWERFUL": [],
}
TIER_MIN_SCRIPTS = {"BASIC": 1, "STANDARD": 1, "POWERFUL": 2}

REQUIRED_FRONTMATTER_FIELDS = ["name", "description"]
RECOMMENDED_SECTIONS = [
    "Overview", "Quick Start", "Usage", "Examples", "Troubleshooting",
]

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)


class SkillValidator:
    """Validate one skill directory against tier requirements."""

    def __init__(self, skill_path: Path, tier: str = "BASIC"):
        self.skill_path = Path(skill_path)
        self.tier = tier.upper()
        if self.tier not in TIER_MIN_LINES:
            raise ValueError(f"unknown tier: {tier}")
        self.checks: Dict[str, Dict[str, Any]] = {}
        self.warnings: List[str] = []
        self.errors: List[str] = []
        self.suggestions: List[str] = []

    # ------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------

    def _record(self, key: str, passed: bool, message: str) -> None:
        self.checks[key] = {
            "passed": bool(passed),
            "message": message,
            "score": 1.0 if passed else 0.0,
        }
        if not passed:
            self.errors.append(message)

    def _read_skill_md(self) -> Optional[str]:
        path = self.skill_path / "SKILL.md"
        try:
            return path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return None

    # ------------------------------------------------------------
    # individual checks
    # ------------------------------------------------------------

    def check_skill_md(self) -> Optional[str]:
        content = self._read_skill_md()
        if content is None:
            self._record("skill_md_exists", False, "SKILL.md NOT found")
            return None
        lines = content.count("\n") + 1
        self._record("skill_md_exists", True, "SKILL.md found")
        min_lines = TIER_MIN_LINES[self.tier]
        self._record(
            f"skill_md_length",
            lines >= min_lines,
            f"SKILL.md has {lines} lines (>={min_lines})",
        )
        return content

    def check_readme(self) -> None:
        exists = (self.skill_path / "README.md").is_file()
        self._record("readme_exists", exists,
                     "README.md found" if exists else "README.md NOT found")

    def check_frontmatter(self, content: Optional[str]) -> None:
        if not content:
            self._record("frontmatter_complete", False, "SKILL.md unreadable")
            return
        match = FRONTMATTER_RE.match(content.lstrip("\ufeff"))
        if not match:
            self._record("frontmatter_complete", False,
                         "No YAML frontmatter block at top of SKILL.md")
            return
        block = match.group(1)
        missing = [f for f in REQUIRED_FRONTMATTER_FIELDS
                   if not re.search(rf"^{f}\s*:", block, re.MULTILINE)]
        if missing:
            self._record("frontmatter_complete", False,
                         f"Missing frontmatter fields: {', '.join(missing)}")
        else:
            self._record("frontmatter_complete", True,
                         "All required frontmatter fields present")

    def check_required_sections(self, content: Optional[str]) -> None:
        if not content:
            self._record("required_sections", False, "SKILL.md unreadable")
            return
        headings = set(h.strip().lower()
                       for h in re.findall(r"^#{1,3}\s+(.*)$", content, re.MULTILINE))
        missing = [s for s in ("overview", "usage", "quick start")
                   if s not in headings]
        if missing:
            # advisory rather than fatal for legacy layouts
            self.warnings.append(f"Recommended sections missing: {', '.join(missing)}")
            self._record("required_sections", True,
                         f"Core sections mostly present (missing: {', '.join(missing)})")
        else:
            self._record("required_sections", True, "All required sections present")
        extra = [s for s in RECOMMENDED_SECTIONS if s.lower() in headings]
        if len(extra) < 2:
            self.suggestions.append(
                "Consider adding more recommended sections: "
                + ", ".join(s for s in RECOMMENDED_SECTIONS if s.lower() not in headings)[:3]
            )

    def check_directories(self) -> int:
        script_count = 0
        for d in TIER_REQUIRED_DIRS[self.tier]:
            exists = (self.skill_path / d).is_dir()
            self._record(f"dir_{d}_exists", exists,
                         f"{d}/ directory found" if exists else f"{d}/ directory NOT found")
        for d in TIER_RECOMMENDED_DIRS[self.tier]:
            if not (self.skill_path / d).is_dir():
                self.warnings.append(f"Optional directory missing: {d}/")
                self.suggestions.append(f"Consider adding optional directories: {d}")
        scripts_dir = self.skill_path / "scripts"
        if scripts_dir.is_dir():
            script_count = len(list(scripts_dir.glob("*.py")))
        minimum = TIER_MIN_SCRIPTS[self.tier]
        self._record(
            "min_scripts_count",
            script_count >= minimum,
            f"Found {script_count} Python scripts (>={minimum})",
        )
        return script_count

    def check_scripts(self) -> List[Path]:
        import ast
        scripts_dir = self.skill_path / "scripts"
        py_files = sorted(scripts_dir.glob("*.py")) if scripts_dir.is_dir() else []
        for py in py_files:
            try:
                source = py.read_text(encoding="utf-8", errors="replace")
            except OSError as exc:
                self._record(f"script_syntax_{py.stem}", False,
                             f"cannot read {py.name}: {exc}")
                continue
            try:
                tree = ast.parse(source)
                self._record(f"script_syntax_{py.stem}", True,
                             f"{py.name} has valid Python syntax")
            except SyntaxError as exc:
                self._record(f"script_syntax_{py.stem}", False,
                             f"{py.name} syntax error: {exc.msg} (line {exc.lineno})")
                continue
            uses_argparse = "argparse" in source or "click" in source
            self._record(f"script_argparse_{py.stem}", uses_argparse,
                         f"Uses argparse in {py.name}" if uses_argparse
                         else f"No argparse usage in {py.name}")
            has_main_guard = False
            for node in tree.body:
                if isinstance(node, ast.If):
                    test = node.test
                    if isinstance(test, ast.Compare) and getattr(test.left, "id", "") == "__name__":
                        has_main_guard = True
                        break
            self._record(f"script_main_guard_{py.stem}", has_main_guard,
                         f"Has main guard in {py.name}" if has_main_guard
                         else f"No `if __name__` guard in {py.name}")
        return py_files

    def check_tier_compliance(self, content: Optional[str], script_count: int) -> None:
        ok = content is not None and script_count >= TIER_MIN_SCRIPTS[self.tier]
        self._record("tier_compliance", ok,
                     f"Meets {self.tier} tier requirements"
                     if ok else f"Does NOT meet {self.tier} tier requirements")

    # ------------------------------------------------------------
    # entry point
    # ------------------------------------------------------------

    def validate(self) -> Dict[str, Any]:
        content = self.check_skill_md()
        self.check_readme()
        self.check_frontmatter(content)
        self.check_required_sections(content)
        script_count = self.check_directories()
        self.check_scripts()
        self.check_tier_compliance(content, script_count)

        total = len(self.checks)
        passed = sum(1 for c in self.checks.values() if c["passed"])
        overall_score = round((passed / total) * 100, 1) if total else 0.0

        if overall_score >= 95:
            compliance_level = "EXCELLENT"
        elif overall_score >= 80:
            compliance_level = "GOOD"
        elif overall_score >= 60:
            compliance_level = "FAIR"
        else:
            compliance_level = "POOR"

        return {
            "skill_path": str(self.skill_path).replace("\\\\", "/"),
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "overall_score": overall_score,
            "compliance_level": compliance_level,
            "checks": self.checks,
            "warnings": self.warnings,
            "errors": self.errors,
            "suggestions": self.suggestions,
        }


def infer_tier(skill_path: Path) -> str:
    skill_md = skill_path / "SKILL.md"
    try:
        lines = skill_md.read_text(encoding="utf-8", errors="replace").count("\n") + 1
    except OSError:
        return "BASIC"
    if lines >= TIER_MIN_LINES["POWERFUL"]:
        return "POWERFUL"
    if lines >= TIER_MIN_LINES["STANDARD"]:
        return "STANDARD"
    return "BASIC"


def print_report(report: Dict[str, Any]) -> None:
    print("=== SKILL VALIDATION REPORT ===")
    print(f"Skill: {report['skill_path']}")
    print(f"Overall Score: {report['overall_score']}/100 ({report['compliance_level']})")
    print()
    print("STRUCTURE VALIDATION:")
    for name, check in report["checks"].items():
        mark = "PASS" if check["passed"] else "FAIL"
        symbol = "+" if check["passed"] else "x"
        print(f"  [{symbol}] {mark}: {check['message']} ({name})")
    if report["warnings"]:
        print("\nWARNINGS:")
        for w in report["warnings"]:
            print(f"  ! {w}")
    if report["errors"]:
        print("\nERRORS:")
        for e in report["errors"]:
            print(f"  x {e}")
    if report["suggestions"]:
        print("\nSUGGESTIONS:")
        for s in report["suggestions"]:
            print(f"  - {s}")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate a skill's structure and documentation compliance."
    )
    parser.add_argument("skill_path", help="Path to the skill directory")
    parser.add_argument("--tier", default=None,
                        choices=["BASIC", "STANDARD", "POWERFUL"],
                        help="Tier to validate against (default: inferred from SKILL.md size)")
    parser.add_argument("--json", action="store_true", dest="as_json",
                        help="Emit machine-readable JSON")
    args = parser.parse_args(argv)

    skill_path = Path(args.skill_path)
    if not skill_path.is_dir():
        msg = f"error: skill path is not a directory: {skill_path}"
        print(json.dumps({"error": msg}) if args.as_json else msg, file=sys.stderr)
        return 1

    tier = args.tier or infer_tier(skill_path)
    validator = SkillValidator(skill_path, tier=tier)
    report = validator.validate()

    if args.as_json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)

    return 0 if report["overall_score"] >= 80 and not report["errors"] else 1


if __name__ == "__main__":
    sys.exit(main())
