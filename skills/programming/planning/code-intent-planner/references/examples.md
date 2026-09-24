# Typical Input/Output Case Library

## Table of Contents

- [Case 1: L1 direct hit (fix + multiple keywords)](#case-1-l1-direct-hit-fix--multiple-keywords)
- [Case 2: L1 miss, L2 Flash handles it (implement + tech stack given)](#case-2-l1-miss-l2-flash-handles-it-implement--tech-stack-given)
- [Case 3: Multiple intents coexist (primary + secondary)](#case-3-multiple-intents-coexist-primary--secondary)
- [Case 4: Cross-turn accumulation (session memory)](#case-4-cross-turn-accumulation-session-memory)
- [Case 5: Clarification protocol triggered](#case-5-clarification-protocol-triggered)
- [Case 6: Complex phrasing → L3 deep reasoning](#case-6-complex-phrasing--l3-deep-reasoning)
- [Case 7: Destructive intent (high risk, manual confirmation)](#case-7-destructive-intent-high-risk-manual-confirmation)
- [Case 8: English input](#case-8-english-input)
- [Case 9: Colloquial / vague input](#case-9-colloquial--vague-input)
- [Case 10: Edge case (no match)](#case-10-edge-case-no-match)
- [Case source notes](#case-source-notes)

> Sources: real user conversations with `code-intent-planner` + edge-case tests
> Purpose: training trigger words, validating output format, helping the model understand boundaries

---

## Case 1: L1 direct hit (fix + multiple keywords)

**Input:**
```
Help me fix this—it crashes on login, error: panic: runtime error: invalid memory address
```

**L1 match:** `fix|bug|error|crash|panic` → hits fix, confidence 0.95

**Output:**
```json
{
  "intent_type": "fix",
  "subtype": "runtime",
  "confidence": 0.95,
  "source_layer": "L1",
  "description": "Fix the runtime panic that crashes on login",
  "slots": [
    {"name": "target", "value": "", "evidence": "assumed"},
    {"name": "scope", "value": "login", "evidence": "verified"},
    {"name": "tech_stack", "value": "", "evidence": "assumed"}
  ],
  "constraints": {"hard": [], "soft": []},
  "solution": "Reproduce first → locate the stack trace → fix the null pointer → regression test"
}
```

**Rendered Markdown:**
```markdown
# Task Plan — fix_login_crash

**Intent type:** fix.runtime
**Confidence:** 0.95 (source: L1)

## Requirement overview
Fix the runtime panic that crashes on login

## Recommended approach
Reproduce first → locate the stack trace → fix the null pointer → regression test
```

---

## Case 2: L1 miss, L2 Flash handles it (implement + tech stack given)

**Input:**
```
I want to build a deployment platform like Vercel, supporting one-click deploy of Next.js projects, with a Go backend
```

**L1 match:** `build|create|implement` → hits implement, but confidence 0.88 < needs confirmation
→ escalate to L2

**L2 output (Mock):**
```json
{
  "intent_type": "implement",
  "subtype": "feature",
  "confidence": 0.90,
  "description": "Build a Vercel-like one-click deployment platform",
  "slots": {
    "target": "deployment-platform",
    "scope": "Next.js auto-deploy",
    "tech_stack": "Go backend"
  },
  "assumptions": [
    {"text": "Use PostgreSQL to store deployment records", "impact": "medium", "evidence": "provisional"},
    {"text": "Frontend uses React + TypeScript", "impact": "medium", "evidence": "provisional"}
  ]
}
```

**Output (Markdown):**
```markdown
# Task Plan — deployment_platform

**Intent type:** implement.feature
**Confidence:** 0.90 (source: L2)

## Requirement overview
Build a Vercel-like one-click deployment platform, supporting Next.js

## Task breakdown
| ID | Task | Depends on | Priority | Est. | Risk |
|----|------|------|--------|------|------|
| T1 | Design the deployment scheduling model | — | P0 | M | medium |
| T2 | Implement Git webhook reception | T1 | P0 | M | medium |
| T3 | Implement the build pipeline | T2 | P0 | L | high |
| T4 | Implement container deployment | T3 | P1 | L | high |
| T5 | Admin dashboard frontend | T3 | P2 | M | medium |

## Critical path
T1 → T2 → T3 → T4

## Assumptions
| Assumption | Confidence | Impact |
|------|--------|------|
| Use PostgreSQL | 🟡 provisional | medium |
| Frontend uses React+TS | 🟡 provisional | medium |
```

---

## Case 3: Multiple intents coexist (primary + secondary)

**Input:**
```
Look into why this endpoint errors, and by the way add a caching layer for me
```

**L1 match results:**
| Rule | Intent | Priority |
|------|------|--------|
| `error` | fix | 2 |
| `add` | implement | 10 |

**Output (multi-intent):**
```json
{
  "primary_intent": "fix",
  "secondary_intents": ["implement"],
  "multi_intent": true,
  "recommendation": "First locate the error cause (fix), then design the caching layer (implement)",
  "sub_tasks": [
    {"id": "T1", "description": "Reproduce the endpoint error", "priority": "P0", "depends_on": []},
    {"id": "T2", "description": "Locate root cause and fix", "priority": "P0", "depends_on": ["T1"]},
    {"id": "T3", "description": "Design the caching solution", "priority": "P1", "depends_on": ["T2"]},
    {"id": "T4", "description": "Implement the caching layer", "priority": "P1", "depends_on": ["T3"]}
  ]
}
```

---

## Case 4: Cross-turn accumulation (session memory)

**Turn 1:**
```
> Help me design a user permission system using the RBAC model, Python FastAPI
```
**Output:**
```json
{
  "session_id": "s1",
  "turn": 1,
  "intent_type": "design",
  "slots": {"target": "auth-system", "scope": "RBAC", "tech_stack": "python/fastapi"}
}
```

**Turn 2:**
```
> Also add role-based endpoint permission checks; I don't need the database part anymore
```
**Injected context:** `{target: auth-system, scope: RBAC, tech_stack: python/fastapi}`
**Incremental recognition:** `{target: auth-system, scope: rbac+permission-check}`

**Output (merged):**
```json
{
  "session_id": "s1",
  "turn": 2,
  "intent_type": "implement",
  "slots": {
    "target": "auth-system",
    "scope": "RBAC + endpoint permission check",
    "tech_stack": "python/fastapi",
    "excludes": "database part"
  }
}
```

---

## Case 5: Clarification protocol triggered

**Input:**
```
Help me make something
```

**L1 match:** `build` → implement (confidence 0.88 ≥ 0.85) → direct hit

But if L2 returns confidence 0.70 (gray zone):
**Output:**
```json
{
  "status": "clarification_needed",
  "questions": [
    "① What feature or module needs to be implemented? (e.g. user auth, order management)",
    "② What is the scope of the change? (new feature development / modifying existing features / code refactoring)",
    "③ What is the target tech stack? (e.g. python/fastapi, node/express)"
  ],
  "partial_intent": {
    "intent_type": "implement",
    "confidence": 0.70,
    "description": "Requirement is vague; needs clarification"
  }
}
```

---

## Case 6: Complex phrasing → L3 deep reasoning

**Input:**
```
I have an e-commerce system now; when a user places an order it calls the inventory service to deduct stock,
but under high concurrency the stock is frequently oversold,
and after a refund the stock isn't restored. I want to first analyze where the bottleneck is, then produce an optimization plan. Tech stack is Java Spring Boot + Redis.
```

**Analysis:**
- L1 hits `optimize` → optimize (confidence 0.85)
- But it contains multiple intents: analyze bottleneck + optimization plan + involves inventory/refund/high concurrency
- L2 confidence may be < 0.60 → escalate to L3

**L3 output:**
```json
{
  "intent_type": "optimize",
  "confidence": 0.88,
  "description": "E-commerce inventory overselling: dual problems of high-concurrency deduction + refund restoration",
  "sub_tasks": [
    {"id": "T1", "description": "Reproduce the oversold scenario and establish a performance baseline", "priority": "P0", "risk": "high"},
    {"id": "T2", "description": "Profile to locate the inventory deduction hotspot", "priority": "P0", "risk": "high"},
    {"id": "T3", "description": "Analyze whether the Redis cache strategy is reasonable", "priority": "P1", "risk": "medium"},
    {"id": "T4", "description": "Design an optimistic-lock / distributed-lock solution", "priority": "P1", "risk": "medium"},
    {"id": "T5", "description": "Design the refund inventory restoration mechanism", "priority": "P1", "risk": "medium"},
    {"id": "T6", "description": "Load-test to verify the optimization effect", "priority": "P2", "risk": "low"}
  ],
  "critical_path": ["T1", "T2", "T4"],
  "parallel_groups": [["T3", "T5"]],
  "solution": "Profile to locate the bottleneck first, then decide on a locking scheme (Redis atomic ops vs. distributed lock)"
}
```

---

## Case 7: Destructive intent (high risk, manual confirmation)

**Input:**
```
Delete all rows in the users table where created_at is over a year old
```

**L1 match:** `delete|remove` → destructive (confidence 0.97)

**Output (hardened version):**
```json
{
  "intent_type": "destructive",
  "confidence": 0.97,
  "risk_level": "high",
  "requires_confirmation": true,
  "confirmation_message": "⚠️ Destructive intent detected: deleting rows from the users table older than one year. This operation is irreversible. Please confirm:\n1. Have you backed up the relevant data?\n2. Is the deletion scope correct?\n3. Are there reports/caches that depend on this data?\n\nReply 'confirm deletion' to continue, otherwise abort.",
  "fallback_solution": "First use SELECT to confirm the affected row count, then run DELETE in batches, verifying after each batch before continuing"
}
```

---

## Case 8: English input

**Input:**
```
I need to refactor the authentication module to support OAuth2, and also add unit tests for the new login endpoint
```

**L1 match:**
- `refactor` → refactor (priority 6)
- `add` → implement (priority 10)

**Multi-intent output:**
```json
{
  "primary_intent": "refactor",
  "secondary_intents": ["implement"],
  "recommendation": "First refactor the auth module to support OAuth2, then write the unit tests"
}
```

---

## Case 9: Colloquial / vague input

**Input:**
```
How do I get this feature done?
```

**L1 match:** `how|how to` → plan (confidence 0.95)

**Output:**
```json
{
  "intent_type": "plan",
  "confidence": 0.95,
  "description": "Requirement planning: analysis of the feature's implementation path",
  "solution": "Requirement clarification → technical design → task breakdown → priority ranking"
}
```

---

## Case 10: Edge case (no match)

**Input:**
```
The weather is nice today
```

**L1 match:** no hit

**Output:**
```json
{
  "matched": false,
  "intent_type": null,
  "confidence": 0.0,
  "source_layer": "L1",
  "recommendation": "upgrade_to_L2"
}
```

**Behavior:** prompt the user to clarify the requirement, or hand off to L2 for broad intent recognition.

---

## Case source notes

| Case | Source | Extraction method |
|------|------|----------|
| Cases 1, 2, 3 | Real user conversations (anonymized) | Extracted from opencode session logs |
| Case 4 | XIntent cross-turn test case | Reference XIntent session tests |
| Case 5 | Clarification protocol test | Constructed low-confidence L2 output |
| Case 6 | Real production issue | From an e-commerce system optimization request |
| Case 7 | Security spec | Reference Ship-Gate destructive rules |
| Cases 8, 9, 10 | Edge tests | Constructed extreme inputs to verify robustness |
