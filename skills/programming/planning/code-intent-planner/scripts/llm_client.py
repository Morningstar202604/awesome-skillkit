#!/usr/bin/env python3
"""L2/L3 LLM call layer -- supports multiple LLM providers"""
import json
import os
import sys
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod


class LLMClient(ABC):
    """Abstract base class for an LLM client"""
    
    @abstractmethod
    def chat(self, prompt: str, temperature: float = 0.1) -> str:
        pass


class MockLLMClient(LLMClient):
    """Mock client for testing"""

    def __init__(self, layer: str = "L2"):
        self.layer = layer

    def chat(self, prompt: str, temperature: float = 0.1) -> str:
        if self.layer == "L2":
            return json.dumps({
                "intent_type": "implement",
                "confidence": 0.90,
                "description": "Mock L2: implement the user authentication module",
                "slots": {"target": "auth", "scope": "login+register", "tech_stack": "python/fastapi"},
                "assumptions": [
                    {"text": "use JWT authentication", "impact": "high", "evidence": "verified"},
                    {"text": "use PostgreSQL", "impact": "medium", "evidence": "provisional"}
                ],
                "constraints": {"hard": [], "soft": ["use JWT", "bcrypt password hashing"]},
                "sub_tasks": [
                    {"id": "T1", "description": "design the user data model", "depends_on": [], "priority": "P0", "effort": "S", "risk": "low"},
                    {"id": "T2", "description": "implement the password hashing utility", "depends_on": ["T1"], "priority": "P0", "effort": "S", "risk": "low"},
                    {"id": "T3", "description": "implement JWT token generation/validation", "depends_on": ["T2"], "priority": "P0", "effort": "M", "risk": "medium"},
                    {"id": "T4", "description": "implement the login/register API", "depends_on": ["T3"], "priority": "P1", "effort": "M", "risk": "medium"},
                    {"id": "T5", "description": "write unit tests", "depends_on": ["T4"], "priority": "P1", "effort": "S", "risk": "low"},
                ],
                "critical_path": ["T1", "T2", "T3", "T4"],
                "parallel_groups": [],
                "solution": "design the schema first, then implement model/service, and finally add the API"
            }, ensure_ascii=False)
        else:
            return json.dumps({
                "intent_type": "implement",
                "confidence": 0.85,
                "description": "Mock L3: implement the user authentication module, including login and register",
                "slots": {
                    "target": "auth", "scope": "login+register",
                    "tech_stack": "python/fastapi", "deadline": "this week",
                    "constraints": ["use JWT", "password hashing"]
                },
                "sub_tasks": [
                    {"id": "T1", "description": "design the user data model", "depends_on": [], "priority": "P0", "effort": "S", "risk": "low"},
                    {"id": "T2", "description": "implement the password hashing utility", "depends_on": ["T1"], "priority": "P0", "effort": "S", "risk": "low"},
                    {"id": "T3", "description": "implement JWT token generation/validation", "depends_on": ["T2"], "priority": "P0", "effort": "M", "risk": "medium"},
                    {"id": "T4", "description": "implement the login/register API", "depends_on": ["T3"], "priority": "P1", "effort": "M", "risk": "medium"},
                    {"id": "T5", "description": "write unit tests", "depends_on": ["T4"], "priority": "P1", "effort": "S", "risk": "low"},
                ],
                "critical_path": ["T1", "T2", "T3", "T4"],
                "parallel_groups": [],
                "solution": "design the schema first, then implement model/service, and finally add the API",
                "assumptions": [
                    {"text": "use PostgreSQL", "impact": "medium", "evidence": "provisional"},
                    {"text": "use JWT authentication", "impact": "high", "evidence": "verified"}
                ]
            }, ensure_ascii=False)


