---
name: toutiao-publisher
description: >
  Helps adapt and write platform-native articles for Toutiao (Toutiao), the
  Chinese algorithmic news and content feed. Produces Toutiao-style headlines,
  body copy, images, and tags optimized for the recommendation engine. Use when
  the user asks for Toutiao content, Toutiao article, toutiao article, toutiao
  adaptation, platform-specific content for toutiao, or publish to Toutiao.
  Do NOT use for cookie-based posting automation or other platforms.
license: Apache-2.0
metadata:
  author: awesome-skillkit
  version: "2.0"
  category: content-adaptation
  platform: toutiao
  verified-date: "2026-09-24"
---

# Toutiao Content Adaptation Skill

## Overview

This skill converts a generic draft into a Toutiao (Toutiao)-native article.
Toutiao is a Chinese algorithmic feed platform: distribution is driven by user
interest signals, not followers. The skill produces the headline, body, images,
and tags the user pastes into the Toutiao editor manually.

## Platform Format Rules

- **Input format**: rich-text editor; Markdown is accepted via the in-editor
  import but the published body is HTML.
- **Title**: up to 30 Chinese characters; the headline is the single biggest
  lever for click-through in the feed.
- **Body**: short paragraphs (1–3 sentences), frequent subheads, no long
  blocks.
- **Images**: inline images must be uploaded to Toutiao's image host; 3–9 images
  per article perform best; wide 16:9 images look good in the feed.
- **Code blocks**: not a code-friendly platform; keep code to screenshots or
  omit it.
- **Tables**: not ideal; use bullet lists or short paragraphs instead.
- **Links**: external links are heavily restricted; put sources in plain text.

## Reader Preferences

- Toutiao readers scroll a fast mobile feed; the first 2 lines decide the click.
- A concrete, specific headline with numbers or a contrast pulls readers.
- Plain, direct language; avoid academic jargon.
- Emotional resonance + useful information; readers share what makes them feel
  something.

## Platform Context & Tone

- Tone: conversational, news-wire fast; like a friend summarizing a headline.
- The algorithm rewards completion rate and dwell time, so keep paragraphs short
  and the pacing tight.
- Taboo: clickbait that does not deliver, fabricated statistics, political
  rumor, medical / investment advice without disclaimers,clickbait.

## Content Length Guidelines

- Quick news / observation: 300–800 characters.
- Standard article: 800–2,000 characters.
- Deep feature: 2,000–4,000 characters.

## Image & Illustration Support

- Cover image: required for better feed distribution; ratio ~16:9, 1080x608,
  JPG/PNG, bright and high-contrast.
- Inline images: 3–9 per article; wide 16:9 photos or simple infographics;
  avoid text-heavy screenshots.
- The cover shows in the feed thumbnail; put the subject in the center.

## Background & Styling

- Toutiao controls the theme; no custom fonts/colors.
- Use bold, subheads, and images for rhythm; avoid heavy formatting.

## SEO & Discovery

- The recommendation engine reads title, tags, and early engagement.
- Title contains the topic keyword and a hook (number, contrast, or question).
- Pick 3–5 tags / categories from Toutiao's list; tags drive interest targeting.
- The first 100 chars restate the headline and set up the body.

## Content Adaptation Workflow

1. Rewrite the headline to ≤30 chars with a number / contrast / question hook.
2. Open with 2 lines that restate the headline and pull the reader in.
3. Split the body into 1–3 sentence paragraphs.
4. Replace tables / code with short lists or screenshots.
5. Mark 3–9 image placements, starting with a 16:9 cover.
6. Remove external hyperlinks; write sources as plain text.
7. Pick 3–5 tags / categories.
8. Run the checklist.

## Quality Checklist

- [ ] Headline ≤30 chars with a hook.
- [ ] Opening 2 lines pull the reader in.
- [ ] Paragraphs are 1–3 sentences.
- [ ] 3–9 images marked, including a 16:9 cover.
- [ ] No external inline links.
- [ ] No code tables / heavy technical formatting.
- [ ] 3–5 tags / categories chosen.
- [ ] No clickbait that does not deliver.

## When to Use

- "Write a Toutiao article about ..."
- "Adapt this for Toutiao / Toutiao"
- "Platform-specific content for toutiao", "publish to Toutiao"
- "A news-style piece optimized for the Toutiao feed"

## Do NOT Use For

- Cookie-based posting automation.
- Technical tutorials (use Juejin / CSDN).
- Literary essays (use Jianshu).
- Image-first product notes (use Xiaohongshu).
