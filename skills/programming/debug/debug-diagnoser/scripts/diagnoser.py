#!/usr/bin/env python3
"""Debug Diagnoser — 解析 stack trace，定位根因，给出修复建议。

用法:
  python3 diagnoser.py --trace "Traceback... TypeError..."
  python3 diagnoser.py --file error.log --project .
"""
import argparse
import json
import re
import sys
from pathlib import Path

ERROR_PATTERNS = [
    {
        "pattern": r"TypeError: .*(None|undefined|not.*callable|argument)",
        "cause": "Null/undefined value passed where type expected",
        "fix": "Add null check or ensure initialization before use",
        "severity": "high",
    },
    {
        "pattern": r"KeyError: .*(\S+)",
        "cause": "Dict key missing — possible typo or data not loaded",
        "fix": "Use .get(key, default) or verify data structure before access",
        "severity": "medium",
    },
    {
        "pattern": r"(ModuleNotFoundError|ImportError): .*'(\S+)'",
        "cause": "Missing dependency or wrong import path",
        "fix": "pip install <module> or fix import path",
        "severity": "medium",
    },
    {
        "pattern": r"(IndexError|list index out of range|string index)",
        "cause": "Accessing index beyond sequence length",
        "fix": "Add bounds check or use safe indexing with default",
        "severity": "high",
    },
    {
        "pattern": r"(ValueError|could not convert|invalid literal)",
        "cause": "Wrong type passed to function (e.g., string where int expected)",
        "fix": "Cast with int()/float() or validate input type",
        "severity": "medium",
    },
    {
        "pattern": r"(ConnectionError|ConnectionRefusedError|ECONNREFUSED)",
        "cause": "Network service not reachable",
        "fix": "Check service is running, verify host/port, add retry with backoff",
        "severity": "high",
    },
    {
        "pattern": r"(FileNotFoundError|No such file)",
        "cause": "File path doesn't exist — relative path issue or missing creation",
        "fix": "Use absolute paths or create parent dirs with mkdir -p",
        "severity": "medium",
    },
    {
        "pattern": r"(PermissionError|EACCES|Permission denied)",
        "cause": "Insufficient file/system permissions",
        "fix": "Check file ownership, use appropriate user, or adjust umask",
        "severity": "high",
    },
    {
        "pattern": r"(MemoryError|OOM|killed)",
        "cause": "Out of memory — data too large or memory leak",
        "fix": "Process in chunks, use streaming, or increase memory limit",
        "severity": "critical",
    },
    {
        "pattern": r"(TimeoutError|timed out|deadline exceeded)",
        "cause": "Operation exceeded time limit",
        "fix": "Increase timeout, add pagination, or optimize the slow query/operation",
        "severity": "medium",
    },
]


def diagnose(trace_text: str) -> dict:
    """Analyze stack trace and identify root cause."""
    issues = []
    matched = []

    for ep in ERROR_PATTERNS:
        m = re.search(ep["pattern"], trace_text, re.IGNORECASE)
        if m:
            issues.append({
                "error_type": m.group(0)[:80],
                "likely_cause": ep["cause"],
                "fix_suggestion": ep["fix"],
                "severity": ep["severity"],
            })
            matched.append(ep["severity"])

    # Extract file/line info
    file_matches = re.findall(r'(?:File "|in .*)?(\S+\.py):(\d+)', trace_text)
    locations = []
    for fname, line in file_matches:
        locations.append({"file": fname, "line": int(line)})

    return {
        "status": "diagnosed" if issues else "no_match",
        "issues": issues,
        "locations": locations[:5],
        "top_severity": max(matched, key=lambda s: {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(s, 1)) if matched else "unknown",
        "recommendation": _recommendation(issues),
        "next_skill": "code-generator" if issues else None,
    }


def _recommendation(issues: list) -> str:
    if not issues:
        return "No known pattern matched. Manual review needed."
    critical = [i for i in issues if i["severity"] == "critical"]
    high = [i for i in issues if i["severity"] == "high"]
    if critical:
        return f"CRITICAL: {critical[0]['likely_cause']}. Fix immediately: {critical[0]['fix_suggestion']}"
    if high:
        return f"HIGH: {high[0]['likely_cause']}. {high[0]['fix_suggestion']}"
    return f"Medium: {issues[0]['likely_cause']}. {issues[0]['fix_suggestion']}"


def main():
    parser = argparse.ArgumentParser(description="Debug diagnoser")
    parser.add_argument("--trace", help="Stack trace text")
    parser.add_argument("--file", help="Error log file to read")
    parser.add_argument("--output", help="Output JSON file")
    args = parser.parse_args()

    trace = ""
    if args.file and Path(args.file).exists():
        trace = Path(args.file).read_text(encoding="utf-8")
    elif args.trace:
        trace = args.trace
    else:
        parser.error("Need --trace or --file")
        return

    result = diagnose(trace)
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
