---
name: static-blog-deploy
description: >
  Helps adapt and write platform-native Markdown content for static site
  generators (Hugo, Jekyll, Hexo). Produces posts with correct front matter,
  Markdown flavor, shortcodes, image shortcodes, draft status, and permalinks
  for self-hosted static blogs. Use when the user asks for Hugo content, Jekyll
  post, Hexo article, static blog post, static-blog adaptation, platform-specific
  content for static blog, or write a post for my Hugo/Jekyll/Hexo blog. Do NOT
  use for build/deploy automation, hosting CLI scripts, or other platforms.
license: Apache-2.0
metadata:
  author: awesome-skillkit
  version: "2.0"
  category: content-adaptation
  platform: static-blog
  generators: [hugo, jekyll, hexo]
  verified-date: "2026-09-24"
---

# Static Blog Content Adaptation Skill

## Overview

This skill turns a generic draft into a ready-to-drop-in Markdown post for a
static site generator (Hugo, Jekyll, or Hexo). It produces the front matter,
Markdown body, image shortcodes, and permalink metadata the user saves into their
`content/posts/` (Hugo), `_posts/` (Jekyll), or `source/_posts/` (Hexo) folder.
The user runs `hugo`, `jekyll build`, or `hexo generate` themselves; this skill
does not deploy.

## Platform Format Rules

- **File naming** (blog-engine post paths):
  ```text
  Hugo:   content/posts/YYYY-MM-DD-title.md (or any slug)
  Jekyll: _posts/YYYY-MM-DD-title.md (date prefix required)
  Hexo:   source/_posts/title.md (no date prefix; date comes from front matter)
  ```
- **Front matter**: YAML between `---` fences at the top of the file.
  - Hugo: `title`, `date`, `draft: true/false`, `tags`, `categories`, `description`.
  - Jekyll: `layout: post`, `title`, `date: YYYY-MM-DD HH:MM:SS +0800`,
    `tags`, `categories`.
  - Hexo: `title`, `date`, `tags`, `categories`, `draft: false`.
- **Markdown flavor**:
  - Hugo: Goldmark (CommonMark + tables, footnotes, task lists).
  - Jekyll: kramdown (GFM + `{: .note}` block attributes).
  - Hexo: hexo-renderer-marked (GFM + Nunjucks-style tags).
- **Headings**: `#` is the page title (also in front matter); body starts at
  `##`.
- **Code blocks**: fenced triple backticks with a language tag; Hugo/Jekyll
  support syntax highlighting (Chroma / Rouge).
- **Images**:
  - Hugo: `{{</* figure src="/images/x.png" caption="..." */>}}` shortcode, or
    plain Markdown.
  - Jekyll: `{% include image.html %}` or plain Markdown `![alt](/images/x.png)`.
  - Hexo: `{% asset_img x.png "alt" %}` tag.
- **Drafts**: set `draft: true` (Hugo/Hexo) or keep the file uncommitted;
  `draft: false` when ready.

## Reader Preferences

- Static-blog readers are your own subscribers / search traffic; they expect
  long-form, well-structured technical or opinion content.
- A clear table of contents (Hugo `{{</* toc */>}}`, Jekyll `{:toc}`, Hexo
  `<!-- more -->` excerpt) helps long posts.
- Working code, reproducible commands, and screenshots.

## Platform Context & Tone

- Tone: your own blog's voice — consistent across posts.
- No platform-specific UI constraints; you control the theme.
- Taboo: content copied verbatim from other platforms without adaptation;
  broken shortcodes; draft files accidentally published.

## Content Length Guidelines

- Short note: 500–1,500 characters.
- Standard post: 1,500–4,000 characters.
- Long-form / reference: 4,000–10,000 characters.

## Image & Illustration Support

- Cover / featured image: set in front matter (`cover` / `image` / `thumbnail`
  depending on theme); 16:9, 1200x630 for social share cards.
- Inline images: place in the theme's asset folder; use the generator's image
  shortcode so relative paths resolve on all hosts.
- SVG diagrams are fine for self-hosted blogs.

## Background & Styling

- You control the theme; custom CSS, fonts, and colors are allowed.
- Use the generator's built-in shortcodes for callouts, tabs, and buttons if
  the theme supports them.

## SEO & Discovery

- Front matter `description` becomes the meta description.
- `slug` / `permalink` controls the URL; keep it short and keyword-rich.
- Tags and categories feed the generator's tag/category pages.
- Add Open Graph / Twitter card tags via the theme (usually automatic).

## Content Adaptation Workflow

1. Ask which generator (Hugo / Jekyll / Hexo) the user runs.
2. Write correct front matter for that generator with `draft: true`.
3. Set the file name per the generator's convention.
4. Convert headings so the body starts at `##` (title is in front matter).
5. Convert image references to the generator's image shortcode.
6. Add a table-of-contents shortcode for long posts.
7. Ensure code blocks have a language tag.
8. Set `slug`, `description`, `tags`, `categories`; run the checklist.

## Quality Checklist

- [ ] Front matter matches the generator (Hugo/Jekyll/Hexo).
- [ ] File name follows the generator's convention.
- [ ] `draft: true` until ready.
- [ ] Body starts at `##`; title is in front matter, not `#`.
- [ ] Images use the generator's image shortcode.
- [ ] Code blocks have a language tag.
- [ ] `description`, `tags`, `categories`, `slug` set.
- [ ] TOC shortcode added for posts over ~2,000 chars.

## When to Use

- "Write a post for my Hugo / Jekyll / Hexo blog"
- "Adapt this for my static blog"
- "Platform-specific content for static blog", "write a Markdown post with front matter"
- "Prepare a draft for my self-hosted blog"

## Do NOT Use For

- `hugo deploy`, `jekyll build`, `hexo deploy`, SSH/S3/Vercel/Netlify hosting.
- Other platforms' format rules (use the per-platform skill).
- Short social posts (use Xiaohongshu / Weibo).
