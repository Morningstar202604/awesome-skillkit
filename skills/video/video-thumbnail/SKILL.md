---
name: video-thumbnail
description: "Design and generate video thumbnails/covers per platform spec (douyin/bilibili/tiktok/youtube), via ffmpeg frame extraction or the image-generation gateway (scripts/thumbnail.py; --mock only for downstream wiring). Use when the user asks to make a video cover / design a cover image / thumbnail / cover art / video thumbnail / design a cover / YouTube cover image, as the final step before publishing. Do NOT use for generating the video itself, or for in-video subtitles."
license: Apache-2.0
compatibility: Route A (gateway) needs the image-generation gateway; Route B (frame extract) needs ffmpeg. No API keys required (gateway auth optional via GATEWAY_API_KEY env).
metadata:
  version: "1.1"
  author: awesome-skillkit
  category: video
  pattern: single-task
  tier: basic
  verified-date: "2026-09-21"
---

# Video Thumbnails (Platform-Spec Covers)

Two routes produce platform-spec covers: A = text-to-image via the image gateway, B = extract a frame from the final cut with ffmpeg.
Everything runs through this directory's `scripts/thumbnail.py`; the script defaults to real mode, exits non-0 on failure, and never silently returns fake results.

## Domain Tacit Knowledge (Four Things You Must Know Before Designing a Cover)

**1. A cover is an arena, not a gallery piece.** The consistent conclusion from high-earning creators' frameworks (cross-referenced against seven-figure-creator practice retrospectives and multiple creator-tool guides): the cover's first design goal is not to "look good" but to **stand out in the feed among same-topic competitors** (feed-level contrast) — designing against competitors matters far more than pursuing refinement in a vacuum. Operationally: before locking the layout, think one sentence — when a viewer scrolls onto this, what colors surround it? Your palette should differ from theirs, not match a "pretty template".

**2. Text is a scalpel: 0-5 words; the title carries the logic, the cover carries curiosity.** Empirical consensus converging across sources: high-click cover text is 0-5 words (Chinese platforms <=12 chars; 9:16 vertical 2-4 words), bold heavy type with outline/drop shadow for readability on any background; if the text is explaining the image, the image pick failed. The cover doesn't repeat the title — repetition wastes a hook slot. Mobile is the main battlefield (most views come from phones); text must be readable at a ~150px-wide thumbnail size; platforms down-rank "too much text" (Chinese-platform empirical: text area <=20-30% of the frame).

**3. Platform safe zones are measured, not aesthetic.** Platform UI overlays fixed regions (sources cross-referenced across color/design references, short-video cover checklists, and creator libraries): douyin/Bilibili covers **overlay a duration label in the lower-left**, so keep important text and the subject clear of it; 9:16 vertical platforms have a progress bar and interaction buttons at the bottom; Xiaohongshu's feed uses **3:4 vertical as the largest slot** (1080x1440), with a 100-150px safe margin around; Bilibili compresses aggressively, so upload JPG at quality >=85. This script's `layout` `bottom_center` and font-size tiers are designed around these measured regions — don't move text into overlay zones for "composition beauty".

**4. A face is a tool, not decoration: only a readable expression helps.** The consistent direction in creator research: faces bring emotional contagion, but **only a clearly readable face lifts clicks** (surprise / confusion / utter joy); neutral faces and side profiles are worse than none at all. For tech / suspense / authority content, objects and results often beat a face. Eyeline direction is also a tool: looking straight at the lens builds connection; looking at something inside the frame steers the viewer's gaze to that object. Without a suitable face asset, don't force one — pick an object subject by content type.

## Input Checklist

| Input | Required | Notes |
|------|------|------|
| route | yes | `A` = AI-generated (needs title); `B` = frame extraction from final cut (needs video_source) |
| title | A required | Cover theme / headline copy |
| platform | no | `douyin` (default) / `bilibili` / `tiktok` / `youtube`; determines resolution and ratio |
| style | no | `funny` (default) / `professional` / `dramatic` / `cute`; funny auto-adds a NEW badge |
| video_source | B required | Final-cut mp4 path |
| character_image | no | Character image path (optional in route A; must actually exist on disk) |
| output | no | Output path; default `thumbnail_<platform>.png` (frame-extract default `thumb_frame.png`) |

When inputs are missing, ask everything at once: "Please provide: ① route (AI-generated / extract from final cut) ② platform (default douyin).
Route A: also give a title; route B: also give the final-cut path."

## Platform Specs

| Platform | Size | Ratio | Size Limit |
|------|------|------|------|
| Douyin | 1080x1920 | 9:16 | 2MB |
| Bilibili | 1920x1080 | 16:9 | 2MB |
| TikTok | 1080x1920 | 9:16 | 2MB |
| YouTube | 1280x720 | 16:9 | 2MB |

