---
name: video-subtitles
description: "Generate SRT subtitles and platform-optimized captions from a video script. Supports multi-language, timing sync, and per-platform caption formats. Use when the user asks to add subtitles / generate subtitles / make a subtitle file / short-video subtitles / burn in subtitles / generate captions / add captions / make an SRT. Do NOT use for burning subtitles into video (see video-editor), translating audio (use a transcription tool), or styling thumbnails."
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

Generate time-aligned SRT subtitles and platform-compliant titles from the script's scene list. Default uses `scripts/subtitles.py` for deterministic output; it only produces subtitle files, doesn't burn them in (burn-in is `video-editor`'s job).

## Input Checklist

| Input | Required | Notes |
|------|------|------|
| script | yes (batch) or `text`+`start`+`end` (single) | Scene-list JSON, with `dialogue` + `duration_sec` |
| platform | no | `douyin` / `bilibili` / `tiktok` / `youtube`, default `douyin` |
| output | no | SRT output path, default `/tmp/subtitles.srt` |

When any required input is missing, ask everything at once:

> Please provide: ① the script scene list (JSON, with each item's dialogue and duration_sec), or ② a single line of text + start/end times. Optional: ③ platform (default douyin), ④ SRT output path.

## Pre-flight Checks

- `python3` available.
- Input parseable: batch JSON has `scenes[].dialogue` and `duration_sec`; single line gives `text` / `start` / `end`.
- Total subtitle duration matches the video duration (within <= 0.5s); otherwise prompt to calibrate the script timing first.

## Workflow

### Step 1: Generate SRT (Batch)

Action:

```bash
python3 scripts/subtitles.py --script script.json --output subtitles.srt --platform douyin
```

Expected: exit code 0; `subtitles.srt` exists, each cue = sequence number + timecode `HH:MM:SS,mmm --> ...` + text, timecodes continuous with no overlap.
If it fails: JSON missing `duration_sec` -> fill it in and rerun; scenes with no `dialogue` are skipped for that cue.

### Step 2: Single-Line Subtitle (Optional)

Action:

```bash
python3 scripts/subtitles.py --text "Guess how much I spent?" --start 0 --end 3 --output line.srt
```

Expected: output is just 1 cue, timecode `00:00:00,000 --> 00:00:03,000`.
If it fails: `end <= start` -> report an invalid time range, fix and rerun.

### Step 3: Generate the Platform Title

Action: cut a compliant title + tags from the script's `caption` field per the "platform title rules" below.
Expected: within the platform's character / tag limits (douyin <=50 chars + 3 tags).
If it fails: over the limit -> trim the title or merge tags.

## SRT Format Example

```text
1
00:00:00,000 --> 00:00:03,000
Guess how much I spent?

2
00:00:03,000 --> 00:00:08,000
Eight thousand nine hundred? That's it?
```

## Platform Title Rules

| Platform | Max Caption | Hashtag Limit | Style |
|----------|-----------|---------------|-------|
| Douyin | 50 chars | 3 tags | Emoji + keyword |
| Bilibili | 100 chars | 5 tags | 【title】 format |
| TikTok | 220 chars | 5 tags | Lowercase + trending |
| YouTube | 100 chars | N/A | Title + description |

## Parameter Quick Reference

| Parameter | Value | Notes |
|------|------|------|
| `--script` | JSON file | Batch scene list |
| `--text` | str | Single-line text (either this or `--script`) |
| `--start` / `--end` | float | Single-line start/end seconds, default 0 / 3 |
| `--platform` | enum | Platform |
| `--output` | file | SRT output path |

## Failure Remediation Table

| Symptom | Cause | Remedy |
|------|------|------|
| Timecodes overlap | Scene-duration accumulation error | Recompute `duration_sec` and rerun |
| Caption over limit | Platform limit | Trim title / merge tags |
| SRT empty | No dialogue in any scene | Add dialogue text |
| Parse failure | JSON syntax error | Fix the `--script` input |

## Delivery Standard

- `subtitles.srt` timecodes continuous, matching the video duration (within <= 0.5s); `caption` within platform constraints.
- Only produces subtitle files, no burn-in; burning into the final cut is `video-editor`'s job.

## References

- `references/caption-formats.md` — per-platform subtitle / title format details and examples.
