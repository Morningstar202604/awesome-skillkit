---
name: tts-voice-director
description: "Direct text-to-speech synthesis for a produced script: cast voices per character from a voice catalog (Kokoro/DIA/Qwen3-TTS families), set per-segment synthesis parameters (speed, stability), plan stitching (per-segment render + ffmpeg concat + crossfade), and voice-design via descriptive prompts on supported models. Reads the script from podcast-producer, hands rendered audio plan to episode-publisher. Use when the user asks to select voices / TTS voiceover / speech synthesis / voice casting / make the voice sound natural / multi-character voiceover / TTS / voice / audio production. Do NOT use for writing or linting the script (podcast-producer), nor for publishing metadata (episode-publisher)."
license: Apache-2.0
compatibility: Pure prompt-based; references only — no bundled synthesis binary (calls user-side TTS per catalog).
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: audio
  pattern: single-task
  tier: standard
  verified-date: "2026-09-14"
---

# TTS Voice Director

Perform **voice direction** on a script that has passed lint: cast voices, set parameters, and plan the stitching. The core judgment is the **role-voice matching table** — pick the wrong voice and, no matter how good the script is, it sounds like a newsreader.

## Input Checklist

| Input | Required | Notes |
|------|------|------|
| Script | Yes | podcast-producer's output (already passed script_lint) |
| Format | Yes | Single / two-voice dialogue / audiobook |
| TTS engine | No | Defaults to the Kokoro family (local, free); if specified, adapt per the catalog |
| Emotion requirements | No | Per-segment emotion tags (calm / excited / whispered) |

When inputs are missing, ask for all at once: "Please provide: ① the lint-passed script; ② the format (single / two-voice dialogue / audiobook); ③ the TTS engine (defaults to the Kokoro family); ④ special emotion requirements (optional)."

## Pre-flight Self-check

This skill itself has no runtime dependencies (pure planning, no bundled synthesis engine). Self-check point:

```bash
test -f references/voice-catalog.md && echo CATALOG-OK
```

- `CATALOG-OK` must appear; failure means the skill package is incomplete — STOP and prompt for reinstall.
- **Whether the engine is in place is a user-side state**; this skill does not bundle an engine and has no unified detection command: before running synthesis, confirm the chosen engine is available per [voice-catalog.md](references/voice-catalog.md)'s "verification method" (each engine's official page / HuggingFace model card), then start the first segment. The planning stage is not blocked by this.

## Workflow

### Step 1: Look Up the Voice Catalog and Cast

Open [voice-catalog.md](references/voice-catalog.md) and cast voices per the "character temperament → voice ID" mapping table. Discipline:

- **Decide the character temperament first, then pick the voice**: warm host / authoritative narrator / easygoing co-host / audiobook narrator — the temperament words come from the character setup in the script outline, not whichever sounds nice on a given day
- **Two-voice dialogue must maximize vocal contrast**: male-female pairing or different registers; if same gender, pick different IDs and audition them against each other
- **Fix the cast for the whole season of a show**: write the voice IDs into the show config; do not change voices between seasons

Expected: every character in the script maps to a candidate voice ID, and the two-voice dialogue has two different voice IDs.
On failure: the catalog has no timbre matching the temperament → pick 2 from the closest temperament family to audition and compare before deciding; do not force a cross-family match. If the user likes neither candidate → go back to podcast-producer to adjust the character temperament description, then come back to re-cast.

### Step 2: Set Synthesis Parameters

- **Speed**: Chinese narration at 1.0 baseline; explanatory narration can be 1.05-1.1, reflective pieces 0.95
- **Pauses rely on punctuation**: the periods/em dashes in the script are all the pause control there is; when the synthesis parameters have no "emotion" slider, rewriting the copy works better than tuning parameters
- **Voice design (supported models only)**: Qwen3-TTS-family supports descriptive timbre generation ("a deep male voice in a library"); zero-shot cloning needs a ≥3-second sample with a record of authorization

Expected: every segment has an explicit speed/parameter value, with the temperament it is based on noted.
On failure: the chosen engine does not support a parameter (e.g. no speed control) → degrade to "use punctuation only to control pacing" per the engine's capability, and write that limit into the synthesis plan. If zero-shot cloning is needed but a ≥3-second sample or authorization record is unavailable → do not clone; use an existing timbre from the catalog.

### Step 3: Plan the Stitching

```text
intro music (fade in 2s)
  → seg-01 (host voice) → 500ms gap → seg-02 (guest voice) → ...
outro music (fade out, matching the intro style)
```

- **Synthesize segment by segment, then concatenate** (ffmpeg concat `-c copy` does not re-encode and finishes in seconds)
- Crossfade adjacent dialogue lines by 300-500ms to eliminate seams
- Music beds only under intro/outro and between segments; do not duck the human voice (unless below -18dB)

Expected: the stitching list gives, line by line, the segment, voice source, gap/crossfade duration, and music segment positions.
On failure: a segment's audio format differs from the rest (concat requires the same encoding) → first re-encode that segment uniformly, then stitch; if a seam crackle appears → raise that seam's crossfade from 300ms to 500ms.

### Step 4: Chain Handoff

Deliver the synthesis plan (role-segment-parameter table) + the stitching list. **Then say: "The synthesis plan is ready; after executing, call episode-publisher to produce the publish package"** — the chain closes.
- Expected: the plan episode-publisher receives has a voice source and parameters per segment, and the stitching list can be fed directly to ffmpeg.
- On failure: after synthesis a segment's timbre turns out unsuitable → re-synthesize only that segment and restitch (that is the point of per-segment synthesis), do not tear down the whole timeline.

## Delivery Standards

- Artifacts: the synthesis plan table (segment × voice ID × speed/parameters) + the stitching list (including crossfade durations and music segments).
- Save location: output directly in the conversation; the actual audio is produced by the execution side, and this skill persists no audio.
- Integrity verification: every segment in the script is assigned a voice and parameters; the two-voice dialogue has two different voice IDs; the season's voice IDs match the show config.

## Failure Handling Table

| Symptom | Cause | Action |
|------|------|------|
| The voice breaks immersion | Temperament does not match the role | Go back to the catalog and re-cast by temperament; for two voices, audition the contrast |
| The pace rushes or drags | Speed parameter applied one-size-fits-all | Set speed per segment: explanatory 1.05+ / reflective 0.95 |
| Seam crackle | Hard concatenation | Crossfade adjacent segments 300-500ms |
| Proper nouns mispronounced | The synthesizer's dictionary lacks the word | Record the wrong word in the shownotes glossary; if it recurs, rewrite with a homophone and arrange human proofreading |
| The emotion is flat | The model has no emotion parameter | Go back to the script and rewrite the copy — pacing lives in punctuation and sentence length, not in parameters |

## References

- [voice-catalog.md](references/voice-catalog.md) — the voice catalog: each TTS's voice IDs, temperament mappings, and verification method
- [emotion-delivery-lexicon.md](references/emotion-delivery-lexicon.md) — the emotion-performance word bank: emotion → copy technique mapping, punctuation pause hierarchy, stress placement, dialogue rhythm, and parameter tiers (check this before changing the script when "the emotion is flat")
