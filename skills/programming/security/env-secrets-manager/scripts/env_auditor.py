#!/usr/bin/env python3
"""
Env Auditor - detect likely secret leaks and env-file hygiene issues.

Scans a repository working tree for credential-shaped values and reports
them by severity:

    critical    active provider keys (OpenAI/GitHub/AWS), private key blocks
    high        Slack tokens, hardcoded assignments to sensitive keys,
                .env files that are not gitignored
    medium      plaintext JWTs, real-looking values committed in .env.example
    low         .env <-> .env.example drift, credentials with no recorded
                rotation date

Values are always redacted in output so the auditor never leaks secrets into
logs or CI output.

Usage:
    python env_auditor.py <repo_path> [--json] [--max-filesize KB]

Exit codes: 0 = no critical/high findings, 1 = critical/high found,
            2 = usage error (bad path).

Stdlib only. Python 3.8+.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

SKIP_DIRS = {".git", ".hg", ".svn", "node_modules", ".venv", "venv",
             "__pycache__", ".pytest_cache", ".ruff_cache", "dist", "build"}
TEXT_SUFFIXES = {
    ".env", ".txt", ".md", ".rst", ".py", ".js", ".ts", ".jsx", ".tsx", ".json",
    ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf", ".sh", ".bash", ".ps1",
    ".rb", ".go", ".rs", ".java", ".kt", ".php", ".sql", ".tf", ".hcl", ".xml",
    ".html", ".css", ".csv", ".properties",
}
DEFAULT_MAX_FILESIZE_KB = 512

# ---------------------------------------------------------------
# Detection patterns.
# Fragments are concatenated so this scanner does not flag its own source
# when pointed at its own skill directory (dogfooding).
# ---------------------------------------------------------------

_PATTERNS: List[Dict[str, Any]] = [
    {
        "severity": "critical",
        "id": "openai_key",
        "label": "OpenAI-style API key",
        "regex": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    },
    {
        "severity": "critical",
        "id": "github_token",
        "label": "GitHub token",
        "regex": re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}\b"
                            r"|github_pat_[A-Za-z0-9_]{40,}"),
    },
    {
        "severity": "critical",
        "id": "aws_access_key",
        "label": "AWS access key ID",
        "regex": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    },
    {
        "severity": "critical",
        "id": "private_key_block",
        "label": "private key block",
        "regex": re.compile("-----BEGIN [A-Z ]*" + "PRIVATE KEY-----"),
    },
    {
        "severity": "high",
        "id": "slack_token",
        "label": "Slack token",
        "regex": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
    },
    {
        "severity": "medium",
        "id": "jwt_plaintext",
        "label": "plaintext JWT",
        "regex": re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
    },
]

# Sensitive key names, fragmented so this file never matches itself.
_ASSIGN_KEY = (
    "(?:pass" "word|pass" "wd|api" "_key|sec"
    "ret|to" "ken|auth_to" "ken|access_ke" "y|private_ke" "y)"
)
PATTERN_SENSITIVE_ASSIGN = re.compile(
    _ASSIGN_KEY + r"\s*[:=]\s*[\"']?([^\s\"']{8,})", re.IGNORECASE
)

_QUOTED_VALUE = re.compile(r"^[\"']")
_PLAIN_TOKEN = re.compile(r"[A-Za-z0-9_+/@.:=+-]{16,}")

EXAMPLE_SUFFIX = ".example"


def redact(value: str) -> str:
    """Show only the leading characters of a suspected secret."""
    value = value.strip()
    if len(value) <= 8:
        return "***"
    return value[:4] + "..." + f"({len(value)} chars)"


def _is_code_expression(value: str) -> bool:
    """Unquoted RHS containing call/bracket/space chars is code, not a literal."""
    return any(ch in value for ch in "(){}[] ")


def is_probably_secret_value(value: str) -> bool:
    """Heuristic filter: skip placeholders, templates and runtime lookups."""
    lowered = value.lower()
    placeholders = (
        "changeme", "change_me", "your_", "<", "${", "{{", "xxx",
        "example", "placeholder", "todo", "fixme", "dummy", "sample",
    )
    if any(p in lowered for p in placeholders):
        return False
    if lowered in {"true", "false", "none", "null", "yes", "no"}:
        return False
    if value.startswith(("$", "${", "%")):
        return False
    if lowered.startswith(("process.env", "os.environ", "os.getenv",
                           "getenv(", "env:")):
        return False
    return True


class EnvAuditor:
    """Audit one directory tree for secret leaks and env hygiene."""

    def __init__(self, root: Path, max_filesize_kb: int = DEFAULT_MAX_FILESIZE_KB):
        self.root = Path(root)
        self.max_filesize_kb = max_filesize_kb
        self.findings: List[Dict[str, Any]] = []

    # ------------------------------------------------------------ helpers

    def _add(self, severity: str, fid: str, message: str, file: Optional[Path] = None,
             line: Optional[int] = None, excerpt: str = "") -> None:
        try:
            rel = str(file.relative_to(self.root)) if file else None
        except ValueError:
            rel = str(file) if file else None
        self.findings.append({
            "severity": severity,
            "id": fid,
            "message": message,
            "file": rel,
            "line": line,
            "excerpt": redact(excerpt) if excerpt else "",
        })

    def _iter_candidate_files(self):
        for path in self.root.rglob("*"):
            try:
                if not path.is_file():
                    continue
                rel_parts = set(path.relative_to(self.root).parts)
                if rel_parts & SKIP_DIRS:
                    continue
                name = path.name.lower()
                looks_env = (name == ".env" or name.startswith(".env.")
                                or name.endswith(".env"))
                suffix = path.suffix.lower()
                if not (looks_env or suffix in TEXT_SUFFIXES):
                    continue
                if path.stat().st_size > self.max_filesize_kb * 1024:
                    continue
                yield path, looks_env
            except OSError:
                continue

    @staticmethod
    def _read_lines(path: Path) -> List[str]:
        try:
            return path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            return []

    # ------------------------------------------------------------ checks

    def scan_content(self) -> None:
        for path, looks_env in self._iter_candidate_files():
            lines = self._read_lines(path)
            for idx, line in enumerate(lines, start=1):
                for spec in _PATTERNS:
                    m = spec["regex"].search(line)
                    if m:
                        self._add(spec["severity"], spec["id"],
                                  f"{spec['label']} detected", path, idx, m.group(0))

                m_assign = PATTERN_SENSITIVE_ASSIGN.search(line)
                if m_assign:
                    value = m_assign.group(1)
                    key = line.split("=")[0].split(":")[0].strip()
                    if not is_probably_secret_value(value):
                        continue
                    quoted = bool(_QUOTED_VALUE.match(value.strip()))
                    if not quoted:
                        # Unquoted RHS must look like a dense token literal;
                        # anything else is code (expressions, booleans, refs).
                        if _is_code_expression(value) or not _PLAIN_TOKEN.fullmatch(value):
                            continue
                    if EXAMPLE_SUFFIX in path.suffix or ".example" in path.name:
                        self._add("medium", "real_value_in_example",
                                  f"real-looking value for '{key}' in an "
                                  f".env.example-style file", path, idx, value)
                    else:
                        self._add("high", "sensitive_assignment",
                                  f"hardcoded assignment to sensitive key '{key}'",
                                  path, idx, value)

            # rotation-date awareness for .env files (rotation Phase 1)
            if looks_env:
                has_secret = any(PATTERN_SENSITIVE_ASSIGN.search(l) for l in lines)
                mentions_rotation = any("rotat" in l.lower() for l in lines)
                if has_secret and not mentions_rotation:
                    self._add("low", "no_rotation_date",
                              "env file contains credential-like keys but records "
                              "no rotation date/comment (e.g. a ROTATED comment)",
                              path)

    def check_gitignore(self) -> None:
        gitignore = self.root / ".gitignore"
        patterns = ""
        if gitignore.is_file():
            patterns = gitignore.read_text(encoding="utf-8", errors="replace").lower()
        env_path = self.root / ".env"
        if env_path.is_file() and ".env" not in patterns:
            self._add("high", "env_not_gitignored",
                      "'.env' exists but is not covered by .gitignore")

    def check_drift(self) -> None:
        env_path = self.root / ".env"
        example = self.root / (".env" + EXAMPLE_SUFFIX)
        if not (env_path.is_file() and example.is_file()):
            return

        def keys_of(p: Path) -> set:
            out = set()
            for line in self._read_lines(p):
                line = line.strip()
                if line and not line.startswith("#"):
                    out.add(re.split(r"[=:]", line, maxsplit=1)[0].strip())
            return out

        missing = keys_of(env_path) - keys_of(example)
        if missing:
            preview = ", ".join(sorted(missing)[:5])
            self._add("low", "env_example_drift",
                      f"{len(missing)} vars present in .env but missing from "
                      f".env.example (update the example): {preview}")

    # ------------------------------------------------------------ entry

    def run(self) -> Dict[str, Any]:
        self.scan_content()
        self.check_gitignore()
        self.check_drift()

        order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        self.findings.sort(key=lambda f: (order.get(f["severity"], 9),
                                          f["file"] or "", f["line"] or 0))
        summary = {sev: 0 for sev in ("critical", "high", "medium", "low")}
        for f in self.findings:
            summary[f["severity"]] += 1
        return {
            "target": str(self.root),
            "summary": summary,
            "total_findings": len(self.findings),
            "findings": self.findings,
        }


def print_report(report: Dict[str, Any]) -> None:
    print("=== ENV AUDITOR ===")
    print(f"Target: {report['target']}")
    print(f"Findings: {report['total_findings']} "
          f"(critical={report['summary']['critical']}, high={report['summary']['high']}, "
          f"medium={report['summary']['medium']}, low={report['summary']['low']})")
    if not report["findings"]:
        print("Clean - no credential-shaped values or hygiene issues detected.")
        return
    current_sev = None
    for f in report["findings"]:
        if f["severity"] != current_sev:
            current_sev = f["severity"]
            print(f"\n[{current_sev.upper()}]")
        loc = f["file"] or "(repo)"
        if f["line"]:
            loc += f":{f['line']}"
        print(f"  - {f['message']} ({loc})")
        if f["excerpt"]:
            print(f"      excerpt: {f['excerpt']}")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Scan a repo working tree for likely secret leaks (redacted output)."
    )
    parser.add_argument("repo", help="Path to the repository/project root")
    parser.add_argument("--json", action="store_true", dest="as_json",
                        help="Emit machine-readable JSON")
    parser.add_argument("--max-filesize", type=int, default=DEFAULT_MAX_FILESIZE_KB,
                        dest="max_filesize", help="Skip files larger than N KB")
    args = parser.parse_args(argv)

    root = Path(args.repo)
    if not root.is_dir():
        msg = f"error: repo path is not a directory: {root}"
        print(json.dumps({"error": msg}) if args.as_json else msg, file=sys.stderr)
        return 2

    auditor = EnvAuditor(root, max_filesize_kb=args.max_filesize)
    report = auditor.run()

    if args.as_json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)

    return 1 if (report["summary"]["critical"] or report["summary"]["high"]) else 0


if __name__ == "__main__":
    sys.exit(main())