---
name: episode-publisher
description: "Package a rendered podcast episode for publishing: markdown shownotes (summary, guest/links, terminology table), timestamped chapter markers (podcasting 2.0 style), platform metadata (title formulas, episode numbering, cover spec) for Chinese platforms (Xiaoyuzhou/Ximalaya) and Apple Podcasts, plus the AI-content disclosure line. Reads the script and synthesis plan from upstream chain steps. Use when the user asks to publish a podcast / shownotes / chapter markers / podcast publishing / publish on Xiaoyuzhou / episode metadata / podcast / audio production. Do NOT use for writing the script (podcast-producer), nor for synthesis/voice selection (tts-voice-director)."
license: Apache-2.0
compatibility: Pure prompt-based; no runtime dependencies.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: audio
  pattern: single-task
  tier: standard
  verified-date: "2026-09-14"
---

# Episode Publisher

The chain's closing step. Package the synthesized audio into a **publishable deliverable**: shownotes, chapter markers, platform metadata, and the AI disclosure statement. Great audio but a weak publish package = wasted effort — half of Xiaoyuzhou's conversion happens in the shownotes.

## Input Checklist

| Input | Required | Notes |
|------|------|------|
| Script | Yes | podcast-producer's output (segmented structure is needed to derive timestamps) |
| Synthesis plan / audio | Yes | tts-voice-director's output (segment durations are used for chapter estimation) |
| Platform | No | Defaults to the Xiaoyuzhou + Apple Podcasts dual spec |

When inputs are missing, ask for all at once: "Please provide: ① the synthesized script; ② the actual duration of each segment (or the audio file's duration); ③ the episode number and show name (these should come from the show config, not be hand-filled)."

## Pre-flight Self-check

This skill is pure-prompt driven: no runtime dependencies, no endpoints, no environment variables. The self-check point is the inputs, not the environment: **the script and the actual per-segment durations are both indispensable** — without actual durations you can only estimate timestamps, and the chapters will inevitably not line up with the audio (see row 1 of the failure table). If missing, ask and then STOP.

## Workflow

### Step 1: Write the Shownotes (fixed structure)

```markdown
## One-line summary (≤40 chars, hook style)
## This episode's key points (3-5, one sentence each)
## Resources mentioned (link + one-line note)
## Glossary (easily misread words in the script → correct pronunciation/definition)
## Timeline (see step 2)
## Production note
- This episode was produced using AI voice synthesis; the content has been human-reviewed.
```

Discipline: the summary writes "what this episode lets you understand," not "we chatted about"; the glossary directly reuses the error-prone words recorded during the podcast-producer stage; **AI disclosure is a hard requirement** — multiple platforms now require labeling synthetic content, so it is hardcoded into the template.

Expected: all six sections present, including the AI disclosure line; the summary is hook-style and ≤40 chars.
On failure: upstream left no record of error-prone words → write "to be filled this episode" in the glossary and call it out in the delivery note; do not fabricate pronunciations. If the summary is written as an outline like "we chatted about," rewrite it as conclusions. If the disclosure line is missing, add it immediately — this is a platform hard requirement; no delivery without it.

### Step 2: Generate Chapter Markers (podcasting 2.0 style)

Derive timestamps from the script's segments plus each segment's actual duration in the synthesis plan:

```text
00:00 Opening
00:35 The phenomenon: tools grew from 3 to 30
02:10 The counter-intuitive gap: demo vs. production
04:20 How to do it: the segmented pipeline
06:00 Wrap-up and preview
```

Format is `HH:MM chapter name`; the first chapter after the main content starts no earlier than 00:30 (platform spec).

Expected: line-by-line `HH:MM chapter name`, with the last chapter's timestamp ≤ the audio's actual total duration.
On failure: you only have estimated durations, not actual ones → first ask the user for the actual audio duration (see pre-flight); do not pad with estimates. The last chapter exceeds the audio total duration → recompute everything against the actual duration. The first chapter is earlier than 00:30 → merge it with the opening or push it back, to meet the platform spec.

### Step 3: Platform Metadata

| Field | Discipline |
|------|------|
| Title | `[episode number] topic hook` — episode number first for sorting; the hook ≤20 chars |
| Subtitle / one-line intro | Sourced from the shownotes summary; do not write a separate one |
| Cover | 3000x3000 square (Apple spec); reuse the visual-design-studio chain's output |
| Category | Pick a top-level category per the platform's category table; tech defaults to "Technology" + "Education" |

Expected: all four fields filled, the title carries the episode number and the hook ≤20 chars.
On failure: the episode number cannot be obtained → ask the user for the show config (do not hand-fill episode numbers, see the failure table); the platform is not in the category table → pick the closest top-level category and note the difference from the platform's original category, then finalize after user confirmation.

### Step 4: Deliver and Close the Chain

Deliver: shownotes.md + chapters.txt + per-platform metadata cards. **The chain closes here** — "topic selection → script → synthesis → publish package" is complete; whichever step is missing, go back to it.
- Expected: the publish package can be pasted directly into the platform backend with no missing fields.
- On failure: the platform review rejects → fix per the failure table and resubmit; do not switch platforms to dodge review.

## Delivery Standards

- Artifacts: `shownotes.md` (with the AI disclosure line), `chapters.txt` (line-by-line `HH:MM chapter name`), and the platform metadata cards (title / subtitle / cover spec / category).
- Save location: output directly in the conversation; when saving files, use the names above.
- Integrity verification: the sum of chapter timestamps matches the audio's actual duration (±1 chapter); the shownotes have all six sections including the disclosure line; the title carries the episode number and the hook ≤20 chars.

## Failure Handling Table

| Symptom | Cause | Action |
|------|------|------|
| Chapter timestamps do not line up | Used estimated durations without back-filling actual values | After synthesis, recompute against the actual audio duration |
| Xiaoyuzhou review rejected | AI content not disclosed / banned words on the cover | Check the disclosure line; strip extreme words from the cover |
| No one reads the shownotes | Written as an outline | Every point carries information; give conclusions directly |
| Episode numbers are messed up | Hand-filled episode numbers | Read episode numbers from the show config, do not hand-fill |

## References

The methodology references live in the podcast-producer skill package (shared within the package, not duplicated here): go into the podcast-producer skill directory and read its references directory's sources-and-methodology document. Platform disclosure requirements and open-source provenance are recorded in that file as well.
