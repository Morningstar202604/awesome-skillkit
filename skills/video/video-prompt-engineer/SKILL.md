---
name: video-prompt-engineer
description: "Engineer and audit text-to-video prompts across generation models: the six-slot structure (subject + action + camera + lighting + style + duration), camera-move and transition vocabulary, and per-model dialect notes with verification steps. Two modes: write a prompt from a scene description, or audit an existing prompt and report which slots are missing or contradictory. Use when the user asks to write a video prompt / video prompt / text-to-video prompt / prompt audit / make the footage more cinematic. Do NOT use for generating the video itself, nor for image-generation prompts (static-image structure differs — no motion slots)."
license: Apache-2.0
compatibility: Pure prompt-based; the bundled prompt_audit.py needs Python 3.8+ only.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: video
  pattern: single-task
  tier: standard
  verified-date: "2026-09-14"
---

# Video Prompt Engineer

Write and audit cross-model text-to-video prompts. The core is the **six-slot structure** — models can't read minds; every missing slot gets improvised, and improvisation is where wasted clips come from.

## Input Checklist

| Input | Required | Notes |
|------|------|------|
| mode | yes | `write` (write a prompt from a scene description) | `audit` (audit an existing prompt) |
| scene description | write required | One-line frame: subject + action + environment |
| target model | no | Default generic structure; if a specific model is given (seedance/kling/veo, etc.), apply its dialect (see references/model-dialects.md) |
| duration | no | Default 5s |
| aspect ratio | no | Default 16:9 |
| prompt to audit | audit required | Paste the original text |

## Pre-flight Checks

- audit mode: do you have the original prompt text? If not, ask for it first; don't audit from memory.
- write mode: does the scene description have a subject? A subjectless description like "shoot a nice-looking shot" is rejected outright.

## Workflow

### Step 1 (write): Fill In the Six Slots

```text
[subject] + [action] + [camera] + [lighting] + [style] + [duration/aspect]
```

Example (copy the whole block and swap words):

```text
A young woman in a black hoodie walks through a rainy neon-lit street,
slow push-in from mid shot to close-up, night exterior with cyan-orange
neon spill and wet-reflective asphalt, cinematic live-action look,
5 seconds, 9:16 vertical.
```

Rules:
- The action must be **single and completable in one shot** ("sit down and light a lighter" is two actions -> split into two prompts)
- One phrase per slot; don't write long-story sentences — a prompt is a parameter table, not a script
- Numbers are always explicit ("5 seconds"), never "a few seconds"

Expected: the output prompt has all 6 slots; running `python3 scripts/prompt_audit.py --prompt "<text>" --mode write` returns 6/6.
If it fails: self-check returns <6/6 -> read the missing list and fill each slot before delivering; don't carry miss items into the next step. A slot truly can't be filled (e.g., no lighting info in the scene description) -> go back to the input checklist and ask the user for environment/time of day; don't invent. The action slot becomes two verbs -> split into two prompts; don't merge.

### Step 2 (audit): Run the Structural Audit

```bash
python3 scripts/prompt_audit.py --prompt "<text to audit>"
```

Expected: JSON output with each slot's `hit/miss` and a missing list. Fill miss items per the remediation table below.
If it fails: `--prompt` passed empty/whitespace only -> the script errors; go back to the input checklist and ask the user for the prompt text. JSON unparseable -> confirm quotes in the prompt are escaped (wrap in single quotes on the command line, or save the prompt to a file first).

### Step 3: Apply the Model Dialect (Only When a Model Is Specified)

Check [model-dialects.md](references/model-dialects.md) for the target model's syntax differences (marker tokens, reference-image slot, audio slot). **All dialect entries are 2026-09 web-researched values; verify against the official prompt-guide links given in the doc before use (VERIFY BEFORE USE)** — model syntax updates on a monthly cadence.

Expected: the prompt has been rewritten in that model's dialect, and the official verification link in the doc has been opened and confirmed.
If it fails: the verification link is dead or the doc is missing -> deliver per the generic six-slot structure and note "dialect not verified" in the deliverable. The doc has no entry for the user's specified model -> same: deliver per the generic structure with a note; don't invent the model's syntax from memory.

### Step 4: Deliver

write mode delivers the original prompt + a slot-annotated version; audit mode delivers the JSON report + a side-by-side of the fixed prompt.
If it fails: the user only wants the original prompt, no slot annotations -> deliver the original and stop; keep the annotated version on file for reference; don't block delivery over a format disagreement.

## Six-Slot Dictionary (Fastest Lookup)

| Slot | Common Phrases |
|------|--------|
| subject | identity + outfit + expression: "a young woman in a black hoodie, tired eyes" |
| action | single verb phrase: "walks slowly toward camera" / "picks up a blue lighter" |
| camera | shot size + move: "extreme close-up, slow push-in" / "wide establishing, static" |
| lighting | time of day + source + contrast: "golden hour backlight" / "high-contrast noir, practical neon" |
| style | medium texture: "cinematic live-action" / "stop-motion feel" / "90s camcorder" |
| duration/aspect | "5 seconds, 9:16 vertical" |

## Failure Remediation Table

| Symptom | Cause | Remedy |
|------|------|------|
| Subject's face changes every frame | Missing reference-image slot / vague subject description | Add character-card description or the model's reference-image slot; see the visual-style-anchor skill's character card |
| The action doesn't happen | Action written as a result | "holding a lit lighter" -> "ignites the lighter" (write the process, not the state) |
| Camera wanders erratically | Two camera moves stacked | Keep only one camera-move verb per prompt |
| Footage doesn't match the duration | Action load exceeds the duration | Cut actions at one verb per second |
| Audit 6/6 but generation is still poor | Right structure, weak word choice | Swap adjectives for concrete nouns: beautiful lighting -> cyan neon spill |

## Delivery Standard

- write: English prompt with all 6 slots + slot-by-slot mapping
- audit: JSON report (hit/miss per slot) + fixed prompt
- Dialect entries confirmed per model-dialects.md's verification steps before use

## References

- [camera-vocabulary.md](references/camera-vocabulary.md) — camera-move and transition vocabulary (quick version)
- [cinematography-lexicon.md](references/cinematography-lexicon.md) — deep lexicon: 17 transitions, action-verb spatial semantics, micro-expression performance, speed/rhythm, physical-attribute descriptions, per-model dialect quick reference, iteration-fix mapping (check this first when writing prompts)
- [model-dialects.md](references/model-dialects.md) — per-model syntax dialects and verification links
- [sources-and-methodology.md](references/sources-and-methodology.md) — open-source provenance and credits (CC BY 4.0 attribution info)

## Chain Handoff (Downstream Suggestions)

This skill takes scene descriptions from storyboard-designer / shot-recipe-designer and produces six-slot prompts to feed video-generation / image-generation; character consistency must reference visual-style-anchor's identity line. Recommended as an upstream planning step in video-domain chains. Currently a standalone skill; handoff is descriptive only.
