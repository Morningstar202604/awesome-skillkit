# Topic–Venue Matching Decisions

> When to read: read this file when you have candidate topics and need to decide **where to submit**. How to find a gap is in the sibling file gap-finding.md (loaded together by SKILL.md).
>
> ## Hard constraints (do not violate)
>
> **This file provides no specific numbers for any journal's impact factor (IF), CiteScore, quartile, acceptance rate, or review cycle.**
> Reason: these values change yearly, sources disagree on methodology, and writing a "plausible-looking" number from memory is the most serious error this kind of document can make — **writing a fake IF is worse than writing none.**
> When you need these data, always follow the §3 verification process to check official / authoritative sources, and record the **query date + source** together.

## Table of Contents

- [1. Matching dimensions table](#1-matching-dimensions-table)
- [2. Decision workflow](#2-decision-workflow)
- [3. How to verify the latest scope (don't rely on memory)](#3-how-to-verify-the-latest-scope-dont-rely-on-memory)
- [4. Common mismatches and how to avoid them](#4-common-mismatches-and-how-to-avoid-them)
- [5. Matching scorecard template](#5-matching-scorecard-template)
- [6. Choosing between journal vs conference vs workshop](#6-choosing-between-journal-vs-conference-vs-workshop)
- [7. Checklist](#7-checklist)

---

## 1. Matching dimensions table

| Dimension | What to look up | Where to look (official / verifiable source) | How to handle numeric info |
|------|----------|--------------------------|--------------------|
| Scope | What topics the venue accepts and rejects | Journal site **Aims & Scope** page; conference site **Call for Papers** | No numbers; record only three judgments: "explicitly includes / explicitly excludes / not mentioned" |
| Method preference | Empirical / theoretical / systems / applied | Papers actually published by the venue in the last 2 years (look at the Method section), not the site's self-description | Qualitative description |
| Impact level | IF / CiteScore / quartile / acceptance rate | Journal site, authoritative citation databases, statistics published on the conference site | **Look it up on demand only**, writing "source + query date" into your notes; do not write it into this file |
| Review cycle | Whether there's a fixed deadline, time from submission to first decision | Conference site **Important Dates** page (abstract/full paper/notification); journal site's "time to first decision" field (if published) | Defer to the site's published value; if not published, record as `undisclosed`, ask mentors/colleagues by experience, and don't hard-code a number |
| Format requirements | Page count, template, anonymity, appendix policy, word count | Site **Author Guidelines / Instructions for Authors / Submission Template** | Copy the official page count directly; this is one of the few hard numbers you can be sure of, but re-check it every time (templates change) |
| Length and genre | Long / short / short paper / extended abstract / demo | Same as above + CFP | Same as above |
| Publishing model | Subscription / open access (OA) / APC and amount | Site APC page | Amounts defer to the site; don't rely on memory |
| Double-blind policy | Double-blind? arXiv preprints allowed? | Site submission policy / FAQ | Qualitative |
| Ethics and data requirements | Data/code availability statement needed? ethics review? | Site author guidelines | Qualitative |
| Credibility | Indexed by authoritative indexes? suspected predatory venue? | Authoritative index directories, DOAJ, Think. Check. Submit. self-check list | Qualitative; if unsure, don't submit |

---

## 2. Decision workflow

| Step | Action | Expected result | Failure branch |
|----|------|----------|----------|
| 1 | Take the one-sentence contribution of the topic from `ranked_topics` and extract **three keywords + one method type** | Get a "topic triple + method type" | Can't extract → the topic isn't specific enough; go back to `gap-finding.md` §8 |
| 2 | Use these three words to search the **recent papers list on candidate venue sites** (not where you personally want to submit) | Find 2–5 venues that have published highly related papers in the last 2 years | 0 → the topic may belong to another community; **change keywords or communities**, don't force a submission |
| 3 | Open each candidate venue's **Aims & Scope / CFP** and compare sentence by sentence | One "explicitly includes/excludes/not mentioned" judgment per venue | All "explicitly excludes" → back to step 2 |
| 4 | Look at the **method-type distribution** of the venue's last-2-year papers (empirical/theoretical/systems/applied shares; qualitative is fine) | Judge whether your method is mainstream there | Your method type is a minority with no precedent → high risk; see §4 |
| 5 | Check hard constraints: page count / template / anonymity policy / DDL or rolling | Get an actionable checklist | Missed the DDL → wait for the next edition or switch to a rolling journal |
| 6 | Check impact and cycle (**look it up on demand, record source and date**) | Get a ranking basis | Can't find → record as `undisclosed`; rank by "scope fit" first |
| 7 | Produce 3 tiers: reach / main / safe | One venue per tier, each with reasons and risks | Only 1 option → the backup pool is too small; go back to step 2 and expand |

**Ranking principle**: scope fit > method-type fit > cycle and DDL feasibility > impact level. **If the scope doesn't fit, no matter how high you aim it will be desk-rejected** — this is the most common newcomer mistake.

---

## 3. How to verify the latest scope (don't rely on memory)

Scopes change (journals change editors, conferences add tracks, new special issues appear). Verification order below; **do at least the first three**:

1. **Official Aims & Scope page** (journal) / **Call for Papers** (conference): read sentence by sentence, paying special attention to the **exclusions** (many journals explicitly state "we don't accept pure engineering implementation reports" or "we don't accept empirical studies with no theoretical contribution").
2. **The list of actually accepted papers in the last 2 years (preferably last 1)**: "Articles in press" / "Latest articles" on the site, or the proceedings (ACL Anthology, IEEE Xplore, DBLP, etc.). **What they actually published is more reliable than what they say** — the self-description is often broad; the actual acceptance criteria are narrower.
3. **Editorial board composition**: the editors' research directions can reverse-engineer the venue's taste boundary.
4. **Special Issue / Track CFP**: if you work a cross-cutting area, a special issue is often easier to hit than the main track, with an explicit scope statement.
5. **Author Guidelines**: confirm page count, template, anonymity, and whether a code/data availability statement is required.
6. **Impact and cycle data**: journal site (if published), authoritative citation databases, the conference site's statistics page. **When querying, record: source + query date.** This file gives no specific numbers; fill them in yourself.

**Record template** (keep in your notes; don't write back to this repo):

```text
Venue: <name>
Verification date: YYYY-MM-DD
Key sentence from Aims & Scope: "..."
Exclusions: "..."
3 related papers from the last 2 years: [title+year]
Method-type distribution (qualitative): empirical-heavy / theoretical-heavy / systems-heavy / mixed
Page count and template: <from Author Guidelines>
Anonymity policy: double-blind / single-blind / non-blind
Impact and cycle: <source: ...; query date: ...; value: ...>
Conclusion: reach / main / safe / unsuitable (reason)
```

---

## 4. Common mismatches and how to avoid them

| Mismatch type | Symptom | Typical reviewer/editor comment | Avoidance action |
|----------|------|----------------------|----------|
| Scope mismatch | The topic only tangentially touches the venue's scope | "out of scope" / "better suited to an XX-type venue" → often a **desk reject** | Before submitting, find **at least one sentence** in Aims & Scope that covers your topic; if you can't, switch venues |
| Method too engineering-heavy | Submitting to a theoretical/algorithmic venue, but the contribution is "we built a system" | "Lacks generality" / "engineering report, not a research contribution" | Add generalizable experimental conclusions / design principles / ablation analysis; or switch to a systems/applied venue or a demo track |
| Method too theoretical | Submitting to a systems/applied venue, but the whole piece is formalization with no experiments | "Not validated in a real setting" / "insufficient practical value" | Add experiments on real load / real data; or switch to a theoretical venue |
| Insufficient increment | Just rerunning on a different dataset / model | "incremental" / "novelty limited" | Go through `gap-finding.md` §4/§5 and give a mechanism explanation or boundary conditions |
| Scale mismatch | Wrote a long paper in a short-paper size, or vice versa | "Exceeds length limit" / "insufficient detail to reproduce" | Choose the genre per the Author Guidelines: short work → short paper, complete work → long paper |
| Ignoring hard format constraints | Over page limit, not anonymized, missing appendix | Rejected outright (technical screening failed) | Check the Author Guidelines item by item before submission; use the official template |
| Multiple submission / duplicate publication | Same content submitted to multiple venues at once | Academic misconduct, severe consequences | Strictly follow each venue's simultaneous-submission policy; confirm preprint policy separately |
| Submitting to a predatory venue | No peer review, publish-for-a-fee | Harms academic reputation | Self-check with authoritative index directories, DOAJ, Think. Check. Submit.; if you can't confirm, better not to submit |

---

## 5. Matching scorecard template

Copy and use. **Do not fill the "impact" column with numbers from memory** — either leave it blank or fill "source + query date + value".

| Candidate venue | Scope fit (includes/excludes/not mentioned) | Method-type fit (high/med/low) | Related papers in last 2 years | Hard constraints (pages/DDL/anonymity) | Impact (source+date) | Cycle (source+date) | Tier |
|-----------|----------------------------------|--------------------------|----------------|------------------------|--------------------|------------------|------|
| Venue A | Explicitly includes (quote original) | High | 4 | 8pp/double-blind/DDL confirmed | See notes 2026-09-14 | See notes 2026-09-14 | Reach |
| Venue B | Not mentioned (cross-cutting) | Medium | 1 | 12pp/single-blind/rolling | Same as above | Same as above | Main |
| Venue C | Explicitly includes | High | 2 | 6pp/double-blind/DDL confirmed | Same as above | Same as above | Safe |

**Tier rules**:
- Reach = scope and method both fit, but impact/competitiveness is above your current work's certainty;
- Main = the one of the three where you can best "say why it's here";
- Safe = scope explicitly includes, cycle controllable, and you're confident it gets in.

All three tiers must be **real submittable venues**; don't pad with an "obviously unsuitable" one.

---

## 6. Choosing between journal vs conference vs workshop

| Format | Traits (qualitative) | When to submit |
|------|-------------|----------------|
| Conference (has DDL) | Fixed deadline and notification dates, mainly one round of review (some have rebuttal / revision; defer to the site) | Time-sensitive results; need fast community feedback; want to publish a first version then extend it into a journal paper |
| Journal (mostly rolling) | Submit any time; review rounds and cycles vary widely; major revision is common | Complete work needing full space; needs a long-term citable version |
| Workshop / Short paper | Small size, focused scope, relatively low bar (not guaranteed; defer to the specific CFP) | Preliminary results, negative results, position papers, seeking feedback |
| Preprint (arXiv, etc.) | Claim the timestamp first, no waiting on peer review | Scoop / public results; **note**: preprint policies differ by venue and must be confirmed separately before submission |

**Extension path** (common practice; defer to each venue's self-plagiarism / prior-publication policy): conference short paper → journal extended version. If you go this route, **the extended version must have substantial new content** (usually a required proportion of new material; the exact proportion defers to the target journal's policy — don't guess), and declare the relationship to the conference version at submission.

---

## 7. Checklist

Tick each item before the submission decision is final:

- [ ] At least 3 candidate venues, each with its official Aims & Scope / CFP opened and key sentences recorded
- [ ] Each candidate was checked for **actually published related papers in the last 2 years**, not just the self-description
- [ ] All three tiers (reach/main/safe) are set, and all are really submittable
- [ ] Hard constraints (page count, template, anonymity, appendix, code/data statement) checked item by item
- [ ] Impact and cycle data: **looked up on demand**, with source and query date recorded; if not available, write `undisclosed`, not a memory value
- [ ] Ruled out the "engineering-heavy / too-theoretical" mismatches (§4 first two rows)
- [ ] Confirmed multiple-submission and preprint policies
- [ ] Done a credibility self-check with authoritative index directories / DOAJ / Think. Check. Submit.
- [ ] **Neither this file nor your notes contain any unverified impact factor, acceptance rate, or cycle number**
- [ ] If this round found a venue's scope disagrees with your memory, you've updated your own notes (**do not** write back to this file; this file holds no specific venue data)
