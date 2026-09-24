---
name: code-intent-planner
description: "Three-tier waterfall intent recognition (L1 regex <10ms, L2 Flash LLM, L3 Pro LLM) that classifies user intent into 10 types, decomposes tasks, and produces execution plans with evidence grading. Use when the user describes a coding task and needs structured planning before implementation, clarifying requirements, producing an implementation plan, or turning a vague requirement into something concrete. Do NOT use for implementing the planned code itself (planning and orchestration only)."
license: Apache-2.0
compatibility: Requires network access and docker. No API keys required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: planning
  pattern: intent-planner
  tier: powerful
  verified-date: "2026-09-09"
---

# Code Intent Planner

Recognizes a programming request as a structured intent + task decomposition + solution recommendations.
Three-tier waterfall: L1 rules (<10ms) → L2 Flash LLM (confidence routing) → L3 Pro LLM (complex scenarios).
All commands are run from the skill directory (the directory containing this file).

## Input Checklist

| Input | Required | Description | Default |
|------|------|------|--------|
| raw_input | Yes | The user's raw input (natural language) | — |
| session_id | No | Session identifier (for cross-turn accumulation) | Auto-generated session_<timestamp> |
| project_root | No | Project root directory | Auto-detected (see pre-flight) |

When missing, ask all at once: "Please provide: (1) your requirement description. I'll handle the project directory and session_id automatically."

## Pre-flight Checks

Run in order; if a fatal item fails → fix it, then STOP; don't push through with known issues.

```bash
# 1. Python available (fatal)
python3 --version          # Expected: Python 3.x; failure → install python3, then STOP

# 2. Script in place (fatal; must run from the skill directory)
test -f scripts/pipeline.py && echo OK   # Expected: OK; failure → cd to the skill directory and retry; still failing → STOP

# 3. Detect the project root (non-fatal; the script has the same logic built in)
for dir in . .. ../..; do
  for f in package.json pyproject.toml go.mod Cargo.toml pom.xml build.gradle requirements.txt; do
    [ -f "$dir/$f" ] && echo "$dir" && exit 0
  done
done
echo "."
```

- Detection 3 expected: prints the project root path. On failure (no project marker file): use the current directory, mark tech_stack as unknown (explicit degradation; can continue).
- Only needed for `--no-mock` (real LLM): `test -n "$LLM_API_KEY"` expected non-empty; on failure → export `LLM_API_KEY` (and `LLM_BASE_URL`/`LLM_MODEL` as needed) and retry. Credentials go through environment variables only, never into files or the command line.
- Default mock mode (`USE_MOCK_LLM=true`): makes no real network request; get the flow working first, then switch to the real LLM.

## Parameter Cheat Sheet

`python3 scripts/pipeline.py` (run):

| Parameter | Values | Description |
|------|------|------|
| input (positional) | Natural-language text | The user's raw input; defaults to printing help and exit 1 |
| --session / -s | string | Session ID, for cross-turn accumulation |
| --project / -p | directory path | Project root directory |
| --skip-normalization | switch | Skip input normalization |
| --no-mock | switch | Use the real LLM (requires env vars like LLM_API_KEY) |
| --format / -f | markdown / json | Output format, default markdown |
| --output / -o | file path | Write to a file; defaults to stdout |

## Workflow

### Step 1: Run the three-tier waterfall pipeline

Action (run):

```bash
# Default mock; verify the flow first
python3 scripts/pipeline.py "add login to the auth module for me" --format json
# Real LLM (after configuring env vars)
python3 scripts/pipeline.py "add login to the auth module for me" --no-mock --format json
# Reuse a session (cross-turn accumulation)
python3 scripts/pipeline.py "continue, add registration" -s session_20260916_100000 --format json
```

Expected: stdout outputs JSON with `intent_type`, `confidence`, `source_layer`, `slots`, `sub_tasks`, exit code 0.
On failure: exit code 1 and the JSON has an `error` field (e.g. `L2 failed: ...`/`L3 failed: ...`) → see the failure-handling table; with `--format markdown` it renders as a plan document.

### Step 2: Input normalization and cache check (done automatically by the script)

