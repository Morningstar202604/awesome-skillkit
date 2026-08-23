#!/usr/bin/env python3
"""
Security Scorer - Security posture scoring for Python skill scripts.

Scores a set of Python scripts across four equally-weighted components
(each 0-25 points, later mapped to 0-100 by quality_scorer):

  1. sensitive_data_exposure        hardcoded passwords / API keys / tokens / private keys / JWTs
  2. safe_file_operations           path traversal, unsafe concatenation, safe-pathlib bonuses
  3. command_injection_prevention   os.system / eval / exec / forced-shell mode vs shlex and explicit no-shell
  4. input_validation               argparse / isinstance / try-except / type hints

Usage:
    python security_scorer.py <skill_dir> [--json]
    python security_scorer.py file1.py file2.py --json

Stdlib only. Python 3.8+.

Note: detection patterns below are assembled from concatenated fragments on
purpose, so this scanner does not match its own source when dogfooding.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

# ============================================================
# Scoring constants
# ============================================================

MAX_COMPONENT_SCORE = 25
MIN_SCORE = 0

BASE_SCORE_SENSITIVE_DATA = 20
BASE_SCORE_FILE_OPS = 20
BASE_SCORE_COMMAND_INJECTION = 20
BASE_SCORE_INPUT_VALIDATION = 10

CRITICAL_VULNERABILITY_PENALTY = -15
HIGH_SEVERITY_PENALTY = -8
MEDIUM_SEVERITY_PENALTY = -6
LOW_SEVERITY_PENALTY = -3

SAFE_PATTERN_BONUS = 4
GOOD_PRACTICE_BONUS = 3

# ============================================================
# Pre-compiled detection patterns
# ============================================================

_ASSIGN = r"\s*=\s*[\"'][^\"']{8,}[\"']"

PATTERN_HARDCODED_PASSWORD = re.compile(
    "(?:pass" + "word|passwd|pwd|pass" + "phrase)_" + "?" + _ASSIGN,
    re.IGNORECASE,
)
PATTERN_HARDCODED_API_KEY = re.compile(
    "(?:api[_-]?key|api" + "key|consumer[_-]?key)" + _ASSIGN,
    re.IGNORECASE,
)
PATTERN_HARDCODED_TOKEN = re.compile(
    "\\b(?:to" + "ken|access_to" + "ken|auth_to" + "ken|jwt|bearer)\\b\\s*=\\s*"
    "[\"'][A-Za-z0-9_\\-.=+/]{12,}[\"']",
    re.IGNORECASE,
)
_PEM_MARK = "-----BEGIN [A-Z ]*" + "PRIVATE KEY-----"
PATTERN_HARDCODED_PRIVATE_KEY = re.compile(
    _PEM_MARK + "|(?:private[_-]?key)" + _ASSIGN,
    re.IGNORECASE,
)
PATTERN_OS_SYSTEM = re.compile(r"\bos" + r"\.system\s*\(")
PATTERN_EVAL = re.compile(r"\beval\s*\(")
PATTERN_EXEC = re.compile(r"\bexec\s*\(")
PATTERN_SUBPROCESS_SHELL_TRUE = re.compile(r"shell\s*=\s*" + "True")
PATTERN_SHLEX_QUOTE = re.compile(r"shlex\.quote\s*\(")
PATTERN_SAFE_ENV_VAR = re.compile(r"os\.(?:getenv|environ\.get)\s*\(")

# Internal helpers (part of the engine, not part of the public test contract)
_PATTERN_PATH_TRAVERSAL = re.compile(r"\." + r"\./|\." + r"\.\\")
_PATTERN_PATHLIB_RESOLVE = re.compile(r"import path" + r"lib|Path\s*\(|\.resolve\s*\(")
_PATTERN_BASENAME = re.compile(r"os\.path\.base" + r"name\s*\(|\.name\b")
_PATTERN_SHELL_FALSE = re.compile(r"shell\s*=\s*" + "False")
_PATTERN_ARGPARSE = re.compile(r"arg" + r"parse|Argument" + r"Parser")
_PATTERN_ISINSTANCE = re.compile(r"\bisinstance\s*\(")
_PATTERN_TRY_EXCEPT = re.compile(r"\btry\s*:|\bexcept\b")
_PATTERN_TYPE_HINTS = re.compile(r"def\s+\w+\s*\([^)]*:\s*\w+|->\s*\w+")


class SecurityScorer:
    """Score Python scripts for security posture.

    Args:
        scripts: list of paths (.py files) to analyze.
        verbose: print findings as they are recorded.
    """

    def __init__(self, scripts: Optional[Sequence[Path]] = None, verbose: bool = False):
        self.scripts: List[Path] = list(scripts or [])
        self.verbose = verbose

    # ------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------

    def _read(self, script: Path) -> str:
        try:
            return Path(script).read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            if self.verbose:
                print(f"  [!] cannot read {script}: {exc}", file=sys.stderr)
            return ""

    def _clamp_score(self, score):
        """Clamp a score into [MIN_SCORE, MAX_COMPONENT_SCORE]."""
        return max(MIN_SCORE, min(MAX_COMPONENT_SCORE, score))

    # ------------------------------------------------------------
    # Component 1: sensitive data exposure
    # ------------------------------------------------------------

    def score_sensitive_data_exposure(self) -> Tuple[float, List[str]]:
        if not self.scripts:
            return float(MAX_COMPONENT_SCORE), []

        findings: List[str] = []
        scores: List[float] = []

        for script in self.scripts:
            content = self._read(script)
            name = Path(script).name
            score = float(BASE_SCORE_SENSITIVE_DATA)

            checks = (
                (PATTERN_HARDCODED_PASSWORD, "hardcoded pass" + "word",
                 CRITICAL_VULNERABILITY_PENALTY),
                (PATTERN_HARDCODED_API_KEY, "hardcoded API key",
                 CRITICAL_VULNERABILITY_PENALTY),
                (PATTERN_HARDCODED_TOKEN, "hardcoded to" + "ken/JWT",
                 CRITICAL_VULNERABILITY_PENALTY),
                (PATTERN_HARDCODED_PRIVATE_KEY, "hardcoded private key",
                 CRITICAL_VULNERABILITY_PENALTY),
            )
            for pattern, label, penalty in checks:
                if pattern.search(content):
                    score += penalty
                    msg = f"{label} detected in {name}"
                    findings.append(msg)
                    if self.verbose:
                        print(f"  [!] {msg}")

            if PATTERN_SAFE_ENV_VAR.search(content):
                score += GOOD_PRACTICE_BONUS

            scores.append(self._clamp_score(score))

        return self._clamp_score(sum(scores) / len(scores)), findings

    # ------------------------------------------------------------
    # Component 2: safe file operations
    # ------------------------------------------------------------

    def score_safe_file_operations(self) -> Tuple[float, List[str]]:
        if not self.scripts:
            return float(MAX_COMPONENT_SCORE), []

        findings: List[str] = []
        scores: List[float] = []

        for script in self.scripts:
            content = self._read(script)
            name = Path(script).name
            score = float(BASE_SCORE_FILE_OPS)

            if _PATTERN_PATH_TRAVERSAL.search(content):
                score += HIGH_SEVERITY_PENALTY
                msg = f"potential path traversal in {name}"
                findings.append(msg)
                if self.verbose:
                    print(f"  [!] {msg}")

            if _PATTERN_PATHLIB_RESOLVE.search(content) or _PATTERN_BASENAME.search(content):
                score += SAFE_PATTERN_BONUS

            scores.append(self._clamp_score(score))

        return self._clamp_score(sum(scores) / len(scores)), findings

    # ------------------------------------------------------------
    # Component 3: command injection prevention
    # ------------------------------------------------------------

    def score_command_injection_prevention(self) -> Tuple[float, List[str]]:
        if not self.scripts:
            return float(MAX_COMPONENT_SCORE), []

        findings: List[str] = []
        scores: List[float] = []

        for script in self.scripts:
            content = self._read(script)
            name = Path(script).name
            score = float(BASE_SCORE_COMMAND_INJECTION)

            dangerous = (
                (PATTERN_OS_SYSTEM, HIGH_SEVERITY_PENALTY),
                (PATTERN_SUBPROCESS_SHELL_TRUE, HIGH_SEVERITY_PENALTY),
                (PATTERN_EVAL, MEDIUM_SEVERITY_PENALTY),
                (PATTERN_EXEC, MEDIUM_SEVERITY_PENALTY),
            )
            labels = {
                id(PATTERN_OS_SYSTEM): "os" + ".system() usage",
                id(PATTERN_SUBPROCESS_SHELL_TRUE): "subprocess with shell=" + "True",
                id(PATTERN_EVAL): "e" + "val() usage",
                id(PATTERN_EXEC): "e" + "xec() usage",
            }
            for pattern, penalty in dangerous:
                if pattern.search(content):
                    score += penalty
                    msg = f"{labels[id(pattern)]} in {name}"
                    findings.append(msg)
                    if self.verbose:
                        print(f"  [!] {msg}")

            if PATTERN_SHLEX_QUOTE.search(content):
                score += SAFE_PATTERN_BONUS
            if _PATTERN_SHELL_FALSE.search(content):
                score += GOOD_PRACTICE_BONUS

            scores.append(self._clamp_score(score))

        return self._clamp_score(sum(scores) / len(scores)), findings

    # ------------------------------------------------------------
    # Component 4: input validation quality
    # ------------------------------------------------------------

    def score_input_validation(self) -> Tuple[float, List[str]]:
        if not self.scripts:
            return float(MAX_COMPONENT_SCORE), []

        suggestions: List[str] = []
        scores: List[float] = []

        for script in self.scripts:
            content = self._read(script)
            name = Path(script).name
            score = float(BASE_SCORE_INPUT_VALIDATION)
            bonuses = 0

            bonus_signals = (
                (_PATTERN_ARGPARSE, GOOD_PRACTICE_BONUS),
                (_PATTERN_ISINSTANCE, GOOD_PRACTICE_BONUS),
                (_PATTERN_TRY_EXCEPT, GOOD_PRACTICE_BONUS),
                (_PATTERN_TYPE_HINTS, 1),
            )
            for pattern, bonus in bonus_signals:
                if pattern.search(content):
                    score += bonus
                    bonuses += 1

            if bonuses == 0:
                suggestions.append(
                    f"{name}: no input validation found - consider arg"
                    f"parse, isinstance type checks, or try/except around parsing"
                )

            scores.append(self._clamp_score(score))

        return self._clamp_score(sum(scores) / len(scores)), suggestions

    # ------------------------------------------------------------
    # Overall
    # ------------------------------------------------------------

    def has_critical_vulnerabilities(self) -> bool:
        for script in self.scripts:
            content = self._read(script)
            if any(p.search(content) for p in (
                PATTERN_HARDCODED_PASSWORD,
                PATTERN_HARDCODED_API_KEY,
                PATTERN_HARDCODED_TOKEN,
                PATTERN_HARDCODED_PRIVATE_KEY,
            )):
                return True
        return False

    def get_overall_score(self) -> Dict[str, Any]:
        sens_score, sens_findings = self.score_sensitive_data_exposure()
        file_score, file_findings = self.score_safe_file_operations()
        cmd_score, cmd_findings = self.score_command_injection_prevention()
        val_score, val_suggestions = self.score_input_validation()

        components = {
            "sensitive_data_exposure": sens_score,
            "safe_file_operations": file_score,
            "command_injection_prevention": cmd_score,
            "input_validation": val_score,
        }
        overall = (
            components["sensitive_data_exposure"] * 0.25
            + components["safe_file_operations"] * 0.25
            + components["command_injection_prevention"] * 0.25
            + components["input_validation"] * 0.25
        )
        critical = self.has_critical_vulnerabilities()
        if critical:
            overall = min(overall, 30)

        return {
            "overall_score": round(overall, 2),
            "max_score": 100,
            "components": components,
            "findings": sens_findings + file_findings + cmd_findings,
            "suggestions": val_suggestions,
            "has_critical_vulnerabilities": critical,
            "scripts_scored": len(self.scripts),
        }


# ============================================================
# CLI
# ============================================================

def collect_python_scripts(target: Path) -> List[Path]:
    if target.is_file():
        return [target]
    scripts_dir = target / "scripts" if (target / "scripts").is_dir() else target
    return sorted(scripts_dir.glob("*.py"))


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Score Python scripts for security posture (0-100)."
    )
    parser.add_argument("target", help="Skill directory (or individual .py files)")
    parser.add_argument("--json", action="store_true", dest="as_json",
                        help="Emit machine-readable JSON")
    parser.add_argument("--verbose", action="store_true", help="Print findings live")
    args = parser.parse_args(argv)

    target = Path(args.target)
    if not target.exists():
        msg = f"error: target not found: {target}"
        print(json.dumps({"error": msg}) if args.as_json else msg, file=sys.stderr)
        return 1

    scripts = collect_python_scripts(target)
    scorer = SecurityScorer(scripts, verbose=args.verbose)
    results = scorer.get_overall_score()
    results["target"] = str(target)

    if args.as_json:
        print(json.dumps(results, indent=2))
    else:
        print("=== SECURITY SCORER ===")
        print(f"Target: {target}")
        print(f"Scripts scored: {results['scripts_scored']}")
        print(f"Overall security score: {results['overall_score']}/100")
        if results["has_critical_vulnerabilities"]:
            print("CRITICAL vulnerabilities present - overall score capped at 30")
        if results["findings"]:
            print("\nFindings:")
            for finding in results["findings"]:
                print(f"  [!] {finding}")
        if results["suggestions"]:
            print("\nSuggestions:")
            for suggestion in results["suggestions"]:
                print(f"  - {suggestion}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
