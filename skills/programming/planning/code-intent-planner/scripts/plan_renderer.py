#!/usr/bin/env python3
"""计划渲染器 — 将结构化意图渲染为 Markdown 计划文档"""
import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


def render_markdown(intent: Dict[str, Any], output_path: Optional[str] = None) -> str:
    """渲染 Markdown 计划文档"""
    session_id = intent.get("session_id", f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    intent_type = intent.get("intent_type", "unknown")
    confidence = intent.get("confidence", 0)
    source_layer = intent.get("source_layer", "unknown")
    description = intent.get("description", "无描述")
    slots = intent.get("slots", [])
    constraints = intent.get("constraints", {"hard": [], "soft": []})
    sub_tasks = intent.get("sub_tasks", [])
    critical_path = intent.get("critical_path", [])
    parallel_groups = intent.get("parallel_groups", [])
    solution = intent.get("solution", "")
    assumptions = intent.get("assumptions", [])
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    lines = []
    lines.append(f"# 任务计划 — {session_id}")
    lines.append("")
    lines.append(f"**意图类型：** {intent_type}")
    lines.append(f"**置信度：** {confidence:.2f}（来源：{source_layer}）")
    lines.append(f"**生成时间：** {now}")
    lines.append("")
    
    # 需求概述
    lines.append("## 需求概述")
    lines.append(description)
    lines.append("")
    
    # 槽位
    if slots:
        lines.append("## 关键槽位")
        lines.append("| 槽位 | 值 | 证据级别 |")
        lines.append("|------|------|----------|")
        for slot in slots:
            name = slot.get("name", "")
            value = slot.get("value", "")
            evidence = slot.get("evidence", "assumed")
            evidence_icon = {"verified": "🟢", "provisional": "🟡", "assumed": "🔴"}.get(evidence, "⚪")
            lines.append(f"| {name} | {value} | {evidence_icon} {evidence} |")
        lines.append("")
    
    # 约束
    hard = constraints.get("hard", [])
    soft = constraints.get("soft", [])
    if hard or soft:
        lines.append("## 已知约束")
        if hard:
            lines.append("### 硬约束（不可违反）")
            for c in hard:
                lines.append(f"- {c}")
        if soft:
            lines.append("### 软约束（尽量满足）")
            for c in soft:
                lines.append(f"- {c}")
        lines.append("")
    
    # 任务分解
    if sub_tasks:
        lines.append("## 任务分解")
        lines.append("")
        lines.append("| ID | 任务 | 依赖 | 优先级 | 预估 | 风险 |")
        lines.append("|----|------|------|--------|------|------|")
        for t in sub_tasks:
            deps = ", ".join(t.get("depends_on", [])) or "—"
            lines.append(f"| {t.get('id', '')} | {t.get('description', '')} | {deps} | {t.get('priority', 'P1')} | {t.get('effort', 'S')} | {t.get('risk', 'low')} |")
        lines.append("")
    
    # 关键路径
    if critical_path:
        lines.append("## 关键路径")
        lines.append(" → ".join(critical_path))
        lines.append("")
    
    # 并行组
    if parallel_groups:
        lines.append("## 可并行组")
        for group in parallel_groups:
            lines.append(f"- [{', '.join(group)}]")
        lines.append("")
    
    # 假设
    if assumptions:
        lines.append("## 假设与待确认")
        lines.append("| 假设 | 置信度 | 影响 |")
        lines.append("|------|--------|------|")
        for a in assumptions:
            text = a.get("text", "")
            evidence = a.get("evidence", "assumed")
            impact = a.get("impact", "medium")
            evidence_icon = {"verified": "🟢", "provisional": "🟡", "assumed": "🔴"}.get(evidence, "⚪")
            lines.append(f"| {text} | {evidence_icon} {evidence} | {impact} |")
        lines.append("")
    
    # 推荐方案
    if solution:
        lines.append("## 推荐方案")
        lines.append(solution)
        lines.append("")
    
    lines.append("---")
    lines.append(f"*生成于 {now} · code-intent-planner v1.0*")
    
    result = "\n".join(lines)
    
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(result, encoding="utf-8")
    
    return result


def render_json(intent: Dict[str, Any], output_path: Optional[str] = None) -> str:
    """输出结构化 JSON"""
    result = json.dumps(intent, ensure_ascii=False, indent=2)
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(result, encoding="utf-8")
    return result


def load_intent_from_stdin() -> Dict[str, Any]:
    """从 stdin 读取 JSON"""
    return json.load(sys.stdin)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Plan Renderer — 渲染任务计划")
    parser.add_argument("--input", "-i", help="输入 JSON 文件路径")
    parser.add_argument("--stdin", action="store_true", help="从 stdin 读取 JSON")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--format", "-m", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--default", action="store_true", help="使用默认示例")
    
    args = parser.parse_args()
    
    if args.default:
        intent = {
            "intent_type": "implement",
            "confidence": 0.92,
            "source_layer": "L2",
            "description": "实现用户认证模块（登录+注册+JWT）",
            "slots": [
                {"name": "target", "value": "auth", "evidence": "verified"},
                {"name": "scope", "value": "login+register", "evidence": "provisional"},
                {"name": "tech_stack", "value": "python/fastapi", "evidence": "verified"}
            ],
            "constraints": {"hard": [], "soft": ["use JWT", "bcrypt password hashing"]},
            "sub_tasks": [
                {"id": "T1", "description": "设计用户数据模型", "depends_on": [], "priority": "P0", "effort": "S", "risk": "low"},
                {"id": "T2", "description": "实现密码哈希工具", "depends_on": ["T1"], "priority": "P0", "effort": "S", "risk": "low"},
                {"id": "T3", "description": "实现 JWT Token 生成/验证", "depends_on": ["T2"], "priority": "P0", "effort": "M", "risk": "medium"},
                {"id": "T4", "description": "实现登录/注册 API", "depends_on": ["T3"], "priority": "P1", "effort": "M", "risk": "medium"},
                {"id": "T5", "description": "编写单元测试", "depends_on": ["T4"], "priority": "P1", "effort": "S", "risk": "low"},
            ],
            "critical_path": ["T1", "T2", "T3", "T4"],
            "parallel_groups": [],
            "solution": "先设计 schema，再实现 model/service，最后加 API",
            "assumptions": [
                {"text": "使用 PostgreSQL", "impact": "medium", "evidence": "provisional"},
                {"text": "使用 JWT 认证", "impact": "high", "evidence": "verified"}
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