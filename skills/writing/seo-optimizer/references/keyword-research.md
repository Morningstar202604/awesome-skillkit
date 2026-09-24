# Keyword Research: An Executable Workflow (No Paid Tools)

> When to read: read this file when the article is finalized and you need to pick **primary and long-tail keywords** and adapt them to the platform. Platform rule differences are in the sibling file platform-rules.md (loaded together by SKILL.md).
> **This file provides no search-volume API and no search-volume numbers for any platform.** Any "magnitude" data (search volume, index, competition score) can only come from official platform tools or third-party services you pay for yourself; this file only provides a **data-free judgment workflow**.
> All ratio ranges are **rules of thumb**, not official platform rules.

## Table of Contents

- [1. Input / output contract](#1-input--output-contract)
- [2. Five-step workflow overview](#2-five-step-workflow-overview)
- [3. Seed-keyword expansion (free)](#3-seed-keyword-expansion-free)
- [4. Long-tail mining (free)](#4-long-tail-mining-free)
- [5. Intent classification](#5-intent-classification)
- [6. Competition assessment (no-data version)](#6-competition-assessment-no-data-version)
- [7. Keyword tiering table template](#7-keyword-tiering-table-template)
- [8. Density and placement (rules of thumb)](#8-density-and-placement-rules-of-thumb)
- [9. Common mistakes](#9-common-mistakes)

---

## 1. Input / output contract

**Input**: `topic`, `target_keywords` (optional, words the user already gave), `platform`, `audience`.
**Output**: a set of words to fill into the `target_keywords` field of `seo_optimizer.py`, plus a tiering table (§7).

How it connects to the script: `scripts/seo_optimizer.py`'s `extract_keywords()` does **pure word-frequency counting** (regex extracts 2–4 character Chinese fragments and English words of ≥3 letters, takes the top 5, and filters out those appearing only once). It can only tell you "what the article already says", **not** "what users will search for". So keyword research must be done by a human / model outside the script; the script only handles on-page checks.

---

## 2. Five-step workflow overview

| Step | Action | Expected output | Failure branch |
|----|------|----------|----------|
| 1 | Seed expansion: break the topic into 5–15 candidates | Candidate word pool | <5 → the topic is too narrow; broaden to a higher-level concept first, then narrow |
| 2 | Long-tail mining: find 3–5 specific variants for each seed | Long-tail list | Can't find variants → the word may have no real demand; demote it |
| 3 | Intent classification: tag each word with an intent | Word list with intent | One word looks like two intents at once → split into two articles; don't cram two into one |
| 4 | Competition assessment: actually search on the target platform | Rough competition read (high/medium/low) | All high → switch to long-tail or change the first-publish platform |
| 5 | Tiering and finalizing: pick 1 primary, 2–3 secondary, 5–10 long-tail | Tiering table + `target_keywords` | Primary word can't blend naturally into the title → change the primary word; don't force it in |

---

## 3. Seed-keyword expansion (free)

Three free methods, done in order:

1. **Hyponym / hypernym breakdown**: ask one level up (the parent category) and two levels down (specific scenarios / specific errors / specific versions).
   - Example: `FastAPI performance optimization` → hypernym: `Python Web performance`; hyponyms: `FastAPI slow query`, `FastAPI asyncpg`, `FastAPI connection pool config`.
2. **Collect synonyms and naming variants**: list every alias you know, then type each one into the target platform's search box and see whether the **search dropdown (autocomplete)** suggests it — if it appears, the platform recognizes that naming; if not, that naming doesn't work on the platform.
   - Example: `message queue` / `MQ` / Chinese equivalent; `vector database` / `vector DB` / Chinese shorthand.
3. **Competitor-title frequency count** (scriptable):
   - Search the seed word on the target platform, sort by relevance or popularity;
   - take the **title + first 100-character abstract** of the top 20 results;
   - tokenize with the same regex as `extract_keywords()`, count the frequency of 2–4 character fragments;
   - take the top 10 frequencies and manually remove stop words.
   - Criterion: a word appearing in ≥30% of competitor titles → it's the platform's "common naming" and is worth a primary-word candidate.
   - Note: before scraping, confirm the target pages' robots and terms of service allow it; don't send high-frequency bulk requests.

---

## 4. Long-tail mining (free)

| Source | How to do it | Output shape |
|------|----------|----------|
| Platform search dropdown | Type the seed word + space + each letter / common suffix into the target search box; record the completions | "seed word + how-to / error / config / compare" |
| Related searches area | The "related searches" module at the bottom or side of the results page; record each one | Same-topic words the platform itself recognizes |
| Users' own words | **Users' original question sentences** in comments, Q&A, and issue threads | Long-tail sentences (often ready-made titles) |
| Error messages | Use the real error string verbatim as a keyword | Very low competition, very high intent clarity |
| Version / year qualifiers | Seed word + version number / + year | `FastAPI 0.110 connection pool`, `2026 Redis caching solutions` |

**Users' own words are the most valuable long-tail source**: turn them directly into titles; the search-intent match is highest. Example: a user asks "during load testing, QPS won't go up — is it the connection pool?" → title "QPS stuck during load testing? Check these 3 connection-pool parameters first".

---

## 5. Intent classification

| Intent | Trigger-word features | What content to give | What not to give |
|------|-----------|-------------|-----------|
| Informational (what / why) | what is, principle, why, how to understand | Explanation + diagram + example | Pushing a solution right off the bat |
| Operational (how to) | how to, tutorial, config, steps | Steps + commands + expected output + failure branches | Long background preamble |
| Troubleshooting (error) | error message, failed, stuck, doesn't work | Symptom → cause → fix, end to end | Only explaining the principle without a solution |
| Comparative (which to pick) | vs, compare, which is better, selection | Evaluation data + scenario-based recommendation | Only listing parameters with no conclusion |
| Transactional (buy / download) | price, buy, download, discount | Clear entry point and conditions | Beating around the bush |

**How to judge**: extract the question word from the keyword and match it against the table; if there's no question word (e.g. `Redis caching`), it's likely informational or comparative — look at the top-ranked content on the results page and **match its format**.

---

## 6. Competition assessment (no-data version)

Without search-volume data, use **observation** to rate "high/medium/low"; three signals, each one vote:

| Signal | Low competition (good) | High competition (hard) |
|------|-------------|-------------|
| Content quality of results | Top 10 are mostly cobbled-together, no live testing, no data, old | Top 10 are mostly long-form, with live-test data and tables/charts |
| Result homogeneity | Titles and structures are highly similar, almost no new angles | Several pieces with different angles, citing each other |
| Authoritative-site share | Few official docs / big-vendor accounts; mostly personal accounts | Half of the top 5 are official or top accounts |

**Criterion**: ≥2 signals point to low → doable; ≥2 point to high → switch to a long-tail (add qualifiers: version, scenario, error, data scale).

**Don't go head-to-head on "high competition"**: demote the primary word to a secondary word, enter through the long-tail, and add the primary-word article after the long-tail one gets indexed.

---

## 7. Keyword tiering table template

Copy and use one per article:

| Tier | Keyword | Intent | Competition | Placement | Target rank | Notes |
|------|--------|------|--------|--------|-----------|------|
| Primary (1) | FastAPI performance optimization | Operational | Medium | Title, first paragraph, first H2, meta | Top 3 | The only primary word in the whole piece |
| Secondary (2–3) | asyncpg, connection pool config | Operational | Low | Each takes one H2 | Top 5 | Same topic as primary, different facet |
| Long-tail (5–10) | FastAPI load testing QPS won't go up | Troubleshooting | Low | Scattered across H3 and body | Top 10 | Allowed to appear only 1–2 times |
| Negative words (exclude) | FastAPI tutorial, FastAPI getting started | — | — | Do not appear | — | Avoid diluting the topic |

Rules:
- The primary word is **unique**. Serving two primary words in one article means serving neither well.
- Don't pad long-tail words; if you can't come up with 5, the topic is too narrow.
- Negative words must be listed explicitly — the easiest accidental dilution while drafting is letting in a broad hypernym, which dilutes the topic.

---

## 8. Density and placement (rules of thumb)

**First, align on the density definition** (a Chinese-specific pitfall): density = keyword occurrences ÷ **total character count** (not ÷ the number of tokens). Because Chinese has no spaces, different definitions can differ by 3× or more. Always state the definition in your report.

| Placement | Rule-of-thumb range | Notes |
|------|----------|------|
| Primary-word density across the piece | 1%–3% (rule of thumb, not a platform rule) | <1% may mean a weak topical signal; >3% looks like stuffing — manual review |
| Primary word in title | 1 time, the earlier the better | Front-loaded beats back-loaded |
| Primary word in first paragraph | Appears once within the first 100 characters | Don't force it in twice in the first paragraph |
| Primary word in H2/H3 | 30%–50% of subheadings contain the primary or secondary word (rule of thumb) | Not every heading gets stuffed |
| meta description | Contains the primary word once within 80–160 characters | Aligns with `seo_optimizer.py`'s desc_max |

> **Be aware of the difference from the script**: `scripts/seo_optimizer.py`'s `_seo_score()` currently marks density `0.01 < d < 0.08` as passing and deducts at ≥8% — the upper bound is loose. In practice, manually review against the 3% cap in the table above; don't let it through just because the script scored it.

**Placement priority** (high to low): title > first H2 > first paragraph > meta/abstract > even body distribution > image alt/caption text > ending.

---

## 9. Common mistakes

| Mistake | Consequence | Fix |
|------|------|------|
| Cramming 2 primary words into one article | Topic signal scattered; ranks for neither | Split into two, or demote one to secondary |
| Primary word won't blend naturally into the title | Forced patchwork; the title doesn't read | Change the primary word. A readable title beats keyword placement |
| Using the "official name" instead of the "user's name" | None of the words users actually search are in your piece | Do the dropdown check in §3; adopt the platform's recognized naming |
| Looking only at frequency, not intent | Traffic arrives but bounce rate is high | Add the §5 intent classification; rewrite the corresponding paragraphs by intent |
| Writing search-volume numbers into the deliverable | Introducing unverifiable data | Don't. Write only the high/medium/low rough call and the rationale |
| Density achieved by repetition | Flagged as stuffing, and reads badly | Carry it with synonyms and long-tail variants; keep the primary word at 1%–3% |
