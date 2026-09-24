---
name: podcast-producer
description: "Produce a podcast episode script from a topic or a document: hook-first outline, segment structure with target durations, two-voice dialogue or single-voice narration, and a shownotes draft. Hard rule: spoken words only — no stage directions, no [pause] markers, TTS reads everything verbatim. Chain entry of audio-studio; hands the script to tts-voice-director. Use when the user asks to make a podcast / write a podcast script / podcast script / audio show / turn an article into a podcast / NotebookLM-style audio / podcast / TTS / voice. Do NOT use for voice selection or synthesis parameters (tts-voice-director), nor for publishing metadata (episode-publisher)."
license: Apache-2.0
compatibility: Pure prompt-based; the bundled script_lint.py needs Python 3.8+ only.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: audio
  pattern: single-task
  tier: standard
  verified-date: "2026-09-14"
---

# Podcast Producer

The chain's entry point. Turn a topic (or a document) into a **segmented script that can be fed directly to TTS**. The one core discipline is extremely hard: **spoken words only — TTS reads everything you write verbatim**. `[pause]`, "(laughs)", and stage directions all become program content.

## Input Checklist

| Input | Required | Notes |
|------|------|------|
| Topic or document | Yes | "Let's talk about this year in AI video" or paste an article directly |
| Format | No | Single narration (default) / two-voice dialogue / document-to-podcast (NotebookLM-style) |
| Target duration | No | Default 5 minutes (≈750-900 Chinese spoken characters, at 150-180 chars/min) |
| Show info | No | Show name, slogan — if present, goes into the opening |

When inputs are missing, ask for all at once: "Please provide: ① the topic or source document; ② the format (single narration / two-voice dialogue / document-to-podcast); ③ the target duration (defaults to 5 minutes); ④ the show name and slogan (optional)."

## Pre-flight Self-check

```bash
test -f scripts/script_lint.py && echo LINT-OK
```

Expect to output `LINT-OK`; failure means the skill package is incomplete — STOP and prompt for reinstall (lint is the hard gate before TTS; no script is delivered without it). The script is stdlib-only with no dependencies to install.

## Workflow

### Step 1: Outline First (hook → three parts → CTA)

```markdown
1. Hook (within 15 seconds): a counter-intuitive fact / a question / a number — grab them before saying the show name
2. Body: 2-3 segments, each with one argument + one example, with explicit transition sentences between segments
3. CTA: follow/subscribe + next-episode preview, one sentence
```

### Step 2: Write the Script Segment by Segment

Rules (all learned from hard-won TTS experience):

- **Only write the words to be spoken.** No stage directions, no `[pause]` / `(sighs)` / `**bold**` / markdown markers — for pauses use punctuation (a period pauses longer than a comma, an em dash creates suspense)
- **Write numbers in the spoken Chinese form**: "2026" → "two-zero-two-six" per the synthesizer's convention; for easily misread terms, add a pinyin note to the shownotes rather than the script
- **Dialogue format**: mark HOST/GUEST line by line, ≤3 sentences per line — a line that is too long instantly produces a synthetic tone; give the GUEST follow-up questions to create rhythm
- **Generate long content in segments**: produce each segment as a finished piece then concatenate (ffmpeg concat); far more natural than synthesizing in one breath
- **Document-to-podcast**: first distill 3-5 key points, then expand into dialogue — it is not reading the article aloud

### Step 3: Run the Script Lint (machine gatekeeper)

```bash
python3 scripts/script_lint.py --file assets/sample-script.md   # bundled sample podcast script
python3 scripts/script_lint.py --file assets/sample-script.md --dialogue   # dialogue mode: enforces HOST/GUEST line prefixes
```

Checks: stage-direction markers, bracket/parenthetical asides, markdown residue, over-long single lines, missing inter-segment transitions. A non-zero exit code means there is a violation; fix and rerun until exit code 0 before going into TTS.

### Step 4: Chain Handoff

Deliver the segmented script + shownotes draft. **Then say: "The script has passed lint; call tts-voice-director for voice casting and synthesis, then episode-publisher for the publish package"** — the chain unfolds automatically.
- Expected: the script tts-voice-director receives has lint exit code 0, segments carry target durations, and can go straight to voice casting.
- On failure: the synthesis stage finds a misread term → write the pronunciation note into the shownotes glossary (do not write back into the script); see the failure table for details.

## Delivery Standards

- Artifacts: the segmented script (spoken words only, no marker residue) + shownotes draft (including the glossary first draft).
- Save location: output directly in the conversation; when saving files, name the script `script.md` (the lint input convention).
- Integrity verification: `python3 scripts/script_lint.py --file script.md` exits 0; the total character count falls within the band for the target duration (150-180 chars/min); every segment has an explicit transition sentence.

## Failure Handling Table

| Symptom | Cause | Action |
|------|------|------|
| TTS reads the markers aloud | The script contains stage directions / brackets | Clear them by running script_lint before synthesizing |
| Heavy synthetic tone, sounds like a robot | Lines too long / missing spoken connectors | ≤3 sentences per line; add spoken words like "actually / put simply / think about it" |
| Rhythm collapses midway | Three parallel arguments with no escalation | Rearrange into an escalating "phenomenon → counter-intuitive point → how to do it" structure |
| The dialogue sounds like self-Q&A | The GUEST only echoes | Give the GUEST an independent stance or follow-up hooks |
| Over duration | Word count not controlled | Back into the word-count limit from the target duration; cut examples first |

## References

- [sources-and-methodology.md](references/sources-and-methodology.md) — methodology provenance (Podify / inference.sh / the open-source TTS ecosystem)
