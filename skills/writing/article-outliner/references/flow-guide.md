# Article Logic-Flow Design Guide

> When to read: read this file when the outline's **section order and transitions** are settled and you need to check "does it read smoothly".
> This file handles "structure", not sentence patterns and word choice (those belong to `article-drafter` and `content-editor`).
> All numbers are rules of thumb, not platform rules.

## Table of Contents

- [1. Cognitive load allocation](#1-cognitive-load-allocation)
- [2. Information order: conclusion-first vs suspense buildup](#2-information-order-conclusion-first-vs-suspense-buildup)
- [3. Inter-section relation labeling](#3-inter-section-relation-labeling)
- [4. Transition-sentence library](#4-transition-sentence-library)
- [5. Common logic gaps: recognition and repair](#5-common-logic-gaps-recognition-and-repair)
- [6. Flow checklist](#6-flow-checklist)

---

## 1. Cognitive load allocation

Readers have limited working memory: the more new concepts floating in one paragraph at once, the higher the bounce rate.

| Metric | Cap (rule of thumb) | Over-cap action |
|------|----------------|----------|
| New terms introduced per 500 chars | ≤ 3 | Split into two sections, or demote one to a footnote/parenthetical |
| Consecutive abstract paragraphs without examples | ≤ 2 | The 3rd must give a concrete example or number |
| Span of a single example | ≤ 15 lines | Split steps, or pull it into its own subsection |
| Position of the peak (information-density climax) | 40%–70% of the piece | If the peak is in the first 20%, the rest is filler; if in the last 90%, the buildup is too long |

**Three load-allocation principles**:

1. **Define before use**: when a term first appears, give a plain-language explanation in the same or next sentence; forbids "use a word first, explain it in section 3".
2. **Front-load the peak**: put the hardest section where the reader still has patience (about 1/3–1/2 through), don't pile the substance at the end.
3. **One job per paragraph**: a paragraph = one claim + its evidence. If a second "therefore/so" appears in a paragraph, split it.

**Mechanical check**: label each section with "new-term count / abstract-paragraph count / has examples?", forming a table like the one below; one glance shows whether load is concentrated in one spot.

| Section | Chars | New terms | Consecutive abstract paras | Has examples |
|----|------|----------|-----------|--------|
| 1 | 300 | 2 | 2 | Yes |
| 2 | 800 | 5 | 4 | No | ← Exceeds two limits; needs split + add examples |

---

## 2. Information order: conclusion-first vs suspense buildup

It's not a style preference; it's determined by the **reader's situation**. Choose per the table; don't go by feel.

| Dimension | Conclusion-first (BLUF) | Suspense buildup |
|------|------------------|----------|
| Who is the reader | Decision-makers, people debugging, people arriving from search | People here to be entertained / drawn in by the title |
| Reader's situation | Time pressure, may leave at any moment | Already decided to read to the end |
| Content type | Technical tutorials, reviews, postmortems, news | Narratives, opinion long-form, case stories |
| Carrier | CSDN / Juejin / search-traffic-heavy pages | WeChat Official Account / Zhihu home recommendation feed |
| Failure cost | Reader leaves without a conclusion in the first 3 screens | Spoiling it early means nobody reads on |
| Opening shape | "The conclusion is X; here's why" | Scenario/conflict → "why is this happening?" |

**Hybrid use (recommended)**: conclusion-first gives the **direction**; suspense holds the **details**.

> "Connection-pool config was the root cause of this avalanche — but why did scaling up make it worse? It starts with a counterintuitive load-test result."

This sentence satisfies both: the search reader gets the conclusion, and the recommendation-fed reader gets the hook.

**How to judge**: ask "if the reader arrived from a search results page, would they get what they want within 3 screens?" Yes → conclusion-first; no but they're willing to read on → suspense buildup.

---

## 3. Inter-section relation labeling

After the outline is finalized, **force-label** one relation between every pair of adjacent sections. Adjacent sections you can't label = a logic gap; either add a transition or reorder.

| Relation | Meaning | Test question |
|------|------|----------|
| Progressive | The next section deepens the previous | "After reading the previous section, what will the reader naturally ask?" → does the next section answer it? |
| Adversative | The next section revises/limits the previous | Is there an explicit transition word (but/however/of course/though)? |
| Parallel | Same-dimension enumeration | Can the two swap order without affecting understanding? Yes → true parallel; no → there's a hidden dependency; relabel as progressive |
| Causal | Previous section is the cause, next is the effect (or the reverse: claim-evidence) | Remove the previous section; does the next section's argument fall apart? |
| Example | The next section instantiates the previous | Does the example really correspond to the previous claim (not a topic change)? |
| Problem-solution | Previous section raises the problem, next gives the solution | Does the solution address each point listed in the problem? |

**Approach:** add a non-standard field `link_to_prev` to each section in the outline JSON (values: `progressive/adversative/parallel/causal/example/problem-solution`), so both model and human can check it mechanically.

---

## 4. Transition-sentence library

Put transitions either at the **end of a section** (leading into the next) or the **start** of a section (picking up from the previous); pick one and be consistent throughout. Each is a fill-in-the-blank template.

| Type | End-of-section transition (leads to next) | Section-start transition (picks up previous) |
|------|----------------------|----------------------|
| Progressive | "But stopping here isn't enough; __ is the key." | "Now that we know __, the next step is __." |
| Adversative | "Of course, this approach breaks down in __ scenarios." | "The conclusion above has a premise: __. What if we remove it?" |
| Causal | "The reason is below." | "So the question becomes: why does __ happen?" |
| Parallel | "That's only the first of three problem classes." | "The second problem class is just as common: __." |
| Example | "Here's a concrete one." | "Take a real scenario: __." |
| Problem-solution | "First, where's the problem?" | "The problem is clear; how do we fix it?" |
| Wrap-up | "Let's pause here and recap three points: __." | "Of the three above, only #__ is worth doing now." |

**Banned transitions**: `next let's look at` (no information), `now to the main topic` (implies what came before was filler), `besides` (doesn't state the relation), `meanwhile` (masks the real causal/adversative).

---

## 5. Common logic gaps: recognition and repair

| Gap type | Typical look | How to spot | Repair action |
|----------|----------|----------|----------|
| Leaping argument | "A, therefore C" (missing B in the middle) | Pull out the two sentences around "therefore" and read them alone; ask "on what basis?" If you can't answer | Supply B with evidence; if you can't, delete "therefore" and demote to parallel |
| Circular argument | "X works because X brings Y; Y matters because X works" | Swap conclusion and premise; the sentence still holds | Introduce evidence independent of the conclusion (external data / experiment) |
| Irrelevant digression | A third of a section is unrelated to its heading | Ask per paragraph "if I delete this, does the section's conclusion change?" Not → irrelevant | Delete, or move it to the section it actually belongs to |
| Straw man | Rebuttal targets a weak version nobody holds | Check whether the quoted view has a source | Restate the opponent's strongest version, then rebut |
| False causality | "After using A, the metric improved, so A works" | Ask "what else changed in the same period?" | Add a control / add a timeline / downgrade wording to "correlates" |
| Granularity jump | Previous section on architecture, next suddenly on one line of code | Check whether the two sections are at the same abstraction level | Insert a middle layer (module-level explanation) or reorder |
| Referential drift | "It" means the framework in the previous sentence, the database in the next | Highlight all pronouns; manually resolve each reference | Swap back to nouns; always use nouns for long-distance references |
| Conclusion drift | The ending conclusion isn't the same thing as the opening promise | Read the title, opening claim, and ending conclusion side by side | Rewrite the ending callback, or rewrite the title (don't rewrite the opening) |

**Repair priority**: conclusion drift > circular argument > leaping argument > granularity jump > irrelevant digression > referential drift. The first three are "the article doesn't hold" and must be fixed; the last three affect readability.

---

## 6. Flow checklist

After the outline or first draft is done, tick each item:

- [ ] Every pair of adjacent sections has a `link_to_prev`; no adjacent pair is "unlabelable"
- [ ] ≤3 new terms per 500 chars, and each term has an explanation on first occurrence
- [ ] No 3 consecutive abstract paragraphs without examples
- [ ] The information-density peak falls in the 40%–70% range of the piece
- [ ] The opening strategy (conclusion-first / suspense / hybrid) is chosen by reader situation, not written by feel
- [ ] All transitions come from the §4 templates or equivalent expressions; no "next let's look at"
- [ ] All "therefore/so/from this we see" pass the "on what basis?" test
- [ ] All "it/this/the former" references resolve uniquely
- [ ] Title, opening claim, and ending conclusion read side by side as pointing to the same thing
- [ ] Delete any one section; does the article still hold? If yes → that section is an irrelevant digression; delete it
