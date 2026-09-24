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
    r"you are (?:a|an|the)", r"you play (?:the )?role", r"act as", r"assume (?:you )?are",
    r"in the role of", r"role\s*:", r"\bas an?\b", r"\bact(?:ing)? as\b", r"\byou are an?\b",
    r"you are a", r"identity\s*:",
]
BACKGROUND_WORDS = [
    r"\bbackground\b", r"\baudience\b", r"reader is", r"user persona", r"target users?",
    r"purpose\s*(?:is|=)?", r"scenario\s*(?:is|:)?", r"the following (?:is|are)",
    r"materials? (?:are )?as follows", r"given as follows", r"aimed at",
    r"\bcontext\b", r"\baudience\b", r"\bfor (?:an? )?(?:beginners?|users?|readers?)\b",
]
TASK_WORDS = [
    r"help me", r"please help", r"\bi need\b", r"help out", r"please (?:based on|use|for)",
    r"help me write", r"organize", r"translate", r"analyze", r"summarize", r"list", r"rewrite",
    r"generate", r"draft", r"draw up", r"proofread", r"interpret", r"plan", r"evaluate",
    r"\bwrite\b", r"\btranslate\b",
    r"\bgenerate\b", r"\bsummarize\b", r"\bhelp me\b",
]
REQUIREMENT_WORDS = [
    r"requirement", r"forbidden", r"must not", r"do not", r"avoid", r"banned",
    r"must not appear", r"tone",
    r"style\s*(?:is|:)?", r"word count", r"within\s*\d+\s*(?:words|characters)", r"no more than",
    r"no more than\s*\d+",
    r"must\b", r"be sure to", r"note that", r"limit", r"\bmust not\b", r"\bavoid\b", r"\bdo not\b",
    r"\bno more than\b", r"\bwithin \d+ (?:words|characters)\b",
]
FORMAT_WORDS = [
    r"format", r"table", r"list", r"bullet points", r"key points", r"outline", r"email",
    r"item by item", r"each paragraph", r"steps?\s*(?:is|:)?", r"output as", r"output into",
    r"in the following structure", r"structure\s*(?:is|:)?",
    r"\bjson\b", r"\bmarkdown\b", r"\btable\b", r"\bbullet\b", r"\bformat\b",
    r"\boutline\b", r"structure\s*(?:is|:)?",
]

# agent mode: five sections
AGENT_SECTIONS = {
    "persona": [
        r"#\s*persona", r"#\s*role", r"##\s*Role", r"role setting", r"you are (?:a|an)",
        r"you play the role", r"\bpersona\b", r"\bidentity\b",
    ],
    "capability-flow": [
        r"#\s*capabilities", r"#\s*features", r"#\s*skills", r"#\s*workflow", r"##\s*Workflow",
        r"\bworkflow\b", r"\bsteps?\b", r"\bskills?\b", r"\btools?\b", r"workflow",
        r"flow\s*:", r"step by step", r"step 1", r"steps",
    ],
    "constraints": [
        r"#\s*constraints", r"#\s*limits", r"##\s*Constraints", r"\bconstraints?\b",
        r"\brestrictions?\b", r"forbidden", r"must not", r"do not", r"avoid", r"strictly forbidden",
    ],
    "output-format": [
        r"#\s*output format", r"#\s*response format", r"output format", r"response format",
        r"response structure",
        r"\boutput format\b", r"\bresponse format\b",
    ],
    "boundary": [
        r"#\s*boundary", r"\bboundary\b", r"\bfallback\b", r"\bsafety\b",
        r"out of .{0,6} scope", r"when uncertain", r"do not make up", r"ask back",
        r"refuse to answer", r"disclaimer",
        r"knowledge scope", r"out of scope", r"sensitive",
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
