# Skill Writing Guide

A practical, machine-first guide for authoring SKILL.md files. It tells you **when** an agent should load a skill (the `description`) and **how** it should execute the task once loaded (the body). Follow this for every new skill and for every migration of an existing one.

---

## 1. First Principles

### 1.1 Write for the model, not for the human reader
A skill is a prompt the model executes. Anything a human takes for granted — what a button is called, what an error looks like, what "done" means — must be stated explicitly. The ceiling of a skill's quality is set by its fuzziest instruction.

### 1.2 Description = WHEN, body = HOW
- **`description` (frontmatter) is the trigger mechanism.** The model reads `name` + `description` to decide whether to *load* the skill at all. If the description is vague or missing trigger phrases, the skill never fires. This is the single most common failure mode in real skill audits.
- **The markdown body is the execution guide.** Once loaded, the body tells the model *how* to do the task. Write it as agent-executable instructions, not as a human article.

### 1.3 Progressive disclosure
Load cost is layered, cheapest first:
1. **Frontmatter metadata** (~100 tokens) — always loaded, routes the skill.
2. **The body** — loaded when the skill activates. Keep it a *table of contents plus the critical path*, not the whole book.
3. **`references/` files** — read on demand, only for the deep branch that needs them.

If a reference file is under ~100 lines it can live inline; above that, split it out and point to it from the step that needs it.

### 1.4 Determinism beats improvisation
- If a task can be done by a script, don't ask the model to freestyle it.
- If a task can be done by copying a template, don't ask the model to invent prose.
- Where the model *must* create, give it the formula, the format, and worked anti-examples.

### 1.5 Verifiability
Every action has an expected output; every run has a success criterion; every failure has a handling branch. Pre-flight checks, exit codes, and "STOP if X" gates beat hopeful assumptions.

### 1.6 Lightweight and focused
One skill = one clear capability. Remove sediment: generic advice, motivational filler, redundant restatements of the obvious, and no-op steps. Branching, optional, or high-volume material goes into `references/`, not the body. A focused skill loads fast and routes cleanly; a bloated one buries the trigger and the critical path.

---

## 2. Anatomy of the Frontmatter

```yaml
---
name: my-skill                    # kebab-case, == directory name, <= 64 chars
description: "..."                # THE trigger line — see §3
license: Apache-2.0
compatibility: "Pure prompt-based; scripts/foo.py needs Python 3.8+ only."
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: video                 # a real domain category
  pattern: single-task           # single-task | chain-entry | ...
  tier: standard
  verified-date: "2026-09-24"
---
```

Rules:
- `name`: lowercase letters, digits, hyphens only; **exactly equals the containing directory name**; no leading/trailing/double hyphens.
- `compatibility`: state what runtime / network / tools the skill actually needs, so the agent knows whether it can run.
- `metadata`: keep machine-readable; `verified-date` is the last time the skill was proven to work.

---

## 3. The Description (WHEN) — the make-or-break field

The model routes on this field alone. A passing description has four parts, in order:

```
[WHAT it does] + [WHEN to use it / trigger phrases] + [keywords users type] + [what it EXCLUDES]
```

Write it as one flowing sentence (or a few), ≤ ~1024 chars.

### 3.1 What
Open with the concrete output/capability: "Produce a segmented TTS-ready podcast script from a topic or document."

### 3.2 When / trigger phrases
List the actual phrasings a user types. Include both English and the localized short phrasings people naturally say. Examples: `make a podcast`, `write a podcast script`, `turn this article into audio`, `NotebookLM-style audio`.

### 3.3 Keyword optimization
Naturally include the keywords users type when they need this skill — synonyms, tool names, task nouns. If you only say "generate media", you lose the user who says "make a short video / 图生视频 / text-to-video".

### 3.4 Exclusions
Close with a clear `Do NOT use for ...`, and point to the *neighboring* skill that owns those cases. Exclusions prevent double-loading and mis-routing.

---

## 4. The Body (HOW) — an agent execution guide

Structure the body as a runnable procedure. A reliable skeleton:

