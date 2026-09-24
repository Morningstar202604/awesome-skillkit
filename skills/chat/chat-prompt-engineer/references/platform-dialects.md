# Platform Dialect Notes (VERIFY BEFORE USE)

> ⚠️ **Timeliness statement**: the official prompt tutorials for chat assistants update on a **quarterly** cadence. The entries in this file are a 2026-09-14 web-research snapshot. Before using, re-confirm per each section's "verification method" (SKILL-STANDARD-v2 commandments 7/8). Source grading: 🟢 official docs · 🟡 third-party aggregation · 🔵 community experience.

## Universal five elements (default when no platform is specified)

```text
[role] + [background] + [task] + [requirements] + [format]
```

Fill in the five elements first, then layer on the platform dialect. The fallback when the dialect is uncertain: **write only the five elements + reverse constraints**,
skipping platform-specific features (agent panels, preset questions, etc.).

## Doubao (ByteDance)

- The official tutorial repeatedly recommends the **five-element formula**: identity + scenario/background + task + requirements + format —
  the core idea is "a prompt isn't better the longer it is, but the more complete it is." 🟡
- Three-step framework: background positioning (role + brand info + user persona) → objective clarified → requirements detailed. 🟡
- Doubao agent (a custom role created inside a chat): the system prompt follows the agent five-part skeleton;
  a published agent should pair an opening line with 3-4 preset questions. 🟡
- Deep ecosystem binding: results can be sent straight to Jianying/Feishu, and the task prompt can declare the delivery form at the tail. 🔵
- Verification method: official tutorials inside the Doubao app / search "Doubao prompt formula official"

## Coze (ByteDance, agent platform)

- Five-module structure: Role / Context / Skills & Tools /
  Workflow / Output — step-by-step workflows are the core of making an agent smarter. 🟡
- Official minimal four-part: persona setup / function and flow / constraints and limits / reply format. 🟢
- Official writing advice: concise and concrete, use context, avoid ambiguity, give example inputs/outputs, test edge-case inputs. 🟢
- Variable syntax: you can embed `{{variables}}` (e.g. time) inside the prompt for dynamic injection. 🟢
- Verification method: the Coze site's help doc "Persona and Reply Logic"

## CO-STAR framework (cross-platform universal)

- Context / Objective / Steps / Tone / Audience five parts — highly isomorphic to the five elements
  (Tone folds into requirements, Audience into background). Good as the English-named skeleton for agent mode. 🟡
- Verification method: search "CO-STAR framework prompt" and cross-check at least two independent sources

## ChatGPT / GPTs

- Custom GPT instructions are separate from the chat prompt; the agent five-part skeleton applies directly. 🟢
- Verification method: OpenAI official "GPTs instructions best practices"

## Kimi / DeepSeek / Qwen, etc.

- No official structured tutorial found; default to the universal five elements; long-context models (Kimi) can put
  the whole material rather than a summary in the background element. 🔵 Rule of thumb, must live-test.
- Verification method: each provider's official docs / help center

## Audit vs dialect

`prompt_audit.py` only audits the five elements / five-part skeleton (the cross-platform invariants). Platform-specific capabilities
(plugin-call declarations, variable injection, preset questions) are checked manually against this file + the official docs —
two layers, neither optional.

## Change maintenance

When a dialect is found to be stale: update the corresponding entry in this file + the snapshot date at the top directly, and let the PR go through normal gates.
