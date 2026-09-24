---
name: paper-topic-selector
description: "Identify research gaps and rank paper topics. Scans recent literature trends, finds underexplored areas, and scores candidates on the four-factor rubric (novelty 40% / feasibility 30% / impact 20% / buildability 10%) with a workload-vs-deadline feasibility model, returning ranked_topics plus rejected-with-reason. Use when selecting a paper topic / finding a research gap / choosing a journal venue / evaluating topic feasibility / scoring research topics / ranking paper candidates at the start of a research project. Do NOT use for writing the paper itself."
license: Apache-2.0
compatibility: Gap analysis is prompt-based (may call web-search for trend scanning). Heuristic scoring via scripts/topic_selector.py, stdlib only. No API keys required.
metadata:
  version: "2.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-21"
---

# Paper Topic Selector (SOTA)

Identify research gaps -> rank multiple candidates on four factors -> output `ranked_topics[]` and `rejected[]` with reasons.

> **Honest disclosure**: don't confuse the two tracks — ① the Novelty/Feasibility/Impact judgments in the workflow are **analyzed** by the model per the scoring rubric below;
> ② `scripts/topic_selector.py`'s novelty defaults to a **keyword heuristic** (`novelty_source: "heuristic-keyword"`,
> `novelty_verified: false`) and **must not be cited as a novelty-search conclusion**. Only when you pass `--lit-review-json` and a gap hits does it
> upgrade to `novelty_source: "lit-review"` + `novelty_verified: true`.

## Input Checklist

| Input | Required | Notes |
|------|------|------|
| research direction | yes | `--topic "..."` (**repeatable, for multi-candidate comparison**) or `--candidates FILE` (JSON: list or `{constraints, candidates}`) |
| resource constraints | no | `--constraints '{"time":"3mo","gpu":"1xA100"}'`; `time` supports `3mo`/`6 months`/`1y`/`8w` (a bare number is treated as months), `gpu` like `8xA100` |
| novelty-search evidence | no | `--lit-review-json lit_review.json`: uses its `summary.gaps_identified` to validate novelty |
| number to return | no | `--top-n 5` (default 5) |
| output path | no | `--output topics.json`; default prints to stdout |

When missing, ask everything at once: "Please provide: ① candidate direction(s) (one or more) ② constraints (time/compute/target venue) ③ whether you already have lit-review results to validate novelty ④ whether to save `--output`."

## Pre-flight Checks
```bash
python3 --version                                 # expect >= 3.8, else error and STOP
test -f scripts/topic_selector.py && echo OK      # expect OK printed, else script missing STOP
```
Pure workflow mode has no script dependency; if web trend scanning is needed and the network is unreachable -> do gap analysis on locally known literature and note "not verified online" in the output.

## Workflow

### Step 1: Coarse Screening and Scoring of Candidates
```bash
python3 scripts/topic_selector.py --topic "LLM agent coordination" --constraints '{"time":"3mo","gpu":"1xA100"}'
python3 scripts/topic_selector.py --topic "A" --topic "B" --topic "C" --constraints '{"time":"6mo","gpu":"8xA100"}'
python3 scripts/topic_selector.py --candidates candidates.json --lit-review-json lit_review.json --output topics.json
```
Expected: JSON output containing `ranked_topics[]` (each with `rank`/`topic`/`scores{novelty,feasibility,impact,buildability}`/`total`/`weights`/`recommendation`/`reason`/`novelty_source`/`novelty_verified`/`workload_weeks`/`deadline_weeks`/`gpu_count`/`next`), `rejected[]` (with `reason`), `n_candidates`, `novelty_source`, `weights`, `honesty_note`.
If it fails: rc=2 -> `--constraints` is invalid JSON or no candidate was given; rc=1 -> the `--candidates`/`--lit-review-json` path doesn't exist.

### Step 2: Scan the Literature and Identify the Gap

1. Scan recent papers in the field (last 6 months)
2. Lay out what work already exists
3. Find what nobody has done (the gap) — feed the result into lit-review's `--s2`, or conversely pass lit-review's `gaps_identified` to this script

Expected: each candidate's gap can point to "who did what / what's missing"; output format per the example below.
If it fails: the field is too broad to find boundaries -> first narrow the sub_area, then scan; offline failure -> note "not verified online" and continue on known literature.

### Step 3: Check the Four-Factor Weights and Constraints

