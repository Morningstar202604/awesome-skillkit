#!/usr/bin/env python3
"""L2/L3 LLM 调用层 — 支持多种 LLM 提供商"""
import json
import os
import sys
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod


class LLMClient(ABC):
    """LLM 客户端抽象基类"""
    
    @abstractmethod
    def chat(self, prompt: str, temperature: float = 0.1) -> str:
        pass


class MockLLMClient(LLMClient):
    """测试用 Mock 客户端"""
    
    def __init__(self, layer: str = "L2"):
        self.layer = layer
    
    def chat(self, prompt: str, temperature: float = 0.1) -> str:
        if self.layer == "L2":
            return json.dumps({
                "intent_type": "implement",
                "confidence": 0.90,
                "description": "Mock L2: 实现用户认证模块",
                "slots": {"target": "auth", "scope": "login+register", "tech_stack": "python/fastapi"},
                "assumptions": [
                    {"text": "使用 JWT 认证", "impact": "high", "evidence": "verified"},
                    {"text": "使用 PostgreSQL", "impact": "medium", "evidence": "provisional"}
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
                "solution": "先设计 schema，再实现 model/service，最后加 API"
            }, ensure_ascii=False)
        else:
            return json.dumps({
                "intent_type": "implement",
                "confidence": 0.85,
                "description": "Mock L3: 实现用户认证模块，含登录注册",
                "slots": {
                    "target": "auth", "scope": "login+register", 
                    "tech_stack": "python/fastapi", "deadline": "本周",
                    "constraints": ["use JWT", "password hashing"]
                },
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
                ]
            }, ensure_ascii=False)


class OpenAICompatibleClient(LLMClient):
    """OpenAI 兼容 API 客户端"""
    
    def __init__(self, base_url: str, api_key: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        import httpx
        self.client = httpx.Client(timeout=120.0)
    
    def chat(self, prompt: str, temperature: float = 0.1) -> str:
        import httpx
        resp = self.client.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "response_format": {"type": "json_object"},
            }
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


def get_llm_client(layer: str) -> LLMClient:
    """根据环境变量获取 LLM 客户端"""
    # 开发/测试环境：使用 Mock
    if os.getenv("USE_MOCK_LLM", "true").lower() == "true":
        return MockLLMClient(layer)
    
    # 生产环境：从环境变量读取配置
    base_url = os.getenv(f"{layer}_BASE_URL", os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"))
    api_key = os.getenv(f"{layer}_API_KEY", os.getenv("LLM_API_KEY"))
    model = os.getenv(f"{layer}_MODEL", os.getenv("LLM_MODEL", "gpt-4o-mini"))
    
    if not api_key:
        print(f"Warning: {layer} API key not set, falling back to Mock", file=sys.stderr)
        return MockLLMClient(layer)
    
    return OpenAICompatibleClient(base_url, api_key, model)


# L2 Prompt 模板
L2_PROMPT = """你是一位资深软件工程师，正在分析用户的编程需求。

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


# L3 Prompt 模板
L3_PROMPT = """你是一位系统架构师，需要将用户需求分解为可执行任务计划。

原始输入：{raw_input}
规范化后：{normalized_text}
技术栈：{tech_stack}
项目结构片段：
{project_snippet}

已识别意图：{intent_type}
已知槽位：{slots_json}
跨轮上下文：{last_intent_json}

请仅返回以下 JSON，不要任何其他内容：

{{
  "intent_type": "implement|fix|refactor|review|test|optimize|plan|design|migrate|destructive",
  "confidence": 0.0-1.0,
  "description": "需求完整描述",
  "slots": {{
    "target": "",
    "scope": "",
    "tech_stack": "",
    "deadline": "",
    "constraints": []
  }},
  "sub_tasks": [
    {{
      "id": "T1",
      "description": "任务描述",
      "depends_on": [],
      "priority": "P0|P1|P2",
      "effort": "S|M|L",
      "risk": "low|medium|high"
    }}
  ],
  "critical_path": ["T1", "T3"],
  "parallel_groups": [["T2", "T4"]],
  "solution": "推荐实现路径的简述",
  "assumptions": [
    {{"text": "假设内容", "impact": "low|medium|high", "evidence": "verified|provisional|assumed"}}
  ]
}}

约束：
- sub_tasks 粒度：单任务 1-4 小时
- depends_on 必须显式声明，无依赖用空数组
- critical_path 必须是 sub_tasks 中实际存在的 ID
- priority：P0=关键路径阻塞项，P1=重要不阻塞，P2=常规
- solution 必须对应 intent_type 的标准方案模板
"""


def call_l2(normalized_text: str, tech_stack: str = "", project_snippet: str = "") -> Dict[str, Any]:
    """调用 L2 Flash LLM"""
    client = get_llm_client("L2")
    prompt = L2_PROMPT.format(
        normalized_text=normalized_text,
        tech_stack=tech_stack or "unknown",
        project_snippet=project_snippet or "无"
    )
    try:
        response = client.chat(prompt, temperature=0.1)
        return json.loads(response)
    except json.JSONDecodeError as e:
        return {"error": f"L2 JSON 解析失败: {e}", "raw": response}
    except Exception as e:
        return {"error": f"L2 调用失败: {e}"}


def call_l3(
    raw_input: str,
    normalized_text: str,
    tech_stack: str,
    project_snippet: str,
    intent_type: str,
    slots: Dict[str, Any],
    last_intent: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """调用 L3 Pro LLM"""
    client = get_llm_client("L3")
    prompt = L3_PROMPT.format(
        raw_input=raw_input,
        normalized_text=normalized_text,
        tech_stack=tech_stack or "unknown",
        project_snippet=project_snippet or "无",
        intent_type=intent_type,
        slots_json=json.dumps(slots, ensure_ascii=False),
        last_intent_json=json.dumps(last_intent, ensure_ascii=False) if last_intent else "无"
    )
    try:
        response = client.chat(prompt, temperature=0.2)
        return json.loads(response)
    except json.JSONDecodeError as e:
        return {"error": f"L3 JSON 解析失败: {e}", "raw": response}
    except Exception as e:
        return {"error": f"L3 调用失败: {e}"}


if __name__ == "__main__":
    # 简单测试
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--layer", choices=["L2", "L3"], default="L2")
    parser.add_argument("--input", required=True)
    args = parser.parse_args()
    
    if args.layer == "L2":
        result = call_l2(args.input)
    else:
        result = call_l3(args.input, args.input, "", "", "implement", {})
    print(json.dumps(result, ensure_ascii=False, indent=2))