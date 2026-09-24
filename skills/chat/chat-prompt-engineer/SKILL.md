---
name: chat-prompt-engineer
description: "Engineer and audit prompts for conversational AI assistants (Doubao, ChatGPT, Kimi, DeepSeek, in-app chat models): the five-element formula (role + background + task + requirements + format) for one-shot task prompts, the five-section skeleton (persona / capability-flow / constraints / output-format / boundary) for agent system prompts, and reverse constraints that cut filler. Two modes: write a prompt from a rough request, or audit an existing prompt / system prompt and report missing elements. Use when the user asks to write prompts / Doubao prompts / prompt optimization / agent persona / system prompt / prompt audit / prompt audit / make the AI obey / prompt engineering / chatbot / conversation / dialogue / AI assistant. Do NOT use for text-to-video or image-generation prompts (those structures live in the video-prompt-engineer skill), nor for agent framework code (that is agent-designer)."
license: Apache-2.0
compatibility: Pure prompt-based; the bundled prompt_audit.py needs Python 3.8+ only.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: chat
  pattern: dual-mode
  tier: standard
  verified-date: "2026-09-14"
---

# Chat Prompt Engineer

Write and audit prompts for conversational AI assistants (Doubao / ChatGPT / Kimi / DeepSeek, etc.). The core is the **five-element formula** — chat models cannot read minds; miss one element and they free-fill one, and free-filling is where filler comes from. It is isomorphic to `video-prompt-engineer`'s six slots: that side manages "a complete picture," this side manages "a complete intent."

## Input Checklist

| Input | Required | Notes |
|------|------|------|
| Mode | Yes | `task` (one-shot task prompt) \| `agent` (agent system prompt) |
| Rough request | write yes | The user's own words, even if only one line: "help me write a Xiaohongshu post" |
| Target platform | No | Defaults to generic Doubao-family phrasing; a named platform uses its dialect (see references/platform-dialects.md) |
| Audience / use case | No | When missing, ask proactively; do not guess |
| Prompt to audit | audit yes | Paste the original text |

When inputs are missing, ask for all at once: "Please provide: ① the mode (task one-shot / agent persona); ② the rough request or the original prompt to audit; ③ the target platform and audience (optional; defaults to generic Doubao-family)."

## Pre-flight Self-check

- write mode: does the rough request contain a **task with a clear verb**? "help me deal with this" has no task verb — ask first.
- audit mode: do you have the text to audit? If not, get it first; do not audit from memory.
- agent mode: confirm the user wants a **persona contract** (long-term behavior rules), not a one-off task — the two have completely different structures.

## Workflow

### Step 1 (task mode): Fill in the Five Elements

```text
[role] + [background] + [task] + [requirements] + [format]
```

Rules (each backed by a hard-won failure case):

- The role is **specific to job + experience**: "you are an AI-tools tutorial editor for beginners," not "you are a helpful assistant"
- The background **answers who it is for and what it is used for** — the use case directly decides the output style; one line like "the use case is a business email" beats ten lines of tone words
- The task verb is **specific**: "rewrite this copy into a version fit for publishing on Xiaohongshu," not "optimize it a bit"
- For requirements, **write reverse constraints first**: hard word limits, banned-word lists, "it only passes if removing any sentence leaves the meaning incomplete" — "what not to do" cuts more filler than "what to do"
- The format **locks the structure**: "core conclusion in 1-2 sentences → bullet out ≤5 points → action recommendation"; from then on the model output needs no layout work

Expected: the produced prompt has all five elements; running `python3 scripts/prompt_audit.py --prompt "<text>"` returns 5/5.

### Step 2 (agent mode): Write the System Prompt from the Five-Section Skeleton

