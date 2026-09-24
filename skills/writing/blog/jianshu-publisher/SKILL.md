---
name: jianshu-publisher
description: >
  Helps adapt and write platform-native Markdown essays and articles for Jianshu
  (Jianshu), the Chinese literary / personal-essay community. Produces Jianshu-style
  posts with a literary voice, short poetic title, collections, and tags. Use
  when the user asks for Jianshu content, Jianshu essay, jianshu essay, jianshu
  adaptation, platform-specific content for jianshu, or publish to Jianshu.
  Do NOT use for cookie-based posting automation or other platforms.
license: Apache-2.0
metadata:
  author: awesome-skillkit
  version: "2.0"
  category: content-adaptation
  platform: jianshu
  verified-date: "2026-09-24"
---

# Jianshu Content Adaptation Skill

## Overview

This skill converts a generic draft into a Jianshu (Jianshu)-native essay. Jianshu
is a Chinese platform for personal essays, literature, life writing, and
opinion pieces. The audience reads for voice and reflection, not code. The skill
produces the Markdown body, short title, collection, and tags the user pastes
into the Jianshu editor manually.

## Platform Format Rules

- **Input format**: Markdown is native.
- **Title**: up to 30 characters (a short, literary title works best).
- **Headings**: `##` for sections; essays often use a single narrative flow
  with few headings, or short section dividers (`---`).
- **Paragraphs**: short paragraphs; blank lines between them; Jianshu renders
  on a comfortable reading-width column.
- **Code blocks**: fenced triple backticks supported, but code is uncommon
  here — keep it small if used.
- **Quote blocks**: `>` supported and commonly used for epigraphs.
- **Images**: Markdown `![alt](URL)`; inline illustrations are welcomed.
- **Tables**: supported but rare in essays.

## Reader Preferences

- Voice, honesty, and a personal story beat beats an outline-style argument.
- An epigraph or a quiet opening line pulls readers in.
- Reflective, lyrical prose; concrete sensory details rather than abstractions.
- A short, resonant ending that leaves the reader thinking.

## Platform Context & Tone

- Tone: intimate, first-person, literary; Jianshu is the closest Chinese
  analog to a personal blog / Medium essay.
- Tag posts with 5–10 topics and submit to relevant "collections" (collection /
  submission) — collections are the main discovery channel.
- Taboo: hard-sell marketing, pure news aggregation, technical how-tos that
  belong on CSDN/Juejin, politically sensitive opinion.

## Content Length Guidelines

- Short essay: 800–1,500 characters.
- Standard essay / life writing: 1,500–3,000 characters.
- Long-form feature: 3,000–6,000 characters.

## Image & Illustration Support

- Cover image: optional; a literary illustration or atmospheric photo, ratio
  3:2 or 16:9.
- Inline images: 1–3, placed at section breaks; Jianshu prefers a clean column
  of text with occasional images.

## Background & Styling

- Jianshu controls the skin; no custom fonts/colors.
- Use italics, quote blocks, and `---` dividers for rhythm.

## SEO & Discovery

- Collections (collection) are the primary discovery channel; pick 1–3 matching
  collections and submit the post to them.
- 5–10 tags (e.g. prose, reading, growth, life) help internal recommendation.
- The title is the main hook; keep it evocative but clear.

## Content Adaptation Workflow

1. Rewrite the title to ≤30 characters, literary and clear.
2. Strip technical jargon and step-by-step structure; reframe as narrative.
3. Split into short, breath-length paragraphs.
4. Add an epigraph quote block if it strengthens the piece.
5. Mark 1–3 image placements at section breaks.
6. Pick 1–3 collections and 5–10 tags.
7. Run the checklist.

## Quality Checklist

- [ ] Title ≤30 chars and evocative.
- [ ] Paragraphs are short and breath-length.
- [ ] No step-list / code-heavy tutorial structure.
- [ ] 1–3 images marked at section breaks.
- [ ] 1–3 collections chosen; 5–10 tags.
- [ ] Personal voice / first-person reflection present.
- [ ] No marketing CTA.

## When to Use

- "Write a Jianshu essay about ..."
- "Adapt this for Jianshu / Jianshu"
- "Platform-specific content for jianshu", "publish to Jianshu"
- "A literary personal essay in the Jianshu style"

## Do NOT Use For

- Cookie-based posting automation.
- Technical tutorials (use Juejin / CNBlogs / CSDN).
- Image-first short notes (use Xiaohongshu).
- Hard news (use Toutiao / Baijiahao).
