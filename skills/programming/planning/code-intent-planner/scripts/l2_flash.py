#!/usr/bin/env python3
"""L2 Flash LLM 意图识别 — 置信度路由 + 槽位填充"""
import json
import sys
import os
from typing import Dict, Any, Optional


# L2 模型配置（通过环境变量配置）
FLASH_MODEL = os.getenv("FLASH_LLM_MODEL", "deepseek-v4-flash")
FLASH_API_KEY = os.getenv("FLASH_LLM_API_KEY")
FLASH_BASE_URL = os.getenv("FLASH_LLM_BASE_URL", "https://api.openai.com/v1")


L2_PROMPT_TEMPLATE = """你是一位资深软件工程师，正在分析用户的编程需求。

任务：识别用户意图类型，提取关键槽位，给出置信度。

用户输入：{normalized_text}
项目技术栈：{tech_stack}
项目结构片段（可选）：{project_snippet}

请仅返回以下 JSON，不要任何其他内容：

{{
  "intent_type": "implement|fix|refactor|review|test|optimize|plan|design|migrate|destructive",
  "confidence": 0.0-1.0,
  "description": "一句话需求描述",
  "slots": {{
    "target": "目标模块/文件，如 auth、user-service",
    "scope": "改动范围，如 login+register、api-only",
    "tech_stack": "技术栈，如 python/fastapi、node/express"
  }},
  "assumptions": ["假设1", "假设2"]
}}

约束：
- confidence 必须诚实反映确信程度
- 无法确定的槽位留空字符串
- assumptions 列出你为得出结论而做的假设
"""


class MockLLM:
    """Mock LLM，用于测试/无 API Key 时"""
    
    @staticmethod
    def analyze(normalized_text: str, tech_stack: str = "unknown") -> Dict:
        """基于关键词的简单模拟"""
        text = normalized_text.lower()
        
        # 简单关键词映射
        if any(k in text for k in ["bug", "crash", "报错", "错误", "fix", "修"]):
            return {
                "intent_type": "fix",
                "confidence": 0.75,
                "description": "修复运行时错误",
                "slots": {"target": "", "scope": "", "tech_stack": tech_stack},
                "assumptions": ["假设为运行时错误"]
            }
        elif any(k in text for k in ["重构", "refactor", "优化代码"]):
            return {
                "intent_type": "refactor",
                "confidence": 0.70,
                "description": "代码重构优化",
                "slots": {"target": "", "scope": "", "tech_stack": tech_stack},
                "assumptions": ["假设需要重构现有模块"]
            }
        elif any(k in text for k in ["测试", "test", "单测", "覆盖率"]):
            return {
                "intent_type": "test",
                "confidence": 0.72,
                "description": "编写或补充测试",
                "slots": {"target": "", "scope": "", "tech_stack": tech_stack},
                "assumptions": ["假设为单元测试"]
            }
        elif any(k in text for k in ["重构", "refactor", "优化代码"]):
            return {
                "intent_type": "refactor",
                "confidence": 0.70,
                "description": "代码重构优化",
                "slots": {"target": "", "scope": "", "tech_stack": tech_stack},
                "assumptions": ["假设需要重构现有模块"]
            }
        elif any(k in text for k in ["性能", "优化", "加速", "profiling"]):
            return {
                "intent_type": "optimize",
                "confidence": 0.68,
                "description": "性能优化",
                "slots": {"target": "", "scope": "", "tech_stack": tech_stack},
                "assumptions": ["假设存在性能瓶颈"]
            }
        elif any(k in text for k in ["设计", "架构", "方案"]):
            return {
                "intent_type": "design",
                "confidence": 0.65,
                "description": "架构设计",
                "slots": {"target": "", "scope": "", "tech_stack": tech_stack},
                "assumptions": ["假设需要新架构设计"]
            }
        elif any(k in text for k in ["迁移", "migrate", "升级", "upgrade"]):
            return {
                "intent_type": "migrate",
                "confidence": 0.68,
                "description": "版本迁移升级",
                "slots": {"target": "", "scope": "", "tech_stack": tech_stack},
                "assumptions": ["假设为版本迁移"]
            }
        else:
            # 默认 implement
            return {
                "intent_type": "implement",
                "confidence": 0.60,
                "description": "实现新功能",
                "slots": {"target": "", "scope": "", "tech_stack": tech_stack},
                "assumptions": ["假设为新功能实现"]
            }


def call_llm(prompt: str) -> Dict:
    """调用 LLM（真实环境替换为实际 API 调用）"""
    if not FLASH_API_KEY:
        # 无 API Key 时使用 Mock
        return {}
    
    # 真实实现时替换为：
    # import openai
    # client = openai.OpenAI(api_key=FLASH_API_KEY, base_url=FLASH_BASE_URL)
    # response = client.chat.completions.create(
    #     model=FLASH_MODEL,
    #     messages=[{"role": "user", "content": prompt}],
    #     temperature=0.1,
    #     response_format={"type": "json_object"}
    # )
    # return json.loads(response.choices[0].message.content)
    
    # 当前返回空，fallback 到 Mock
    return {}


def l2_analyze(normalized_text: str, tech_stack: str = "unknown", project_snippet: str = "") -> Dict:
    """L2 分析入口"""
    # 1. 构建 prompt
    prompt = L2_PROMPT_TEMPLATE.format(
        normalized_text=normalized_text,
        tech_stack=tech_stack,
        project_snippet=project_snippet or "无"
    )
    
    # 2. 调用 LLM
    result = call_llm(prompt)
    
    # 3. 无 API Key 或调用失败时 fallback 到 Mock
    if not result:
        result = MockLLM.analyze(normalized_text, tech_stack)
    
    # 4. 校验必要字段
    result.setdefault("intent_type", "implement")
    result.setdefault("confidence", 0.5)
    result.setdefault("description", normalized_text[:100])
    result.setdefault("slots", {"target": "", "scope": "", "tech_stack": tech_stack})
    result.setdefault("assumptions", [])
    
    # 5. 置信度校准（简单版）
    result["confidence"] = min(max(result["confidence"], 0.0), 1.0)
    
    return result


def route_by_confidence(confidence: float) -> str:
    """置信度路由决策"""
    if confidence >= 0.85:
        return "accept"
    elif confidence >= 0.60:
        return "clarify"
    else:
        return "upgrade_to_L3"


if __name__ == "__main__":
    # 测试入口
    text = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read().strip()
    tech_stack = sys.argv[2] if len(sys.argv) > 2 else "unknown"
    result = l2_analyze(text, tech_stack)
    route = route_by_confidence(result["confidence"])
    result["route"] = route
    print(json.dumps(result, ensure_ascii=False, indent=2)