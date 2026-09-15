---
name: video-script-writer
description: "Write video scripts: dialogue, narration, shot descriptions, timing markers, and platform-compliant titles/captions. Supports multiple video types (talking character, meme, tutorial, vlog, short). Use when the user needs a script for a video before production. 当用户要求 写视频脚本 / 短视频文案 / 分镜脚本 时使用。 Do NOT use for generating video files (script text only)."
license: Apache-2.0
compatibility: Pure prompt-based; may call LLM for generation. No API keys required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: video
  pattern: single-task
  tier: standard
  verified-date: "2026-09-09"
---

# Video Script Writer

Write production-ready video scripts with dialogue, timing, and visual cues.

## When to Use

- User has a video concept but no script
- Need dialogue for talking-character videos (baby, nailong, etc.)
- Writing narration for explainer/tutorial videos
- Creating meme video punchlines with timing
- Preparing scripts for TTS + lip-sync pipeline

## Input Format

```json
{
  "concept": "talking baby reviewing phones",
  "video_type": "talking_character | meme | tutorial | vlog | short",
  "duration_seconds": 30,
  "character": {
    "name": "Baby",
    "personality": "sarcastic adult in baby voice",
    "voice_style": "high-pitched, fast"
  },
  "platform": "douyin | bilibili | tiktok",
  "language": "zh | en",
  "tone": "funny | educational | dramatic"
}
```

## Output Format

```json
{
  "title": "宝宝测评iPhone 16",
  "hook": "你们猜我花了多少钱买了这个？",
  "scenes": [
    {
      "id": 1,
      "duration_sec": 3,
      "dialogue": "你们猜我花了多少钱买了这个？",
      "visual": "baby holds phone up to camera, zoom in",
      "camera": "close-up, front-facing",
      "sfx": "phone notification sound"
    },
    {
      "id": 2,
      "duration_sec": 5,
      "dialogue": "八千九！就这个？",
      "visual": "baby shakes phone, screen shows price",
      "camera": "medium shot, slight tilt",
      "sfx": "squeaky toy sound"
    }
  ],
  "caption": "#宝宝测评 #iPhone16 #科技 #搞笑",
  "total_duration": 30
}
```

## Workflow

1. **Parse concept** — understand the video idea, type, and constraints
2. **Design hook** — first 2-3 seconds must grab attention (question, surprise, conflict)
3. **Write dialogue** — match character voice, keep lines short (< 10 words for baby, < 20 for others)
4. **Assign timing** — each scene gets a duration; total must match target duration
5. **Add visual cues** — describe what the character does, camera angle, props
6. **Write caption** — platform-optimized hashtags + title (include keywords)
7. **Validate** — check total duration, line count, and platform compliance

## Platform Constraints

| Platform | Max Duration | Safe Zone | Caption Limit |
|----------|-------------|-----------|---------------|
| Douyin | 60s (short) / 15min (long) | Top 10%, Bottom 15% | 50 chars + 3 tags |
| Bilibili | Unlimited | Full frame | 100 chars |
| TikTok | 10min | Top 10%, Bottom 15% | 220 chars + 5 hashtags |

## Script Types

### Talking Character (baby, nailong, etc.)
- Dialogue-driven, 2-4 scenes
- Each scene: one line + one action
- Punchline at 70-80% mark
- Visual: character + prop, minimal background

### Meme / Reaction
- 1-3 scenes, fast cuts
- Text overlay + audio punchline
- 3-7 seconds per scene
- Loop-friendly ending

### Tutorial / Explainer
- Intro (5s) → Steps (20-60s) → Outro (5s)
- Each step: voiceover + screen capture
- Keep each step < 10s

## References

- [references/script-templates.md](references/script-templates.md) — ready-made templates per type
- [references/timing-guide.md](references/timing-guide.md) — pacing rules, beat sheets