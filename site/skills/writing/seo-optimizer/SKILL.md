---
name: seo-optimizer
description: "Optimize article for search: extract keywords, generate meta tags, score SEO quality, and adapt titles/captions per platform. Use after editing, before publishing to specific platforms. Use when the user asks to do SEO optimization / pick keywords / optimize the title / check keyword density / generate a meta description / optimize SEO / extract keywords / SEO score / meta description / platform title limits. Do NOT use for paid advertising strategy, ad bidding, or writing the article itself."
license: Apache-2.0
compatibility: Pure Python analysis. No API keys required.
metadata:
  version: "2.0"
  author: awesome-skillkit
  category: writing
  pattern: single-task
  tier: sota
  verified-date: "2026-09-21"
---

# SEO Optimizer: Evaluate an Article's SEO Readiness and Adapt Titles and Meta per Platform

## Pick Your Path by Task

| What You Want | Go Straight To | Key Actions |
|---|---|---|
| Produce a title + meta for a finished article | Steps 1-4 | run the script -> adjust the title per platform culture -> re-score |
| Judge whether this article can be found | read "Search-Intent Matching" first, then run the script | align search intent; don't tune keywords first |
| The title change made traffic worse | read "Platform Title Culture" first | check whether you hit a platform throttling red line |
| Can't pick keywords | [references/keyword-research.md](references/keyword-research.md) | manually specify `target_keywords` |

## Domain Tacit Knowledge (Build Judgment Before Running the Script)

### 1. Keyword Density Is an Outdated Superstition; Position Consistency Is Modern SEO

Rules like 1-3% keyword density come from the 2010s TF-IDF era. Baidu adopted BERT in 2019, Google even earlier —
**search engines now judge "what search intent does this article answer", not "how many times does this word appear"**. Stuffing density instead triggers thin/spammy-content judgment (Baidu's Hurricane Algorithm specifically targets scraping and keyword stuffing).

The three position-consistency points that actually matter in modern SEO:

| Position | Why | How |
|---|---|---|
| Title | The #1 factor in search-result click-through, which feeds back into ranking | Put the main keyword in the title's **first half** (truncation-safe zone) |
| First 100 chars of the lead | The search snippet is clipped right here; readers decide stay/leave in 3 seconds | Main keyword appears once naturally + directly answer the title's promise |
| At least one H2 | Source for long-article anchor jumps and featured snippets | Write H2s as questions readers would search ("why..." / "how...") |

This script's density check (weight 15) is **kept but downweighted**: its real job is catching the extreme case "zero keywords",
not tuning 1.8% to 2.2%.

### 2. Three Search-Intent Types; Title Sentence Follows the Intent

| Intent | What the User Is Searching | Title Sentence Form | Counter-example |
|---|---|---|---|
| Informational | "how to / why / what is" | Question or how-to: "Why Does Your Redis Always Time Out" | "Research on Redis Timeout Issues" |
| Comparative | "A vs B / which is better / is it worth it" | Name both comparators + a stance: "SQLite vs PostgreSQL: Which to Pick for a Small Project" | "An Introduction to Two Databases" |
| Problem-solving | "error / optimize / fix + specific symptom" | Symptom first + result first: "From 200ms to 30ms: A FastAPI Endpoint Optimization Log" | "FastAPI Performance Analysis" |

Before running the script, judge which type the article is — **a title sentence mismatched to intent is the #1 cause of "keywords all right but no traffic"**.

### 3. Platform Title Culture (One Title Has Five Fates on Five Platforms)

| Platform | Traffic Source | Title Culture | Red Lines (triggers throttling/demotion) |
|---|---|---|---|
| CSDN | On-site search + SEO traffic | Technical keyword front-loaded + concrete numbers; searchers scan for tech-stack words | Clickbait judgment ("shocking!""must read") lowers exposure; tags unrelated to content get reported |
| Juejin | Editor picks + follow feed | Conversational, scene-based, "I" perspective; 【】prefixes are recognizable but don't overuse | Pure-marketing outbound-link posts get demoted |
| WeChat Official Account | Social sharing | Emotion + suspense + identity label ("anyone doing backend gets this"); the hook must land within 30 chars | **Clickbait explicitly cracked down on**: words like "shocking/must read/99% of people don't know" trigger throttling; share-bait ("if you don't repost you're not...") is directly penalized |
| Baijiahao | Baidu search + feed | Numbers + pain points, review extremely strict | Extreme words, exaggerated medical/finance claims fail review outright; title-body mismatch docks credit score |
| Toutiao | Feed recommendation, completion-rate driven | Question form + numbers perform well; the title's promise must be delivered in the body, or completion collapses -> recommendation halved | Machine "clickbait" review: a concept in the title absent from the body is judged clickbait |

**Universal red-line word list** (cracked down on across all platforms): shocking, must read, instantly get it, 99% of people, stunned, if you don't repost you're not...,
just leaked, inside information. The script can't catch these — **if any of these 8 appears, rewrite the title manually**.

### 4. Honest Disclosure: What This Score Is and Isn't

`score` is a **self-check heuristic**, meant to sort 20 drafts and find which basics were skipped.
It is **not** a real search-engine ranking prediction — real ranking is decided by site authority, backlinks, and user-behavior signals, which no local
script can compute. Don't tell the user "score 85 = top-3 ranking"; say "8/9 basics are in place, missing X".

## Workflow

### Pre-flight Checks

```bash
python3 --version                                   # expect >= 3.8
test -f scripts/seo_optimizer.py && echo OK         # expect OK; on failure -> cd to the skill directory
python3 scripts/seo_optimizer.py --title "smoke" --content "smoke content" | head -c 20
# expect: JSON starting with {; on failure -> see the Failure Remediation Table
```

### Step 1: Judge Search Intent + Run the Baseline

First judge the article's type by "Three Search-Intent Types" (this determines Step 2's title sentence form), then run:

