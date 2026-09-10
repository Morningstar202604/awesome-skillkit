#!/usr/bin/env python3
"""L1 规则引擎 — 三层瀑布式意图识别的第一层（零 LLM，<10ms）"""
import json
import re
import sys
from typing import Dict, Any, List, Optional


RULES: List[tuple] = [
    (r'删|删除|remove|uninstall|销毁',            "destructive", 0.97, 1),
    (r'fix|修[好复]|bug|报错|错误|crash|panic',    "fix",         0.95, 2),
    (r'测试|test|单测|单元测试|覆盖率|coverage',   "test",        0.90, 3),
    (r'审查|review|code.?review|audit|检[查核]',   "review",      0.92, 4),
    (r'规划|拆解|分析.*需求|怎么[做搞]|plan|break.?down', "plan",  0.95, 5),
    (r'重构|refactor|优化代码|整理代码',            "refactor",    0.90, 6),
    (r'性能|加速|profiling|bottleneck',            "optimize",    0.85, 7),
    (r'设计|架构|设计方案',                        "design",      0.82, 8),
    (r'迁移|migrate|升级|upgrade|版本升级',        "migrate",     0.88, 9),
    (r'写|做|实现|添加|新增|build|create|开发',    "implement",   0.88, 10),
]


INTENT_SUBTYPES: Dict[str, List[tuple]] = {
    "fix": [
        (r"语法|syntax|编译", "syntax"),
        (r"crash|panic|exception|运行时", "runtime"),
        (r"安全|漏洞|注入|越权", "security"),
    ],
    "implement": [
        (r"接口|api|endpoint|路由", "api"),
        (r"组件|widget|component", "component"),
        (r"脚本|工具|utility|script", "script"),
    ],
    "test": [
        (r"e2e|端到端", "e2e"),
        (r"集成|integration", "integration"),
        (r"覆盖率|coverage", "coverage"),
    ],
}


def match(text: str) -> Dict[str, Any]:
    """L1 规则匹配，返回匹配结果"""
    t = text.lower().strip()
    for pattern, intent_type, confidence, priority in RULES:
        if re.search(pattern, t):
            # 尝试确定 subtype
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
    """返回所有匹配的规则（用于多意图检测）"""
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
    # 按优先级排序
    results.sort(key=lambda x: x["priority"])
    return results


if __name__ == "__main__":
    text = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read().strip()
    result = match(text)
    print(json.dumps(result, ensure_ascii=False, indent=2))