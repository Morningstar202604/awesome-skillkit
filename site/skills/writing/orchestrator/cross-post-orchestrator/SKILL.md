---
name: cross-post-orchestrator
description: >
  Cross-platform content adaptation guide. Helps adapt ONE source article into
  platform-native versions for multiple Chinese platforms (Zhihu, WeChat MP,
  Juejin, CNBlogs, CSDN, Jianshu, Xiaohongshu, Weibo, Toutiao, Baijiahao,
  Bilibili, Douban, V2EX, SegmentFault, OSChina, static blog) simultaneously.
  Produces per-platform titles, adapted bodies, tag sets, and image briefs. Use
  when the user asks to adapt an article for multiple platforms, cross-post
  content, multi-platform content adaptation, one article for many platforms, or
  distribute content across platforms. Do NOT use for posting automation,
  scheduling scripts, or single-platform deep formatting (use the per-platform
  skill).
license: Apache-2.0
metadata:
  author: awesome-skillkit
  version: "2.0"
  category: content-adaptation
  scope: cross-platform
  verified-date: "2026-09-24"
---

# Cross-Platform Content Adaptation Guide

## Overview

This skill turns one source article into a matrix of platform-native versions.
It does not post anything; it produces a deliverable package — per-platform
titles, adapted bodies, tag sets, and image briefs — that the user then copies
into each platform editor by hand. It coordinates the work of the individual
platform skills but never calls them as scripts.

## Why Adapt Instead of Copy-Paste

Each platform has different length limits, tone, audience, and discovery
mechanics. A straight copy-paste underperforms everywhere. The goal is: same
core idea, different shape per platform.

## Platform Quick-Reference Matrix

| Platform | Best for | Title limit | Body length | Image ratio |
|---|---|---|---|---|
| Zhihu | Long-form depth, Q&A | 100 chars | 3k–10k chars | 3:2 |
| WeChat MP | Subscriber long read | 64 chars | 1.5k–6k chars | 2.35:1 (900x383) |
| Juejin | Tech tutorials | 100 chars | 1.5k–10k chars | 16:9 / 3:2 |
| CNBlogs | Developer blog | 100 chars | 1.5k–8k chars | 3:2 |
| CSDN | SEO troubleshooting | 80 chars | 1.5k–8k chars | 16:9 |
| Jianshu | Literary / essay | 30 chars | 0.8k–6k chars | 3:2 |
| Xiaohongshu | Image-first notes | 20 chars | <=1k chars | 3:4 (1080x1440) |
| Weibo | Public-square take | ~140 visible | 0.2k–2k chars | 1:1 / 3:2 |
| Toutiao | Algorithmic news feed | 30 chars | 0.3k–4k chars | 16:9 |
| Baijiahao | Baidu-search explainer | 30 chars | 0.5k–5k chars | 16:9 |
| Bilibili | Video / column / dynamic | 80 chars | dynamic <=230 / column 1.5k–6k | 16:9 (1920x1080) |
| Douban | Cultural review | 100 chars | 0.2k–5k chars | 3:2 |
| V2EX | Hacker discussion | 120 chars | 0.2k–2k chars | none native |
| SegmentFault | Tech Q&A / blog | 100 chars | 0.3k–6k chars | 16:9 |
| OSChina | Open-source tooling | 80 chars | 0.5k–8k chars | 16:9 |
| Static blog | Self-hosted long-form | unlimited | 0.5k–10k chars | 1200x630 |

## Reader Preferences by Bucket

- **Knowledge / dev bucket** (Zhihu, Juejin, CNBlogs, CSDN, SegmentFault,
  OSChina, V2EX): depth, code, evidence, clear reasoning.
- **Subscriber bucket** (WeChat MP, static blog): personal voice, mobile-first
  pacing, loyalty-driven.
- **Feed bucket** (Toutiao, Baijiahao, Bilibili): hook in first 2 lines,
  algorithmic discovery.
- **Lifestyle bucket** (Xiaohongshu, Douban, Jianshu): voice, authenticity,
  cultural / personal angle.
- **Microblog bucket** (Weibo): punchy take, hashtag, retweet-driven.

## Platform Context & Taboos

- No external links in WeChat MP body.
- No inline images in V2EX.
- Xiaohongshu body <=1k chars, title <=20 chars.
- CNBlogs / static blog: no h1 in body.
- V2EX: pick the right node; no ads.
- Douban: no marketing-disguised reviews.
- All platforms: avoid exaggerated / absolute claims that trigger moderation.

## Content Length Guidelines

- Start from the source article (typically 2k–6k chars).
- Expand for Zhihu / Juejin / static blog / WeChat MP.
- Condense for Xiaohongshu (<=1k), Weibo (<=2k), Toutiao/Baijiahao (<=2k), V2EX
  (<=2k).
- For Bilibili, also produce a video title/description and a dynamic post.

## Image & Illustration Support

- Generate one master hero image; re-crop per platform ratio.
- Xiaohongshu needs a 3:4 portrait cover with large text.
- WeChat MP needs a wide 900x383 cover.
- Zhihu / Juejin / CNBlogs accept 3:2.
- Toutiao / Baijiahao / Bilibili / CSDN / OSChina use 16:9.
- Use `ai-cover-generator` to produce the master image and crops.

## Background & Styling

- Each platform controls its own skin; do not try to share custom CSS.
- Keep shared structure (headings, code blocks, image placement) consistent so
  the user can move between editors.

## SEO & Discovery

- Each platform needs its own keyword choice:
  - Zhihu / Baidu: match question phrasing.
  - Xiaohongshu: match how users search lifestyle terms.
  - Juejin / CSDN / SegmentFault / OSChina: match tech keywords.
  - WeChat MP: optimize for WeChat search.
- Produce a tags list per platform (2–12 tags depending on the platform).

## Content Adaptation Workflow

1. **Ingest the source article**: title, body, key points, code blocks, images.
2. **Choose target platforms** (default: ask the user which subset).
3. **For each platform**, produce:
   a. A platform-specific title within the limit.
   b. An adapted body (expanded / condensed / re-toned).
   c. A tag / category / node set.
   d. An image brief (master crop to the platform ratio).
4. **Hand off**: group the deliverables in a labeled section per platform so
   the user can copy-paste each into its editor.
5. **Do not post**: no scripts, no cookies, no API calls.

## Quality Checklist

- [ ] Every target platform has its own title within its limit.
- [ ] Bodies are adapted, not copy-pasted (length/tone matched per platform).
- [ ] Platform-specific taboos respected (no WeChat external links, no V2EX
      images, Xiaohongshu <=1k chars, etc.).
- [ ] Tag / category / node sets provided per platform.
- [ ] Image briefs cropped to each platform's ratio.
- [ ] No automation scripts referenced.
- [ ] Deliverables labeled per platform for easy copy-paste.

## When to Use

- "Adapt this article for multiple platforms"
- "Cross-post / multi-platform content adaptation"
- "One article for Zhihu, WeChat, Juejin, Xiaohongshu ..."
- "Prepare platform-adapted versions of this draft"

## Do NOT Use For

- Posting automation, scheduling, cookie/API scripts.
- A single platform's deep formatting (use that platform's skill directly).
- Generating cover images (use `ai-cover-generator`).
- Deployment to static hosts (use static-blog content adaptation for content;
  do not deploy).
