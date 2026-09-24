---
name: xiaohongshu-publisher
description: >
  Helps adapt and write platform-native notes for Xiaohongshu (Xiaohongshu / RedNote),
  the image-first Chinese lifestyle and product-discovery community. Produces
  Xiaohongshu-style notes with a short punchy title, emoji-rich body under the
  1000-character limit, hashtags, and image/carousel guidance. Use when the user
  asks for Xiaohongshu content, Xiaohongshu note, RedNote note, xiaohongshu adaptation,
  platform-specific content for xiaohongshu, or publish to Xiaohongshu. Do NOT use
  for cookie-based posting automation, image editing, or other platforms.
license: Apache-2.0
metadata:
  author: awesome-skillkit
  version: "2.0"
  category: content-adaptation
  platform: xiaohongshu
  verified-date: "2026-09-24"
---

# Xiaohongshu (RedNote) Content Adaptation Skill

## Overview

This skill converts a generic draft into a Xiaohongshu (Xiaohongshu / RedNote) note.
Xiaohongshu is an image-first community: a note is a carousel of images plus a
short caption. Distribution is driven by the discovery feed, and the cover image
is the #1 click lever. The skill produces the title, caption, hashtags, and image
plan the user enters manually.

## Platform Format Rules

- **Title**: up to 20 Chinese characters; punchy, benefit-driven, often with an
  emoji; the title shows on the cover thumbnail.
- **Body / caption**: up to 1,000 Chinese characters; write like a friend
  sharing a tip.
- **Formatting**: no Markdown rendering in the caption — use line breaks,
  emoji, and all-caps sparingly; bullet style with emoji (✅ ❌ 🔥).
- **Hashtags**: use `#topic#` syntax in the caption; add 5–15 tags at the end
  or inline.
- **Images / carousel**: 1–9 images; the cover decides the click; preferred
  ratios are 3:4 (portrait) or 1:1; vertical 3:4 takes the most feed space.
- **Links**: external hyperlinks are not allowed in the caption; guides put
  "link in bio" or "comment" but must follow platform rules.
- **Code / tables**: not supported; keep to plain text lists.

## Reader Preferences

- Xiaohongshu readers scan the cover first; if the cover is clear and
  benefit-driven, they swipe.
- Tone: enthusiastic, personal, "I tried this and here's the honest review".
- Lists with emoji checkmarks, before/after, and price/spec details perform
  well.
- Authenticity beats polish; filters and staged ads are called out.

## Platform Context & Tone

- Tone: best-friend recommendation; first-person "I" sharing a real experience.
- Taboo: hard-sell ads without disclosure, fake reviews, exaggerated "must-buy /
  god-tier" claims, traffic diversion to WeChat, politically sensitive content,
  weight-loss / medical claims.
- Use platform-safe language; avoid absolute words (best, number one, 100%) that trigger
  moderation.

## Content Length Guidelines

- Caption: 200–800 characters (under 1,000 max).
- Title: ≤20 characters.
- Carousel: 3–9 images; more images = longer dwell time.

## Image & Illustration Support

- **Cover image (cover image)**: the most important asset; 3:4 portrait (e.g.
  1080x1440) or 1:1; bright, high-contrast, with large readable text overlay
  stating the benefit.
- **Carousel images**: 2nd–9th images carry the detail (screenshots, close-ups,
  before/after, specs); keep a consistent visual style.
- Recommended: clean, warm, high-saturation; avoid dark moody tech looks.

## Background & Styling

- No custom backgrounds; the note renders in Xiaohongshu's card style.
- Use emoji, line breaks, and all-caps for emphasis in the caption.

## SEO & Discovery

- Xiaohongshu search is a primary discovery channel; the title and caption must
  contain the words users actually search (e.g. "dry-skin foundation recommendation").
- 5–15 `#hashtags#`; mix broad (beauty), niche (dry-skin base-makeup), and scene (student-budget).
- The cover text should match the search keyword.
- Early engagement (saves, comments) drives the feed; end with a question to
  prompt comments.

## Content Adaptation Workflow

1. Rewrite the title to ≤20 chars, benefit-driven, with an emoji.
2. Rewrite the body as a friendly caption under 1,000 chars; use emoji bullets.
3. Strip Markdown, tables, code, and external links.
4. End with a question or a "comment below" prompt.
5. Append 5–15 `#hashtags#`.
6. Specify a 3:4 cover (1080x1440) with large text overlay; plan 3–9 carousel
   images.
7. Run the checklist.

## Quality Checklist

- [ ] Title ≤20 chars, benefit-driven, with emoji.
- [ ] Caption under 1,000 chars, friendly tone, no Markdown.
- [ ] No external links or WeChattraffic diversion.
- [ ] 5–15 `#hashtags#` included.
- [ ] Cover brief 3:4 (1080x1440) with large text overlay.
- [ ] 3–9 carousel images planned.
- [ ] No absolute claims (best, 100%, number one).
- [ ] Ends with a comment prompt / question.

## When to Use

- "Write a Xiaohongshu note about ..."
- "Adapt this for Xiaohongshu / RedNote"
- "Platform-specific content for xiaohongshu", "publish to Xiaohongshu"
- "A product review / lifestyle tip in the RedNote style"

## Do NOT Use For

- Cookie-based posting automation.
- Image editing / cropping (use image tools).
- Long-form articles (use Zhihu / Juejin).
- Hard news (use Toutiao / Baijiahao).
