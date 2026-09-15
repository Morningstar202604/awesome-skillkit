---
name: video-subtitles
description: "Generate SRT subtitles and platform-optimized captions from video script. Supports multi-language, timing sync, and per-platform caption formats. Use when the user asks to 加字幕 / 生成字幕 / 做字幕文件 / 短视频字幕 / 烧录字幕 / generate subtitles / add captions / make an SRT. Do NOT use for burning subtitles into video (see video-editor), translating audio (use a transcription tool), or styling thumbnails."
license: Apache-2.0
compatibility: Pure Python, no external dependencies. No API keys required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: video
  pattern: single-task
  tier: basic
  verified-date: "2026-09-09"
---

# Video Subtitles & Captions

Generate SRT subtitles and platform-optimized captions.

## When to Use

- Video script is written, need timing-synced subtitles
- Creating accessible videos (captions for muted viewing)
- Generating platform-specific captions (douyin vs bilibili format)
- Adding on-screen text overlays

## Input

```json
{
  "scenes": [
    {"id": 1, "dialogue": "你们猜我花了多少钱？", "duration_sec": 3},
    {"id": 2, "dialogue": "八千九！就这个？", "duration_sec": 5}
  ],
  "platform": "douyin",
  "language": "zh"
}
```

## Output

```json
{
  "srt_path": "/tmp/subtitles.srt",
  "caption": "#宝宝测评 #iPhone16 #搞笑",
  "total_cues": 2,
  "total_duration": 8
}
```

## SRT Format

```text
1
00:00:00,000 --> 00:00:03,000
你们猜我花了多少钱？

2
00:00:03,000 --> 00:00:08,000
八千九！就这个？
```

## Platform Caption Rules

| Platform | Max Caption | Hashtag Limit | Style |
|----------|-----------|---------------|-------|
| Douyin | 50 chars | 3 tags | Emoji + keyword |
| Bilibili | 100 chars | 5 tags | 【标题】 format |
| TikTok | 220 chars | 5 tags | Lowercase + trending |
| YouTube | 100 chars | N/A | Title + description |

## Workflow

1. Parse script scenes with timing
2. Generate SRT file (time-synced)
3. Generate platform caption (title + hashtags)
4. Validate: total duration matches video length
5. Output: SRT + caption text

## References

- [references/caption-formats.md](references/caption-formats.md) — per-platform formats
