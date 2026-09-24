# A Systematic Method for Identifying Research Gaps

> When to read: read this file "after you've settled the broad direction but before you've locked the specific topic". Submission matching is in the sibling file venue-matching.md (loaded together by SKILL.md).
> **This file provides no literature-database API details and no search-volume numbers.** The search portals (arXiv / ACL Anthology / IEEE Xplore / Google Scholar / DBLP / PubMed / CNKI, etc.) and search syntax change; confirm them yourself before use. Below we only cover **method**.
> Core warning: **"I didn't find it" does not mean "it doesn't exist."** Every gap conclusion must go through the §5 counter-evidence search before being written into a proposal.

## Table of Contents

- [1. Contract with topic_selector.py](#1-contract-with-topic_selectorpy)
- [2. Method A: literature matrix](#2-method-a-literature-matrix)
- [3. Method B: contradiction spotting](#3-method-b-contradiction-spotting)
- [4. Method C: method transfer](#4-method-c-method-transfer)
- [5. Method D: boundary-condition method](#5-method-d-boundary-condition-method)
- [6. Method E: mining future work](#6-method-e-mining-future-work)
- [7. Literature matrix template and how to read it](#7-literature-matrix-template-and-how-to-read-it)
- [8. Gap validity check (counter-evidence)](#8-gap-validity-check-counter-evidence)
- [9. Execution checklist](#9-execution-checklist)

---

## 1. Contract with topic_selector.py

`scripts/topic_selector.py` only does **keyword heuristic scoring** (`novelty` is triggered by words like `first/novel/unexplored/without/zero-shot`; `feasibility` is penalized by words like `large/multi/distributed/real-time/end-to-end`), and its output explicitly states:

```text
"next": "Run lit-review to verify gap exists"
```

In other words: **the script gives hypotheses to verify, not conclusions.** This file handles that verification step.

| Script output field | Which step of this file lands it |
|--------------|------------------------|
| `novelty` | §2–§6 finds a gap → §8 counter-evidence → backfill |
| `feasibility` | Read off the "data/compute/code" column in the §7 matrix |
| `impact` | Look at whether anyone cites that dimension in the matrix, and whether there's a benchmark |
| `recommendation: risky` | Return to §8 to check whether it's "truly infeasible" or just "I didn't find the baseline" |

---

## 2. Method A: literature matrix

**Idea**: lay N papers in the same subfield out as a table across **fixed dimensions**; the blank cells are candidate gaps.

**Approach:**

1. Search the same database with 2–3 different query sets (synonyms/hypernyms-hyponyms/English and Chinese), then do **citation snowballing** (forward citations + backward references) on highly relevant papers.
2. Take 10–25 highly relevant papers (mostly from the last 3–5 years, plus 2–3 foundational older papers).
3. Fill in the table paper by paper using the columns in §7. **Every cell must be filled with a basis from the original text; don't fill from impression.**
4. Read the table: look for **blank columns** (dimensions nobody has done) and **mode columns** (everyone does it this way; a different approach may be a gap).

**Output**: one filled matrix + 3–5 candidate gaps.

**Failure branches**:

- Can't fill the table (many cells are "?") → you haven't read the papers closely enough; go back and read the Method and Limitation sections; don't infer from the abstract.
- Fewer than 10 papers → the subfield may be too narrow or known by a different term; broaden the queries. If broadening to 3 query sets still gives fewer than 10, record it as "sparse literature in this subfield" — this could be a gap or a **no-man's-land (no value)**, and it must go through §8.

---

## 3. Method B: contradiction spotting

**Idea**: when similar studies give **mutually conflicting** conclusions, the conflict itself is the gap.

**Approach:**

1. Add a dedicated "core conclusion" column to the matrix.
2. Find two groups of papers with opposite conclusion directions (e.g. A says method X works on small models; B says it doesn't work at the same scale).
3. Compare their **differing variables** one by one: dataset, model size, metric definitions, prompt/hyperparameters, whether the code implementation is the same.
4. If the differing variables can't explain the conflict → it's a real gap (e.g. "X's effectiveness depends on __, a dependency not systematically studied before").

**Output shape (a directly usable gap statement)**:

> "Existing work gives opposite conclusions on X's effect under condition Y (A 2024 vs B 2025); the two differ on __, which was not controlled. We reproduce under a unified setup and give the boundary conditions."

**Note**: contradictions must be **checked line by line against the experimental setup**, not just the abstract's conclusion sentence — many "contradictions" are actually different evaluation protocols, which is a lower-value "evaluation standardization" gap, not a real contradiction.

---

## 4. Method C: method transfer

**Idea**: take a mature method from field A and apply it where field B hasn't used it.

**Approach:**

1. List field B's current mainstream methods (read from the matrix's "method" column).
2. List field A's mature methods (from your knowledge of neighboring fields, or read 1–2 A-field surveys).
3. Cross: **A's methods × B's problems**, and ask for each "why hasn't B used it?"
   - If the answer is "nobody tried" → candidate gap (but the value depends on whether there's reason to believe it would work better, see below).
   - If the answer is "tried, but there's a fundamental obstacle (data shape mismatch / assumption doesn't hold / unacceptable complexity)" → give up, or research "how to overcome the obstacle".
4. **Must answer "on what basis do you believe the transfer works"**: give a mechanistic reason (e.g. the B problem's structure is equivalent to some formalization in A); otherwise it's just brute-force method-applying, and reviewers will ask "why this method?"

**Output shape**:

> "Method X is widely used for __ in field A, but the __ task in field B has an isomorphic __ structure. We introduce X to B for the first time and adapt Y for the __ difference."

---

## 5. Method D: boundary-condition method

**Idea**: the **applicable range** of an existing conclusion hasn't been characterized.

**Approach:**

1. Find a widely cited conclusion (e.g. "method X beats the baseline").
2. List its implicit premises: data scale, language/domain, model size, task type, annotation volume, latency budget, distribution shift.
3. Pick one premise and ask "what happens when the premise doesn't hold?"
4. If the original paper only validated under a single setup, and that premise often doesn't hold in practice → gap.

**Output shape**:

> "X's effectiveness has only been validated under __ setup. We systematically evaluate under __ (a more realistic setup), find __, and give the applicability boundary of __."

**Why this kind of gap is easy to do**: no need to propose a brand-new method, the experiment design is clear, and it's easy to write the contribution clearly; and it has clear value to reviewers (preventing community misuse). **But** avoid being judged "insufficiently incremental" — you need a **mechanism explanation** or an **operational criterion**, not just "we tested it and it doesn't work."

---

## 6. Method E: mining future work

**Idea**: the future-work sections of surveys and highly cited papers are **public gap lists**, but also the most competitive spot.

**Approach:**

1. Find 3–5 related **surveys** from the last 2 years; read the future work / open challenges sections closely.
2. Copy each future-work item into a table, noting: proposed when, by whom, and whether it's been done already (verify by searching again).
3. **Key action**: for each future-work item, run a targeted "has it been solved?" search (using the sentence's core words + last 1 year + preprint servers).
4. For items still open: assess feasibility (is data/compute/baseline code available?).

**Risks and countermeasures**:

- Risk: everyone reads the same surveys → high collision; and some future work goes undone because it's **hard or worthless**.
- Countermeasure: prefer items that ① are independently mentioned by multiple surveys, but ② have **no clear technical roadmap** (meaning everyone knows it matters but not how; if you can give the roadmap, that's a contribution).

**Output shape**: `{future-work original quote, source+year, query, already solved? (evidence), my entry point}`.

---

## 7. Literature matrix template and how to read it

Copy and use (fill each cell with an original-text basis; if unsure, write `?` and go back to the source to verify):

| Paper (author+year+venue) | Task/problem | Method | Data/scale | Metrics | Core conclusion | Declared limitations | Open-sourced? | Uncovered dimensions |
|---|---|---|---|---|---|---|---|---|
| A et al. 2024, ACL | Multi-agent negotiation | Role prompts + voting | Self-built 500 cases | Success rate | Voting beats single-agent | English only, 3 agents only | Yes | No shared-memory setting |
| B et al. 2025, arXiv | Multi-agent collaboration | Shared blackboard | AgentBench | Task completion | Blackboard mechanism works | Assumes shared context | No | Zero-sharing setting |

**How to read it (in order)**:

1. **Read a row across**: what didn't this paper do? (→ the "declared limitations" column)
2. **Read a column down**: does every paper look the same on this dimension? (→ the mode is the blind spot; e.g. all tested English only → multilingual is a gap)
3. **Find blanks**: a cell in a paper is empty / `?` → that paper didn't evaluate on that dimension (could be your reproduction-and-fill-in opportunity)
4. **Find conflicts**: rows with opposite conclusion directions → go to §3
5. **Look at "open-sourced?"**: none open → **reproduction and the benchmark itself is the contribution** (but first confirm the community actually needs this benchmark)
6. **Look at time**: have new papers suddenly increased in the last 12 months → the area is heating up (early entry vs already red ocean; judge yourself; this file gives no heat data)

---

## 8. Gap validity check (counter-evidence)

After finding a candidate gap, **first try to falsify it**. If any check below fails, don't write it into `ranked_topics`:

| Check | How | Failure handling |
|------|------|--------------|
| Existence counter-evidence | Swap in 3 query sets (synonyms/hypernyms-hyponyms/abbreviations), swap 1 database, check the last 12 months of **preprints** (arXiv, etc. — many gaps have been scooped but not formally published) | Found similar work → demote or pivot to the sub-dimension it doesn't cover |
| No-value hypothesis | Ask "if done, who would cite it? On what problem is it a necessary step?" | Can't answer → suspected no-man's-land; give up |
| Infeasibility hypothesis | Ask "is it undone because of missing data / compute / unfalsifiability?" | If yes and you also can't solve it → give up; if you can solve it, write "how to solve it" as one of the contributions |
| Falsifiability | The gap statement must be decidable as true/false by experiment | Can't → rewrite it into a measurable form |
| Entry-point uniqueness | Is your angle just "a different dataset" from existing work? | If yes → add a mechanism explanation or method improvement; otherwise judge it insufficiently incremental |
| Resource check | Are data, compute, baseline code, and evaluation scripts all available? | Missing one → record it as a `feasibility` deduction and write it into constraints |

The script's `rejected` list must state the rejection reason clearly (e.g. `Already covered by X et al. 2025 — query: ..., search date: ...`), so it can be reviewed later.

---

## 9. Execution checklist

- [ ] At least 3 query sets + citation snowballing, covering the last 3–5 years (including preprints)
- [ ] Literature matrix ≥10 papers, every cell has an original-text basis, nothing filled from impression
- [ ] Used at least 2 gap-finding methods (don't rely only on future work)
- [ ] Every candidate gap passed the 6 counter-evidence checks in §8, with query sets and search dates recorded
- [ ] The gap statement is falsifiable, stating "under what conditions, with what metrics, judged true/false"
- [ ] Confirmed data/compute/baseline-code availability, reflected in `feasibility`
- [ ] Every `ranked_topics` entry fills in the three fields `gap` / `baseline` / `contribution_angle`
- [ ] The `rejected` list is non-empty (showing you really screened, not just kept everything you thought of)
- [ ] Explicitly recorded "the coverage boundary of this round of searching" (which databases, cutoff date, which terms weren't searched) — this step determines whether your conclusions can be reproduced later