```bash
python3 scripts/seo_optimizer.py \
  --title "FastAPI performance optimization" \
  --content article.md \
  --platform csdn \
  --output seo_result.json
```

Expected: exit code 0, JSON with `title` (`issues`/`suggestions`) and `meta` (`meta_description`/`tags`/`keywords`/`score`).

### Step 2: Rewrite the Title per Platform Culture (Human Step; the Script Only Suggests)

Rewrite per the "Platform Title Culture" table + the search-intent sentence form, with three hard constraints: main keyword in the first half, length <= platform cap,
at least one of a number or a comparison. **Run the red-line word list through word by word** — the script can't catch clickbait words; this is the human gate.

### Step 3: Meta Description and Tags

- Meta description: 80-160 chars (search results clip around 155); the main keyword appearing once gets highlighted in search results;
  write "what the reader sees when they click in", not a slogan.
- Tags: dedupe `meta.tags` then truncate per platform cap (CSDN <=5, Juejin <=3); **tags must be topics the body actually covers**;
  hanging hot unrelated tags is a top report trigger.

### Step 4: Re-score + Real-World Verification

1. Rerun the script on the optimized title; `score` must not drop (if it dropped = you squeezed out the main keyword; roll back).
2. **Real-world verification (what the script can't measure)**: put the final title in the target platform's search box and search the main keyword,
   compare against the current top three — does your title offer an angle none of them has? If not, traffic won't come; change the angle, not the words.

## Parameter Quick Reference

| Parameter | Value | Notes |
|------|------|------|
| `--title` | string | The original article title |
| `--content` | path or text | Full body text; either works |
| `--platform` | `csdn` (default) / `juejin`/`wechat`/`baijiahao`/`toutiao` | Determines title-length rules |
| `--output` | JSON file path | default prints to stdout |

## Scoring Factors (With Weight Rationale)

| Factor | Weight | Rationale |
|------|------|------|
| Title contains keyword | 20 | The #1 factor in search-result click-through |
| Meta description | 15 | The snippet clip zone; affects clicks, not directly ranking |
| Keyword density | 15 | Only for catching the "zero-keyword" extreme miss (see tacit knowledge 1) |
| Title length | 10 | Platform truncation protection |
| Title structure | 10 | H1>H2>H3 hierarchy = H2 anchors and featured-snippet eligibility |
| Body word count | 10 | <800 words struggles to fully answer one intent |
| Internal links | 10 | On-site authority flow |
| Readability | 10 | Short paragraphs affect completion; completion affects recommendation |

## Failure Remediation Table

| Symptom / Error Code | Cause | Remedy |
|-------------|------|------|
| `ModuleNotFoundError` / `python3: command not found` | Python not installed or not on PATH | Install Python 3.8+ and rerun the pre-flight checks |
| `FileNotFoundError` | Wrong `--content` path | Switch to an absolute path; or pass the body text directly to `--content` |
| `unrecognized arguments` | Misspelled parameter name | Use only the 4 parameters in the quick reference |
| `score` stuck at 50 and `keywords` empty | Body too short or all non-content words | Add >800 words of body and rerun |
| `tags` empty but the body is normal | No word-frequency hits | Manually pass `target_keywords`, or accept empty tags and add them by hand |

## Delivery Standard

- Artifact: `seo_result.json` (optimized title + meta + tags + score), validated by `python3 -m json.tool`.
- Completeness: final title passes the red-line word list, matches the intent sentence form, and complies with platform length — all three green.

## References

- [references/keyword-research.md](references/keyword-research.md) — keyword-selection method when you can't pick a main keyword or want a better one.
- [references/platform-rules.md](references/platform-rules.md) — per-platform SEO details (tag caps, review strictness).
