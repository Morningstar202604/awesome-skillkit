#!/usr/bin/env python3
"""Performance Profiler — scan a project directory and identify performance-risk signals.

Usage:
  python3 performance_profiler.py /path/to/project
  python3 performance_profiler.py /path/to/project --json
  python3 performance_profiler.py /path/to/project --large-file-threshold-kb 256
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Any


# Risk patterns by category
PATTERNS = {
    "n_plus_one": {
        "patterns": [
            r"for\s+.*\bin\s+.*:.*\.(find|query|get|filter|select)\(",
            r"\.forEach\(.*=>\s*\{[^}]*\.(find|query|get|filter|select)\(",
        ],
        "severity": "high",
        "description": "Potential N+1 query pattern detected",
    },
    "missing_index": {
        "patterns": [
            r"WHERE\s+\w+\s*(=|<|>|<=|>=|LIKE|IN)\s*.*(?:AND|OR)\s*\w+\s*(=|<|>|<=|>=|LIKE|IN)",
            r"\.filter\(.*\.(where|find|query)\(",
        ],
        "severity": "medium",
        "description": "Potential missing database index (multi-column WHERE clause)",
    },
    "unbounded_loop": {
        "patterns": [
            r"while\s*\(\s*true\s*\)",
            r"while\s*\(\s*1\s*\)",
            r"for\s*\(\s*;\s*;\s*\)",
        ],
        "severity": "high",
        "description": "Unbounded loop detected (potential infinite loop)",
    },
    "sync_io_in_handler": {
        "patterns": [
            r"readFileSync|writeFileSync|statSync|accessSync",
            r"\.execSync\(|\.spawnSync\(",
        ],
        "severity": "medium",
        "description": "Synchronous I/O in request handler (blocks event loop)",
    },
    "large_dependency": {
        "patterns": [
            r"import\s+.*from\s+['\"](?:(?:lodash|moment|axios|express|react)(?:/|'|\"|\s))",
            r"require\(\s*['\"](?:lodash|moment|axios|express|react)(?:/|'|\"|\s)",
        ],
        "severity": "low",
        "description": "Heavy dependency detected (consider lighter alternatives)",
    },
    "unoptimized_image": {
        "patterns": [
            r"<img\s+[^>]*src=['\"][^'\"]*\.(?:png|bmp)(?:\?[^'\"]*)?['\"]",
            r"Image\.require\(\s*['\"][^'\"]*\.(?:png|bmp)",
        ],
        "severity": "low",
        "description": "Unoptimized image format (consider WebP/AVIF)",
    },
    "hardcoded_secrets": {
        "patterns": [
            r"(?:password|secret|api_key|apikey|token)\s*[:=]\s*['\"][^'\"]{8,}['\"]",
        ],
        "severity": "critical",
        "description": "Potential hardcoded secret detected",
    },
    "nested_callback": {
        "patterns": [
            r"(?:function\s*\(|=>\s*\{)[^}]{200,}",
        ],
        "severity": "medium",
        "description": "Deeply nested callback (potential callback hell)",
    },
}

SKIP_DIRS = {
    "node_modules", ".git", "__pycache__", ".venv", "venv", "env",
    ".tox", ".mypy_cache", ".pytest_cache", "dist", "build",
    ".next", ".nuxt", "coverage", ".cache",
}

MAX_FILE_SIZE_KB = 500


def scan_file(filepath: Path, large_file_threshold_kb: int) -> List[Dict[str, Any]]:
    """Scan a single file for performance issues."""
    issues = []
    
    try:
        size_kb = filepath.stat().st_size / 1024
    except OSError:
        return issues

    # Check file size
    if size_kb > large_file_threshold_kb:
        issues.append({
            "file": str(filepath),
            "line": 0,
            "category": "large_file",
            "severity": "medium",
            "message": f"Large file: {size_kb:.0f}KB (threshold: {large_file_threshold_kb}KB)",
        })

    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
    except (OSError, UnicodeDecodeError):
        return issues

    lines = content.split("\n")

    for category, config in PATTERNS.items():
        for pattern in config["patterns"]:
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append({
                        "file": str(filepath),
                        "line": line_num,
                        "category": category,
                        "severity": config["severity"],
                        "message": config["description"],
                        "snippet": line.strip()[:120],
                    })

    return issues


def scan_project(project_path: Path, large_file_threshold_kb: int) -> Dict[str, Any]:
    """Scan entire project for performance issues."""
    all_issues = []
    files_scanned = 0

    for root, dirs, files in os.walk(project_path):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for filename in files:
            filepath = Path(root) / filename

            # Only scan code files
            if filepath.suffix not in {
                ".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs",
                ".java", ".rb", ".php", ".cs", ".cpp", ".c", ".h",
            }:
                continue

            issues = scan_file(filepath, large_file_threshold_kb)
            all_issues.extend(issues)
            files_scanned += 1

    # Aggregate by category
    summary = {}
    for issue in all_issues:
        cat = issue["category"]
        if cat not in summary:
            summary[cat] = {"count": 0, "severity": issue["severity"]}
        summary[cat]["count"] += 1

    return {
        "project": str(project_path),
        "files_scanned": files_scanned,
        "total_issues": len(all_issues),
        "summary": summary,
        "issues": all_issues,
    }


def format_text_report(result: Dict[str, Any]) -> str:
    """Format results as human-readable text."""
    lines = []
    lines.append(f"Performance Scan: {result['project']}")
    lines.append(f"Files scanned: {result['files_scanned']}")
    lines.append(f"Total issues: {result['total_issues']}")
    lines.append("")

    if not result["issues"]:
        lines.append("No performance issues detected.")
        return "\n".join(lines)

    # Summary
    lines.append("Summary by Category:")
    for cat, info in sorted(result["summary"].items()):
        lines.append(f"  [{info['severity'].upper()}] {cat}: {info['count']} issues")
    lines.append("")

    # Details
    lines.append("Issues:")
    for issue in result["issues"]:
        rel_file = issue["file"]
        lines.append(f"  [{issue['severity'].upper()}] {rel_file}:{issue['line']}")
        lines.append(f"    {issue['message']}")
        if "snippet" in issue:
            lines.append(f"    > {issue['snippet']}")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Scan project for performance risk indicators")
    parser.add_argument("project_path", help="Path to project root")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--large-file-threshold-kb", type=int, default=MAX_FILE_SIZE_KB,
                        help=f"Large file threshold in KB (default: {MAX_FILE_SIZE_KB})")
    args = parser.parse_args()

    project_path = Path(args.project_path).resolve()
    if not project_path.is_dir():
        print(f"Error: {project_path} is not a directory", file=sys.stderr)
        sys.exit(1)

    result = scan_project(project_path, args.large_file_threshold_kb)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(format_text_report(result))

    # Exit with non-zero if critical issues found
    critical = sum(1 for i in result["issues"] if i["severity"] == "critical")
    sys.exit(1 if critical > 0 else 0)


if __name__ == "__main__":
    main()
