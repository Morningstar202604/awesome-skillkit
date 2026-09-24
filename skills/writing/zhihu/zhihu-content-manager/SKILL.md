---
name: zhihu-content-manager
description: >
  Helps adapt and write platform-native long-form articles and answers for Zhihu
  (Zhihu). Produces Zhihu-style columns (zhuanlan), detailed answers, topic tags,
  cover images, and the HTML/Markdown structure the Zhihu editor accepts.
  Use when the user asks for Zhihu content, a Zhihu article, a Zhihu answer,
  zhihu column post, zhihu adaptation, platform-specific content for zhihu,
  publish to Zhihu, or SEO content for the Zhihu knowledge community.
  Do NOT use for automation, cookies, browser scripts, or posting to other platforms.
license: Apache-2.0
metadata:
  author: awesome-skillkit
  version: "2.0"
  category: content-adaptation
  platform: zhihu
  verified-date: "2026-09-24"
---

# Zhihu Content Adaptation Skill

## Overview

This skill turns a generic draft into a Zhihu-native article or answer. Zhihu
is a Chinese knowledge Q&A and column community (zhuanlan.zhihu.com) whose
audience rewards depth, evidence, and clear reasoning. The skill does not post
anything; it produces the formatted text, title, tags, cover brief, and
checklist the user then pastes into the Zhihu editor by hand.

## Platform Format Rules

- **Input format**: paste rich HTML or use the built-in Markdown editor; the
  underlying editor is Draft.js and is picky about block structure.
- **Title**: 1–100 Chinese characters; answer titles are the question itself.
- **Headings**: use `<h2>` for major sections (Chinese numbering "1, 2") and
  `<h3>` for subsections ("1.1", "1.2"); do not skip levels.
- **Paragraphs**: every paragraph is a block; add an empty spacer paragraph
  `<p><br/></p>` between sections for breathing room.
- **Bold**: use `<b>`, not `<strong>`.
- **Code blocks**: fenced code with a language tag; escape `<` and `>` inside
  code as `&lt;` / `&gt;` or the editor will swallow them as tags.
- **Images**: wrap in `<figure data-size="normal"><img src="URL"/></figure>`;
  bare `<img>` tags are stripped.
- **Tables**: not supported in the Draft.js editor — convert tables to lists or
  quote blocks.
- **Math**: inline and block LaTeX are supported; wrap inline formulas in `$...$`.
- **Lists**: `<ul><li>` for structured points.

## Reader Preferences

- Long-form, well-reasoned answers beat short takes; the algorithm rewards
  reading time and upvotes.
- Open with a concrete story, a counterintuitive claim, or a question hook.
- Use everyday analogies to explain technical concepts; show a timeline, the
  people involved, and the key events.
- Build progressively: basic concept -> core principle -> hands-on example ->
  advanced tips.
- End with a takeaway and a concrete learning path or action.

## Platform Context & Tone

- Tone: knowledgeable, candid, slightly academic but never stiff. Zhihu users
  dislike marketing fluff and unverifiable claims.
- Cite sources and data; opinions must be labeled as opinions.
- Taboo: hard-sell CTAs, "follow me for more", disguised ads, fabricated
  quotes, politically sensitive or rumour-driven content.
- Add 2–5 topic tags (topic) from the official tag picker; pick tags that match
  the question feed.

## Content Length Guidelines

- Column article: 3,000–10,000 Chinese characters; deep features can reach
  15,000.
- Answer: 800–5,000 characters depending on the question depth.
- Short opinion post: 300–800 characters.

## Image & Illustration Support

- Cover image: required for columns; 3:2 ratio, around 1536x1024, JPG/PNG
  under 2 MB.
- Inline images: 3–5 per article, evenly spaced between sections, captioned.
- Use `<figure>` with `data-caption`; avoid pure gradient "PPT-style" covers.

## Background & Styling

- No custom backgrounds, fonts, or color theming; Zhihu controls the skin.
- Keep emphasis to `<b>`, `<i>`, blockquotes, and hr dividers (`---` or `<hr/>`).

## SEO & Discovery

- Title contains the core question / keyword users would search.
- First 100 characters restate the question and your thesis.
- Choose 2–5 official topic tags; one broad + two narrow works best.
- Cross-link to related Zhihu answers/columns when natural.

## Content Adaptation Workflow

1. Identify whether the target is a column article or an answer; match the
   hook to the question.
2. Rewrite the title to 1–100 chars containing the main keyword.
3. Restructure into h2 (1, 2) / h3 (1.1) sections with hr dividers.
4. Convert any tables to lists or quote blocks.
5. Escape code brackets; wrap images in `<figure>`.
6. Add spacer paragraphs for visual rhythm.
7. Draft 2–5 topic tags and a 3:2 cover brief.
8. Run the Quality Checklist, then hand the formatted HTML/Markdown to the user.

## Quality Checklist

- [ ] Title is 1–100 chars and contains the core keyword.
- [ ] No `<h1>`; headings start at h2 and do not skip levels.
- [ ] No `<table>` anywhere.
- [ ] All images wrapped in `<figure>`; no bare `<img>`.
- [ ] Code blocks have escaped `<` / `>` and a language tag.
- [ ] Bold uses `<b>`, not `<strong>`.
- [ ] 2–5 topic tags chosen from the official picker.
- [ ] Cover brief is 3:2, ~1536x1024, under 2 MB.
- [ ] No marketing CTA, no "follow me", no disguised ad.

## When to Use

- "Write a Zhihu article about ..."
- "Adapt this for Zhihu / zhihu column / zhihu answer"
- "Platform-specific content for zhihu", "publish to Zhihu"
- "A long-form knowledge post for the Zhihu audience"

## Do NOT Use For

- Browser automation, cookie/session scripts, or posting APIs.
- Short social posts (use Xiaohongshu / Weibo skills).
- Code-only snippets (use Juejin / SegmentFault).
- Video scripts (use Bilibili skill).
