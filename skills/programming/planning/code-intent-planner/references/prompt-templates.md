# Prompt 模板库

## L2 Flash LLM Prompt

```markdown
你是一位资深软件工程师，正在分析用户的编程需求。

任务：识别用户意图类型，提取关键槽位，给出置信度。

用户输入：{normalized_text}
项目技术栈：{tech_stack}
项目结构片段（可选）：{project_snippet}

请仅返回以下 JSON，不要任何其他内容：

{
  "intent_type": "implement|fix|refactor|review|test|optimize|plan|design|migrate|destructive",
  "confidence": 0.0-1.0,
  "description": "一句话需求描述",
  "slots": {
    "target": "目标模块/文件，如 auth、user-service",
    "scope": "改动范围，如 login+register、api-only",
    "tech_stack": "技术栈，如 python/fastapi、node/express"
  },
  "assumptions": ["假设1", "假设2"]
}
```

**约束**：
- confidence 必须诚实反映确信程度
- 无法确定的槽位留空字符串
- assumptions 列出你为得出结论而做的假设

---

## L3 Pro LLM Prompt

```markdown
你是一位系统架构师，需要将用户需求分解为可执行任务计划。

原始输入：{raw_input}
规范化后：{normalized_text}
技术栈：{tech_stack}
项目结构片段：
{project_snippet}

已识别意图：{intent_type}
已知槽位：{slots_json}
跨轮上下文：{last_intent_json}

请仅返回以下 JSON，不要任何其他内容：

{
  "intent_type": "implement|fix|refactor|review|test|optimize|plan|design|migrate|destructive",
  "confidence": 0.0-1.0,
  "description": "需求完整描述",
  "slots": {
    "target": "",
    "scope": "",
    "tech_stack": "",
    "deadline": "",
    "constraints": []
  },
  "sub_tasks": [
    {
      "id": "T1",
      "description": "任务描述",
      "depends_on": [],
      "priority": "P0|P1|P2",
      "effort": "S|M|L",
      "risk": "low|medium|high"
    }
  ],
  "critical_path": ["T1", "T3"],
  "parallel_groups": [["T2", "T4"]],
  "solution": "推荐实现路径的简述",
  "assumptions": [
    {"text": "假设内容", "impact": "low|medium|high", "evidence": "verified|provisional|assumed"}
  ]
}
```

**约束**：
- sub_tasks 粒度：单任务 1-4 小时
- depends_on 必须显式声明，无依赖用空数组
- critical_path 必须是 sub_tasks 中实际存在的 ID
- priority：P0=关键路径阻塞项，P1=重要不阻塞，P2=常规
- solution 必须对应 intent_type 的标准方案模板

---

## 澄清问题生成 Prompt

```markdown
用户输入：{normalized_text}
当前识别结果：intent={intent_type}, confidence={confidence}
缺失槽位：{missing_slots}
歧义点：{ambiguity_points}

请生成最多 3 个澄清问题，要求：
1. 每个问题针对一个关键缺失信息
2. 问题具体、可回答、不模糊
3. 给出示例回答格式

输出格式：
[
  "问题1（示例：回答格式）",
  "问题2（示例：回答格式）",
  "问题3（示例：回答格式）"
]
```

---

## 计划渲染 Prompt（可选，用于生成 markdown）

```markdown
输入：结构化意图 JSON（见输出格式）

输出：markdown 格式的任务计划文档

包含：
1. 标题：任务计划 — {session_id}
2. 意图类型、置信度、来源层、生成时间
3. 需求概述
4. 已知约束（硬/软）
5. 任务分解表（ID、任务、依赖、优先级、预估、风险）
6. 关键路径
7. 可并行组
8. 假设与待确认表
9. 推荐方案
```