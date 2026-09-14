#!/usr/bin/env python3
"""prompt_audit.py — audit a chat prompt against the five-element structure.

task mode elements (per chat-prompt-engineer SKILL.md):
  role / background / task / requirement / format

agent mode sections (system-prompt skeleton, Coze-style + boundary):
  persona / capability-flow / constraints / output-format / boundary

Heuristic keyword tables — structural check only (does the element have
plausible content), not a quality judgement. Output: JSON with per-element
hit/miss. Exit codes: 0 = all elements hit; 1 = one or more missing.
"""
import argparse
import json
import re
import sys

# task mode: five elements
ROLE_WORDS = [
    r"你是[一名位个]?", r"你扮演", r"充当", r"假设你", r"以.{0,6}的身份",
    r"角色[::]", r"\bas an?\b", r"\bact(?:ing)? as\b", r"\byou are an?\b",
    r"你是一", r"身份[::]",
]
BACKGROUND_WORDS = [
    r"背景", r"受众", r"读者是", r"用户画像", r"目标用户", r"用途[是为::]?",
    r"场景[是::]", r"以下是", r"材料如下", r"给定如下", r"面向",
    r"\bcontext\b", r"\baudience\b", r"\bfor (?:an? )?(?:beginners?|users?|readers?)\b",
]
TASK_WORDS = [
    r"帮我", r"请你?帮", r"我需要", r"帮忙", r"请(?:根据|把|将|按|为)",
    r"帮我?写", r"整理", r"翻译", r"分析", r"总结", r"列出", r"改写", r"生成",
    r"起草", r"拟定", r"校对", r"解读", r"规划", r"评估", r"\bwrite\b", r"\btranslate\b",
    r"\bgenerate\b", r"\bsummarize\b", r"\bhelp me\b",
]
REQUIREMENT_WORDS = [
    r"要求", r"禁止", r"不得", r"不要", r"避免", r"禁用", r"不能出现", r"语气",
    r"风格[是为:：]?", r"字数", r"\d+\s*字以内", r"不超过", r"不超过\s*\d+",
    r"必须", r"务必", r"注意", r"限制", r"\bmust not\b", r"\bavoid\b", r"\bdo not\b",
    r"\bno more than\b", r"\bwithin \d+ (?:words|characters)\b",
]
FORMAT_WORDS = [
    r"格式", r"表格", r"清单", r"分点", r"要点", r"大纲", r"邮件", r"逐条",
    r"每段", r"步骤[是:：]?", r"输出为", r"输出成", r"按以下结构", r"结构[是:：]",
    r"\bjson\b", r"\bmarkdown\b", r"\btable\b", r"\bbullet\b", r"\bformat\b",
    r"\boutline\b", r"结构[为:：]",
]

# agent mode: five sections
AGENT_SECTIONS = {
    "persona": [
        r"#\s*人设", r"#\s*角色", r"##\s*Role", r"角色设定", r"你是[一名位个]?",
        r"你扮演", r"\bpersona\b", r"\bidentity\b",
    ],
    "capability-flow": [
        r"#\s*能力", r"#\s*功能", r"#\s*技能", r"#\s*工作流程", r"##\s*Workflow",
        r"\bworkflow\b", r"\bsteps?\b", r"\bskills?\b", r"\btools?\b", r"工作流",
        r"流程[是:：]", r"分步", r"第一步", r"步骤",
    ],
    "constraints": [
        r"#\s*约束", r"#\s*限制", r"##\s*Constraints", r"\bconstraints?\b",
        r"\brestrictions?\b", r"禁止", r"不得", r"不要", r"避免", r"严禁",
    ],
    "output-format": [
        r"#\s*输出格式", r"#\s*回复格式", r"输出格式", r"回复格式", r"回复结构",
        r"\boutput format\b", r"\bresponse format\b",
    ],
    "boundary": [
        r"#\s*边界", r"\bboundary\b", r"\bfallback\b", r"\bsafety\b",
        r"超出.{0,6}范围", r"不确定时", r"不编造", r"反问", r"拒答", r"免责",
        r"知识范围", r"范围外", r"敏感",
    ],
}


def _hit(patterns, text):
    return [p for p in patterns if re.search(p, text, re.I)]


def audit_task(text):
    elements = {
        "role": ROLE_WORDS,
        "background": BACKGROUND_WORDS,
        "task": TASK_WORDS,
        "requirement": REQUIREMENT_WORDS,
        "format": FORMAT_WORDS,
    }
    return {name: bool(_hit(pats, text)) for name, pats in elements.items()}


def audit_agent(text):
    return {name: bool(_hit(pats, text)) for name, pats in AGENT_SECTIONS.items()}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Audit a chat prompt's structure.")
    ap.add_argument("--prompt", help="prompt text to audit")
    ap.add_argument("--file", help="read prompt text from a file instead")
    ap.add_argument("--mode", choices=["task", "agent"], default="task")
    args = ap.parse_args(argv)

    if args.file:
        text = open(args.file, encoding="utf-8").read()
    elif args.prompt:
        text = args.prompt
    else:
        text = sys.stdin.read()

    if not text.strip():
        print(json.dumps({"error": "empty prompt"}, ensure_ascii=False))
        return 2

    checks = audit_task(text) if args.mode == "task" else audit_agent(text)
    missing = [k for k, hit in checks.items() if not hit]
    report = {
        "mode": args.mode,
        "score": f"{len(checks) - len(missing)}/{len(checks)}",
        "elements": checks,
        "missing": missing,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
