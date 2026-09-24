---
name: cnblogs-skill
description: >
  Helps adapt and write platform-native Markdown articles for CNBlogs (CNBlogs),
  the Chinese developer blogging community. Produces CNBlogs-format Markdown with
  short paragraphs, emoji headings, code blocks, tables, images, categories, and
  tags. Use when the user asks for CNBlogs content, cnblogs article, blog garden
  post, cnblogs adaptation, platform-specific content for cnblogs, or publish to
  CNBlogs. Do NOT use for automation, image upload scripts, or posting to other
  platforms.
license: Apache-2.0
metadata:
  author: awesome-skillkit
  version: "2.0"
  category: content-adaptation
  platform: cnblogs
  verified-date: "2026-09-24"
---

# CNBlogs Content Adaptation Skill

## Overview

This skill converts a generic draft into a CNBlogs (CNBlogs)-native Markdown
article. CNBlogs is a long-running Chinese developer blog platform with a
technical, no-nonsense audience. The skill produces the Markdown body, title,
tags, and image placement the user pastes into the CNBlogs editor manually.

## Platform Format Rules

- **Input format**: standard Markdown (GFM) supported; you can also paste HTML.
- **Title**: 1–100 characters; avoid HTML entities in the title.
- **Headings**: do **not** use `#` (h1) — it duplicates the page title; start
  at `##` (h2) for sections and `###` (h3) for subsections; never skip from h2
  to h4.
- **Paragraphs**: short paragraphs with a blank line between them; do not rely
  on `<br>` tags (they show as raw text in Markdown mode).
- **Dividers**: use `---` between major sections.
- **Tables**: GFM tables supported; center-align numeric columns (`:---:`),
  left-align text columns (`:---`).
- **Code blocks**: fenced with triple backticks and a language tag
  (```python, ```bash); leave a blank line before and after.
- **Quote blocks**: `>` for emphasis / key quotes; keep to ≤5 per article.
- **Images**: `![alt](URL)` with a blank line before and after.

## Reader Preferences

- The core house style is **short paragraphs with generous white space** — one
  or a few sentences per block, never a wall of text.
- A hooky opening heading (often with an emoji) that tells a story or sets up
  tension.
- Technical depth: working code, real data, comparison tables, and pitfalls.
- End with a "key takeaways" recap.

## Platform Context & Tone

- Tone: senior developer peer-to-peer; concrete, practical, slightly informal.
- Emoji in section headings are expected (📊, 🔥, 📌) for visual rhythm.
- Taboo: hype marketing, "repost please", keyword stuffing, non-technical fluff.
- A signature (author + original link) is managed in CNBlogs site settings, not
  pasted into the body.

## Content Length Guidelines

- How-to / tutorial: 1,500–4,000 Chinese characters.
- Deep analysis: 4,000–8,000 characters.
- Quick note: 300–800 characters.

## Image & Illustration Support

- 2 images per article is the house norm: a concept image after the opening, and
  a comparison/trend image in the middle.
- Markdown syntax `![desc](URL)`; image URLs are hosted on CNBlogs' image bed.
- Recommended 3:2 ratio, 1536x1024, dark-theme flat design (#0d1117 background,
  green #238636 + blue #58a6ff accents) if generating technical illustrations.

## Background & Styling

- No custom backgrounds or fonts; CNBlogs renders its own skin.
- Use headings, bold, tables, quote blocks, and `---` dividers for structure.

## SEO & Discovery

- Pick one category (category) and 3–10 tags (tags) matching the topic.
- Put the primary keyword in the title and first paragraph.
- Alt text on images describes the chart, not "image1".

## Content Adaptation Workflow

1. Rewrite the title to ≤100 chars with no HTML entities.
2. Convert all `#` h1 headings to `##`; ensure no heading level skips.
3. Split long paragraphs into 1–3 sentence blocks with blank lines.
4. Add `---` between major sections and an emoji to each section heading.
5. Convert comparisons into GFM tables with aligned columns.
6. Ensure fenced code blocks have a language tag and surrounding blank lines.
7. Place 2 images after the opening and after a key data section.
8. Add ≤5 quote blocks for punchy conclusions.
9. End with a "📌 Key Takeaways" recap.
10. Choose category + 3–10 tags; run the checklist.

## Quality Checklist

- [ ] Zero h1 (`#`) headings.
- [ ] Title has no HTML entities and is ≤100 chars.
- [ ] No `<br>` tags in Markdown body.
- [ ] Heading levels do not skip.
- [ ] Fenced code blocks use triple backticks with a language.
- [ ] At least 2 comparison tables where useful.
- [ ] Quote blocks ≤5.
- [ ] 2 images placed with blank lines around them.
- [ ] Section headings carry an emoji.
- [ ] Ends with a key-takeaways section.

## When to Use

- "Write a CNBlogs article about ..."
- "Adapt this for CNBlogs / CNBlogs"
- "Platform-specific content for cnblogs", "publish to CNBlogs"
- "A developer tutorial in the CNBlogs style"

## Do NOT Use For

- Image upload automation or cookie/session scripts.
- Literary essays (use Jianshu).
- Short social notes (use Xiaohongshu / Weibo).
- Q&A answers (use Zhihu / SegmentFault).
