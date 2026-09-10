#!/usr/bin/env python3
"""输入规范化 — pre-normalization（指代消解、省略补全、术语标准化）"""
import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class NormalizedInput:
    original: str
    normalized: str
    resolved_references: dict = None
    assumptions: list[str] = None


PRONOUN_PATTERNS = [
    (r'\b它\b', 'last_target'),
    (r'\b这个\b', 'last_target'),
    (r'\b那个\b', 'last_target'),
    (r'\b第二个\b', 'second_target'),
    (r'\b第一个\b', 'first_target'),
    (r'\b上一个\b', 'last_target'),
    (r'\b下一个\b', 'next_target'),
]

ELLIPSIS_PATTERNS = [
    (r'^帮我\s*$', '帮我写代码'),
    (r'^做个\s*$', '做个功能'),
    (r'^写个\s*$', '写个功能'),
    (r'^实现\s*$', '实现一个功能'),
    (r'^修复\s*$', '修复一个bug'),
]

TERM_NORMALIZATION = {
    r'后端|server端|服务端|backend|server': 'backend',
    r'前端|client端|客户端|frontend|client': 'frontend',
    r'数据库|DB|db|持久化|存储': 'database',
    r'API接口|接口|endpoint|路由': 'api',
    r'认证|鉴权|登录|auth|authentication': 'auth',
    r'缓存|cache|redis|memcached': 'cache',
    r'消息队列|MQ|队列|queue|kafka|rabbitmq': 'mq',
    r'微服务|微服务架构|service mesh': 'microservice',
    r'单体|单体应用|monolith': 'monolith',
    r'容器|docker|k8s|kubernetes|k8s集群': 'container',
    r'CI/CD|流水线|pipeline|jenkins|gitlab ci': 'ci_cd',
}


def normalize(text: str, last_intent: Optional[dict] = None) -> NormalizedInput:
    """输入规范化主入口"""
    if not text or not text.strip():
        return NormalizedInput(original=text, normalized=text, assumptions=["输入为空"])

    normalized = text.strip()
    assumptions = []
    resolved = {}

    # 1. 指代消解
    for pattern, ref_key in PRONOUN_PATTERNS:
        if re.search(pattern, normalized):
            if last_intent and ref_key in last_intent.get("slots", {}):
                replacement = last_intent["slots"][ref_key]
                normalized = re.sub(pattern, replacement, normalized)
                resolved[pattern] = replacement
            else:
                assumptions.append(f"无法消解指代: {pattern}")

    # 2. 省略补全
    for pattern, completion in ELLIPSIS_PATTERNS:
        if re.match(pattern, normalized.strip()):
            normalized = completion
            assumptions.append(f"补全省略: {pattern} -> {completion}")
            break

    # 3. 术语标准化
    for pattern, standard in TERM_NORMALIZATION.items():
        if re.search(pattern, normalized, re.IGNORECASE):
            normalized = re.sub(pattern, standard, normalized, flags=re.IGNORECASE)
            assumptions.append(f"术语标准化: {pattern} -> {standard}")

    return NormalizedInput(
        original=text,
        normalized=normalized,
        resolved_references=resolved,
        assumptions=assumptions,
    )


if __name__ == "__main__":
    import sys
    text = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read().strip()
    result = normalize(text)
    print(f"原始: {result.original}")
    print(f"规范化: {result.normalized}")
    print(f"假设: {result.assumptions}")