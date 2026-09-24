---
name: v2ex-publisher
description: >
  Helps adapt and write platform-native posts for V2EX, the Chinese hacker /
  developer community forum organized by nodes. Produces V2EX-style discussion
  threads with a concise title, plain-text body, node targeting, and no inline
  images. Use when the user asks for V2EX content, v2ex post, v2ex thread, v2ex
  adaptation, platform-specific content for v2ex, or publish to V2EX. Do NOT use
  for cookie-based posting automation or other platforms.
license: Apache-2.0
metadata:
  author: awesome-skillkit
  version: "2.0"
  category: content-adaptation
  platform: v2ex
  verified-date: "2026-09-24"
---

# V2EX Content Adaptation Skill

## Overview

This skill converts a draft into a V2EX-native post. V2EX (v2ex.com) is a
Chinese developer / hacker forum organized into "nodes" (node). The audience is
skeptical, technical, and bilingual; posts are short discussion threads rather
than long articles. The skill produces the title, body, and node recommendation
the user enters manually.

## Platform Format Rules

- **Title**: 1–120 characters; clear, specific, and honest — V2EX dislikes
  clickbait titles.
- **Body**: Markdown is supported but used sparingly; plain text with line
  breaks is the norm.
- **Images**: V2EX does not support inline image upload in posts; reference
  external image links only when essential, and prefer text.
- **Code blocks**: fenced triple backticks for snippets.
- **Links**: bare links are common; V2EX users paste raw URLs.
- **Polls / tags**: posts are assigned to one node (node); there are no free
  tags.

## Reader Preferences

- V2EX users want a concrete problem and real details (OS, tools, versions,
  config).
- Short, direct posts beat long essays; if you have a question, state it in the
  title.
- Show your work: what you tried, what failed, what you searched.
- Self-deprecating humor and technical bluntness fit the culture.

## Platform Context & Tone

- Tone: peer-to-peer hacker; terse, honest, no marketing.
- Pick the correct node (e.g. programming, share-creation, questions, VPS, cool-jobs,
  broadband); wrong-node posts get downvoted.
- Taboo: obvious ads, invite/affiliate spam, "follow me" CTAs, politically
  sensitive rants, title-only posts with no body, reposted scraped content.

## Content Length Guidelines

- Discussion / question: 200–800 characters.
- Show-and-tell / share-creation: 500–2,000 characters.
- Long write-up: V2EX is not the right venue; link out to a blog post instead.

## Image & Illustration Support

- No native inline images; attach external image URLs only when they materially
  help.
- Prefer ASCII diagrams or fenced code blocks over screenshots.

## Background & Styling

- V2EX controls the theme; no custom fonts/colors.
- Use plain text, line breaks, and occasional code blocks.

## SEO & Discovery

- Discovery is node-based, not search-based.
- Choose the node that matches the topic; wrong nodes kill reach.
- The title is the hook for node subscribers; make it specific.

## Content Adaptation Workflow

1. Write a specific title (≤120 chars) that states the problem or the thing
   being shared.
2. Open with context (what OS/tools/versions, what you tried).
3. Keep the body short; strip long essay sections into a linked blog post.
4. Use fenced code blocks for config / commands.
5. Avoid inline images; reference external URLs only if needed.
6. Recommend the correct node (node).
7. Run the checklist.

## Quality Checklist

- [ ] Title ≤120 chars, specific, no clickbait.
- [ ] Body states context and what was tried.
- [ ] Post is short (≤2,000 chars); long content linked out.
- [ ] Code snippets use fenced blocks.
- [ ] No inline image uploads (use external links only if essential).
- [ ] Correct node (node) recommended.
- [ ] No ads / affiliate spam / "follow me".

## When to Use

- "Write a V2EX post about ..."
- "Adapt this for V2EX"
- "Platform-specific content for v2ex", "publish to V2EX"
- "A hacker-style discussion thread for V2EX"

## Do NOT Use For

- Cookie-based posting automation.
- Long-form articles (use Zhihu / Juejin).
- Image-first social posts (use Xiaohongshu).
- Marketing / product launches (V2EX downvotes undisclosed ads).
