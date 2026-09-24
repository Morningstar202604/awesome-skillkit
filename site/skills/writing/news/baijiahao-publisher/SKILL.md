---
name: baijiahao-publisher
description: >
  Helps adapt and write platform-native articles for Baijiahao (Baijiahao), Baidu's
  content platform. Produces Baijiahao-style headlines, body copy, images, and
  tags optimized for Baidu search and the Baijiahao feed. Use when the user asks
  for Baijiahao content, Baijiahao article, baijiahao article, baijiahao adaptation,
  platform-specific content for baijiahao, or publish to Baijiahao. Do NOT use for
  cookie-based posting automation or other platforms.
license: Apache-2.0
metadata:
  author: awesome-skillkit
  version: "2.0"
  category: content-adaptation
  platform: baijiahao
  verified-date: "2026-09-24"
---

# Baijiahao Content Adaptation Skill

## Overview

This skill converts a generic draft into a Baijiahao (Baijiahao)-native article.
Baijiahao is Baidu's content platform; articles rank in Baidu search and are
distributed through the Baijiahao feed. The skill produces the headline, body,
images, and tags the user pastes into the Baijiahao editor manually.

## Platform Format Rules

- **Input format**: rich-text editor; Markdown can be imported but the published
  body is HTML.
- **Title**: up to 30 Chinese characters; front-load the Baidu-search keyword.
- **Body**: short paragraphs (2–4 sentences), subheads every few paragraphs.
- **Images**: inline images uploaded to Baidu's image host; 3–6 images per
  article; bright, clear photos.
- **Code blocks / tables**: not ideal for a general-news audience; use short
  lists instead.
- **Links**: external links are restricted; cite sources as plain text.

## Reader Preferences

- Baijiahao readers arrive from Baidu search or the feed looking for a clear
  answer to a question.
- Direct, explanatory language; avoid jargon.
- A headline that matches how someone would type the question into Baidu.
- Useful, practical information with a clear takeaway.

## Platform Context & Tone

- Tone: informative, encyclopedia-meets-news; slightly more formal than Toutiao.
- Baidu heavily indexes Baijiahao, so keyword coverage matters for discovery.
- Taboo: fabricated statistics, medical / financial advice, politically
  sensitive content, exaggerated headlines, content farms scraping.

## Content Length Guidelines

- Quick explainer: 500–1,000 characters.
- Standard article: 1,000–2,500 characters.
- Deep feature: 2,500–5,000 characters.

## Image & Illustration Support

- Cover image: recommended; ratio ~16:9, 1080x608, bright and clear.
- Inline images: 3–6 per article; wide photos or simple infographics.
- Avoid text-heavy screenshots; use clean diagrams if needed.

## Background & Styling

- Baijiahao controls the theme; no custom fonts/colors.
- Use bold, subheads, and images for rhythm.

## SEO & Discovery

- Baijiahao articles rank directly in Baidu search; the title must match a
  likely Baidu query.
- Repeat the core keyword in the first paragraph, a subhead, and the conclusion.
- Pick 3–5 tags / categories from Baijiahao's list.
- Add a clear, keyword-rich summary at the end.

## Content Adaptation Workflow

1. Rewrite the title to ≤30 chars matching a Baidu search query.
2. Open with a direct answer to the query.
3. Split the body into short paragraphs with subheads.
4. Replace code/tables with bullet lists.
5. Mark 3–6 image placements, including a 16:9 cover.
6. Remove external links; cite sources as plain text.
7. Pick 3–5 tags / categories.
8. Add a keyword-rich summary; run the checklist.

## Quality Checklist

- [ ] Title ≤30 chars and matches a Baidu query.
- [ ] Opening directly answers the query.
- [ ] Core keyword appears in first paragraph, subhead, and conclusion.
- [ ] Paragraphs are short; subheads every few paragraphs.
- [ ] 3–6 images marked, including a 16:9 cover.
- [ ] No external inline links.
- [ ] 3–5 tags / categories chosen.
- [ ] No fabricated statistics or unsourced claims.

## When to Use

- "Write a Baijiahao article about ..."
- "Adapt this for Baijiahao / Baijiahao"
- "Platform-specific content for baijiahao", "publish to Baijiahao"
- "A Baidu-search-optimized explainer"

## Do NOT Use For

- Cookie-based posting automation.
- Technical tutorials (use Juejin / CSDN).
- Literary essays (use Jianshu).
- Image-first social notes (use Xiaohongshu).
