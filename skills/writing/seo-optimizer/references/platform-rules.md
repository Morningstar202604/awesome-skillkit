# SEO / Recommendation Rule Differences Across Content Platforms

> When to read: read this file when you've settled on a target platform and need to adapt **title length / tags / external links / original-content marking**.
>
> ## Disclaimer (required reading — do not skip)
>
> **Everything below reflects common situations as of 2026-09; defer to each platform's latest rules.** Platform rules change frequently, and most platforms do not publish their recommendation algorithms or indexing criteria.
> The guiding principle of this file is: **if we cannot say something for certain, we will never fabricate a number.**
> - Any item marked `needs live testing`: please run through the publish page once yourself, and treat the real limits / errors / truncation you hit while entering as authoritative.
> - Any item marked `undisclosed`: the platform has not published the exact value; any claim like "affects X% of weight" is not credible.
> - Suggested ranges are **rules of thumb**, chosen for demonstration and readability — they are not platform limits.
> - Also: the "Platform Title Limits" table in `SKILL.md` and the `PLATFORM_META` values in `scripts/seo_optimizer.py` (e.g. csdn title 50, Juejin 60) are **script-internal default baselines**, set from the author's experience at skill-writing time, **not officially verified platform-by-platform**. They are fine for rough filtering, but must be live-tested before publishing.

## Table of Contents

