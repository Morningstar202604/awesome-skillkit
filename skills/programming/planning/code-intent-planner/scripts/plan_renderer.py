#!/usr/bin/env python3
"""Plan renderer -- render a structured intent into a Markdown plan document."""
import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


def render_markdown(intent: Dict[str, Any], output_path: Optional[str] = None) -> str:
    """Render a Markdown plan document."""
    session_id = intent.get("session_id", f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    intent_type = intent.get("intent_type", "unknown")
    confidence = intent.get("confidence", 0)
    source_layer = intent.get("source_layer", "unknown")
    description = intent.get("description", "No description")
    slots = intent.get("slots", [])
    constraints = intent.get("constraints", {"hard": [], "soft": []})
    sub_tasks = intent.get("sub_tasks", [])
    critical_path = intent.get("critical_path", [])
    parallel_groups = intent.get("parallel_groups", [])
    solution = intent.get("solution", "")
    assumptions = intent.get("assumptions", [])

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = []
    lines.append(f"# Task plan - {session_id}")
    lines.append("")
    lines.append(f"**Intent type:** {intent_type}")
    lines.append(f"**Confidence:** {confidence:.2f} (source: {source_layer})")
    lines.append(f"**Generated:** {now}")
    lines.append("")

    # requirement overview
    lines.append("## Requirement overview")
    lines.append(description)
    lines.append("")

    # slots
    if slots:
        lines.append("## Key slots")
        lines.append("| Slot | Value | Evidence |")
        lines.append("|------|-------|----------|")
        for slot in slots:
            name = slot.get("name", "")
            value = slot.get("value", "")
            evidence = slot.get("evidence", "assumed")
            evidence_icon = {"verified": "🟢", "provisional": "🟡", "assumed": "🔴"}.get(evidence, "⚪")
            lines.append(f"| {name} | {value} | {evidence_icon} {evidence} |")
        lines.append("")

    # constraints
    hard = constraints.get("hard", [])
    soft = constraints.get("soft", [])
    if hard or soft:
        lines.append("## Known constraints")
        if hard:
            lines.append("### Hard constraints (must not be violated)")
            for c in hard:
                lines.append(f"- {c}")
        if soft:
            lines.append("### Soft constraints (best effort)")
            for c in soft:
                lines.append(f"- {c}")
        lines.append("")

    # task breakdown
    if sub_tasks:
        lines.append("## Task breakdown")
        lines.append("")
        lines.append("| ID | Task | Depends on | Priority | Estimate | Risk |")
        lines.append("|----|------|------------|----------|----------|------|")
        for t in sub_tasks:
            deps = ", ".join(t.get("depends_on", [])) or "-"
            lines.append(f"| {t.get('id', '')} | {t.get('description', '')} | {deps} | {t.get('priority', 'P1')} | {t.get('effort', 'S')} | {t.get('risk', 'low')} |")
        lines.append("")

    # critical path
    if critical_path:
        lines.append("## Critical path")
        lines.append(" -> ".join(critical_path))
        lines.append("")

    # parallel groups
    if parallel_groups:
        lines.append("## Parallelizable groups")
        for group in parallel_groups:
            lines.append(f"- [{', '.join(group)}]")
        lines.append("")

    # assumptions
    if assumptions:
        lines.append("## Assumptions & to-confirm")
        lines.append("| Assumption | Confidence | Impact |")
        lines.append("|------------|------------|--------|")
        for a in assumptions:
            text = a.get("text", "")
            evidence = a.get("evidence", "assumed")
            impact = a.get("impact", "medium")
            evidence_icon = {"verified": "🟢", "provisional": "🟡", "assumed": "🔴"}.get(evidence, "⚪")
            lines.append(f"| {text} | {evidence_icon} {evidence} | {impact} |")
        lines.append("")

    # recommended solution
    if solution:
        lines.append("## Recommended solution")
        lines.append(solution)
        lines.append("")

    lines.append("---")
    lines.append(f"*Generated {now} - code-intent-planner v1.0*")

    result = "\n".join(lines)

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(result, encoding="utf-8")

    return result


def render_json(intent: Dict[str, Any], output_path: Optional[str] = None) -> str:
    """Emit structured JSON."""
    result = json.dumps(intent, ensure_ascii=False, indent=2)
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(result, encoding="utf-8")
    return result


def load_intent_from_stdin() -> Dict[str, Any]:
    """Read JSON from stdin."""
    return json.load(sys.stdin)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Plan Renderer - render a task plan")
    parser.add_argument("--input", "-i", help="input JSON file path")
    parser.add_argument("--stdin", action="store_true", help="read JSON from stdin")
    parser.add_argument("--output", "-o", help="output file path")
    parser.add_argument("--format", "-m", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--default", action="store_true", help="use the built-in example")

    args = parser.parse_args()

    if args.default:
        intent = {
            "intent_type": "implement",
            "confidence": 0.92,
            "source_layer": "L2",
            "description": "Implement the user authentication module (login + register + JWT)",
            "slots": [
                {"name": "target", "value": "auth", "evidence": "verified"},
                {"name": "scope", "value": "login+register", "evidence": "provisional"},
                {"name": "tech_stack", "value": "python/fastapi", "evidence": "verified"}
            ],
            "constraints": {"hard": [], "soft": ["use JWT", "bcrypt password hashing"]},
            "sub_tasks": [
                {"id": "T1", "description": "Design the user data model", "depends_on": [], "priority": "P0", "effort": "S", "risk": "low"},
                {"id": "T2", "description": "Implement the password-hashing utility", "depends_on": ["T1"], "priority": "P0", "effort": "S", "risk": "low"},
                {"id": "T3", "description": "Implement JWT token generation/verification", "depends_on": ["T2"], "priority": "P0", "effort": "M", "risk": "medium"},
                {"id": "T4", "description": "Implement the login/register API", "depends_on": ["T3"], "priority": "P1", "effort": "M", "risk": "medium"},
                {"id": "T5", "description": "Write unit tests", "depends_on": ["T4"], "priority": "P1", "effort": "S", "risk": "low"},
            ],
            "critical_path": ["T1", "T2", "T3", "T4"],
            "parallel_groups": [],
            "solution": "Design the schema first, then implement model/service, then add the API",
            "assumptions": [
                {"text": "Use PostgreSQL", "impact": "medium", "evidence": "provisional"},
                {"text": "Use JWT auth", "impact": "high", "evidence": "verified"}
            ],
            "session_id": f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat()
        }
    elif args.input:
        with open(args.input, encoding="utf-8") as f:
            intent = json.load(f)
    elif args.stdin:
        intent = load_intent_from_stdin()
    else:
        parser.print_help()
        sys.exit(1)

    if args.format == "markdown":
        render_markdown(intent, args.output)
    else:
        render_json(intent, args.output)


if __name__ == "__main__":
    main()
