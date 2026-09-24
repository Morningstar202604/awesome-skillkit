---
name: channel-adapter
description: "Adapt finished marketing copy into per-channel variants with machine-checked fit: built-in channel constraint table (word budgets, line limits, CTA counts, banned patterns) for Xiaohongshu notes, Douyin spoken scripts, WeChat moments, email subjects, and search-ad headlines; audit each variant with channel_fit_check.py. Final chain step of growth-marketing. Use when the user asks to adapt for a channel / publish one piece everywhere / rewrite for Xiaohongshu / Douyin spoken script / Moments copy / email subject / channel variants / content marketing / SEO / conversion. Do NOT use for writing the base copy (product-copywriter), nor for planning the campaign calendar (campaign-designer)."
license: Apache-2.0
compatibility: Python 3.8+ (channel_fit_check.py); no third-party dependencies.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: marketing
  pattern: single-task
  tier: standard
  verified-date: "2026-09-14"
---

# Channel Adapter

The chain's closing step. One piece published everywhere is not copy-paste — **each channel has its own physical constraints** (word budget / line count / CTA count / tone norms). Get the constraints wrong and the platform throttles traffic or rejects the review outright. This skill pairs rewriting with machine validation for double assurance.

## Input Checklist

| Input | Required | Notes |
|------|------|------|
| Base copy | Yes | product-copywriter's output |
| Target channels | Yes | xhs / douyin-spoken / moments / email-subject / search-ad (multi-select) |
| Channel roles | No | campaign-designer's channel matrix role (acquisition / capture / private domain) |

When inputs are missing, ask for all at once: "Please provide: ① the base copy text; ② the target channels (xhs / douyin-spoken / moments / email-subject / search-ad, multi-select)."

## Pre-flight Self-check

```bash
test -f scripts/channel_fit_check.py && echo SCRIPT-OK
```

Expect to output `SCRIPT-OK`; failure means the skill package is incomplete — STOP and prompt for reinstall. The script is stdlib-only with no third-party dependencies, so no environment setup is needed. If the target channel name is not in the set `{xhs, douyin-spoken, moments, email-subject, search-ad}`, the script errors directly — check the spelling first.

## Workflow

### Step 1: Look Up the Channel Constraint Table (built into the script; read before rewriting)

| Channel | Hard constraint | Tone norm |
|------|--------|----------|
| Xiaohongshu note | Body ≤1000 chars; title ≤20 chars; CTA ≤1 | Like a friend sharing; no hard-sell tone |
| Douyin spoken | 15 seconds ≈60 chars; the first 3 seconds must have a hook | Short spoken sentences; no written-form language |
| Moments | ≤6 lines; the first line is the hook | Personable; no piled-up layout symbols |
| Email subject | ≤30 chars (the mobile truncation line) | No stacked exclamation marks |
| Search-ad headline | ≤30 chars; includes the core keyword | Noun-style selling point |

### Step 2: Rewrite Per Channel (not abbreviation)

- Constraints are **physical boundaries**; adaptation is **re-laying the information architecture**: Xiaohongshu leads with the scenario then the product, Douyin puts conflict in the first 3 seconds, search-ad leads with the keyword
- Every variant keeps the source copy's evidence-chain numbers — rewriting does not change facts
- When publishing on two channels at once, maximize the tone difference (seeding like a friend, search like a manual)

### Step 3: Run the Fit Check (machine gatekeeper)

```bash
python3 scripts/channel_fit_check.py --file assets/sample-variant.md --channel xhs   # bundled sample variant (within xhs limits); replace with your variant.md
python3 scripts/channel_fit_check.py --text "a search headline within 30 chars" --channel search-ad
```

Output JSON: word count / line count / CTA count, each pass/fail, plus a fix suggestion. A non-zero exit code means there is a fail; fix and rerun.

### Step 4: Deliver and Close the Chain

Deliver: the channel-variant pack (one per channel + the check report). **The chain closes here** — "copy → campaign → channel variants" is complete; when a channel underperforms, take the data back to campaign-designer to tune the matrix.
- Expected: each variant corresponds to a passing check record, and each channel can be deployed independently.
- On failure: a channel repeatedly fails the check → go back to product-copywriter to supplement the evidence chain (see the last row of the failure table); do not force it through.

## Delivery Standards

- Artifacts: one variant per channel (file name / section title matches the channel) + the check report (JSON pass/fail summary).
- Save location: output directly in the conversation; when saving files, one file per channel (e.g. `variant-xhs.md`).
- Integrity verification: every channel variant has passed `python3 scripts/channel_fit_check.py` with exit code 0; the source copy's evidence-chain numbers are preserved item by item.

## Failure Handling Table

| Symptom | Cause | Action |
|------|------|------|
| Xiaohongshu throttled | Hard-sell tone / banned words | Rewrite the tone to a sharing style; clear all extreme words |
| Douyin completion rate low | No hook in the first 3 seconds | Rewrite the spoken opening, front-load the conflict |
| Email open rate low | The subject is truncated on mobile | Rewrite the subject to the character limit |
| The check passes but conversion is poor | Facts lack an evidence chain | Go back to product-copywriter to add evidence — it is not the channel's fault |

## References

The direct-marketing framework provenance is in product-copywriter's sources-and-methodology.md (shared within the package).
