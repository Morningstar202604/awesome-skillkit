---
name: csdn-publisher
description: >
  Helps adapt and write platform-native Markdown articles for CSDN, the Chinese
  developer blog and search-indexed tech content platform. Produces CSDN-style
  posts with SEO-friendly titles, code blocks, tags, categories, and a tutorial
  voice. Use when the user asks for CSDN content, csdn article, CSDN blog post,
  csdn adaptation, platform-specific content for csdn, or publish to CSDN.
  Do NOT use for cookie-based posting automation or other platforms.
license: Apache-2.0
metadata:
  author: awesome-skillkit
  version: "2.0"
  category: content-adaptation
  platform: csdn
  verified-date: "2026-09-24"
---

# CSDN Content Adaptation Skill

## Overview

This skill converts a generic draft into a CSDN-native article. CSDN (csdn.net)
is the largest Chinese developer blog platform and is heavily indexed by Baidu
and other search engines. Its audience is developers troubleshooting concrete
problems. The skill produces the Markdown body, title, tags, and category the
user pastes into the CSDN editor manually.

## Platform Format Rules

- **Input format**: Markdown editor (with an HTML toggle) is native.
- **Title**: 1–80 characters; CSDN search and Baidu index the title, so front-load
  the exact problem / technology keyword.
- **Headings**: `##` for sections, `###` for subsections; avoid h1 in body.
- **Code blocks**: fenced triple backticks with a language tag; CSDN has strong
  syntax highlighting and a copy button.
- **Tables / lists**: GFM tables and bullet lists supported.
- **Images**: Markdown `![alt](URL)`; CSDN image host is used on upload.
- **Quote blocks / bold**: supported.
- **LaTeX / Mermaid**: supported via the editor's Markdown engine.

## Reader Preferences

- CSDN readers arrive via search with a specific error message or task.
- Lead with the problem and the exact solution; show the error → cause → fix.
- Screenshots of the actual error and the working result are expected.
- Step-by-step numbered sections beat narrative essays.

## Platform Context & Tone

- Tone: practical troubleshooter; "how I solved X" posts perform best.
- Taboo: pure marketing, scraped content without a solution, keyword stuffing,
  hidden CTAs that force a like/follow to reveal code.
- CSDN has a reputation for SEO-driven posts; write genuinely useful content,
  not just keyword-laden filler.

## Content Length Guidelines

- Quick fix / error resolution: 500–1,500 characters.
- Tutorial / how-to: 1,500–4,000 characters.
- Deep technical article: 4,000–8,000 characters.

## Image & Illustration Support

- Cover image: optional; when used, 16:9 or 3:2, around 1080x720.
- Inline screenshots: 3–8 per tutorial, showing the exact error / output.
- Prefer crisp terminal or IDE screenshots; avoid blurry phone photos.

## Background & Styling

- CSDN controls the theme; no custom fonts/colors.
- Use headings, numbered steps, code blocks, and screenshots for structure.

## SEO & Discovery

- CSDN is one of the most search-indexed Chinese tech domains; SEO is the main
  discovery channel.
- Title matches a search query verbatim (e.g. "solve Error: ... in Python 3.12").
- Pick 1 category and 3–5 tags; tags drive CSDN's internal recommendation and
  Baidu indexing.
- Put a keyword-rich summary in the first paragraph.

## Content Adaptation Workflow

1. Rewrite the title as a search-friendly problem statement (≤80 chars).
2. Open with the exact error / problem and a one-line solution.
3. Structure as numbered steps: environment → reproduction → cause → fix → verify.
4. Ensure code blocks have language tags and copy-paste-ready commands.
5. Insert screenshots at the error and the success state.
6. Pick 1 category + 3–5 tags.
7. Add a short "summary" / "FAQ" section at the end.
8. Run the checklist.

## Quality Checklist

- [ ] Title ≤80 chars and matches a likely search query.
- [ ] Opening states the problem and the fix in one line.
- [ ] Code blocks have language tags and are copy-paste ready.
- [ ] Screenshots show both error and success states.
- [ ] No h1 (`#`) headings in body.
- [ ] 1 category + 3–5 tags chosen.
- [ ] No "like/follow to reveal code" gating.
- [ ] Ends with a short summary / FAQ.

## When to Use

- "Write a CSDN article about ..."
- "Adapt this for CSDN"
- "Platform-specific content for csdn", "publish to CSDN"
- "A search-friendly tech tutorial for CSDN"

## Do NOT Use For

- Cookie-based posting automation.
- Literary / non-technical posts (use Jianshu).
- Image-first social posts (use Xiaohongshu).
- Short news pushes (use Toutiao / Baijiahao).
