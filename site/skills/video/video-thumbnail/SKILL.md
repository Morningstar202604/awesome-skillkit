---
name: video-thumbnail
description: "Design and generate video thumbnails/covers optimized for each platform. Supports text overlay, character placement, and platform-specific sizing. Use as final step before publishing. 当用户要求 做视频封面 / 设计封面图 / 缩略图 时使用。 Do NOT use for generating the video itself (cover image only)."
license: Apache-2.0
compatibility: Uses image-generation gateway for creation; FFmpeg for frame extraction. No API keys required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: video
  pattern: single-task
  tier: basic
  verified-date: "2026-09-09"
---

# Video Thumbnail / Cover

Generate platform-optimized video thumbnails.

## When to Use

- Video is assembled, need a clickable cover before publishing
- A/B testing multiple thumbnail designs
- Creating consistent brand thumbnails across series

## Platform Specs

| Platform | Size | Ratio | Max Size |
|----------|------|-------|----------|
| Douyin | 1080x1920 | 9:16 | 2MB |
| Bilibili | 1920x1080 | 16:9 | 2MB |
| TikTok | 1080x1920 | 9:16 | 2MB |
| YouTube | 1280x720 | 16:9 | 2MB |

## Input

```json
{
  "title": "宝宝测评iPhone 16",
  "style": "funny",
  "platform": "douyin",
  "character_image": "/tmp/baby.png",
  "video_source": "/tmp/final.mp4"
}
```

## Output

```json
{
  "output_path": "/tmp/thumbnail_douyin.png",
  "spec": {"width": 1080, "height": 1920},
  "text_overlay": "宝宝测评iPhone 16",
  "badge": "NEW"
}
```

## Workflow

1. Determine platform spec (size, ratio)
2. Choose approach: AI-generated or frame-extract + overlay
3. Add text overlay (title, 2-4 words max for 9:16)
4. Add badge/sticker if applicable
5. Export at platform resolution
6. Validate: file size < platform limit

## References

- [references/thumbnail-design.md](references/thumbnail-design.md) — design principles, examples