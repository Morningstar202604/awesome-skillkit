# Chinese Technical Writing Style Rules

> When to read: read this file when entering the proofreading / polishing stage and needing to **unify the style**. Grammatical and syntactic issues are in the sibling file grammar-checks.md (loaded together by SKILL.md).
> Format: each entry = **rule (mechanically checkable) / good example / bad example**. Rules should, as far as possible, be "detectable by regex or string matching".
> Some rules reference GB/T 15834 "Usage of Punctuation Marks" and GB/T 15835 "Usage of Numerals in Publications" — standards get revised, **defer to the currently valid version**; all other numbers in this file are rules of thumb.

## Table of Contents

- [1. Chinese–English mixed typesetting and spacing](#1-chineseenglish-mixed-typesetting-and-spacing)
- [2. Full-width vs half-width punctuation](#2-full-width-vs-half-width-punctuation)
- [3. Quotation marks and book-title marks](#3-quotation-marks-and-book-title-marks)
- [4. Numbers and units](#4-numbers-and-units)
- [5. Terminology consistency](#5-terminology-consistency)
- [6. Person, tone, and tense](#6-person-tone-and-tense)
- [7. Heading hierarchy](#7-heading-hierarchy)
- [8. Mechanical check-script approach](#8-mechanical-check-script-approach)

---

## 1. Chinese–English mixed typesetting and spacing

| Rule (mechanically checkable) | Good example | Bad example |
|--------------------|------|------|
| Add a half-width space between Chinese characters and English/numbers | Use the `FastAPI` framework | UseFastAPIframework |
| No space between Chinese and English punctuation | This article covers FastAPI, focusing on performance. | This article covers FastAPI , focusing on performance. |
| Add a space between numbers and Chinese | 3 steps total | 3steps total |
| Wrap inline code / identifiers in backticks, and keep a space outside the backticks | Call `create_async_engine()` to establish a connection | Callcreate_async_engine()to establish a connection |
| Use only one half-width space between consecutive English words (don't widen for Chinese rules) | `async def handler` | `async  def  handler` |

Detection regex (for scanning; a hit means a suspected violation):

```text
[一-龥][A-Za-z0-9]     → Chinese immediately followed by English/number, missing space
[A-Za-z0-9][一-龥]     → English/number immediately followed by Chinese, missing space
[一-龥] ?[，。；：！？]  → space between Chinese and full-width punctuation should be removed
```

**Exemptions (don't flag)**: spaces after English punctuation, inside code blocks, URLs, unit symbols adjacent to numbers (see §4), and English-period abbreviations after Chinese.

---

## 2. Full-width vs half-width punctuation

| Rule | Good example | Bad example |
|------|------|------|
| Chinese sentences use full-width punctuation `，。；：！？（）` | Test first, then optimize. | Test first, then optimize. |
| Inside English/code, use half-width punctuation, unaffected by Chinese rules | `if x > 0 and y < 10:` | `if x > 0 and y < 10：` |
| Use the enumeration comma `、` between short coordinated Chinese words | Throughput, latency, memory | Throughput,latency,memory |
| No period at the end of a subheading | `## Why it's slow` | `## Why it's slow。` |
| If a list item is a full Chinese sentence, end it with a period and make all items consistent | All with periods / all without | Some with periods, some without |
| Use two `……` (full-width) for ellipsis, not three dots | And more… | And more... |
| Chinese inside parentheses uses full-width parens; if there's English inside, space per §1 | (See §3) | (See §3) |

---

## 3. Quotation marks and book-title marks

| Rule | Good example | Bad example |
|------|------|------|
| Use **only one kind** of Chinese quotation marks throughout; don't mix | Consistently use “” or consistently use 「」 | “” in the first half, 「」 in the second |
| When the quoted content is a full sentence, place the sentence-ending punctuation inside the quotes | He said: "This step must add load testing." | He said: "This step must add load testing". |
| When the quotes only quote a word/phrase, place the ending punctuation outside the quotes | This is the so-called "zero copy". | This is the so-called "zero copy。" |
| Nested quotes: outer double, inner single | "What he called the 'connection pool' was actually…" | "What he called the "connection pool" was actually…" |
| Don't put work / file / platform names in book-title marks | The example in this article is `drafter.py` | The example in this article is 《drafter.py》 |
| Use book-title marks for books, papers, standards, newspapers, films/TV | 《Usage of Punctuation》 | "Usage of Punctuation" |
| No enumeration comma between book-title marks | 《A》《B》 | 《A》、《B》 |
| Course / project / product names don't use book-title marks; quotes or backticks are fine | Project `awesome-skillkit` | 《awesome-skillkit》 |

---

## 4. Numbers and units

| Rule | Good example | Bad example |
|------|------|------|
| Statistics, version numbers, and parameter values always use Arabic numerals | P99 dropped from 200ms to 30ms | P99 dropped from two hundred ms to thirty ms |
| Fixed phrases, idioms, and approximations use Chinese numerals | Three-party consensus / a dozen times | 3-party consensus / 10-some times |
| Use the "two" variant before a classifier, not the "two/second" variant | Two approaches | The wrong numeral variant before a classifier |
| No space between number and unit symbol (except `%`, `ms`, `GB` — see next row) | 8GB memory / 30ms | 8 GB memory / 30 ms |
| Percent sign sits right next to the number | Down 12% | Down 12 % |
| Numbers of 4+ digits either all use thousands separators or none; be consistent throughout | 12,000 or 12000 (pick one) | Mixed |
| No thousands separators in years or version numbers | Python 3.11 / 2026 | Writing Python 3.11.0 as 3,11 (bad example) |
| Use `~` or `–` or "to" for ranges; be consistent throughout | 300~500 words | 300-500 words (half-width hyphen with no space) |
| When units repeat, write "number unit" consistently, not mixed | 4 cores 8G | 4core8G (inconsistent with context) |

> The row above ("no space between number and unit") and §1 ("space between Chinese and English") look like they conflict; the resolution order is: first detect unit symbols (`ms` `GB` `%` `KB/s`) — if it's a unit, add **no** space; otherwise add a space per §1.

---

## 5. Terminology consistency

| Rule | Good example | Bad example |
|------|------|------|
| Use only one translation of the same concept throughout; on first occurrence give "Chinese (English)" | Connection pool | Mixing connection pool / connection buffer / connection pool |
| Keep fixed capitalization; don't change it freely | `FastAPI`, `PostgreSQL`, `Redis` | `fastapi`, `postgresql`, `redis` (in body text) |
| On first use of an abbreviation, give the full name | Queries per second (QPS) | Using QPS right off the bat |
| The same abbreviation doesn't stand for two concepts | QPS means only "queries per second" throughout | QPS meaning "requests per second" in section 3 and "queries" in section 5 |
| When Chinese and English terms differ, defer to English; Chinese is only an annotation | Use the `asyncio` event loop | Translating "event loop" as both "event polling" and "event loop" |

**Approach:** open a glossary, fill it before drafting, and replace by the table when revising.

| Chinese | English / original | First-occurrence section | Banned aliases |
|------|-----------|--------------|----------|
| Connection pool | connection pool | §2 | Connection buffer, connection cache |

---

## 6. Person, tone, and tense

| Rule | Good example | Bad example |
|------|------|------|
| In technical writing, use "we" to mean author + reader as a group; avoid "the author" | Let's first run a load test | The author first ran a load test |
| Don't use "you" to blame the reader | Beginners often trip up here | You definitely didn't add an index |
| State facts in present tense | This function returns None | This function will return None |
| Describe completed experiments in past tense or with an explicit time | Last week we measured 62ms on a 4-core container | We measured 62ms (without saying when/in what env) |
| Don't make assertions with "should/maybe/probably" (banned words in the technical style) | Live-tested P99 is 62ms | P99 should be around 60ms |
| Don't give unsourced quantitative claims | This approach performs better in comparable scenarios (add: see the §3 table for the basis) | This approach improves performance by 80% (no source) |
| Prefer active voice | We used `EXPLAIN` to locate the slow query | The slow query was located by us via `EXPLAIN` |

> The banned words for the technical style match `scripts/editor.py`'s `STYLE_RULES["technical"]["ban"]`: `I think / should / maybe / probably`. A hit counts as a `banned_word` issue.

---

## 7. Heading hierarchy

| Rule | Good example | Bad example |
|------|------|------|
| Only one level-1 heading (`#`) in the whole piece, i.e. the article title | `# FastAPI performance optimization` | Another `#` mid-body |
| Don't skip levels: from `##` go directly to `###`; don't jump to `####` | `##` → `###` | `##` → `####` |
| Same-level headings are parallel in structure (all noun phrases or all judgments) | `Why it's slow / how to check / how to fix` | `Why it's slow / optimization methods / numbered heading` |
| Headings carry no period and no quoted emphasis | `## The bigger the connection pool, the better? No` | `## The bigger the connection pool, the better!` |
| Headings carry no empty words | `## Live-test data` | `## Overview` / `## Preface` / `## Some notes` |
| Headings carry information; reading the headings lets you retell the article's arc | Reading the 6 `##`s in order tells a one-sentence story | After reading the headings you still don't know what the article is about |
| Numbering is consistent throughout | All "一、二、三" or all "1. 2. 3." | Mixing the two |

---

## 8. Mechanical check-script approach

Don't write complex assertions. A workable approach (an idea, not a full implementation):

1. **Spacing check**: scan line by line for `[一-龥][A-Za-z0-9]` and `[A-Za-z0-9][一-龥]`, outputting line number and context; on a hit, first judge whether it's in the exemption whitelist (units, URLs, code blocks).
2. **Full/half-width check**: within **non-code-block** regions, look for `,` `.` `;` `:` `(` `)`; if their left and right are Chinese characters → suspected need for full-width. Approach: first strip out the whole code blocks wrapped in ```` ``` ````, then scan.
3. **Terminology consistency**: read the glossary as an `alias → canonical name` map, run `str.count()` on each alias, and report the location if nonzero.
4. **Banned words**: `for w in ban_list: if w in text` → record `text.find(w)` as the position (consistent with the existing implementation in `scripts/editor.py`).
5. **Heading hierarchy**: match `^(#{1,6})\s` line by line, record the level sequence, and check ① how many times `#` appears; ② any adjacent-level jump > 1.
6. **Sentence length**: split on `。！？；`; report when `len(sentence) > max_sentence_len` (technical=40 / news=30 / casual=25, aligned with `editor.py`).

**Output contract**: for each category of issue, output `{type, original fragment, line number, suggested replacement}` — don't edit the file directly. The `content-editor` output is a **problem list + score**; the rewriting action is done by a human or the next model pass.
