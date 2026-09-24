#!/usr/bin/env python3
"""L1 rule engine -- the first layer of three-layer waterfall intent recognition (zero LLM, <10ms)."""
import json
import re
import sys
from typing import Dict, Any, List, Optional


RULES: List[tuple] = [
    (r'remove|uninstall|delete|destroy',            "destructive", 0.97, 1),
    (r'fix|bug|crash|panic|error',                 "fix",         0.95, 2),
    (r'test|unit test|coverage',                    "test",        0.90, 3),
    (r'review|code.?review|audit|inspect',          "review",      0.92, 4),
    (r'plan|break.?down|analyze.*requirement',      "plan",        0.95, 5),
    (r'refactor|optimize code',                     "refactor",    0.90, 6),
    (r'performance|profiling|bottleneck',           "optimize",    0.85, 7),
    (r'design|architecture',                        "design",      0.82, 8),
    (r'migrate|upgrade',                           "migrate",     0.88, 9),
    (r'build|create|implement|add',                 "implement",   0.88, 10),
]


INTENT_SUBTYPES: Dict[str, List[tuple]] = {
    "fix": [
        (r"syntax|compile", "syntax"),
        (r"crash|panic|exception|runtime", "runtime"),
        (r"security|vulnerability|injection", "security"),
    ],
    "implement": [
        (r"api|endpoint|route", "api"),
        (r"component|widget", "component"),
        (r"utility|script|tool", "script"),
    ],
    "test": [
        (r"e2e|end.to.end", "e2e"),
        (r"integration", "integration"),
        (r"coverage", "coverage"),
    ],
}


def match(text: str) -> Dict[str, Any]:
    """L1 rule matching; returns the match result."""
    t = text.lower().strip()
    for pattern, intent_type, confidence, priority in RULES:
        if re.search(pattern, t):
            # try to determine the subtype
            subtype = None
            if intent_type in INTENT_SUBTYPES:
                for st_pattern, st_name in INTENT_SUBTYPES[intent_type]:
                    if re.search(st_pattern, t):
                        subtype = st_name
                        break
            return {
                "matched": True,
                "intent_type": intent_type,
                "subtype": subtype,
                "confidence": confidence,
                "source_layer": "L1",
                "rule": pattern,
                "priority": priority,
            }
    return {
        "matched": False,
        "intent_type": None,
        "subtype": None,
        "confidence": 0.0,
        "source_layer": "L1",
        "recommendation": "upgrade_to_L2",
    }


def match_all(text: str) -> List[Dict[str, Any]]:
    """Return all matching rules (for multi-intent detection)."""
    t = text.lower().strip()
    results = []
    for pattern, intent_type, confidence, priority in RULES:
        if re.search(pattern, t):
            results.append({
                "intent_type": intent_type,
                "confidence": confidence,
                "priority": priority,
                "rule": pattern,
            })
    # sort by priority
    results.sort(key=lambda x: x["priority"])
    return results


if __name__ == "__main__":
    text = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read().strip()
    result = match(text)
    print(json.dumps(result, ensure_ascii=False, indent=2))