(The script has the same `PLATFORM_SPECS` built in; 2026 common values — check the platform's latest spec before publishing.)

## Pre-flight Checks

- Route B: does `command -v ffmpeg` produce output? If not -> `sudo apt install -y ffmpeg`
  or `brew install ffmpeg` and retry, or switch to route A.
- Route B: does `test -f <video_source>` pass? If not -> ask the user for the correct path, STOP.
- Route A: gateway liveness probe
  `curl -sS -m 5 -o /dev/null -w '%{http_code}' http://127.0.0.1:30080/`
  printing any HTTP code (2xx/401/403/404 all count as alive) passes; connection failure -> have the user
  start the gateway or `export GATEWAY_BASE_URL=http://<host>:<port>` (no trailing slash), STOP.
- Only for downstream wiring may you add `--mock` (or `SKILLKIT_MOCK=1`): it only outputs layout metadata,
  generates no file; **the artifact is not deliverable**.

## Workflow

### Step 1: Determine the Platform Spec

Take resolution/ratio from the table above, or just use the script default `--platform douyin`.
Expected: target width/height and the 2MB limit written down.
If it fails: platform not among the four -> map to 9:16 or 16:9 as closest and tell the user.

### Step 2A: Route A — Gateway Generation

```bash
python3 scripts/thumbnail.py --mock --title "Baby reviews the iPhone 16" --style funny \   # --mock is for integration testing only; remove --mock for real generation (needs gateway/character image)
  --platform douyin --character /tmp/baby.png --output thumbnail_douyin.png
```

Expected: exit code 0, stdout prints JSON containing `output_path`, `spec` (width/height),
`layout` (`text_position`/`font_size`/`badge`), and the file is non-empty.
If it fails: non-0 exit per stderr guidance (exit 3 = character image missing; exit 4 = gateway unreachable
or HTTP error), see the failure table.

### Step 2B: Route B — ffmpeg Frame Extraction

```bash
python3 scripts/thumbnail.py --mock --video /tmp/final.mp4 --timestamp 1.0 \
  --output thumb_frame.png
```

Expected: exit code 0, `thumb_frame.png` non-empty. `--timestamp` defaults to 0.5s; the opening is often
a black frame, so recommend >=1.0. If it fails: exit 3 and the extracted frame is empty -> raise `--timestamp` and rerun.

### Step 3: Text Overlay & Badge

The script's JSON `layout` gives the layout parameters:

- 9:16 uses `bottom_center` (avoiding platform UI, tacit knowledge 3); others use `center`;
- width >=1920 uses `font_size 72`, otherwise 48;
- `style=funny` automatically carries a `NEW` badge;
- text content = title; 9:16 at most 2-4 words (the scalpel discipline of tacit knowledge 2: 0-5 words, title carries logic, cover carries curiosity).

Design principles per [references/thumbnail-design.md](references/thumbnail-design.md) (read it now).

Expected: the overlay plan can restate the three elements of position / font size / copy; the text sits outside platform overlay zones.
If it fails: title too long -> confirm a shortened version with the user before locking; if the user insists on long text -> explain per tacit knowledge 2 the thumbnail-size readability and the platform's "too much text" down-rank risk; if they insist, note the risk honestly and proceed.

### Step 4: Validate & Deliver

```bash
ls -lh thumbnail_douyin.png
```

Expected: file exists, non-empty, under the platform's 2MB cap (over-limit prints `[WARN]`; per the prompt,
switch to JPG or lower quality and re-export). Report the absolute path and platform spec to the user.
If it fails: over-limit warning -> switch to JPG / lower quality, rerun Step 2, and validate once more.

## Failure Remediation Table

| Symptom / Error Code | Cause | Remedy |
|------|------|------|
| exit 2: ffmpeg not on PATH | Route B missing dependency | Install ffmpeg per stderr; or switch to route A |
| exit 3: character image missing | Wrong `--character` path | `test -f` to verify the path; ask the user for the correct file |
| exit 3: video file missing | Wrong `--video` path | `test -f` to verify the path; ask the user for the correct file |
| exit 3: extracted frame empty | Timestamp lands on a black/bad frame | Raise `--timestamp` (e.g. 1.5, 2.0) and rerun |
| exit 4: can't reach the gateway | Gateway not started or wrong address | Troubleshoot per the pre-flight probe command; confirm `GATEWAY_BASE_URL` has no trailing slash |
| exit 4: gateway returns HTTP 4xx/5xx | Auth / rate limit / service error | Auth via the `GATEWAY_API_KEY` env var (never on the command line); retry 429 later |
| `[WARN]` cover over 2MB | High resolution / over-high quality | Switch to JPG or lower quality, re-export, re-validate |
| User says the cover "isn't pretty enough" and keeps asking for changes | Treating the cover as art (tacit knowledge 1) | Remind: first compare differentiation against the competitor feed, then talk refinement; suggest A/B testing two versions instead of repeated subjective rework |
| Text unreadable on mobile | Wrong font-size tier or too-long text | Lock to the layout tier; shorten the title first, don't shrink the font to cram it in |
| Got mock output | Misused `--mock`/SKILLKIT_MOCK=1 | Mock has no real file; remove the mock flag and rerun real mode |

## Delivery Standard

- Success = a real-mode cover file, non-empty, dimensions matching the platform spec, size < 2MB cap,
  absolute path reported (default name `thumbnail_<platform>.png` or the user-specified `--output`).
- The 9:16 platform text-overlay plan (position / font size / copy) is implemented per layout.
- The mock artifact is not a deliverable — receiving mock JSON counts as incomplete.

## References

- [references/thumbnail-design.md](references/thumbnail-design.md) — cover design principles and examples; read before locking text/badges in Step 3