```markdown
# Persona
You are [identity + domain + tone], specific down to "what kind of person it is like."

# Capabilities and Flow
1. [capability name]: when it triggers + how to do it + what it returns
2. ... (write the thinking order step-by-step; this is the core of making the agent smarter)

# Constraints
- Forbid [AI-tone word list]
- Do not [out-of-bounds behavior]

# Output Format
[fixed structure template]

# Boundary Handling
- When out of scope [ask back / refuse / disclaimer]; when unsure, do not make things up
```

Five-section correspondence: persona ≈ CO-STAR's Role, capabilities & flow ≈ Skills&Tools+Workflow, constraints & boundary ≈ the two sides of Constraints. **Capabilities first, then constraints, then the catch-all at the end** — a system prompt that only says "who you are" is an empty shell.

### Step 3 (audit mode): Run the Structural Audit

```bash
python3 scripts/prompt_audit.py --file assets/sample-system-prompt.md            # task mode's five elements (bundled sample)
python3 scripts/prompt_audit.py --file assets/sample-system-prompt.md --mode agent   # five-section skeleton (bundled sample, expect 5/5)
```

Expected: outputs JSON with a `hit/miss` per element and a missing-items list. Fill the misses by the element's semantics; do not pad the word count.

### Step 4: Iterate and Deliver

For long-content tasks, run **three rounds of iteration**: round one asks only for the outline skeleton → round two expands the chosen parts into body → round three polishes (cut repetition, passive to active, add a hook at the opening). Asking the model to write the full text at once = giving yourself three rounds of rework.

## Delivery Standards

- Artifacts (task): the prompt text with all five elements + an annotated version of the elements.
- Artifacts (audit): the JSON audit report + before/after comparison.
- Artifacts (agent): the five-section system prompt + 3 suggested opening lines and 3 preset questions each (Coze/Doubao agent publishable artifacts).
- Save location: output directly in the conversation (this skill writes no files).
- Integrity verification: the task artifact returns 5/5 on `python3 scripts/prompt_audit.py --prompt "<text>"`; the agent artifact has all five section headings; dialect entries have been confirmed via platform-dialects.md's verification steps before use (VERIFY BEFORE USE).

## Five-Element Quick Reference

| Element | Common phrasing |
|------|----------|
| Role | "You are a [position] in [domain], good at [style]" |
| Background | "The reader is [audience], the use case is [scenario]; here is the material: …" |
| Task | "Help me turn [input] into [output]" (specific verb) |
| Requirements | "Length ≤N; banned words: …; every sentence carries information; open by getting to the point" |
| Format | "Output as [table/list/JSON], structure: conclusion → bullets → action" |

## Failure Handling Table

| Symptom | Cause | Action |
|------|------|------|
| The output is all boilerplate like "in today's society" | Missing reverse constraints | Add a banned-word list + "open by getting to the point, no preamble" |
| The style differs every conversation | Missing role anchoring + format lock | Copy the role and format sections from the five elements to the start of the conversation, only swap the task content |
| Long-text logic breaks | Wrote the full text at once | Split into three rounds: outline → expand → polish |
| The agent answers off-target and invents | The system prompt has no boundary section | Add "ask back when out of scope, do not make things up when unsure" |
| The audit is 5/5 but the output is still poor | Structure right, weak word choice | Swap in concrete numbers and word lists in the requirements section; replace "be more vivid" with a checkable constraint |

## References

- [platform-dialects.md](references/platform-dialects.md) — the Doubao / Coze / CO-STAR dialect structures and verification links
- [sources-and-methodology.md](references/sources-and-methodology.md) — methodology provenance and acknowledgments

## Chain Handoff (downstream suggestion)

This skill is independent of other domains — a standalone "prompt engineering" skill that any domain's orchestrator can call when it needs to "write the prompt well before executing"; its structure is isomorphic to video-prompt-engineer but they are not linked to each other. Suggest adding a chat domain in skill_chains.json and registering this skill, e.g. the chat domain's prompt_audit chain: chat-prompt-engineer (self-audit across task / agent two modes).
