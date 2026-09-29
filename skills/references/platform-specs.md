# Platform Spec Shared Reference (single source of truth)

Cross-referenced platform constants used by publishing/design/thumbnail skills
(`layout-spec-auditor`, `video-thumbnail`, publisher family). Each entry carries
a `verified` date and a re-verification command, because platform specs change
without notice — **treat any number here as "last verified", not permanent**.

Rule: when two skills disagree on a platform constant, fix the data here first,
then point both skills at this file. Never fork the value locally.

## Bilibili (哔哩哔哩) video cover

- Recommended size: **1146×717** (≈16:10) — the ratio the web player crops to;
  1920×1080 (16:9) uploads are also accepted and auto-cropped, but text near
  edges may be trimmed.
- File size limit: **≤5MB**.
- Format: JPG/PNG; upload JPG at quality ≥85 (Bilibili recompresses aggressively).
- Safe zone: duration label overlays the **lower-left** corner — keep title text
  and subject clear of it.
- Verified: 2026-09-29 via public creator-library specs (稿定设计 B 站封面模板
  1146×717 ≤5MB 口径). Re-verify before relying on it:
  `curl -s https://member.bilibili.com/york/console | grep -i cover` in a
  logged-in browser session, or upload a test cover via the投稿 console.

## Other platforms (as shipped in skill-local tables)

Douyin 1080×1920 9:16 ≤2MB; TikTok 1080×1920 9:16 ≤2MB; YouTube thumbnail
1280×720 16:9 ≤2MB; WeChat 公众号 header 900×383; Xiaohongshu feed 3:4
1080×1440 (largest slot), 1:1 square. Values move — re-verify per campaign.