Action (internal read logic): in order, do a cache-hit check → coreference resolution ("it/this/that" replaced with the previous turn's `last_intent.slots.target`) → ellipsis completion ("help me write" → "help me write code") → term standardization ("backend/server/API" → backend).
Expected: get `normalized_text`; within the same session, identical intent_type + similar input hits the cache directly (cache_key = `session_id:intent_type:hash(normalized[:100])`) and doesn't call the LLM again.
On failure (no cache): proceed normally into L1.

### Step 3: L1 rule-layer decision (zero LLM, <10ms)

Match in priority order; the first hit with confidence ≥ 0.85 → output directly (`source_layer=L1`), skipping L2/L3:

| Rule | Intent | Confidence | Priority |
|------|------|--------|--------|
| `delete\|remove\|uninstall\|destroy` | destructive | 0.97 | 1 |
| `fix\|bug\|error\|crash\|panic` | fix | 0.95 | 2 |
| `test\|unit test\|coverage` | test | 0.90 | 3 |
| `review\|code.?review\|audit\|inspect` | review | 0.92 | 4 |
| `plan\|break.?down\|analyze.*requirement\|how to` | plan | 0.95 | 5 |
| `refactor\|clean up code` | refactor | 0.90 | 6 |
| `performance\|speed up\|profiling\|bottleneck` | optimize | 0.85 | 7 |
| `design\|architecture\|design proposal` | design | 0.82 | 8 |
| `migrate\|upgrade\|version upgrade` | migrate | 0.88 | 9 |
| `implement\|build\|create\|add\|develop` | implement | 0.88 | 10 |

Expected: output intent_type + confidence; note that design (0.82) is below the 0.85 threshold and will actually fall into L2 review.
On failure (no match) → escalate to L2.

### Step 4: L2 Flash LLM and confidence routing

Model: Flash/Mini (e.g. deepseek-v4-flash, glm-4-flash). Prompt template (injected by the script):

```text
Analyze the user's programming intent; return JSON only:
{
  "intent_type": "<implement|fix|refactor|review|test|optimize|plan|design|migrate|destructive>",
  "confidence": <0.0-1.0>,
  "description": "<short requirement summary>",
  "slots": {"target": "", "scope": "", "tech_stack": ""},
  "assumptions": ["<assumption 1>"]
}

User input: "{normalized_text}"
Project tech stack: {tech_stack}
```

Confidence routing:

| Confidence | Action |
|--------|------|
| ≥ 0.85 | Accept → Step 6 |
| 0.60 - 0.85 | Clarification protocol (see below) |
| < 0.60 | Escalate to L3 |

Expected: returns parseable JSON. On failure (an error field) → failure-handling table (mostly LLM endpoint/key issues).

### Step 5: L3 Pro LLM fallback (complex scenarios)

Trigger: L2 confidence < 0.60, or five classes of complex scenarios: (1) complex expression (implicit multi-layer requirements) (2) cross-turn context ("continue from last time") (3) intent switch (changing goal mid-way) (4) multi-intent decomposition (one request, multiple subtasks) (5) implicit-info completion (needs project context to infer).
Model: Pro/reasoning model. Prompt template (injected by the script):

```text
You are an architect; decompose the requirement into executable tasks. Return JSON only:

Raw input: "{raw_input}"
After normalization: "{normalized_text}"
Tech stack: {tech_stack}
Project structure snippet:
{project_structure_snippet}

Known intent: {intent_type}
Known slots: {slots_json}

{
  "intent_type": "...",
  "confidence": <0.0-1.0>,
  "sub_tasks": [
    {"id": "T1", "description": "...", "depends_on": [], "priority": "P0", "effort": "S", "risk": "low"}
  ],
  "critical_path": ["T1", "T3"],
  "parallel_groups": [["T2", "T4"]],
  "solution": "recommended implementation path",
  "assumptions": [{"text": "...", "impact": "medium", "evidence": "provisional"}]
}
```

Expected: the JSON contains `sub_tasks`/`critical_path`/`parallel_groups`. On failure → failure-handling table.

### Step 6: Interpret output and render deliverables

Slot evidence grading (the output `slots[].evidence` field):

| Source | Evidence level | Example |
|------|--------|------|
| User explicitly specified | verified | "modify the auth module" → target=auth |
| L1 rule inference | verified | contains "bug" + "crash" → fix.runtime |
| L2 LLM output | provisional | L2 infers target=api |
| Project context | provisional | infer tech_stack from package.json |
| Model guess | assumed | No evidence; must be flagged |

Hard constraints (user explicitly specified, cannot be violated) take precedence over soft constraints (suggestions, adjustable).
Recommended implementation path by intent type:

| Intent type | Recommended implementation path |
|---------|-------------|
| implement.feature | design → implement → test |
| implement.api | API contract first → implement each layer |
| fix.runtime | reproduce → locate → fix → regression test |
| fix.security | assess impact → fix → security scan → upgrade dependencies |
| refactor | analyze impact → protect tests → small-step refactor → verify |
| test.coverage | analyze blind spots → add tests → verify |
| optimize | baseline → profiling → optimize → regression |
| design | clarify requirements → draft proposal → selection rationale → review |
| migrate | compatibility analysis → plan → pilot → full rollout |
| destructive | risk assessment → backup → confirm → execute → verify |

See [references/solution-templates.md](references/solution-templates.md) for details.
The destructive intent is a security red line: before any delete/destroy action, you must back up first and get the user's explicit confirmation.

Action (run): `python3 scripts/pipeline.py "<raw_input>" --format markdown -o plans/<session_id>_<YYYYMMDD>.md`
Expected: generate a Markdown plan document.
On failure: the plans/ directory doesn't exist → `mkdir -p plans` first, then rerun.

---

## Clarification Protocol

**Trigger**: L2 confidence 0.60-0.85 and the ambiguity can't be resolved, or required slots are missing (in which case the pipeline returns `status=clarification_needed` + a `questions` list).

**Follow-up template** (ask all at once, at most 3 questions):
```text
To plan accurately, please confirm:
(1) [question 1]
(2) [question 2]
(3) [question 3]
If unsure for now, you may answer "TBD".
```

**Max clarification rounds**: 3 rounds. Beyond that → degrade to a conservative proposal, flagging all assumptions.

---

## Cross-Turn Accumulation and Sessions

- Real state-file location: `~/.code_intent_planner/sessions/_session_<session_id>.json` (override with the env var `SKILLKIT_SESSION_DIR`; the script doesn't write session files into the project directory, and don't edit them by hand).

```json
{
  "session_id": "...",
  "turn": 2,
  "last_intent": {"type": "implement", "slots": {"target": "auth"}},
  "slots_history": [...],
  "cache": {...}
}
```

- Merge strategy: latest-wins + conflict detection. On conflict, mark provisional and ask the user to adjudicate.
- Injection rule: on the next turn's input, automatically inject `last_intent.slots` into context.

---

## Failure Handling Table

| Symptom / error code | Cause | Action |
|------|------|------|
| L1 no match | Input lacks rule keywords | Normal branch: escalate to L2 |
| L2 confidence 0.60-0.85 | Ambiguous input | Follow the clarification protocol; at most 3 rounds, beyond that → degrade to a conservative proposal and flag all assumptions |
| L2 confidence < 0.60 | Complex/multi-intent input | Escalate to L3 |
| Exit code 1, JSON contains `L2 failed: ...` / `L3 failed: ...` | LLM endpoint unreachable or key invalid | Check `LLM_API_KEY`/`LLM_BASE_URL`/`LLM_MODEL`; or verify the flow first with the default mock mode |
| Prints help + exit 1 | No input positional argument provided | Provide raw_input and rerun |
| Project detection failed | Directory has no project marker files | Continue; tech_stack = unknown |
| Session state lost | State directory cleaned / machine changed | Start a new session; no cross-turn accumulation |

---

## Output Formats

### Structured JSON

```json
{
  "intent_type": "implement",
  "confidence": 0.92,
  "source_layer": "L2",
  "description": "Implement the user-authentication module",
  "slots": [
    {"name": "target", "value": "auth", "evidence": "verified"},
    {"name": "scope", "value": "login+register", "evidence": "provisional"}
  ],
  "constraints": {"hard": [], "soft": ["use JWT"]},
  "sub_tasks": [
    {"id": "T1", "description": "Design the user data model", "depends_on": [], "priority": "P0", "effort": "S", "risk": "low"}
  ],
  "critical_path": ["T1"],
  "solution": "Design the schema first, then implement the model, finally add the API",
  "assumptions": [{"text": "Use PostgreSQL", "impact": "medium", "evidence": "provisional"}],
  "session_id": "...",
  "timestamp": "2026-09-08T10:00:00Z"
}
```

### Markdown plan document

Save path: `plans/<session_id>_<YYYYMMDD>.md`

Structure:
1. Requirement overview
2. Known constraints (hard/soft)
3. Task breakdown table
4. Critical path
5. Parallelizable groups
6. Assumptions and items to confirm
7. Recommended solution

---

## Delivery Criteria

- Definition of success: exit code 0, the output JSON has no `error` field and contains `intent_type`/`confidence`/`source_layer`; returning `status=clarification_needed` + a question list is also a valid output.
- Artifact naming: Markdown plan `plans/<session_id>_<YYYYMMDD>.md`; the JSON result is persisted to a path specified with `-o` as needed.
- Save location: plan documents go in the project root `plans/`; session state is written by the script to `~/.code_intent_planner/sessions/`.
- Completeness verification: `python3 -m json.tool <output>.json` parses cleanly; the plan document has the 7 sections above; `source_layer` matches the actual routing layer; all `assumed`-evidence-level assumptions are explicitly flagged.

---

## References

- references/solution-templates.md — read after Step 6 selects the intent type, to apply the corresponding solution template
- references/prompt-templates.md — read when you need to adjust the L2/L3 prompt (switch models / change output fields)
- references/gotchas.md — read when results are abnormal or confidence is systematically low (common pitfalls and anti-patterns)
- references/examples.md — read when calibrating the judgment standard (10 real cases, including edge scenarios)
