# Sources and Methodology

This skill is self-authored; its methodology skeleton is distilled from the following public materials (structural borrowing only, no text copied):

| Source | Type | What was borrowed | License/attribution |
|------|------|----------|-----------|
| Doubao official tutorials and the "Doubao Advanced Handbook" series (the five-element formula: identity + scenario + task + requirements + format) | 🟡 Third-party aggregation (collected in the ima knowledge base) | The task-mode five elements, the three-step framework (background positioning → objective clarified → requirements detailed) | Structural methodology citation, source noted |
| "Doubao summarized 5 'strongest prompts'" (a Toutiao hands-on article, 2026-09) | 🟡 Third party | Reverse-constraint discipline (banned-word list, hard word-count limit, "every sentence carries information"), the three-round iteration method (skeleton → flesh → polish), role anchoring + output-format lock | Structural methodology citation, source noted |
| Coze official docs (persona and reply logic: the four-part persona/function-and-flow/constraints/reply-format) | 🟢 Official | The direct predecessor of the agent-mode five-part skeleton (this skill splits out "edge handling" as its own part on top of the four) | Official doc structural citation, source noted |
| Coze community best practices (five modules: Role/Context/Skills&Tools/Workflow/Output) | 🟡 Third party | "Step-by-step workflows are the core of making an agent smarter," and the three elements of capability definition (when to trigger + how + what to return) | Structural methodology citation, source noted |
| CO-STAR framework (Context/Objective/Steps/Tone/Audience) | 🟡 Third party | The English naming counterpart for the agent-mode five parts | Framework-name citation, source noted |

## Design decisions

1. **Isomorphic with video-prompt-engineer**: the five elements for chat = the six slots for video. The same
   mental model of "missing a slot and it improvises → improvisation means a wasted draft," learned once and reused across scenarios.
2. **Edge handling as its own part**: Coze's official four-part has no fallback section, but in practice "answer outside scope /
   don't make things up" is the first gate against agent hallucination, worth making a mandatory, separately audited part.
3. **Reverse constraints up front**: official tutorials put requirements fourth; this skill puts reverse constraints first within the requirements section —
   it's the most effective cut against boilerplate.
4. **Heuristic auditing, not semantic scoring**: same philosophy as the repo's video side — the script handles structural completeness,
   the human handles word choice. Two layers, neither optional.

## Verification obligation

Every dialect entry (platform-dialects.md) carries a source grade and a verification method, and must be
re-verified before use — the model ecosystem changes monthly; this file does not exempt VERIFY BEFORE USE.
