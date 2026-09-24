---
name: personal-voice-profile
description: "Distill a reusable personal voice profile from >=3 samples of the user's own writing: lexical habits and catchphrases, syntactic stats (sentence length median/variance, paragraph habits), tonal markers, structural tics, plus 3 verbatim representative snippets; outputs voice-profile.json and a one-page imitation card. Use when the user asks to build a style profile / distill my writing style / analyze my writing habits / make AI write like me / voice profile / writing style analysis / mimic my writing style. Do NOT use on third-party text without the author's consent, and never to impersonate someone else."
license: Apache-2.0
compatibility: Pure prompt-based; no scripts, no environment probing. Optionally pairs with ai-trace-auditor's stdlib scanner downstream, but needs nothing itself.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: writing
  pattern: single-task
  tier: standard
  verified-date: "2026-09-16"
---

# Personal Voice Profile (Personal Style Profiling)

The prerequisite for "sounds like I wrote it" is knowing who "I" is. This skill distills a reusable style profile from the user's own past writing — four layers (vocabulary, syntax, tone, structure) plus three verbatim samples — so downstream rewriting and writing skills have a concrete target rather than a vague "be more conversational".

## Input Checklist

| Input | Required | Notes |
|---|---|---|
| Past writing samples | yes | >=3 articles/posts/emails written by the user themselves; longer is more accurate; >=200 chars each is ideal |
| Primary publishing platform | no | Official Account / Zhihu / chat-asides — multi-platform samples may split stylistically; declare the primary sample |
| Profile purpose | no | for humanize-rewriter alignment / for the user's own retrospective; purpose affects the imitation card's detail |

When a required item is missing, ask only once:

> Please provide in one go: ① at least 3 texts written by you (paste directly or give a path; the longer the better, 200+ chars each); ② which platform these mainly appeared on; ③ who the profile is for.

## Pre-flight Checks

This is a pure-prompt skill; no environment probing — only check input completeness:

- >=3 samples? Fewer -> refuse to produce per Red Line 1, and use the ask-everything phrasing above to fill the gap; don't force it with 2 samples.
- Are the samples written by the user themselves, or authorized by the author? Unstated -> first ask about authorship and authorization, then act.
- Is the style difference between samples abnormally large (e.g. a paper + a casual chat)? Yes -> group by register in Step 1; the profile is only responsible for the user-designated primary register.

## Red Lines (Hard Bans, Non-Negotiable)

1. Refuse to produce with <3 samples: two texts can't support a style profile, and a forced profile misleads downstream rewriting — better to ask for more.
2. Authorization boundary: only analyze text the user authored or is authorized for; third-party mimicry requests like "mimic this writer's style" are refused outright — this skill only profiles the user themselves.
3. The profile must not be used to impersonate others: attach a purpose statement when delivering voice-profile.json; if the user uses it for identity impersonation, this skill doesn't endorse the consequences.

## Workflow

### Step 1: Read Through and Group by Register

- **Action:** read all samples, judge whether they're the same register (formal/casual, platform differences); different registers are weighted primary/secondary per the user's direction.
- **Expected:** a register-judgment record: which are the primary samples, how secondary samples are downweighted.
- **If it fails:** the user can't articulate platform differences -> treat all as primary samples, and note the register limitation in the profile.

### Step 2: Lexical-Layer Statistics

- **Action:** count high-frequency content verbs (e.g. casual "do/handle/juggle" vs. formal "execute/push forward"), catchphrases and openers ("actually""honestly""by the way"), punctuation habits (em-dash, ellipsis, exclamation-mark frequency and position), and the Chinese-English mixing tendency.
- **Expected:** each item gives a frequency or proportion, with 1-2 verbatim quotes as evidence; no unverifiable vague words like "occasionally used". Record-format example:

```text
High-frequency verbs: handle (14x) > hit a pitfall (6x) > implement (3x)
Catchphrases: "actually" (11x, 7 at sentence start); "honestly" (4x, all at paragraph start)
Punctuation: em-dash 2.1x per 1000 chars; ellipsis only on trailing pause sentences; exclamation mark once across all samples
CN-EN mixing: technical terms kept in English (pipeline / review), everything else in Chinese
```

- **If it fails:** total sample too small for meaningful frequencies -> switch to an enumeration-style record (what appears), and note insufficient statistical significance.

### Step 3: Syntactic-Layer Statistics

- **Action:** count the median and variance of sentence length (same convention as ai-trace-auditor: effective-character count), average paragraph length and sentences per paragraph, and list-usage habits (love lists or not, average list-item length).
- **Expected:** numbers are re-checkable — spot-checking any paragraph manually under the same convention should match. Record-format example:

```text
Sentence: median 22 chars / cv 0.58 (convention: effective chars, excluding punctuation and whitespace, matching trace_scanner)
Paragraph: avg 3.2 sentences/paragraph; 1 one-sentence standalone paragraph (used for turns)
List: only 1 of 5 posts uses lists, and items avg <=12 chars -> list_usage: rare
```

- **If it fails:** samples are mostly short posts with no paragraph concept -> mark the paragraph layer not_applicable; don't force it.

### Step 4: Tonal-Layer Induction

- **Action:** induce the baseline ratio of self-deprecation/excitement/calm, interjections and modal particles, how the reader is addressed ("you/everyone/folks"), and emotional expression (direct vs. irony).
- **Expected:** each conclusion is backed by an original snippet; tone scenarios the samples don't cover are marked "unknown", not guessed. Induction example:

