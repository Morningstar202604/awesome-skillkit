# Voice Catalog (VERIFY BEFORE USE)

> ⚠️ **Time-sensitivity notice**: TTS models and voice IDs update at a **quarterly** cadence (added/removed/renamed).
> This catalog is a 2026-09-14 web research snapshot; confirm per each section's "verification method" before execution.
> Source grading: 🟢 official · 🟡 third-party · 🔵 community.

## Temperament → Voice Mapping (casting order: temperament first, ID second)

| Character temperament | Preferred traits | Reference entry |
|----------|----------|----------|
| Warm host | Female, natural, approachable | Kokoro `af_sarah` |
| Professional announcer/news | Female, clear, steady | Kokoro `af_nicole` |
| Authoritative narrator/documentary | Male, composed, authoritative | Kokoro `am_michael` |
| Lighthearted companion/chitchat | Male, conversational | Kokoro `am_adam` |
| Audiobook narration | British accent, refined | Kokoro `bf_emma` / `bm_george` |
| Improvisational dialogue feel | Dialogue-specialized model | DIA TTS (dialogue-specialized) |

*Verification method: each engine's official voice list page; IDs may be renamed with versions—list and audition voices before synthesizing.*

## Engine Capability Boundaries

| Engine | Strengths | Boundaries | Best for |
|------|------|------|------|
| Kokoro-82M | 82M params CPU-runnable, zero-cost local, natural audio quality | No emotion slider; long passages flat | Explanatory/news-style shows 🟡 |
| DIA TTS | Dialogue naturalness specialized | Non-dialogue content mediocre | Two-person dialogue 🟡 |
| Chatterbox | Strong expressiveness | Stability mediocre | Entertainment-oriented 🔵 |
| Qwen3-TTS | 3-second zero-shot cloning, descriptive voice design ("low male voice in a library") | Cloning requires authorization chain | Personalized shows 🟢 |
| Coqui XTTS / Piper | Open-source self-hosting mature / fast low-power | XTTS project status needs verification | Self-hosted pipeline 🟡 |

*Verification method: Kokoro GitHub (hexgrad/Kokoro-82M), Qwen3-TTS official blog,
HuggingFace model cards.*

## Three Selection Questions (same decision-tree style as the open-source video side)

1. Where does it run—local CPU/single GPU, or cloud API?
2. Do you need cloning—if you need the person's own voice, go the cloning route (keep authorization records); if not, select a voice from the zero-shot catalog.
3. Commercial license—Kokoro Apache-2.0 friendly; commercial APIs check quota and terms.

## Synthesis Parameter Quick Reference 🔵

| Parameter | Baseline | Notes |
|------|------|------|
| speed | 1.0 | Chinese voiceover baseline; narration 1.05-1.1; reflective 0.95 |
| Per-segment duration | ≤2-3 min/segment | Synthesize in segments then concatenate; high naturalness and repairability |
| Concatenation | ffmpeg concat `-c copy` | No re-encode, done in seconds; dialogue segments crossfade 300-500ms |
| BGM | Only lay intro/outro | Vocal segments bed ≤-18dB; off by default |

## Change maintenance

Voice ID invalid: update the corresponding row + the snapshot date at the top. New engines go through the "three selection questions" first before entering the table.
