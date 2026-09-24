# Drafting Tips for Long-Form Chinese Articles (Ready to Apply)

> When to read: read this file when entering the stage of "filling the outline into prose".
> This file is a reference for **writing craft**; hard style/grammar checks live under the `content-editor` skill — don't fuss over punctuation at this stage.
> All numbers, unless sourced, are **rules of thumb (not platform rules)** and can be adjusted for your audience and carrier.

## Table of Contents

- [1. Input/output contract with drafter.py](#1-inputoutput-contract-with-drafterpy)
- [2. Opening hook: 5 reusable sentence patterns](#2-opening-hook-5-reusable-sentence-patterns)
- [3. Paragraph rhythm: paragraph length, sentence length, subheading density](#3-paragraph-rhythm-paragraph-length-sentence-length-subheading-density)
- [4. Argument organization: claim–evidence–rebuttal three-part structure](#4-argument-organization-claim-evidence-rebuttal-three-part-structure)
- [5. AI-tell phrase list and replacements](#5-ai-tell-phrase-list-and-replacements)
- [6. Ending CTA writing](#6-ending-cta-writing)
- [7. Right/wrong contrast (two versions of the same passage)](#7-rightwrong-contrast-two-versions-of-the-same-passage)
- [8. Pre-submission self-check checklist](#8-pre-submission-self-check-checklist)

---

## 1. Input/output contract with drafter.py

`scripts/drafter.py` only assembles the skeleton and **does not generate body text** (`status: draft_placeholder`). The body is filled in by the model following the rules in this file.

| Field | Source | How to use while drafting |
|------|------|--------------|
| `section.points[]` | Outline | One point = the smallest unit of one natural paragraph; don't mix across points |
| `section.word_count_target` | Outline | Allow ±20% deviation; beyond ±35% you must split paragraphs or add evidence |
| `audience` | Input | Determines terminology density and example count — see the table below |
| `hook` | Outline | The first paragraph must reuse/rewrite it; don't start from scratch |

Audience tier → writing parameters (rules of thumb):

| Audience | Each new term | Examples per section | Code | Max sentence length (chars) |
|----------|-----------|-----------|------|----------------|
| beginner | Give a plain-language explanation on first occurrence | 3-4 | Complete runnable snippet | 30 |
| intermediate | Explain only non-standard terms | 2-3 | Key snippet | 40 |
| expert | No explanation | 0-1 | One command / signature | 50 |

> The max sentence length aligns with `content-editor`'s `max_sentence_len=40` (technical); if the target style is casual, press it to 25.

---

## 2. Opening hook: 5 reusable sentence patterns

Rule: the hook must land within **the first 2 sentences (≤ 80 characters)**; start delivering substance at the 3rd sentence. Pick 1 of 5; don't stack two or more.

| # | Pattern | Template (just fill in the blanks) | Fits | Example |
|---|------|------------------|----------|------|
| 1 | Counterintuitive conclusion | "Most people think X, but live testing shows Y is the real cause." | Technical, reviews | Most slow FastAPI endpoints aren't the framework's fault — they're your few lines of sync I/O. |
| 2 | Concrete number contrast | "Same endpoint, changed N places, dropped from A to B." | Tutorials, postmortems | Same query endpoint, 5 changes, P99 dropped from 200ms to 30ms. |
| 3 | Scenario pain-point question | "Ever hit this: __? I tripped on it last week." | Tutorials, checklists | Ever hit this: load testing starts and QPS sticks at 300? I tripped on it last week. |
| 4 | Slice-of-life narrative | "Last Wednesday at 3 AM, __ went down. The cause was __." | Postmortems, commentary | Last Wednesday at 3 AM, the order service timed out. Four hours of digging, and the culprit was one SQL that didn't use an index. |
| 5 | Direct verdict | "If you can only change one thing, change __. Reasons below." | Opinion, checklists | If you can only change one thing, change the connection pool. Reasons and live-test data below. |

**Failure criterion**: after writing the hook, read it — if deleting it doesn't weaken the article's conclusion, it's an ineffective hook (just pleasantries); rewrite with another pattern.

---

## 3. Paragraph rhythm: paragraph length, sentence length, subheading density

| Metric | Cap (rule of thumb, mobile reading) | Over-cap action |
|------|--------------------------|----------|
| Chars per paragraph | 120 | Split by "one point per paragraph" |
| Lines per paragraph (mobile) | 5 | Same as above |
| Consecutive pure-text paragraphs | 3 | The 4th must insert a list / code block / quote / figure |
| Subheading spacing | One subheading every 300–500 chars | Split long sections into h3 |
| Chars per sentence | See §1 table | Split into two sentences, or use a semicolon to shorten |
| Paragraphs per section | 2–4 | >4 means it should be split into two h3s |

**Mechanical rhythm check** (run per section after drafting):

1. Section char count ÷ paragraph count > 120 → split paragraphs.
2. Does the section have 4 consecutive pure-text paragraphs? → insert a structured block.
3. Is the section > 500 chars with no h3? → add an h3; the heading states the section's conclusion, not "Overview" / "Introduction".

**Subheading naming bans**: `Overview`, `Introduction`, `Preface`, `What is X` (as a title), `Summary`. Headings must carry information, written as a judgment: `X is not the bottleneck, Y is`.

---

## 4. Argument organization: claim–evidence–rebuttal three-part structure

Expand each "claim" in three parts below; if any part is missing, demote that claim to "personal feeling" and either delete it or add evidence.

```
[Claim] A one-sentence assertion (no "maybe/should/I think")
   ↓
[Evidence] Reproducible facts: command + output / data + source / doc citation + version
   ↓
[Rebuttal] Proactively give the strongest counterexample or limiting condition,
   explaining why the claim still holds (or how far it yields)
```

- **Claim**: one sentence, complete subject–verb–object, falsifiable. Write "P99 dropped from 200ms to 30ms", not "performance improved noticeably".
- **Three kinds of evidence** (priority high to low): ① commands you ran yourself with raw output; ② official docs or papers with version/date; ③ third-party data with a clearly labeled source. **Unsourced data must not carry specific numbers.**
- **Rebuttal**: at least one sentence like "of course, this conclusion doesn't hold when __". Paragraphs without a rebuttal are the hardest hit zone of AI tone.

**Example (technical writing)**

> Setting the connection-pool cap to 20 is enough. We load-tested with `pgbench -c 100` on a 4-core 8G container; when connections went from 20 to 100, QPS actually dropped 12% (see `pgbench` output below). Of course, if each query itself takes seconds and concurrency is below 20, this cap needs to go up — in that scenario the bottleneck is the SQL, not the connection count.

---

## 5. AI-tell phrase list and replacements

After drafting, run a string scan over the whole piece. Anything hit in the left column of the table below should be rewritten; don't keep it.

| Hit phrase | Why it's AI tone | Suggested replacement |
|--------|----------------|----------|
| First / second / third / finally | Mechanical sequence words that expose the template structure | Delete outright; show order via subheadings and transitions |
| In summary / to sum up / in a word | Empty summary spins; the reader knows you're summarizing | Write the specific conclusion: "of the three, only #2 is worth doing now" |
| It's worth noting / it should be pointed out | An emphasis cue with zero information | State directly, or switch to "here's a trap:" |
| In today's society / in this day and age | Useless era backdrop | Delete, go straight to the topic |
| With the continuous development of… / increasingly popular | Useless preamble | Replace with concrete data or event: "in the 2026-09 DB-Engines ranking…" |
| As everyone knows / it's not hard to see / obviously | Disguising an assertion as consensus | Give a source, or delete |
| In fact / essentially / fundamentally / in a sense | Vague hedging that hides weak argument | Delete, or supply the real limiting condition |
| Seamlessly connect / empower / lever / closed loop / ship / granularity | Internet jargon | Replace with a concrete action: "let A read B's output directly" |
| All-around / multi-dimensional / in-depth analysis / systematic | Cost-free exaggerated adjectives | Replace with countable description: "covers 3 scenarios" |
| Not just… but even… | Hollow escalation | Keep only the second half |
| Let's… / hope this helps / welcome discussion in the comments | Cheap engagement | Replace with a concrete CTA (see §6) |
| Escort / escort-style ending | Cliché | Delete |
| Carry out / implement / conduct + verb (e.g. "carry out optimization") | Nominalization clutter | Use the verb directly: "optimize" |

**Mechanical scan**: make the left column above a list and, one by one, `if word in text: flag`. ≥3 hits → rewrite that whole section; don't replace word-by-word (word-by-word replacement produces new awkwardness).

---

## 6. Ending CTA writing

Ending = 1 callback conclusion + 1–3 concrete actions + 1 CTA. Total length ≤ 5% of the whole piece.

Pick 1 of 3 CTA types by platform; **don't write all three**:

| Type | Template | Fits |
|------|------|------|
| Action | "Follow §2's three steps, drop your P99 in the comments, and I'll help you see what's left to squeeze." | Zhihu, WeChat Official Account |
| Save | "I've turned this checklist into a table; before you save, confirm your current project matches at least 3 items." | CSDN, Juejin |
| Follow-up | "Next I'll write the live-tested comparison of connection-pool parameters; follow so you don't miss it." | WeChat Official Account, Bilibili description |

**Banned**: `hope this helps`, `if you found this useful please like`, `thanks for reading` (as a standalone sentence).

---

## 7. Right/wrong contrast (two versions of the same passage)

**Bad example (typical AI draft)**

> With the continuous development of web frameworks, performance optimization has increasingly become a focus for developers. First, we need to understand FastAPI's basics; second, we should leverage async; finally, we must also pay attention to database queries. It's worth noting that caching is also a very important part. In summary, performance optimization is a systematic project, and I hope this helps.

Problems: era-backdrop preamble (2 sentences, 0 information) + first/second/finally (template exposed) + "it's worth noting" (empty emphasis) + no evidence + no rebuttal + cheap CTA.

**Good example**

> Eight out of ten slow FastAPI calls aren't the framework's fault. We load-tested a read-only endpoint with `locust` on a 4-core container; the flame graph showed 78% of time stuck on `psycopg2`'s synchronous wait — after switching to `asyncpg`, P99 dropped from 200ms to 62ms.
>
> Of course, if your query itself takes 800ms, switching the driver won't save you; in that case, look at `EXPLAIN ANALYZE` first.
>
> For the other three bottleneck types (N+1, no index, connection pool full), the troubleshooting order is in the next section.

Difference: first sentence is an assertion → command + numeric evidence → proactive rebuttal giving the boundary → points to the next section (carrying the transition).

---

## 8. Pre-submission self-check checklist

Tick each item; if any fails, go back and revise:

- [ ] The hook completes within the first 2 sentences, and deleting it would weaken the article's conclusion (not pleasantries)
- [ ] Each `points[]` corresponds to at least one natural paragraph; nothing skipped
- [ ] Each section's char count is within `word_count_target` ±20%
- [ ] No 4 consecutive pure-text paragraphs; each paragraph ≤120 chars; sentence length matches the audience tier
- [ ] Every claim carries evidence, and the evidence has a source or a reproducible command
- [ ] Every claim carries at least one rebuttal / boundary condition
- [ ] The AI-tell phrase scan hits < 3
- [ ] The ending has a conclusion callback + one concrete CTA, with no "hope this helps"
- [ ] In the output JSON, `status: "draft"`, `needs_review: true` (the drafter's output is by default unreviewed)
