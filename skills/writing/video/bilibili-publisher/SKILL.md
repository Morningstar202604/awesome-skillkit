---
name: bilibili-publisher
description: >
  Helps adapt and write platform-native text for Bilibili (Bilibili): video
  titles, descriptions, tags, cover/intro copy, short dynamic posts (dynamic post), and
  Bilibili column articles (column). Produces Bilibili-style metadata, danmu-friendly
  hooks, and the Markdown for Bilibili's in-house article editor. Use when the
  user asks for Bilibili content, bilibili video description, Bilibili column article,
  bilibili dynamic post, bilibili adaptation, platform-specific content for
  bilibili, or publish to Bilibili. Do NOT use for upload automation, cookie
  scripts, or other platforms.
license: Apache-2.0
metadata:
  author: awesome-skillkit
  version: "2.0"
  category: content-adaptation
  platform: bilibili
  verified-date: "2026-09-24"
---

# Bilibili Content Adaptation Skill

## Overview

This skill adapts a draft into Bilibili-native text: it writes the video title,
description, tags, intro/hook line, the post for Bilibili's feed (dynamic post), and / or
a Bilibili column article (column). Bilibili is a Chinese video community with a
young, meme-aware audience that rewards personality and clear structure. The
skill does not upload video; it produces the text metadata and article body the
user enters manually.

## Platform Format Rules

- **Video title**: 1–80 characters; front-load the hook, use `【】` brackets for
  the series / topic, and keep it click-worthy but not misleading.
- **Video description**: up to 250 characters in the visible snippet; longer
  text hides behind "expand". Put the most important info first.
- **Tags**: up to 12 tags; mix 1 broad tag (e.g. knowledge, tech), 2–3 niche tags,
  and 1–2 meme / community tags.
- **Column article (column)**: Markdown supported; headings, code blocks, images,
  and quote blocks render natively.
- **Dynamic (dynamic post)**: a short feed post, up to ~230 chars visible; supports
  images, @mentions, and hashtags.
- **Chapters / timestamps**: in the description, list `0:00 Intro` style
  timestamps; Bilibili turns them into chapter markers.

## Reader Preferences

- Bilibili viewers decide in the first 5 seconds; the title and the video
  intro must state the payoff immediately.
- A friendly, energetic, slightly nerdy tone fits; self-deprecating humor and
  "danmu memes" (danmu memes) are welcomed when on-topic.
- Column readers expect the same level of detail as a Juejin / Zhihu post but
  with a more casual voice.

## Platform Context & Tone

- Tone: enthusiastic peer; "uploader" (uploader) voice; speak directly to "you".
- Taboo: clickbait that does not deliver, hard ads without disclosure,
  politically sensitive content, copyright-music misuse, and fake "I spent
  300 hours" exaggeration that the community calls out.
- Respect community memes but do not force them; overused memes feel inauthentic.

## Content Length Guidelines

- Video description snippet: ≤250 chars; full description up to ~2,000 chars.
- Dynamic post: 100–230 chars.
- Column article: 1,500–6,000 Chinese characters.

## Image & Illustration Support

- **Video cover (cover)**: 16:9, recommended 1920x1080 or 1280x720, JPG/PNG;
  Bilibili crops to a wide banner; keep text large and centered.
- **Column inline images**: 1080px wide, Markdown `![alt](URL)`.
- **Dynamic images**: 1–9 images; square or 3:4 works best in the feed.

## Background & Styling

- Bilibili controls the video player skin and column theme.
- In column articles, use headings, bold, quote blocks, and code blocks for
  structure; emojis in headings are common.

## SEO & Discovery

- Bilibili search ranks title, description, and tags; repeat the core keyword
  naturally in all three.
- 12 tags is the ceiling; use them all with a mix of broad + niche.
- Column articles are indexed by search engines; a keyword-rich first paragraph
  helps.
- Chapters / timestamps improve session length and recommendation.

## Content Adaptation Workflow

1. Decide the deliverable: video metadata, dynamic post, or column article.
2. For video: write a ≤80-char title with `【topic】` brackets; a ≤250-char
   description snippet; list timestamps; pick 12 tags.
3. For dynamic: condense to a 100–230-char feed post with 1–2 hashtags.
4. For column: restructure the draft into Markdown with `##` headings, code
   blocks, and images; add an emoji to section headers.
5. Specify a 16:9 cover brief (1920x1080, large centered text) if needed.
6. Run the checklist.

## Quality Checklist

- [ ] Video title ≤80 chars with `【】` topic brackets.
- [ ] Description snippet ≤250 chars with the payoff up front.
- [ ] 12 tags chosen (broad + niche + community mix).
- [ ] Timestamps listed if the video has multiple sections.
- [ ] Dynamic post ≤230 chars if used.
- [ ] Column Markdown has `##` headings, no h1.
- [ ] Cover brief 16:9, 1920x1080, large readable text.
- [ ] No misleading clickbait; no undisclosed ads.

## When to Use

- "Write a Bilibili title / description for this video"
- "Write a Bilibili column article about ..."
- "Adapt this into a Bilibili dynamic post"
- "Platform-specific content for bilibili", "publish to Bilibili"

## Do NOT Use For

- Video upload / cookie automation scripts.
- Pure text articles better suited to Zhihu / Juejin.
- Image-first product notes (use Xiaohongshu).
- News headlines (use Toutiao / Baijiahao).
