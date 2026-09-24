---
name: douban-publisher
description: >
  Helps adapt and write platform-native content for Douban (Douban), the Chinese
  book / movie / music / culture community. Produces Douban-style notes (diary),
  reviews (film/book review), and group posts with a thoughtful, literary voice, tags,
  and group targeting. Use when the user asks for Douban content, Douban note,
  douban review, douban adaptation, platform-specific content for douban, or
  publish to Douban. Do NOT use for cookie-based posting automation or other
  platforms.
license: Apache-2.0
metadata:
  author: awesome-skillkit
  version: "2.0"
  category: content-adaptation
  platform: douban
  verified-date: "2026-09-24"
---

# Douban Content Adaptation Skill

## Overview

This skill converts a draft into Douban (Douban)-native content: a personal note
(diary), a book/movie review (book review/film review), or a group post (group). Douban's
audience is educated, culturally curious, and skeptical of marketing. The skill
produces the text, tags, and group recommendation the user enters manually.

## Platform Format Rules

- **Note / review title**: 1–100 characters; Douban prefers thoughtful,
  understated titles over clickbait.
- **Body**: rich text with limited Markdown; headings, bold, lists, and images
  are supported.
- **Paragraphs**: medium-length paragraphs; literary reflection, not bullet
  spam.
- **Images**: Markdown `![alt](URL)`; inline images are welcomed in reviews.
- **Groups**: posts to groups (group) have a separate title field and body; pick
  a group whose rules match the topic.
- **Code blocks**: rare; if used, keep them small.

## Reader Preferences

- Douban readers reward insight, honesty, and cultural references.
- A review should have a clear, defensible opinion backed by specific examples,
  not generic praise.
- Personal notes (diary) work best as reflective first-person writing.
- Avoid "this is great" hype; readers can smell marketing.

## Platform Context & Tone

- Tone: thoughtful, slightly intellectual; like writing for a literary magazine.
- Tags (tags): 3–10 tags help Douban search and recommendation.
- Taboo: marketing disguised as reviews, five-star product shilling, politically
  sensitive content, group rule violations (self-promotion in groups that forbid
  it), fabricated "I watched this" claims.

## Content Length Guidelines

- Group post: 200–1,000 characters.
- Note / diary: 800–3,000 characters.
- Book / movie review: 1,000–5,000 characters.

## Image & Illustration Support

- Cover image for notes: optional; a cultural / atmospheric image, 3:2.
- Inline images in reviews: 1–5; film stills, book covers, personal photos.
- Keep images tasteful and thematically relevant.

## Background & Styling

- Douban controls the theme; no custom fonts/colors.
- Use headings, bold, and quote blocks for reflection structure.

## SEO & Discovery

- Douban pages rank well in Baidu for book/movie queries.
- Include the exact work title (book/film) in the review title and body.
- 3–10 tags; pick a relevant group (group) for group posts.
- A clear opinion (e.g. "3.5 stars, why it almost worked") drives comments.

## Content Adaptation Workflow

1. Decide the type: note, review, or group post.
2. Write an understated title (≤100 chars); for reviews, name the work.
3. Reframe the voice as thoughtful first-person; strip marketing hype.
4. Split into medium paragraphs; add headings for long reviews.
5. Place 1–5 images at thematic moments.
6. Pick 3–10 tags and 1–2 matching groups.
7. Run the checklist.

## Quality Checklist

- [ ] Title ≤100 chars, understated, names the work for reviews.
- [ ] Voice is thoughtful first-person; no marketing hype.
- [ ] Clear opinion backed by specific examples.
- [ ] 3–10 tags chosen.
- [ ] 1–2 relevant groups identified (for group posts).
- [ ] 1–5 images marked.
- [ ] No self-promotion that violates group rules.

## When to Use

- "Write a Douban note / review about ..."
- "Adapt this for Douban / Douban"
- "Platform-specific content for douban", "publish to Douban"
- "A cultural review in the Douban style"

## Do NOT Use For

- Cookie-based posting automation.
- Product shilling / undisclosed ads.
- Technical tutorials (use Juejin / CSDN).
- Image-first lifestyle notes (use Xiaohongshu).
