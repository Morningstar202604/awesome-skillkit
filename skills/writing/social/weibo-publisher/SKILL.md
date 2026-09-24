---
name: weibo-publisher
description: >
  Helps adapt and write platform-native short posts for Weibo (Weibo), the Chinese
  microblog and public-square platform. Produces Weibo-style posts with punchy
  copy, hashtags, @mentions, image plans, and thread-style long-post formatting.
  Use when the user asks for Weibo content, Weibo copy, weibo post, weibo adaptation,
  platform-specific content for weibo, or publish to Weibo. Do NOT use for
  cookie-based posting automation or other platforms.
license: Apache-2.0
metadata:
  author: awesome-skillkit
  version: "2.0"
  category: content-adaptation
  platform: weibo
  verified-date: "2026-09-24"
---

# Weibo Content Adaptation Skill

## Overview

This skill converts a draft into a Weibo (Weibo)-native post. Weibo is China's
public-square microblog: distribution is driven by retweets, hot-search topics,
and hashtags. The skill produces the short post, the long-form article version
when needed, hashtags, @mentions, and image plan the user enters
manually.

## Platform Format Rules

- **Short post**: up to ~2,000 characters visible (but only the first ~140 chars
  show in the feed before "expand"); lead with the hook.
- **Hashtags**: `#topic#` syntax; 1–3 relevant hashtags, ideally an existing hot
  topic.
- **@mentions**: `@username` to tag accounts.
- **Images / video**: up to 9 images per post or one video; square (1:1) or
  3:2 images look best in the feed.
- **Long post / Weibo article (Toutiao article)**: for >2,000 chars, use the article
  editor; Markdown-ish rich text with headings and images.
- **Links**: a single link per post is allowed in the body; Weibo shortens and
  gates it behind a redirect warning.

## Reader Preferences

- Weibo users scroll fast; the first line must be a hook, a number, or a
  controversy.
- Punchy, conversational, slightly sensational but accurate.
- Emoji and line breaks help; walls of text get skipped.
- Thread-style (a short opening + "1/5" numbered continuation) works for
  multi-point takes.

## Platform Context & Tone

- Tone: public-square commentator; sharp, timely, shareable.
- Taboo: spreading unverified rumors, politically sensitive commentary,
  coordinated spam, buying retweets, medical/financial claims.
- Respect hot-search etiquette: do not hijack unrelated trending topics.

## Content Length Guidelines

- Short post: 80–200 characters for the visible hook.
- Thread: 500–2,000 characters across multiple posts.
- Weibo article / long post: 2,000–6,000 characters.

## Image & Illustration Support

- Cover / post images: 1–9 per post; 1:1 square or 3:2; bright, high-contrast.
- Video: 15s–15min; cover frame should match the hook.
- Long-post article: 1080px wide inline images.

## Background & Styling

- Weibo controls the skin; no custom fonts/colors.
- Use emoji, line breaks, hashtags, and @mentions for emphasis.

## SEO & Discovery

- Hot-search topics (hot search) drive distribution; attach a relevant `#topic#` only
  if it genuinely fits.
- The first line is the meta description in search and cards.
- A clear opinion / take drives retweets; retweets are the main discovery loop.

## Content Adaptation Workflow

1. Write a hook first line (the visible ~140 chars).
2. If over ~2,000 chars, split into a Weibo article; otherwise keep as a post.
3. Add 1–3 relevant `#topic#` hashtags and any @mentions.
4. Insert line breaks and emoji; strip Markdown formatting.
5. Plan 1–9 images (1:1 or 3:2) or a video cover.
6. Run the checklist.

## Quality Checklist

- [ ] First line is a hook (numbers, opinion, or question).
- [ ] Visible snippet under ~140 chars.
- [ ] 1–3 relevant `#topic#` hashtags.
- [ ] No Markdown; uses line breaks and emoji.
- [ ] 1–9 images planned at 1:1 or 3:2.
- [ ] No unverified rumors or hot-topic hijacking.
- [ ] Long content split into a Weibo article if over 2,000 chars.

## When to Use

- "Write a Weibo post about ..."
- "Adapt this for Weibo / Weibo"
- "Platform-specific content for weibo", "publish to Weibo"
- "A timely public take in the Weibo style"

## Do NOT Use For

- Cookie-based posting automation.
- Long technical articles (use Zhihu / Juejin).
- Image-first product notes (use Xiaohongshu).
- Personal literary essays (use Jianshu).
