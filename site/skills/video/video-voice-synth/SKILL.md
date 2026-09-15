---
name: video-voice-synth
description: "Text-to-speech (TTS) for video production. Converts script dialogue to natural voice audio. Supports multiple voices (baby, adult, mascot), languages (zh/en), and styles (funny, serious, excited). Gateway-based with mock fallback. Use when the script is ready and audio needs to be generated before lip-sync. 当用户要求 配音 / 合成语音 / 文字转语音 / TTS 时使用。 Do NOT use for cloning a real person's voice without documented consent."
license: Apache-2.0
compatibility: Requires local TTS gateway at 127.0.0.1:30081 or mock mode. No API keys required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: video
  pattern: single-task
  tier: standard
  verified-date: "2026-09-09"
---

# Video Voice Synthesis (TTS)

Convert script dialogue to voice audio for video production.

## When to Use

- Script is written, need audio before lip-sync
- Generating character voices (baby, mascot, adult)
- Multi-voice dialogue for conversation videos
- Batch TTS for multiple scenes

## Input

```json
{
  "text": "你们猜我花了多少钱买了这个？",
  "voice": "baby_f01 | adult_m01 | mascot_01 | narrator_01",
  "language": "zh",
  "speed": 1.2,
  "pitch_shift": 3,
  "output_format": "wav | mp3"
}
```

## Output

```json
{
  "audio_path": "/tmp/tts_result.wav",
  "duration_sec": 2.4,
  "sample_rate": 24000,
  "voice_used": "baby_f01",
  "text": "你们猜我花了多少钱买了这个？"
}
```

## Gateway Protocol

Local TTS service at `http://127.0.0.1:30081`:

```text
POST /v1/tts
{
  "text": "...",
  "voice": "baby_f01",
  "speed": 1.2,
  "pitch": 3,
  "format": "wav"
}
Response: audio binary + metadata headers
```

Mode: real by default. If the gateway is unreachable the script prints diagnostics and
exits non-zero (exit 4) — it never silently returns fake audio. Pass `--mock` (or
`SKILLKIT_MOCK=1`) to get silent WAV placeholders for downstream wiring only.

## Voice Catalog

| Voice ID | Description | Best For |
|----------|-------------|----------|
| baby_f01 | High-pitched child voice, fast | Baby podcast, cute characters |
| baby_f02 | Slightly lower baby, slower | Baby educational |
| adult_m01 | Male narrator, calm | Tutorials, vlogs |
| adult_f01 | Female narrator, warm | Tutorials, reviews |
| mascot_01 | Enthusiastic, slightly robotic | Mascot/animated characters |
| narrator_01 | Neutral, clear | Explainer videos |

## Workflow

1. Parse script JSON (from script-writer output)
2. For each scene: extract dialogue text
3. Apply voice/speed/pitch config
4. Call TTS gateway (or mock)
5. Output: per-scene audio files + total duration report
6. Validate: audio duration matches scene timing

## References

- [references/voice-config.md](references/voice-config.md) — voice parameters, pronunciation hints
- [references/gateway-setup.md](references/gateway-setup.md) — local TTS service setup