class OpenAICompatibleClient(LLMClient):
    """OpenAI-compatible API client"""
    
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
    """Get the LLM client based on environment variables"""
    # dev/test environment: use Mock
    if os.getenv("USE_MOCK_LLM", "true").lower() == "true":
        return MockLLMClient(layer)

    # production environment: read config from environment variables
    base_url = os.getenv(f"{layer}_BASE_URL", os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"))
    api_key = os.getenv(f"{layer}_API_KEY", os.getenv("LLM_API_KEY"))
    model = os.getenv(f"{layer}_MODEL", os.getenv("LLM_MODEL", "gpt-4o-mini"))
    
    if not api_key:
        print(f"Warning: {layer} API key not set, falling back to Mock", file=sys.stderr)
        return MockLLMClient(layer)
    
    return OpenAICompatibleClient(base_url, api_key, model)


# L2 Prompt template
L2_PROMPT = """You are a senior software engineer analyzing a user's programming request.

Task: identify the user's intent type, extract key slots, and give a confidence.

User input: {normalized_text}
Project tech stack: {tech_stack}
Project structure snippet (optional): {project_snippet}

Return ONLY the following JSON, with nothing else:

{{
  "intent_type": "implement|fix|refactor|review|test|optimize|plan|design|migrate|destructive",
  "confidence": 0.0-1.0,
  "description": "one-sentence requirement description",
  "slots": {{
    "target": "target module/file, e.g. auth, user-service",
    "scope": "change scope, e.g. login+register, api-only",
    "tech_stack": "tech stack, e.g. python/fastapi, node/express"
  }},
  "assumptions": ["assumption 1", "assumption 2"]
}}

Constraints:
- confidence must honestly reflect your certainty
- leave slots you cannot determine as an empty string
- assumptions lists the assumptions you made to reach your conclusion
"""


# L3 Prompt template
L3_PROMPT = """You are a system architect who must decompose the user's requirement into an executable task plan.

Raw input: {raw_input}
Normalized: {normalized_text}
Tech stack: {tech_stack}
Project structure snippet:
{project_snippet}

Recognized intent: {intent_type}
Known slots: {slots_json}
Cross-turn context: {last_intent_json}

Return ONLY the following JSON, with nothing else:

{{
  "intent_type": "implement|fix|refactor|review|test|optimize|plan|design|migrate|destructive",
  "confidence": 0.0-1.0,
  "description": "full requirement description",
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
      "description": "task description",
      "depends_on": [],
      "priority": "P0|P1|P2",
      "effort": "S|M|L",
      "risk": "low|medium|high"
    }}
  ],
  "critical_path": ["T1", "T3"],
  "parallel_groups": [["T2", "T4"]],
  "solution": "brief description of the recommended implementation path",
  "assumptions": [
    {{"text": "assumption content", "impact": "low|medium|high", "evidence": "verified|provisional|assumed"}}
  ]
}}

Constraints:
- sub_tasks granularity: a single task takes 1-4 hours
- depends_on must be declared explicitly; use an empty array when there are no dependencies
- critical_path must be IDs that actually exist in sub_tasks
- priority: P0 = critical-path blocker, P1 = important but non-blocking, P2 = routine
- solution must match the standard solution template for intent_type
"""


def call_l2(normalized_text: str, tech_stack: str = "", project_snippet: str = "") -> Dict[str, Any]:
    """Call the L2 Flash LLM"""
    client = get_llm_client("L2")
    prompt = L2_PROMPT.format(
        normalized_text=normalized_text,
        tech_stack=tech_stack or "unknown",
        project_snippet=project_snippet or "none"
    )
    try:
        response = client.chat(prompt, temperature=0.1)
        return json.loads(response)
    except json.JSONDecodeError as e:
        return {"error": f"L2 JSON parsing failed: {e}", "raw": response}
    except Exception as e:
        return {"error": f"L2 call failed: {e}"}


def call_l3(
    raw_input: str,
    normalized_text: str,
    tech_stack: str,
    project_snippet: str,
    intent_type: str,
    slots: Dict[str, Any],
    last_intent: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Call the L3 Pro LLM"""
    client = get_llm_client("L3")
    prompt = L3_PROMPT.format(
        raw_input=raw_input,
        normalized_text=normalized_text,
        tech_stack=tech_stack or "unknown",
        project_snippet=project_snippet or "none",
        intent_type=intent_type,
        slots_json=json.dumps(slots, ensure_ascii=False),
        last_intent_json=json.dumps(last_intent, ensure_ascii=False) if last_intent else "none"
    )
    try:
        response = client.chat(prompt, temperature=0.2)
        return json.loads(response)
    except json.JSONDecodeError as e:
        return {"error": f"L3 JSON parsing failed: {e}", "raw": response}
    except Exception as e:
        return {"error": f"L3 call failed: {e}"}


if __name__ == "__main__":
    # simple test
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