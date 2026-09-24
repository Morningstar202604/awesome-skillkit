# Mechanical Checklist for Chinese Grammatical Errors

> When to read: read this file when doing **syntactic-layer** checks during the polishing stage. Style issues (punctuation / terminology / spacing) are in the sibling file style-guide.md (loaded together by SKILL.md).
> Format: each entry = bad original / corrected / how to tell. The "how to tell" column gives scannable strings or regex features wherever possible.
> All regexes are **heuristic (they will false-positive)**, and are only used to "locate candidates"; final judgment must be by a human or the model — do not write a complex assertion you believe is 100% correct.

## Table of Contents

- [1. Missing components](#1-missing-components)
- [2. Improper collocation](#2-improper-collocation)
- [3. Subject switching (hidden subject change)](#3-subject-switching-hidden-subject-change)
- [4. Ambiguous reference](#4-ambiguous-reference)
- [5. Redundancy](#5-redundancy)
- [6. Misused classifiers](#6-misused-classifiers)
- [7. de / de / de (的 / 地 / 得)](#7-de--de--de--的--地--得)
- [8. Connectives and two-sided vs one-sided](#8-connectives-and-two-sided-vs-one-sided)
- [9. Check-script approach and regex snippets](#9-check-script-approach-and-regex-snippets)

---

## 1. Missing components

| # | Original (bad) | Rewritten | How to tell |
|---|----------|--------|----------|
| 1.1 | Through this load test, made the connection pool the bottleneck. | This load test shows the connection pool is the bottleneck. | Sentence-initial "通过/经过/由于" + mid-sentence "使/让/令" → subject swallowed. Scan `通过.*使` `由于.*让`. |
| 1.2 | This article will detail how to troubleshoot, and how to optimize. | This article will detail how to troubleshoot the bottleneck, and how to optimize the config. | Coordinated items joined by "以及/和" are at different grammatical levels (one a clause, one a noun) → missing object. Restore the head noun in each coordinated item. |
| 1.3 | Regarding connection-pool parameters, need to based on load-test results. | Connection-pool parameters need to be adjusted based on load-test results. | "关于…" prepositional phrase acts as adverbial, and the sentence has no predicate → missing predicate. Scan whether after sentence-initial "关于/对于" there is only one comma-separated clause. |
| 1.4 | Reduced from 62ms. | Dropped from 200ms to 62ms. | "从/由" lacks a start or end. Scan `从[^，。]*?（降低\|提升\|减少）` with no "到/至/了+number" in the sentence. |
| 1.5 | During troubleshooting found that the index was unused. | During troubleshooting we found that the index was unused. | "在…中/时" directly followed by a verb with no subject. Scan `在[^，]*?(中\|过程中\|时)，[^我你他它我们]*?[发动]`. |

---

## 2. Improper collocation

| # | Original (bad) | Rewritten | How to tell |
|---|----------|--------|----------|
| 2.1 | This approach raised latency. | This approach lowered latency / raised throughput. | "提高" clashes semantically with "latency/elapsed time/error rate". Maintain a whitelist of "verb → collocating nouns"; flag reverse collocations. |
| 2.2 | We enhanced performance by 30%. | We improved performance by 30%. | "增强" doesn't collocate with "performance" (enhance: capability/confidence/protection). Check a collocation dictionary. |
| 2.3 | A very enormous improvement. | An enormous improvement. | "非常" doesn't modify words that already contain a degree sense (huge/extremely/unique). Scan `非常(巨大\|极其\|唯一\|首选)`. |
| 2.4 | Solved users' pain-point problem. | Solved users' pain point / solved the problem. | "痛点" already contains the sense of "problem", creating redundant modification (also hits §5). |
| 2.5 | This method's accuracy is very precise. | This method's accuracy is high / this method is very precise. | "Accuracy" pairs with "high/low"; "method" pairs with "precise". Subject–adjective mismatch. |

---

## 3. Subject switching (hidden subject change)

| # | Original (bad) | Rewritten | How to tell |
|---|----------|--------|----------|
| 3.1 | After the connection pool filled up, the database connection count kept not dropping. | After the connection pool filled up, its connection count kept not dropping. | The previous clause's subject is "connection pool"; the next clause's actual subject becomes "connection count" — the reader misreads. Check: are adjacent clauses' subjects the same entity? |
| 3.2 | We first looked at the flame graph, found 78% of time waiting on I/O. | We first looked at the flame graph, and from it found 78% of time waiting on I/O. | Should the subject of "found" be "we" or "the flame graph"? Add "from it" to disambiguate. |
| 3.3 | This library supports async, but requires you to manage transactions yourself. | This library supports async, but transactions require you to manage them yourself. | The omitted subject before "requires" has become "this library". Restore the real subject. |
| 3.4 | After optimization P99 dropped from 200ms to 62ms, the team decided to roll out fully. | After optimization P99 dropped from 200ms to 62ms; based on this result, the team decided to roll out fully. | Two clauses with no connective and a sudden subject change → add a connective. |

**How to tell (semi-automatic)**: split the sentence on `，；` → extract the **first noun phrase** of each clause as the candidate subject → if two adjacent clauses have different candidate subjects and the latter has no explicit subject → flag as "suspected subject switch" for human confirmation.

---

## 4. Ambiguous reference

| # | Original (bad) | Rewritten | How to tell |
|---|----------|--------|----------|
| 4.1 | We put Redis in front of Postgres; it will crash first under high concurrency. | We put Redis in front of Postgres; the former will crash first under high concurrency. | When ≥2 entities of the same type appear in the sentence, "it" is unrecoverable. Scan "它/其/这个/那个/前者/后者" and count the nouns within the preceding 60 characters. |
| 4.2 | This approach is faster than the last one, but it hasn't been load-tested. | This approach is faster than the last one, but the new one hasn't been load-tested. | "It" could mean the new or the old approach. |
| 4.3 | This problem has little to do with that approach. | That approach helps little with this problem. | Overuse of "该" creates an abstract pile-up where the two "该"s point to different objects. |
| 4.4 | The former is more stable than the latter, which we've verified in our tests. | The former is more stable than the latter, a conclusion we've verified in our tests. | Does "这" refer to the whole sentence or to "the former"? Restore the head noun. |

**How to tell**: count the positions of `它|其|这个|那个|前者|后者|该`; for each, look back 80 characters and count candidate antecedents — ≥2 means flag it. Cross-paragraph references must always be turned back into nouns.

---

## 5. Redundancy

| # | Original (bad) | Rewritten | How to tell |
|---|----------|--------|----------|
| 5.1 | This is a necessary condition we must do. | This is a necessary condition. | "必须" and "必要" repeat. Scan `必须.*必要` `必要.*必须`. |
| 5.2 | About 30ms or so. | About 30ms. / Around 30ms. | "大约" and "左右" are both approximate-number markers. Scan `大约.*左右` `大概.*上下`. |
| 5.3 | Free gift / book ahead / mutual cooperate / triumphant return | Gift / book / cooperate / triumph | Fixed redundancy where the word already contains the sense. |
| 5.4 | This is a very unique and one-of-a-kind approach. | This is a unique approach. | Synonymous coordination (unique / one-of-a-kind) — keep one. Scan for co-occurring synonym pairs. |
| 5.5 | Carried out optimization processing. | Optimized it. | "进行/加以/予以 + disyllabic verb" nominalization clutter. Scan `(进行\|加以\|予以\|给予)(优化\|调整\|分析\|处理\|改进)`. |
| 5.6 | The reason it slowed down is because the index wasn't created. | It slowed down because the index wasn't created. | "之所以…的原因" + "because" double causal marking. Scan `之所以.*原因`. |

---

## 6. Misused classifiers

| # | Original (bad) | Rewritten | How to tell |
|---|----------|--------|----------|
| 6.1 | Three optimization techniques (个) | Three optimization techniques | Noun–classifier mismatch: abstract items use "条/点", concrete objects use "个". |
| 6.2 | A problem of the connection pool filling up | A connection-pool problem | Stacked modifiers push the classifier too far from the head noun; the head should be "problem". |
| 6.3 | This command threw 5 kinds (个种) of errors. | This command threw 5 types of errors. | "个" used together with "种". Scan `\d+\s*个(种\|类\|条\|份)`. |
| 6.4 | Several 4-core servers (们) | Multiple 4-core servers | "们" isn't used for inanimate nouns or with quantity words. Scan `[数量词].*们` and non-human nouns + 们. |

Common collocations (rule-of-thumb table, not exhaustive): approach/technique/suggestion → 个/条; problem/error → 个/类/种; data → 组/份/条; metric → 个/项; server/machine → 台; code → 段/行/份.

---

## 7. de / de / de (的 / 地 / 得)

| # | Original (bad) | Rewritten | How to tell |
|---|----------|--------|----------|
| 7.1 | This approach can quickly (的) locate the problem. | This approach can quickly (地) locate the problem. | "地" + verb/adjective predicate: "quickly" modifies the verb "locate" → use "地". |
| 7.2 | He analyzed very clear (的). | He analyzed very clearly (得). | "得" + complement (degree/result). Verb + 得 + elaboration. |
| 7.3 | This is a doc that detailed (地) explains the principle. | (If emphasizing the action, use 地; if as an attributive, it should be 的.) | See the judgment order below. |
| 7.4 | The problem of the connection pool filling up (地) | The problem of the connection pool filling up (的) | Noun modifier-head structure → "的". |

**Judgment order (as rules, not intuition)**:

1. "X 的 Y": Y is a noun or noun phrase → **的**.
2. "X 地 V": V is a verb/adjective predicate, X is an adverbial → **地**.
3. "V 得 C": C is a complement (degree/result/possibility), with "得" inserted → **得**.
4. Doesn't fit any of the three → hand to a human; don't guess.

Quick scan: if `地` is immediately followed by a nominal tail ("problem/approach/reason/situation", etc.) → likely should be `的`; if `的` is immediately followed by a verb preceded by an adverb (e.g. "quickly detail") → likely should be `地`.

---

## 8. Connectives and two-sided vs one-sided

| # | Original (bad) | Rewritten | How to tell |
|---|----------|--------|----------|
| 8.1 | Although the connection pool was enlarged, however QPS didn't change. | Although the connection pool was enlarged, QPS didn't change. (Keep "but" if you like, but don't stack it with "however".) | Scan `虽然.*然而.*但是` for multiple adversatives. |
| 8.2 | Not only raised throughput, but also lowered latency. | Not only raised throughput, but also lowered latency. | When the two clauses of "不但…而且" share a subject, the subject should precede "不但"; when they differ, place them separately. |
| 8.3 | Whether we can hit 60ms depends on whether the index is built correctly. | Whether we can hit 60ms depends on whether the index can be built correctly. | **Two-sided vs one-sided**: the front "能否" is two-sided, the back "正确" is one-sided. Scan `能否\|是否\|有没有` and check whether the second half has a matching two-sided word. |
| 8.4 | Because we added caching, so the reason latency dropped. | Because we added caching, latency dropped. | "因为…所以" mixed with "…的原因". Scan `因为.*原因`. |

---

## 9. Check-script approach and regex snippets

Only do "candidate location", not automatic rewriting. Suggested check order:

1. **Preprocessing**: strip code blocks (wrapped in ```` ``` ````) and inline code (wrapped in `` ` ``), so content inside code isn't treated as a grammatical error.
2. **Sentence splitting**: split on `。！？；\n` into sentences, preserving original line numbers (compute via cumulative offsets; don't use post-`split` indices as line numbers).
3. **Per-category scan**: one independent function per category, returning `{type, fragment, line, suggestion}`.
4. **Aggregate output**: keep consistent with the `issues` structure in `scripts/editor.py` so the upper layer can consume it directly.

Simple regex snippets you can use (**explicitly: these will false-positive, for location only**):

```python
import re

CANDIDATES = {
    # Prepositional phrase swallowing the subject: 通过/经过/由于 … 使/让/令
    "missing_subject": re.compile(r"(通过|经过|由于)[^。；]{0,30}(使|让|令)"),
    # Redundant approximate numbers
    "approx_dup": re.compile(r"(大约|大概|约)[^。；]{0,15}(左右|上下)"),
    # Nominalization clutter
    "nominalization": re.compile(r"(进行|加以|予以|给予)(优化|调整|分析|处理|改进|讨论)"),
    # "之所以" mixed with "原因"
    "causal_mix": re.compile(r"之所以[^。；]{0,30}原因"),
    # Repeated classifiers
    "classifier_dup": re.compile(r"\d+\s*个(种|类|条|份)"),
    # Two-sided-vs-one-sided leading clue (needs further judgment of the second half)
    "two_vs_one": re.compile(r"(能否|是否|有没有)[^。；]{0,40}"),
    # Anaphora candidates (locate only, don't judge)
    "anaphora": re.compile(r"(它|其|这个|那个|前者|后者|该)"),
}

def scan(text: str):
    for t, pat in CANDIDATES.items():
        for m in pat.finditer(text):
            line = text.count("\n", 0, m.start()) + 1
            yield {"type": t, "fragment": m.group(0), "line": line,
                   "advice": "candidate, needs human confirmation"}
```

**Why no complex assertions**: Chinese has no whitespace tokenization, so the boundaries of subject, predicate, and complement can't be reliably judged by regex; correctness of "地/得" depends on part-of-speech tagging. Rather than writing one long regex that looks clever but both misses and false-flags, the **certain** procedure is "candidates + mandatory human confirmation".

**Output contract**: problem entries merge into the `issues` list in `scripts/editor.py`; `score = 100 - issue_count×5 - long_sentence_count×2` (consistent with the existing implementation) — don't invent a separate scoring scheme.
