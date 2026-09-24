---
name: juejin-publisher
description: >
  Helps adapt and write platform-native Markdown articles for Juejin (Juejin), the
  Chinese front-end / full-stack developer community. Produces Juejin-format posts
  with strong code blocks, tags, categories, and a tech-blog voice. Use when the
  user asks for Juejin content, juejin article, Juejinarticle, juejin adaptation,
  platform-specific content for juejin, or publish to Juejin. Do NOT use for
  cookie-based posting automation or other platforms.
license: Apache-2.0
metadata:
  author: awesome-skillkit
  version: "2.0"
  category: content-adaptation
  platform: juejin
  verified-date: "2026-09-24"
---

# Juejin Content Adaptation Skill

## Overview

This skill converts a generic draft into a Juejin (Juejin)-native article. Juejin
is a developer community focused on front-end, full-stack, AI tooling, and
career topics. The audience is technical, Markdown-savvy, and expects clean code
samples. The skill produces the Markdown body, title, tags, and category the user
pastes into the Juejin editor manually.

## Platform Format Rules

- **Input format**: GitHub-flavored Markdown is the native editor.
- **Title**: 1–100 characters; include the technology/topic keyword.
- **Headings**: `##` for sections, `###` for subsections; do not use h1 (the
  article title is h1).
- **Code blocks**: fenced triple backticks with a language tag
  (```javascript, ```python, ```bash); syntax highlighting is first-class.
- **Inline code**: backticks `like this`.
- **Tables**: GFM tables supported.
- **Images**: Markdown `![alt](URL)`; Juejin has an in-editor image upload.
- **Quote blocks**: `>` supported for tips / callouts.
- **Math / Mermaid**: Juejin supports LaTeX and Mermaid diagrams in Markdown.

## Reader Preferences

- Developers scan for code, screenshots, and TL;DR blocks.
- Open with a problem statement and the outcome, then show the solution.
- Short, punchy sections; a "TL;DR" or "conclusion first" up front is appreciated.
- Real code that runs, not pseudocode; call out pitfalls and version notes.

## Platform Context & Tone

- Tone: peer developer, enthusiastic but precise; first-person "I" sharing
  lessons from a real project.
- Tags and topics matter: pick 1 primary category (e.g. frontend, backend, AI,
   career) and 3–5 tags.
- Taboo: reposted scraped content, tutorial-spam, "follow me" CTA, misleading
  "I made $X" clickbait.

## Content Length Guidelines

- Quick tip: 300–800 characters.
- Tutorial: 1,500–4,000 characters.
- Deep dive / source-reading: 4,000–10,000 characters.

## Image & Illustration Support

- Cover image: recommended 16:9 or 3:2, around 1080x720, JPG/PNG.
- Inline screenshots: 1–5 per article; prefer code screenshots that show the
  real terminal / devtools output.
- Mermaid diagrams are preferred over images for architecture flows.

## Background & Styling

- Juejin renders its own light/dark skin; no custom fonts or colors.
- Use headings, code blocks, Mermaid, and callout quote blocks for structure.

## SEO & Discovery

- Juejin is indexed by search engines and has its own recommendation feed.
- Title contains the primary keyword (e.g. "React 19", "Python async").
- Choose one category and 3–5 tags from the tag picker; tags drive discovery.
- Add a "bookmark-friendly" summary section developers will save.

## Content Adaptation Workflow

1. Rewrite the title to ≤100 chars with the technology keyword.
2. Add a TL;DR / conclusion-first opening.
3. Convert headings to `##` / `###`; remove any h1.
4. Ensure all code blocks have a language tag and a real, runnable sample.
5. Add Mermaid diagrams for architecture / flow where an image would be used.
6. Place 1–5 screenshots at the right steps.
7. Pick 1 category + 3–5 tags.
8. Run the checklist.

## Quality Checklist

- [ ] Title ≤100 chars with the keyword.
- [ ] No h1 (`#`) headings in the body.
- [ ] Every code block has a language tag.
- [ ] Code is real/runnable, not pseudocode.
- [ ] 1 category + 3–5 tags chosen.
- [ ] Cover image ~16:9 or 3:2.
- [ ] TL;DR / conclusion-first opening.
- [ ] Mermaid used where a flow diagram helps.

## When to Use

- "Write a Juejin article about ..."
- "Adapt this for Juejin / Juejin"
- "Platform-specific content for juejin", "publish to Juejin"
- "A developer tutorial in the Juejin style"

## Do NOT Use For

- Cookie-based posting automation.
- Non-technical essays (use Jianshu).
- Short image-first social posts (use Xiaohongshu).
- Video descriptions (use Bilibili).
