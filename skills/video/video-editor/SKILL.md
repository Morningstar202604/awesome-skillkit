---
name: video-editor
description: "Assemble video clips with transitions, mix audio tracks, add effects, and produce final video. Supports FFmpeg-based real editing and mock mode. Use after lip-sync clips are ready, before subtitle/thumbnail steps. 当用户要求 剪辑视频 / 拼接片段 / 合成成片 / 加背景音乐 时使用。"
license: Apache-2.0
compatibility: Requires FFmpeg for real editing; mock mode works without. No API keys required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: video
  pattern: single-task
  tier: standard
  verified-date: "2026-09-09"
---

# Video Editor / Assembly

Combine clips, audio, and effects into final video.

## When to Use

- Lip-sync clips are ready, need to combine into one video
- Adding background music (from music-generation)
- Applying transitions between scenes
- Finalizing before subtitle overlay and publishing

## Input

```json
{
  "clips": ["/tmp/scene_1.mp4", "/tmp/scene_2.mp4", "/tmp/scene_3.mp4"],
  "audio": ["/tmp/bgm.mp3"],
  "transitions": ["fade", "cut", "slide"],
  "output": "/tmp/final.mp4"
}
```

## Output

```json
{
  "output_path": "/tmp/final.mp4",
  "duration_sec": 30,
  "clips_used": 3,
  "audio_tracks": 1,
  "resolution": "1080x1920"
}
```

## Workflow

1. Collect all scene clips from lip-sync step
2. Collect BGM from music-generation
3. Apply transitions between scenes
4. Mux audio (dialogue + BGM)
5. Export final video (platform-appropriate resolution)
6. Validate: duration matches script target

## FFmpeg Commands

```bash
# Concat clips
ffmpeg -f concat -safe 0 -i clips.txt -c copy combined.mp4

# Add BGM (lower volume)
ffmpeg -i combined.mp4 -i bgm.mp3 -filter_complex \
  "[1:a]volume=0.3[bgm];[0:a][bgm]amix=inputs=2" final.mp4

# Add transitions (crossfade)
ffmpeg -i clip1.mp4 -i clip2.mp4 -filter_complex \
  "xfade=transition=fade:duration=0.5" output.mp4
```

## References

- [references/ffmpeg-recipes.md](references/ffmpeg-recipes.md) — common editing recipes