```text
Baseline: calm and restrained, self-deprecation only in pitfall scenarios (2x across 3 posts)
Address: uses "you" throughout, never "dear readers/folks"
Emotion: irony > direct — gripes use "great, it broke again" style deadpan
Interjections: "ha" as a standalone sentence = speechless, not laughter
```

- **If it fails:** samples are all work emails with a single tone -> honestly record the register limitation, suggest the user add casual samples.

### Step 5: Structural-Layer Induction

- **Action:** distill opening routines (get straight to substance / scene entry / raise a question first), closing routines (stop abruptly / summarize one line / throw a question to the reader), and transition habits (subheadings, dividers, or hard cuts).
- **Expected:** each routine gives a frequency (e.g. "4 of 5 posts get straight to substance").
- **If it fails:** structural features are highly inconsistent -> downgrade the conclusion to "no obvious fixed routine", which is itself a valid profile.

### Step 6: Produce voice-profile.json and the Imitation Card

- **Action:** consolidate into JSON, and separately write a one-page imitation card (executable instructions for downstream skills or humans).

```json
{
  "lexical": {"catchphrases": ["actually", "honestly"], "punct_habits": {"dash_per_1k_chars": 2.1}},
  "syntactic": {"median_sentence_len": 22, "sentence_len_cv": 0.58, "list_usage": "rare"},
  "tonal": {"baseline": "calm with self-deprecation", "reader_address": "you", "interjections": ["ha"]},
  "structural": {"opening": "straight to substance (4/5)", "closing": "throw a question to reader (3/5)"},
  "example_snippets": ["original snippet 1", "original snippet 2", "original snippet 3"]
}
```

- **Expected:** the JSON parses with `json.loads`; example_snippets are verbatim originals, the 3 passages most representative of the style; the card has no fewer than 3 DO and 3 DON'T items. Card sample:

```text
Imitation Card (one page)
DO   median sentence 22 chars; dare to end a long sentence with a 3-char short one
DO   paragraph openings may use "actually"/"honestly", but at most twice per post
DO   keep technical terms in the original English; don't force-translate them
DON'T use official cliches like "in summary / it is worth noting"
DON'T string three exclamation marks — the whole sample has only 1 exclamation mark
DON'T end with a slogan; close with a question or one line
```

- **If it fails:** JSON serialization fails -> fix escaping and re-output; can't find 3 representative passages -> honestly use fewer and explain.

## Output Spec

| Artifact | Structure | Notes |
|---|---|---|
| voice-profile.json | lexical / syntactic / tonal / structural / example_snippets, five layers | English field names; frequency conventions noted; readable by downstream programs |
| Imitation card | one page: four-layer conclusions + DO/DON'T list | DO writes "what to do"; DON'T writes "what this author would never do" |
| Register statement | one sentence | The register and platform the profile applies to; out-of-scope use is the caller's own risk |

## Failure Remediation Table

| Symptom | Cause | Remedy |
|---|---|---|
| Only 1-2 samples | User in a hurry | Refuse per Red Line 1, use the ask-phrasing to get samples; explain why forcing it won't work |
| Severely split sample styles | Multi-platform, multi-register mixed submission | Group out profiles or have the user name a primary register; mark the profile's scope |
| It's someone else's article | Wanting to mimic a third party | Hits Red Line 2: refuse, explain this only profiles the user themselves |
| Profile is vague ("the user is quite humorous") | Conclusions lack evidence | Re-attach original quotes to each; delete conclusions that can't be backed |
| Samples are all formal documents | Single register | Deliver honestly and declare the limitation; suggest adding everyday texts |
| Can't scrape together 3 example_snippets | Samples too short | Give fewer than 3, note why, don't pad with repeats |
| User later asks to add a celebrity's corpus "while you're at it, learn from him" | Hits Red Line 2 | Refuse; once confirmed, the sample set is not mixed with third-party text |
| Same user asks for "a profile for another platform" | Register-extension need | Produce a separate profile from that platform's samples; deliver two independently, don't merge |

## Delivery Standard

- voice-profile.json parses with `json.loads`, all five layers present (mark not_applicable for unusable layers).
- Every profile conclusion is traceable: backed by an original quote or occurrence frequency; no out-of-thin-air style assertions.
- example_snippets are verbatim originals (may mark the excerpt range); 3 passages ideal, fewer honestly explained.
- The imitation card is executable on one page: downstream humanize-rewriter can calibrate by DO/DON'T immediately.
- Authorization confirmed on record: sample ownership and purpose statement confirmed with the user once, not assumed by default.
- Frequency conventions are recomputable: rerunning statistics on a different sample with the same convention is expected to differ; convention drift is a defect.

## References

- `references/sources-and-methodology.md` — read when you need to explain the provenance of the style-analysis methodology (voice/tone distinction, style-measurement approach) or for external attribution.

## Chain Position

- Upstream: the past text the user provides; closed loop with article-drafter — its old outputs can also serve as profile samples.
- Downstream: humanize-rewriter (feed voice-profile.json so the rewrite aligns to "you"); article-drafter can also read the profile when writing new pieces.
- Parallel: own-voice-rewrite (the education domain's student-essay case, which uses coarser profiling anchored to grade level).
