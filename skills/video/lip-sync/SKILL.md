---
name: video-lip-sync
description: "Synchronize character mouth movements with TTS audio. Takes a face image + audio file, generates lip-synced video. Gateway-based with mock fallback. Use after TTS is ready and before video assembly."
license: Apache-2.0
compatibility: Requires local lip-sync gateway at 127.0.0.1:30081 or mock mode. No API keys required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: video
  pattern: single-task
  tier: standard
  verified-date: "2026-09-09"
---

# Video Lip Sync

Synchronize character mouth movements with TTS audio.

## When to Use

- TTS audio is generated, need matching mouth movements
- Talking character videos (baby, nailong, mascots)
- Before video assembly (lip-synced clips feed into editor)

## Input

```json
{
  "face_image": "/tmp/character.png",
  "audio_path": "/tmp/scene_1.wav",
  "mouth_width": 40,
  "mouth_height": 30,
  "frame_rate": 30
}
```

## Output

```json
{
  "output_path": "/tmp/lipsync_scene_1.mp4",
  "duration_sec": 2.4,
  "frame_rate": 30,
  "face_image": "/tmp/character.png"
}
```

## Workflow

1. Load face image (consistent character across scenes)
2. Load TTS audio from voice-synth step
3. Call lip-sync gateway (or mock)
4. Output: lip-synced video clip per scene
5. Validate: duration matches audio duration

## Batch Mode

Accepts script JSON + audio directory, processes all scenes:

```bash
python3 lip_sync.py --face character.png --script script.json --audio-dir /tmp/tts/
```

## References

- [references/gateway-setup.md](references/gateway-setup.md) — lip-sync service setup