| Factor | Weight | What to Check |
|------|--------|---------------|
| Novelty | 40% | Has nobody done this specific angle? (not the broad field itself) |
| Feasibility | 30% | `1 - workload_weeks / deadline_weeks`; workload includes complexity words, from-scratch penalty, few-GPU discount |
| Impact | 20% | Will reviewers care? Is there a clear evaluation plan? |
| Buildability | 10% | Can it be built on existing code? (fine-tune/adapter/LoRA get bonus, from-scratch loses points) |

Expected: `total` is exactly the weighted sum of the four factors (the script backfills `weights` for re-checking); `recommendation` in `go`/`risky`/`reject`; rejected items carry a `reason`.
If it fails: a score has no basis -> it must cite specific papers/facts as support; otherwise downgrade it to `rejected`.

### Step 4: Produce the Ranked List

Expected: output `{"ranked_topics": [...], "rejected": [...]}`, with recommended items carrying `next` (default points to lit-review for verification).
If it fails: the list is empty -> broaden the area or do a systematic lit-review first.

```json
{
  "ranked_topics": [
    {
      "rank": 1,
      "topic": "Conflict resolution in LLM agent teams without shared memory",
      "scores": {"novelty": 0.75, "feasibility": 0.72, "impact": 0.65, "buildability": 0.8},
      "total": 0.729,
      "recommendation": "go",
      "novelty_source": "heuristic-keyword",
      "novelty_verified": false,
      "next": "Verify the gap with lit-review (Semantic Scholar) before committing"
    }
  ],
  "rejected": [{"topic": "...", "reason": "feasibility 0.2 (workload 33.0w vs 4.3w)", "total": 0.38}]
}
```

## Parameter Quick Reference

| Parameter | Value | Notes |
|------|------|------|
| `--topic` | string | Candidate direction, **repeatable** |
| `--candidates` | path(JSON) | list or `{constraints, candidates}`; stacks with `--topic` |
| `--constraints` | JSON string | `time` (`3mo`/`6 months`/`1y`/`8w`), `gpu` (`8xA100`) |
| `--lit-review-json` | path(JSON) | Reads `summary.gaps_identified` to validate novelty |
| `--top-n` | int | Number of `ranked_topics` to return, default 5 |
| `--output` | path | Results JSON output path |

## Failure Remediation Table

| Symptom / Error Code | Cause | Remedy |
|------------|------|------|
| rc=2, `status: "error"` | `--constraints` is invalid JSON, or no candidate given | First self-check with `python3 -c "import json;json.loads(...)"`; add `--topic`/`--candidates` |
| rc=1, `Not found` | The `--candidates` or `--lit-review-json` path doesn't exist | Check the path |
| Everything lands in `rejected` | The field is saturated or constraints are too tight (deadline too short) | Switch sub_area, relax `time`, or read `references/gap-finding.md` for another approach |
| `novelty_verified: false` but you've already read the literature | Didn't pass `--lit-review-json` | Pass in the lit-review output JSON to justify the claim of "novelty searched" |
| Scores badly contradict intuition | novelty is a keyword heuristic, feasibility is a workload estimate | Trust Step 3's model judgment; lay out `workload_weeks` vs `deadline_weeks` for manual review |

## Delivery Standard

Success: produce a ranked list, each item's four factors scored with evidence and `total` = weighted sum; rejected items carry a `reason`.
Artifact name: `topics.json` (if `--output` is given) or direct text output.
Save location: the caller's current directory or the `--output` path.
Verification: `python3 -c "import json;d=json.load(open('<output>'));assert d['ranked_topics'] or d['rejected'];assert d['weights']"` passes; workflow-produced scores must have a supporting sentence findable in the body.
Honest rule: when `novelty_verified` is false, you MUST NOT write claims like "to our knowledge, no one has studied this" in the body.

## References

- [references/gap-finding.md](references/gap-finding.md) — **read before Step 2**: systematic gap-finding methods (classification dimensions, how to write search queries)
- [references/venue-matching.md](references/venue-matching.md) — **read when matching target_venue in Step 3**: venue preferences and fit judgment
- In-script internals: `WEIGHTS` (four-factor weights), `_workload_weeks`/`_deadline_weeks` (feasibility model), `_novelty` (novelty source and verification), `rank` (sorting and rejection).

## Chain Position

No upstream prerequisite; hand the output to lit-review to verify whether the gap is real (and feed its output back into `--lit-review-json` to raise novelty confidence), then move into experiment planning (experiment-runner) once the topic is set.
