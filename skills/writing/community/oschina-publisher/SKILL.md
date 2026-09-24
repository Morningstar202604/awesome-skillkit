---
name: oschina-publisher
description: >
  Helps adapt and write platform-native articles for OSChina (OSChina), the
  Chinese open-source developer community. Produces OSChina-style Markdown posts
  with open-source framing, code blocks, tags, and a practitioner voice. Use when
  the user asks for OSChina content, OSChina article, oschina article, oschina
  adaptation, platform-specific content for oschina, or publish to OSChina.
  Do NOT use for cookie-based posting automation or other platforms.
license: Apache-2.0
metadata:
  author: awesome-skillkit
  version: "2.0"
  category: content-adaptation
  platform: oschina
  verified-date: "2026-09-24"
---

# OSChina Content Adaptation Skill

## Overview

This skill converts a draft into an OSChina (OSChina)-native article. OSChina is
a Chinese developer community focused on open-source projects, tools, and
engineering practice. The audience is hands-on and open-source aware. The skill
produces the Markdown body, title, tags, and open-source framing the user enters
manually.

## Platform Format Rules

- **Input format**: Markdown is native.
- **Title**: 1–80 characters; practical and keyword-rich.
- **Headings**: `##` for sections, `###` for subsections; no h1 in body.
- **Code blocks**: fenced triple backticks with a language tag; OSChina has
  strong syntax highlighting.
- **Tables / lists**: GFM supported.
- **Images**: Markdown `![alt](URL)`.
- **Links**: external links are allowed; OSChina is a developer audience that
  expects GitHub / project links.

## Reader Preferences

- OSChina readers want practical, runnable content: tools, source-reading,
  deployments, open-source comparisons.
- Link to the actual project / GitHub repo when relevant.
- Short intro, then code; call out license, stars, anduse cases.
- "How I used X to solve Y" posts perform well.

## Platform Context & Tone

- Tone: open-source practitioner; share tools, not hype.
- Tags: 1–5 tags (e.g. Java, Python, open source, tools, architecture).
- Taboo: undisclosed product marketing, closed-source shilling, reposted scraped
  CSDN content, politically sensitive posts.

## Content Length Guidelines

- Tool introduction / tip: 500–1,500 characters.
- Tutorial / source-reading: 1,500–4,000 characters.
- Deep technical article: 4,000–8,000 characters.

## Image & Illustration Support

- Cover image: optional; 16:9 or 3:2, tool screenshots or architecture diagrams.
- Inline images: 1–5; prefer screenshots of the tool running.
- Mermaid diagrams supported for architecture.

## Background & Styling

- OSChina controls the theme; no custom fonts/colors.
- Use headings, code blocks, and Mermaid for structure.

## SEO & Discovery

- OSChina pages rank for open-source / tool queries.
- Title contains the tool / project name and the use case.
- 1–5 tags; link back to the project repo.
- A "use cases / pros and cons" comparison section drives saves.

## Content Adaptation Workflow

1. Rewrite the title to ≤80 chars with the tool / project name.
2. Open with the problem the tool solves.
3. Strip h1; use `##` / `###` headings.
4. Ensure code blocks have language tags; link to the GitHub repo.
5. Add 1–5 screenshots or Mermaid diagrams.
6. Add a "use cases / pros and cons" section.
7. Pick 1–5 tags; run the checklist.

## Quality Checklist

- [ ] Title ≤80 chars with tool/project name.
- [ ] Opens with the problem the tool solves.
- [ ] Code blocks have language tags and link to the project repo.
- [ ] No h1 (`#`) headings in body.
- [ ] 1–5 tags chosen.
- [ ] Cover image ~16:9 if used.
- [ ] "use cases / pros and cons" section present.
- [ ] No undisclosed marketing.

## When to Use

- "Write an OSChina article about ..."
- "Adapt this for OSChina / OSChina"
- "Platform-specific content for oschina", "publish to OSChina"
- "An open-source tool tutorial in the OSChina style"

## Do NOT Use For

- Cookie-based posting automation.
- Literary essays (use Jianshu).
- Image-first social posts (use Xiaohongshu).
- News (use Toutiao / Baijiahao).