1. **One-paragraph purpose.** What this skill produces and the one hard discipline it enforces.
2. **Input Checklist.** A table: `Input | Required | Notes`. When inputs are missing, ask for all of them in one batch.
3. **Pre-flight self-check.** A concrete command (`test -f scripts/foo.py && echo OK`) and what to do if it fails (STOP, don't improvise).
4. **Workflow.** Numbered steps, each actionable and verifiable.
5. **Failure handling.** A table of expected errors → the branch to take.
6. **Delivery checklist.** The exact, sign-offable list the output must satisfy before returning.

### 4.1 Concrete steps
Every step should be actionable and verifiable:
- Give the input shape, the operation, and the expected output.
- Use ordered workflows, input checklists, and delivery checklists.
- State the tradeoff or the hard rule the step enforces, so the model doesn't silently weaken it.

### 4.2 Failure handling
When a step can fail, say so explicitly:

| Failure signal | Meaning | Action |
|---|---|---|
| `LINT-OK` not printed | Package incomplete | STOP; prompt reinstall; deliver nothing |
| Input topic empty | Cannot outline | Ask once, in a batch, for all missing inputs |

### 4.3 Platform adaptation
For platform-specific skills (a publisher, a generator, a formatter), bake in the exact rules the model can't guess:
- **Format rules**: file types, field names, length limits.
- **Reader / audience preferences**: tone, reading level, hook expectations.
- **Context & tone**: formal vs. casual, first vs. third person.
- **Length limits**: per-platform caps, enforced as numbers not vibes.
- **Image / media support**: sizes, counts, ratios, alt-text requirements.
- **Styling constraints**: allowed markup, forbidden patterns (e.g. no 3D, zero baseline mandatory for bar charts).

Put long platform tables in `references/`; keep the binding numbers in the step.

---

## 5. Template — copy this skeleton

```markdown
---
name: my-skill
description: "Do THE CONCRETE OUTPUT from INPUT. Use when the user asks to <trigger phrase 1> / <trigger phrase 2> / <localized short phrasing> / <synonym>. Hard rule: <the one non-negotiable discipline>. Do NOT use for <excluded case> (see <neighboring-skill>), nor for <other excluded case>."
license: Apache-2.0
compatibility: "Pure prompt-based; scripts/check.py needs Python 3.8+ only."
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: <domain>
  pattern: single-task
  tier: standard
  verified-date: "2026-09-24"
---

# My Skill

One paragraph: what this produces, and the single hard discipline enforced.

## Input Checklist

| Input | Required | Notes |
|-------|----------|-------|
| ...   | Yes/No   | ...   |

When inputs are missing, ask for all at once: "Please provide: ① ...; ② ...; ③ ... ."

## Pre-flight Self-check

```bash
test -f scripts/check.py && echo READY
```

Expect `READY`; failure means the package is incomplete — STOP and prompt reinstall.

## Workflow

### Step 1: <Action> (<expected result>)
- Operation, input shape, expected output.
- Hard rule: ...

### Step 2: <Action> (<expected result>)
...

## Failure Handling

| Signal | Meaning | Action |
|--------|---------|--------|
| ...    | ...     | ...    |

## Delivery Checklist

- [ ] ...
- [ ] ...
- [ ] ...
```

---

## 6. Verification Checklist (before you ship)

**Frontmatter parses**
- [ ] YAML parses with no tabs / stray indentation; `description` is quoted or uses `>` cleanly.
- [ ] `name` == directory name, kebab-case, ≤64 chars.
- [ ] `description` contains all four parts: what, when/triggers, keywords, exclusions.

**Body is executable**
- [ ] Every step names an input, an operation, and an expected output.
- [ ] Missing inputs are batched into one ask, not one-at-a-time prompts.
- [ ] Pre-flight command exists and its expected output is stated.
- [ ] At least one failure-handling branch and a delivery checklist.

**Scripts and references resolve**
- [ ] Every script referenced in the body exists under `scripts/`.
- [ ] Any CLI flags the body tells the model to pass actually match the script's `argparse`.
- [ ] Every `references/...` link points to a file that exists.

**Lean**
- [ ] No motivational filler, no redundant restatements, no no-op steps.
- [ ] Long/optional material is in `references/`, not the body.
- [ ] All prose is English; no leftover localized prose in instructions.

**It still works**
- [ ] The Python scripts `ast.parse` cleanly.
- [ ] `test -f scripts/...` pre-flight actually succeeds in the packaged layout.

---

## 7. Common Mistakes

| Mistake | Why it fails | Fix |
|---|---|---|
| Description is a title, not a trigger ("Video generation tool") | Model can't route; skill never loads | Add trigger phrases, keywords, and `Do NOT use for ...` |
| No exclusions | Two similar skills both fire, or wrong one fires | Close with `Do NOT use for ... (see <neighbor>)` |
| Body reads like a blog post | Model can't extract an action sequence | Rewrite as checklists, numbered steps, expected outputs |
| "Use your judgment" with no rule | The hardest decision is left to vibes | Give the formula, the threshold, or worked anti-examples |
| Referencing a script the package doesn't ship | Pre-flight fails at runtime | Ship the script; make the command match the real path |
| Passing flags that aren't in `argparse` | CLI errors mid-run | Read the script's parser; copy exact flag names |
| Dumping a 300-line table in the body | Bloats load cost, buries the critical path | Move it to `references/`; link from the step that needs it |
| Asking for inputs one question at a time | Wastes turns | Batch all missing inputs into a single prompt |
| Hard rule buried in prose | Model silently drops it | Put it up top and repeat it in the relevant step |
| Localized prose left in the instructions | Non-localized agents can't follow it | Translate all instructional prose to English |

---

## 8. Worked Examples

### 8.1 Description: bad vs. good

**Bad**
```yaml
description: 视频生成工具
```
No trigger scenarios, no keywords, no exclusions. The model has nothing to route on.

**Good**
```yaml
description: >
  Generate videos from text prompts or reference images via the configured
  gateway. Use when the user asks to 生成视频 / make a short video / text-to-video /
  image-to-video / 图生视频 / make a promo clip. Hard rule: confirm the output
  aspect ratio and duration before calling the gateway. Do NOT use for video editing,
  burning subtitles onto an existing clip, or downloading an existing video.
```
What (generate via gateway) → when/trigger phrases (bilingual phrasings) → the hard rule → exclusions with a neighboring-scope boundary.

### 8.2 Workflow step: bad vs. good

**Bad**
```markdown
### Step 2: Write the script
Write a good podcast script that sounds natural. Keep it engaging.
```
No input shape, no length, no expected output, no verifiable result. "Good" and "engaging" are vibes.

**Good**
```markdown
### Step 2: Outline first (hook -> three parts -> CTA)
- Input: the topic/document and the target duration (default 5 min).
- Operation: produce an outline with one hook, three numbered parts, and a CTA.
- Expected output: each part tagged with a target duration in seconds, summing to
  the target (at 150-180 spoken chars/min, 5 min = 750-900 chars).
- Hard rule: spoken words only — no [pause], no "(laughs)", no stage directions;
  TTS reads everything verbatim.
- Verify: `scripts/script_lint.py` reports zero stage-direction markers.
```
Actionable, bounded by a number, with a hard rule and a machine check the model can run.

---

## 9. In one sentence

Frontmatter is the address on the envelope (WHEN to open it); the body is the step-by-step inside (HOW to do it). Make the address unmissable and the inside executable, and keep both lean.
