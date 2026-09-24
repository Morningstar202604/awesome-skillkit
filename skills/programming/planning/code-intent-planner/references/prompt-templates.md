# Prompt Template Library

## Table of Contents

- [L2 Flash LLM Prompt](#l2-flash-llm-prompt)
- [L3 Pro LLM Prompt](#l3-pro-llm-prompt)
- [Clarification Questions Generation Prompt](#clarification-questions-generation-prompt)
- [Plan Rendering Prompt (optional, for generating markdown)](#plan-rendering-prompt-optional-for-generating-markdown)

## L2 Flash LLM Prompt

```markdown
You are a senior software engineer analyzing a user's programming request.

Task: identify the user's intent type, extract key slots, and give a confidence score.

User input: {normalized_text}
Project tech stack: {tech_stack}
Project structure snippet (optional): {project_snippet}

Return ONLY the following JSON, with nothing else:

{
  "intent_type": "implement|fix|refactor|review|test|optimize|plan|design|migrate|destructive",
  "confidence": 0.0-1.0,
  "description": "one-sentence requirement description",
  "slots": {
    "target": "target module/file, e.g. auth, user-service",
    "scope": "change scope, e.g. login+register, api-only",
    "tech_stack": "tech stack, e.g. python/fastapi, node/express"
  },
  "assumptions": ["assumption 1", "assumption 2"]
}
```

**Constraints**:
- confidence must honestly reflect your degree of certainty
- leave slots you cannot determine as empty strings
- assumptions lists the assumptions you made to reach the conclusion

---

## L3 Pro LLM Prompt

```markdown
You are a system architect who must break the user's request down into an executable task plan.

Raw input: {raw_input}
Normalized: {normalized_text}
Tech stack: {tech_stack}
Project structure snippet:
{project_snippet}

Recognized intent: {intent_type}
Known slots: {slots_json}
Cross-turn context: {last_intent_json}

Return ONLY the following JSON, with nothing else:

{
  "intent_type": "implement|fix|refactor|review|test|optimize|plan|design|migrate|destructive",
  "confidence": 0.0-1.0,
  "description": "full requirement description",
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
      "description": "task description",
      "depends_on": [],
      "priority": "P0|P1|P2",
      "effort": "S|M|L",
      "risk": "low|medium|high"
    }
  ],
  "critical_path": ["T1", "T3"],
  "parallel_groups": [["T2", "T4"]],
  "solution": "brief description of the recommended implementation path",
  "assumptions": [
    {"text": "assumption content", "impact": "low|medium|high", "evidence": "verified|provisional|assumed"}
  ]
}
```

**Constraints**:
- sub_tasks granularity: a single task is 1-4 hours
- depends_on must be declared explicitly; use an empty array when there are no dependencies
- critical_path must be IDs that actually exist in sub_tasks
- priority: P0 = critical-path blocker, P1 = important but not blocking, P2 = routine
- solution must correspond to the standard solution template for the intent_type

---

## Clarification Questions Generation Prompt

```markdown
User input: {normalized_text}
Current recognition result: intent={intent_type}, confidence={confidence}
Missing slots: {missing_slots}
Ambiguity points: {ambiguity_points}

Generate at most 3 clarification questions, requiring:
1. Each question targets one key missing piece of information
2. The questions are specific, answerable, and unambiguous
3. Give an example answer format

Output format:
[
  "question 1 (example: answer format)",
  "question 2 (example: answer format)",
  "question 3 (example: answer format)"
]
```

---

## Plan Rendering Prompt (optional, for generating markdown)

```markdown
Input: structured intent JSON (see output format)

Output: a task plan document in markdown

Includes:
1. Title: Task Plan — {session_id}
2. Intent type, confidence, source layer, generation time
3. Requirement overview
4. Known constraints (hard/soft)
5. Task breakdown table (ID, task, depends on, priority, estimate, risk)
6. Critical path
7. Parallelizable groups
8. Assumptions and pending-confirmation table
9. Recommended approach
```
