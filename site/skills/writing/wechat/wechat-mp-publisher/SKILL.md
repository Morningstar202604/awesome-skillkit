---
name: wechat-mp-publisher
description: >
  Helps adapt and write platform-native articles for WeChat Official Accounts
  (WeChat Official Account). Produces WeChat-MP-style rich-text articles with the right title
  length, cover image ratio, inline images, no external links, and a
  mobile-first reading flow. Use when the user asks for WeChat MP content,
  official account article, official account article, wechat adaptation, platform-specific
  content for wechat, or publish to WeChat Official Account. Do NOT use for
  WeChat API automation, draft scripts, or posting to other platforms.
license: Apache-2.0
metadata:
  author: awesome-skillkit
  version: "2.0"
  category: content-adaptation
  platform: wechat-mp
  verified-date: "2026-09-24"
---

# WeChat Official Account Content Adaptation Skill

## Overview

This skill turns a generic draft into a WeChat Official Account (WeChat Official Account)
article. WeChat MP is a closed mobile-first reading environment: articles are
read inside the WeChat app, external links are mostly disabled, and the cover
image controls the share card. The skill produces the formatted body, title,
abstract, and cover brief the user pastes into the MP editor manually.

## Platform Format Rules

- **Input format**: WeChat MP editor is rich-text (HTML-ish); Markdown is
  imported via third-party tools but the published article is rendered HTML.
- **Title**: up to 64 characters; keep the most important words in the first
  ~20 (they are visible in the chat-list share card).
- **Author / digest**: author ≤8 chars; digest (digest) ≤120 chars and shows in
  the share card.
- **Headings**: wechat renders h2/h3; use bold section headers with an emoji or
  divider (`---`) to break the article.
- **Paragraphs**: short (2–4 lines on mobile); one idea per paragraph; generous
  blank lines.
- **Images**: inline images must be uploaded to WeChat's own image host; hot-
  linking external URLs does not work. Recommended width 1080px, JPG/PNG, under
  5 MB.
- **Code blocks**: WeChat has no native code-block styling — paste code as an
  image, or use a fenced block with a light background; long code should be a
  screenshot.
- **Tables / external links**: external hyperlinks are stripped except inside
  approved "Read More" (read-more) and article-card contexts; avoid inline links.
- **Quote blocks / bold / italic**: supported natively.

## Reader Preferences

- Readers scroll vertically in a chat stream; the first screen decides whether
  they keep reading.
- A personal, story-driven hook in the opening 100 words performs best.
- Short punchy sections, subheads every 300–500 chars, frequent images.
- Tone: warm but professional; a clear point of view; avoid dry encyclopedia
  style.

## Platform Context & Tone

- Tone: like a knowledgeable friend writing a long message; first-person "I"
  is common.
- Taboo: obvious ads, share-to-unlock ("share to unlock"), exaggerated claims,
  politically sensitive topics, medical/financial claims without disclaimers.
- No inline external URLs; put the source / call-to-action in the "Read More"
  field.

## Content Length Guidelines

- Standard article: 1,500–3,000 Chinese characters.
- Long feature / deep dive: 3,000–6,000 characters.
- Short push / news: 500–1,000 characters.

## Image & Illustration Support

- **Cover image (cover)**: required. Ratio ~2.35:1; a common crop is 900x383
  (round to 16-multiple, e.g. 896x384). JPG under 2 MB.
- **Inline images**: 3–8 per article; 1080px wide; every 300–500 chars on
  long posts.
- **Thumbnail / share card**: the cover is reused; ensure the focal subject is
  centered because it is cropped square in chat previews.

## Background & Styling

- WeChat MP controls the global font and background; you cannot set custom
  fonts or colors in the body.
- Use built-in quote blocks, bold, and colored text (available in the editor)
  sparingly for emphasis.

## SEO & Discovery

- WeChat search (WeChat Search) indexes titles, digests, and body keywords.
- Put the core keyword in the title and first 100 chars.
- Add a topic category (original/repost/column) and, if eligible, add the article to
  related topic pages (topic).
- The digest is the meta description — write it like an ad for the article.

## Content Adaptation Workflow

1. Rewrite the title to ≤64 chars, key words in the first 20.
2. Write a ≤120-char digest for the share card.
3. Split the body into mobile-short paragraphs (2–4 lines each).
4. Add a subhead every 300–500 chars, with an emoji or `---` divider.
5. Replace any external hyperlinks with WeChat-friendly phrasing; put the CTA
   in the "Read More" field.
6. Convert code blocks to light-background fenced blocks or screenshots.
7. Mark where inline images go (3–8 total, 1080px wide).
8. Specify a 900x383 (≈896x384) cover with centered focal subject.
9. Run the checklist; hand the formatted text + cover brief to the user.

## Quality Checklist

- [ ] Title ≤64 chars with key words up front.
- [ ] Digest written (≤120 chars).
- [ ] No external inline hyperlinks (CTA goes to "Read More").
- [ ] Paragraphs are mobile-short (2–4 lines).
- [ ] Subheads every 300–500 chars with dividers.
- [ ] Code is fenced or screenshot, not raw.
- [ ] 3–8 inline image placeholders at 1080px width.
- [ ] Cover brief at ~900x383 (≈896x384), JPG <2 MB, centered subject.
- [ ] No "share to unlock" language, no exaggeration.

## When to Use

- "Write a WeChat official account article about ..."
- "Adapt this for WeChat MP / WeChat MP"
- "Platform-specific content for wechat", "publish to WeChat Official Account"
- "A mobile-first long read for WeChat subscribers"

## Do NOT Use For

- WeChat API / draft / freepublish automation scripts.
- Personal WeChat chat messages.
- External-link-heavy blog posts (use CNBlogs / Juejin).
- Video scripts (use Bilibili).