- [1. Quick-reference master table](#1-quick-reference-master-table)
- [2. WeChat ecosystem (Official Account)](#2-wechat-ecosystem-official-account)
- [3. Zhihu](#3-zhihu)
- [4. CSDN](#4-csdn)
- [5. Juejin](#5-juejin)
- [6. Toutiao](#6-toutiao)
- [7. Baijiahao](#7-baijiahao)
- [8. Xiaohongshu](#8-xiaohongshu)
- [9. Bilibili (columns / video)](#9-bilibili-columns--video)
- [10. General verification workflow and multi-platform distribution notes](#10-general-verification-workflow-and-multi-platform-distribution-notes)

---

## 1. Quick-reference master table

> The "indexing", "external links", and "tag count" columns are all **qualitative descriptions + verification status**; no unverified precise numbers are given. All entries reflect common situations as of 2026-09; defer to the platform's latest rules.

| Platform | External search-engine indexing | External-link policy | Tags / topics count | Hard-limit verification |
|------|------------------|----------|---------------|-----------|
| WeChat Official Account | Primarily in-app; off-site indexing has long been restricted and unstable | In-body hyperlinks restricted; mostly pointing inside the WeChat domain | No tag system (relies on account positioning and collections) | needs live testing |
| Zhihu | Off-site indexing historically good (but changes) | Allowed, but impact on recommendation and presentation uncertain | Has a topic mechanism; count limit needs live testing | needs live testing |
| CSDN | Off-site indexing historically good (but changes) | Relatively permissive; reference links allowed | Has tags; count limit needs live testing | needs live testing |
| Juejin | Off-site indexing mediocre (undisclosed) | Relatively permissive | Has tags; count limit needs live testing | needs live testing |
| Toutiao | Primarily in-app recommendation; off-site indexing undisclosed | Whether in-body external links are restricted needs live testing | Has tags; needs live testing | needs live testing |
| Baijiahao | Part of the Baidu ecosystem; search visibility has a home-court advantage (weight undisclosed) | needs live testing | Has tags; needs live testing | needs live testing |
| Xiaohongshu | In-app search is central; off-site indexing limited | Off-site traffic diversion usually restricted; higher risk | Has topics; count limit needs live testing | needs live testing |
| Bilibili | In-app search is central; off-site indexing limited | Description / comment external-link policy needs live testing | Has sections and tags; needs live testing | needs live testing |

**How to use**: this table is for **directional choices** (publish where first, whether you can include links, whether to add tags), not for precise configuration. Precise values must always be live-tested.

---

## 2. WeChat ecosystem (Official Account)

> The below reflects common situations as of 2026-09; defer to the platform's latest rules.

| Dimension | Description |
|------|------|
| Indexing | Content is distributed mainly inside WeChat (chats, Moments, Top Stories, Search). **Whether and how much it is indexed by external search engines is undisclosed and has changed repeatedly historically** → treat it as "unstable off-site indexing"; do not treat external-search traffic as your main source. |
| Title | Hard cap `needs live testing` (visible once you type on the publish page). Suggested range: **within 20–30 characters** (rule of thumb), so it is not truncated in chat lists and share cards; the first clause must be self-explanatory. |
| Tags | No traditional tag system. Available categorization tools: account positioning, collections / albums, topic tags (if the current version offers them → `needs live testing`). |
| External links | In-body hyperlinks have long been restricted; usually they can only point to addresses inside the WeChat domain or to associated content. How external links can be placed and their limits are `needs live testing` — do not assume you can freely include them. |
| Original marking | Has an original-declaration mechanism. **The exact weighting it gives to recommendation / search is undisclosed.** Common practice is to declare original only for original content, and not to declare for reposts. |
| Abstract | You can fill in an abstract at publish time (char limit `needs live testing`); if left blank, the system auto-truncates the opening of the body → write it by hand. |

---

## 3. Zhihu

> The below reflects common situations as of 2026-09; defer to the platform's latest rules.

| Dimension | Description |
|------|------|
| Indexing | Off-site search indexing has historically been good, but **the exact criteria are undisclosed and change**. How to check: use a site-search operator on the target search engine with your own article title, and see whether it is indexed (live test — do not guess). |
| Title | Hard cap `needs live testing`. Suggested range: **25–40 characters** (rule of thumb). Zhihu titles lean toward "question-form / declarative long titles" and can carry more information than Official Account titles. |
| Tags | Topic binding exists; count and selection method `needs live testing`. Suggestion: prefer **high-traffic and precise** topics, not generic topics just to fill a quota. |
| External links | You can include them, but the impact on recommendation / presentation is `undisclosed`. Conservative approach: put sources at the end under "References" rather than inserting them frequently in the body. |
| Original marking | Has an original / repost mechanism; exact impact `undisclosed`. |
| Structure | Long-form friendly; supports multi-level headings, code blocks, formulas (the long-form templates in `article-drafter` and `content-editor` can be used directly). |

---

## 4. CSDN

> The below reflects common situations as of 2026-09; defer to the platform's latest rules.

| Dimension | Description |
|------|------|
| Indexing | Off-site search indexing has historically been good, `undisclosed` and changes → live test. |
| Title | Hard cap `needs live testing` (`seo_optimizer.py` defaults to 50, not officially verified). Suggested range: **keyword + number + scenario**, e.g. "Optimizing X from A to B: N steps". |
| Tags | Has tags; count cap `needs live testing` (script default 5, unverified). Suggest 3–5, all strongly related to the body. |
| External links | Relatively permissive; reference links and original sources allowed. `needs live testing` whether there are special restrictions (e.g. short links, off-site redirects). |
| Original marking | Has classification options like original / repost / translation; exact impact on recommendation `undisclosed`. |
| Notes | Technical content is sensitive to **code completeness and reproducibility**; spacing between Chinese and English outside code blocks and consistent terminology (the style rules in `content-editor`) directly affect presentation. |

---

## 5. Juejin

> The below reflects common situations as of 2026-09; defer to the platform's latest rules.

| Dimension | Description |
|------|------|
| Indexing | Off-site indexing mediocre, `undisclosed` → live test. |
| Title | Hard cap `needs live testing` (script default 60, unverified). Suggested range: 30–50 characters, technical keywords up front. |
| Tags | Has tags / categories; count cap `needs live testing` (script default 3, unverified). |
| External links | Relatively permissive, `needs live testing`. |
| Original marking | Has an original mechanism; impact `undisclosed`. |
| Notes | Readers lean toward front-end / full-stack; examples should be copy-paste-runnable; `content > form`, and clickbait carries a high cost. |

---

## 6. Toutiao

> The below reflects common situations as of 2026-09; defer to the platform's latest rules.

| Dimension | Description |
|------|------|
| Indexing | Primarily **in-app recommendation distribution**; off-site indexing `undisclosed` → do not target external-search traffic as your main goal. |
| Title | Hard cap `needs live testing` (script default 30, unverified). Suggested range: 20–30 characters; **number + question/pain-point** titles are common in this ecosystem (empirical observation, not an official conclusion). |
| Tags | Has tags; cap `needs live testing`. |
| External links | In-body external-link policy `needs live testing`; external links in recommendation-feed content are usually discouraged. |
| Original marking | Has an original mechanism, and the platform has handling rules for **non-original / low-quality** content; exact standards `undisclosed`. |
| Notes | The recommendation mechanism is sensitive to **completion rate / engagement** (exact weights `undisclosed`) → the opening hook and paragraph rhythm matter more than keyword density. |

---

## 7. Baijiahao

> The below reflects common situations as of 2026-09; defer to the platform's latest rules.

| Dimension | Description |
|------|------|
| Indexing | Same ecosystem as Baidu Search; content usually has an advantage in Baidu search results — but **the exact weighting rules are undisclosed**, so do not treat it as a guaranteed-traffic promise → live test. |
| Title | Hard cap `needs live testing` (script default 30, unverified). Suggested range: 20–30 characters, keywords up front. |
| Tags | Has tags; cap `needs live testing` (script default 3, unverified). |
| External links | `needs live testing`. |
| Original marking | Has an original mechanism; impact on recommendation / search `undisclosed`. |
| Notes | Has review rules against **clickbait and exaggerated claims**; exact penalty standards `undisclosed` → avoid words like "shocking / incredible" in titles (the banned words for the news style in `content-editor` already cover this). |

---

## 8. Xiaohongshu

> The below reflects common situations as of 2026-09; defer to the platform's latest rules.

| Dimension | Description |
|------|------|
| Indexing | **In-app search is central**; off-site indexing is limited and `undisclosed` → optimize for "in-app search"; put keywords in the title and the first few lines of the body. |
| Title | Hard cap `needs live testing` (community content titles are usually short). Suggested range: **within 20 characters** (rule of thumb), containing 1 core search term. |
| Tags | Has topic tags; count cap `needs live testing`. Suggestion: choose topics that **actually exist in the community and have some heat**; made-up topics do not work. |
| External links | **Off-site traffic diversion is usually restricted and carries higher risk** (exact penalty standards undisclosed) → conservative approach: no external links or contact info in the body. |
| Original marking | The community handles **non-original / reposted** content strictly; standards `undisclosed`. |
| Notes | Images / covers carry high weight; the body should use short sentences, frequent line breaks, and emoji as section dividers (the style differs from long Official Account articles; the long paragraphs in `article-drafter` need to be compressed). |

---

## 9. Bilibili (columns / video)

> The below reflects common situations as of 2026-09; defer to the platform's latest rules.

| Dimension | Description |
|------|------|
| Indexing | In-app search is central; off-site indexing limited, `undisclosed` → live test. |
| Title | Hard cap `needs live testing`. Suggested range: video title 20–30 characters; **the first 10 characters should carry the core keyword** (the list view truncates). |
| Tags | Videos have sections + tags; count cap `needs live testing`. Picking the wrong section matters more than picking the wrong tag. |
| External links | Description / comment-area external-link policy `needs live testing`. |
| Original marking | Has self-made / reposted marking; impact `undisclosed`. |
| Notes | A video's keywords live mainly in **title + description + tags + subtitles**; subtitle text has value for in-app search (whether it is indexed is `undisclosed`). |

---

## 10. General verification workflow and multi-platform distribution notes

### 10.1 Pre-publish verification workflow (run through this for every platform, every article)

| Step | Action | Expected result | Failure branch |
|----|------|----------|----------|
| 1 | Open the target platform's **publish page**, paste in the title | Observe the actual character cap / counter / whether it is truncated | No counter → binary-search the length, record the first length that is rejected |
| 2 | Open the platform's official help center / creator guidelines and search for "original", "external links", "tags" | Get the official wording | Can't find it → mark as `undisclosed`, follow the conservative strategy and record it |
| 3 | Use a site-search operator on an external search engine to search one of your own already-published articles on that platform | Confirm whether it is indexed | Not indexed → plan traffic around "in-app distribution" for that platform; do not write external-search expectations |
| 4 | Live-test external links: publish a test piece with 1 external link, observe whether it is restricted / down-ranked | Get the platform's current stance on external links | Restricted → replace clickable links with "text source at the end" |
| 5 | Backfill the live-test results next to the tables in this file | Build your own baseline | — |

**Suggested record format** (keep in your own notes; do not write back to this repo):

```text
platform / verification date / actual title cap / tag cap / indexed? / external link works? / notes
csdn / 2026-09-14 / still accepts input past 50 chars → cap ≥50 (hard edge not found) / 5 / indexed / works / defer to publish page
```

### 10.2 Multi-platform distribution notes

- **First-publish platform choice**: combine "original declaration + indexing capability + your own account weight". If a platform requires first-publish in order to declare original, the exact rule is `needs live testing` (policies differ by platform and change).
- **Syndicating one piece to multiple platforms**: each platform's handling of duplicate content is `undisclosed`. Conservative approach: change the title, the opening, and the layout for different platforms; avoid identical bodies across all of them.
- **Version titles**: after writing the main version, **trim the length** to each platform's suggested range rather than writing a new title; keep the core keyword in the first half of the title.
- **Do not**: assume a number from the script's `PLATFORM_META` is the official value; treat any description in this file as a platform promise.

### 10.3 Update convention for this file

- Every time you live-test new data, update the corresponding section and **also update the "verification date"** (write the actual date; do not carry over 2026-09).
- If you cannot verify a rule, write its status back as `needs live testing` / `undisclosed`; **do not fill in a plausible-looking number** — writing a fake character cap is worse than leaving it blank.
