# Chinese Article Outline Template Library (5 Templates)

> When to read: when the topic is set and you need to lock the structure. Pick a template first, then fill in content; don't improvise structure while writing.
> The length shares are **rules of thumb** (based on a 2000-character mid-length baseline); short pieces (800) compress "background" and "extension", long pieces (5000) enlarge the "argument/steps" parts.
> The mapping to `scripts/outliner.py --type` is in §1; the script only generates the section-name skeleton, and this file fills in the meat.

## Table of Contents

- [1. Template selection quick reference](#1-template-selection-quick-reference)
- [2. Template A: technical tutorial](#2-template-a-technical-tutorial)
- [3. Template B: opinion / commentary](#3-template-b-opinion--commentary)
- [4. Template C: listicle / roundup](#4-template-c-listicle--roundup)
- [5. Template D: case postmortem](#5-template-d-case-postmortem)
- [6. Template E: review / comparison](#6-template-e-review--comparison)
- [7. Universal validation: outline acceptance criteria](#7-universal-validation-outline-acceptance-criteria)

---

## 1. Template selection quick reference

| Core question you're answering | Pick template | `--type` | Typical carrier |
|--------------------|--------|----------|----------|
| "How do I do it?" | A technical tutorial | `tutorial` | CSDN, Juejin, WeChat Official Account |
| "What do I think? Why?" | B opinion / commentary | `opinion` | Zhihu, WeChat Official Account |
| "What's out there? Which fits me?" | C listicle / roundup | `listicle` | WeChat Official Account, Xiaohongshu, CSDN |
| "What happened? What did we learn?" | D case postmortem | `blog` | Zhihu, WeChat Official Account, Bilibili scripts |
| "Which is better, A or B?" | E review / comparison | `technical` | Juejin, CSDN, Bilibili |

How to judge: extract the question word from the title — "how to" → A; "should I / is it really" → B; "which ones / how many" → C; "why did it fail / how to recover" → D; "vs / or / compare" → E. If the title has no question word → add a question word first; the topic hasn't converged yet.

---

## 2. Template A: technical tutorial

**Fits**: hand-holding teaching of a reproducible result (install, configure, run, verify).

| Section | Purpose | Share of length | Required elements |
|------|------|----------|----------|
| Result up front | Give the end state first, so readers know what they'll walk away with | 5% | One verifiable result (number / screenshot) |
| Prerequisites | Intercept people who can't run it | 5% | Version numbers, OS, dependencies, time needed |
| Steps 1..N | The body, one step per section | 60% | Per step: command + expected output + failure branch |
| Verification | Prove you did it right | 10% | A copy-pasteable verification command and the criterion |
| Common pitfalls | Intercept early | 15% | ≥3 "symptom → cause → fix" |
| FAQ / next steps | Wrap up | 5% | 3 high-frequency follow-up questions |

**Filled-in example**: "Using asyncpg to drop FastAPI's P99 from 200ms to 60ms"

- Result up front (100 chars): 4-core 8G, Postgres 15, read-only endpoint P99 200ms → 62ms, 3 changes.
- Prerequisites (100 chars): Python 3.11+, FastAPI 0.110+, PostgreSQL 14+; about 20 minutes total.
- Step 1: swap `psycopg2` for `asyncpg` (including `pip install` and the `create_async_engine` change)
- Step 2: build a composite index on `where user_id` (including the `CREATE INDEX` statement and before/after `EXPLAIN` comparison)
- Step 3: connection pool `pool_size=20, max_overflow=10` (including why bigger isn't better)
- Verification (200 chars): `locust -u 200 -r 20` for 3 minutes; give the P50/P99 table
- Common pitfalls (300 chars): 1) mixing `async def` with a sync ORM session blocks the event loop; 2) index built but the query uses `OR`; 3) load-test machine colocated with the server skews the data
- FAQ (100 chars): works with SQLAlchemy 2.0? / need to change business code? / should read-write splitting be done at the same time?

---

## 3. Template B: opinion / commentary

**Fits**: passing judgment on a phenomenon / technical route; needs to persuade, not teach.

| Section | Purpose | Share of length | Required elements |
|------|------|----------|----------|
| The target | Name the popular view you're rebutting/revising | 10% | One-sentence quote, ideally with a source |
| Thesis | Your judgment, falsifiable | 5% | "I believe X because Y" in one sentence |
| Arguments 1..3 | Each an independent pillar | 45% | Each = data/case + reasoning |
| Opponent's strongest view | Proactively build the straw man | 20% | Use their strongest version, not a straw man |
| Response and boundary | Concede + qualify | 15% | "Under __ conditions, my judgment doesn't hold" |
| Conclusion | Wrap up | 5% | Callback to the thesis; no new evidence |

**Filled-in example**: ""If AI writes code, it should generate everything" is a dangerous misreading"

- The target (200 chars): the recent common claim that "the model can write a whole module in one shot, and humans just review."
- Thesis (100 chars): in **teams with an existing codebase**, full generation has a negative net benefit; in greenfield projects, it's positive.
- Argument 1 (300 chars): interface-consistency cost — the conflict rate between generated code and existing conventions (a self-run count of 30 PRs, with the counting method attached)
- Argument 2 (300 chars): review-cost transfer — a person reading 800 lines of unfamiliar code is slower than writing 200
- Argument 3 (300 chars): regression risk — paths your test coverage doesn't reach
- Opponent's strongest view (400 chars): generation is indeed 3–5× faster, and new projects carry no historical baggage; I accept that point
- Response and boundary (300 chars): give the dividing line — codebase size, whether there's a type system, whether there are tests
- Conclusion (100 chars): split strategy by size, don't take sides by camp

---

## 4. Template C: listicle / roundup

**Fits**: a set of parallel items (tools, tips, resources, mistakes).

| Section | Purpose | Share of length | Required elements |
|------|------|----------|----------|
| Intro + inclusion criteria | Explain why these N items made the cut | 10% | Verifiable screening conditions |
| Items 1..N | The parallel body | 70% | Per item: what it is / who it's for / one concrete use / the pitfall |
| Quick-pick table | Help the reader decide | 10% | 2D table: item × applicable scenario |
| How to choose | Decision path | 5% | 3-step selection method |
| Closing | Guidance | 5% | CTA |

**Hard structural constraint**: items must be **same-dimension** (all tools or all tips); mixing granularities is forbidden; each item's length must differ by ≤30%, or readers will assume the ordering is the weighting.

**Filled-in example**: "6 tools for troubleshooting a CPU-pinned Python service"

- Intro (200 chars): inclusion criteria — no code change to integrate, usable in a production read-only environment, actively maintained
- Items: `py-spy` (sampling, no intrusion) / `cProfile` (stdlib, function-level) / `flamegraph` (visualization) / `perf` (system-level) / `Scalene` (separates Python vs native) / `austin` (low overhead)
- Each ~230 chars: one-line positioning + minimal usable command + what the output looks like + one pitfall
- Quick-pick table (200 chars): tool × "production-safe? / needs restart? / granularity / overhead"
- How to choose (100 chars): first see if it's production-safe → then whether it needs a restart → finally the granularity
- Closing (100 chars): CTA

---

## 5. Template D: case postmortem

**Fits**: outages, incidents, project retrospectives; the focus is "why" and "what to do next time".

| Section | Purpose | Share of length | Required elements |
|------|------|----------|----------|
| Timeline | Objective reconstruction | 20% | Minute-level event sequence (table) |
| Blast radius | Damage assessment | 10% | Affected users / duration / amount, or explicitly write "no external impact" |
| Root cause | Technical layer | 20% | One chain: trigger → direct cause → root cause |
| Why we didn't catch it earlier | Process/monitoring layer | 20% | Monitoring blind spots, alert thresholds, release process |
| What we did | Actions taken | 10% | Each step + effect + whether rolled back |
| Action items | Trackable | 15% | Itemized, with owner and deadline (can be redacted) |
| Reusable conclusion | Abstracted out | 5% | One sentence others can apply |

**Banned**: writing the retrospective as a praise piece (devoting space to "the team responded quickly") or as a running log (only a timeline with no root cause).

**Filled-in example**: "An endpoint avalanche triggered by a saturated connection pool"

- Timeline (400 chars): `03:12` first alert → `03:15` P99 breaks 5s → `03:22` decide to scale out (ineffective) → `03:40` locate the connection count → `03:47` rate limiting restores service
- Blast radius (200 chars): ordering endpoint down 35 minutes, affecting N orders (redacted: `about X%` + method note)
- Root cause (400 chars): slow query (trigger) → longer connection hold time (direct) → connection-pool cap of 200 saturated with no timeout recycling (root)
- Why we didn't catch it earlier (400 chars): only monitored CPU, not connection-pool utilization; alert threshold P99>1s, never triggered during the slow-query period
- What we did (200 chars): why scaling out didn't help (connections grew linearly with instances, pushing pressure to the DB)
- Action items (300 chars): 5 items, with metric, threshold, owner
- Reusable conclusion (100 chars): "for connection-pool outages, scaling out is a negative optimization; rate-limit first, then check hold time"

---

## 6. Template E: review / comparison

**Fits**: A vs B (frameworks, approaches, models, tools).

| Section | Purpose | Share of length | Required elements |
|------|------|----------|----------|
| Conclusion up front | Give the verdict first | 5% | "Pick A in scenario X, pick B in scenario Y" |
| Evaluation design | Build credibility | 15% | Environment (version/hardware), dataset, metric definitions, why tested this way |
| Dimension 1..N comparison | The body | 45% | Per dimension: data + table/chart + one-line interpretation |
| Scenario-based recommendation | Land on decisions | 20% | Advice by reader type (startup/big corp/individual/…) |
| Limitations and untested items | Honest boundaries | 10% | Explicitly state what wasn't tested and the conclusion's scope |
| Conclusion | Callback | 5% | Same as the opening; no new conclusions |

**Filled-in example**: "FastAPI vs Flask: a live comparison on a 4-core container"

- Conclusion up front (100 chars): want async and auto-docs → FastAPI; want ecosystem plugins and lower sync mental load → Flask
- Evaluation design (300 chars): Python 3.11 / 4-core 8G / `wrk -t4 -c200 -d60s` / three endpoint types (pure compute, DB read, JSON serialization) / 3 runs each, take the median; explain why not hello world
- Dimension comparison (900 chars): throughput, P99 latency, cold start, ecosystem plugin count, type hints and docs, learning curve — a table per dimension
- Scenario recommendation (400 chars): internal tools / high-concurrency API / teaching / migrating legacy projects
- Limitations (200 chars): didn't test WebSocket long connections; didn't test ORM-layer differences; single hardware
- Conclusion (100 chars)

---

## 7. Universal validation: outline acceptance criteria

After the outline is written, check each item; if any fails, rework:

- [ ] The title contains a concrete object and verifiable information (number/scenario/qualifier), not "XX getting started"
- [ ] Section count is between 3–7; beyond that, merge like items
- [ ] Every h2 can be rewritten as a single **assertion** (not "what is X" / "overview")
- [ ] Each section has 2–5 `points`; fewer than 2 means the section should merge, more than 5 means it should split
- [ ] Sum of each section's `word_count_target` = `total_words_target` (±10%)
- [ ] The body (argument/steps/items) is ≥55%, background buildup ≤15%
- [ ] The `hook` is within 2 sentences and matches the title's promise
- [ ] The `conclusion` states a concrete CTA, not "summarize the whole piece"
- [ ] Opponent/limitations/boundaries are at least 10% (mandatory for templates B/D/E; template A uses "common pitfalls" instead)

If the target platform is multi (`platforms` field), make **only one outline**, scaling `word_count_target` by platform: short-form platforms take 40% of the long-form version, keeping only the "conclusion up front" and "quick-pick table" modules; the rest can be cut.
