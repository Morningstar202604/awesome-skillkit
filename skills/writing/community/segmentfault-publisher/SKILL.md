---
name: segmentfault-publisher
description: >
  Helps adapt and write platform-native articles and Q&A for SegmentFault
  (SegmentFault), the Chinese developer Q&A and technical blog community. Produces
  SegmentFault-style Markdown posts with strong code blocks, tags, and a
  technical Q&A / how-to voice. Use when the user asks for SegmentFault content,
  SegmentFault article, segmentfault article, segmentfault adaptation, platform-specific
  content for segmentfault, or publish to SegmentFault. Do NOT use for
  cookie-based posting automation or other platforms.
license: Apache-2.0
metadata:
  author: awesome-skillkit
  version: "2.0"
  category: content-adaptation
  platform: segmentfault
  verified-date: "2026-09-24"
---

# SegmentFault Content Adaptation Skill

## Overview

This skill converts a draft into a SegmentFault (SegmentFault)-native article or Q&A.
SegmentFault is a Chinese developer community modeled on Stack Overflow +
Medium: it hosts questions (Q&A) and technical blogs (article). The audience is
technical, code-first, and expects reproducible examples. The skill produces the
Markdown body, title, tags, and Q&A framing the user enters manually.

## Platform Format Rules

- **Input format**: Markdown is native; strong code highlighting.
- **Article title**: 1–100 characters; problem-oriented and keyword-rich.
- **Question title**: must end in a question and state the exact problem;
  Stack-Overflow style (e.g. "How do I ... in Python 3.12?").
- **Headings**: `##` for sections, `###` for subsections; no h1 in body.
- **Code blocks**: fenced triple backticks with a language tag; copy button is
  built in.
- **Tables / lists**: GFM supported.
- **Images**: Markdown `![alt](URL)`; in-editor image upload available.
- **LaTeX / Mermaid**: supported.

## Reader Preferences

- Q&A posts: show the minimal reproduction, what you expected, what happened.
- Articles: real code that runs, version numbers, and pitfall notes.
- Direct, technical writing; no filler intro.
- A clear "answer" / "solution" section up front for Q&A.

## Platform Context & Tone

- Tone: precise Stack Overflow-style technical writing.
- Tags: 1–5 tags from the tag picker; tags drive Q&A routing and blog
  discovery.
- Taboo: "how do I code" with no research, homework dumps, reposted CSDN
  scrapes, marketing disguised as an article.

## Content Length Guidelines

- Q&A question: 300–1,500 characters.
- Short article / tip: 500–1,500 characters.
- In-depth article: 1,500–6,000 characters.

## Image & Illustration Support

- Cover image for articles: optional; 16:9 or 3:2.
- Inline screenshots: 1–5; prefer IDE / terminal screenshots showing real output.
- Mermaid diagrams preferred for architecture.

## Background & Styling

- SegmentFault controls the theme; no custom fonts/colors.
- Use headings, code blocks, callout quote blocks, and Mermaid.

## SEO & Discovery

- SegmentFault pages rank well in Baidu / Bing for technical queries.
- Title matches a searchable technical question.
- 1–5 tags from the picker drive internal recommendation.
- Q&A questions are routed by tags to users following them.

## Content Adaptation Workflow

1. Decide: article or Q&A. For Q&A, rewrite the title as a clear question.
2. For Q&A: structure as Problem / What I tried / Expected / Actual / Solution.
3. For articles: conclusion-first, then code examples.
4. Ensure code blocks have language tags and reproducible commands.
5. Add Mermaid for flows; place 1–5 screenshots.
6. Pick 1–5 tags.
7. Run the checklist.

## Quality Checklist

- [ ] Title ≤100 chars; Q&A titles end in a question.
- [ ] Q&A posts include minimal reproduction and expected vs actual behavior.
- [ ] All code blocks have a language tag and runnable commands.
- [ ] No h1 (`#`) headings in body.
- [ ] 1–5 tags chosen.
- [ ] Cover image ~16:9 if used.
- [ ] No homework-dump or marketing disguised as tech.

## When to Use

- "Write a SegmentFault article / Q&A about ..."
- "Adapt this for SegmentFault / SegmentFault"
- "Platform-specific content for segmentfault", "publish to SegmentFault"
- "A Stack-Overflow-style technical Q&A for SegmentFault"

## Do NOT Use For

- Cookie-based posting automation.
- Literary essays (use Jianshu).
- Image-first social posts (use Xiaohongshu).
- News (use Toutiao / Baijiahao).
