#!/usr/bin/env python3
"""Topic Selector — research-direction evaluation and ranking.

Implements the four-factor scoring rubric from SKILL.md (Novelty 40% / Feasibility 30% /
Impact 20% / Buildability 10%). It upgrades the old "single-topic keyword score" to:
  - **multi-candidate comparison**: `--topic` (repeatable) or `--candidates FILE`, ranked
    together with reasons for why lower-ranked ones lost;
  - **real feasibility model**: estimate workload (person-weeks) from time/compute/complexity,
    then feasibility = 1 - workload/schedule;
  - **honest novelty source**: `novelty_source` is tagged `heuristic-keyword` (default, not
    a real novelty search) or `lit-review` (only counts as **verified** when `--lit-review-json`
    is supplied and a gap hits).

Honest disclaimer: on the default path novelty is a **keyword heuristic**, not a novelty-search
conclusion, so `novelty_verified=false`. To claim "no one has done this", you MUST first run a
real search with lit-review and pass `--lit-review-json`.

Usage:
  python3 topic_selector.py --topic "LLM agent coordination" --constraints '{"time":"3mo","gpu":"1xA100"}'
  python3 topic_selector.py --candidates candidates.json --lit-review-json lit_review.json
"""
import argparse
import json
import math
import re
import sys
from pathlib import Path

WEIGHTS = {"novelty": 0.40, "feasibility": 0.30, "impact": 0.20, "buildability": 0.10}

COMPLEXITY_TERMS = ["large", "multi", "distributed", "real-time", "end-to-end",
                    "multimodal", "billion", "pretrain", "from scratch"]
NOVELTY_TERMS = ["without", "zero-shot", "first", "unexplored", "cross-domain",
                 "under-studied", "no shared", "unsupervised"]
IMPACT_TERMS = ["benchmark", "evaluation", "dataset", "safety", "robustness",
                "generalization", "efficiency", "theory", "analysis"]
BUILDABLE_TERMS = ["fine-tune", "finetune", "prompt", "adapter", "lora", "on top of",
                   "existing", "post-hoc"]


def _clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def _deadline_weeks(constraints: dict) -> float:
    """Parse the time constraint into weeks. Supports '3mo' / '6 months' / '1y' / '8w' / a bare number (treated as months)."""
    raw = str(constraints.get("time", "6mo")).strip().lower()
    m = re.match(r"(\d+(?:\.\d+)?)\s*(mo|month|months|m|y|yr|year|years|w|week|weeks)?", raw)
    if not m:
        return 26.0
    n = float(m.group(1))
    unit = m.group(2) or "mo"
    if unit.startswith("y"):
        return n * 52
    if unit.startswith("w"):
        return n
    return n * 4.345


def _gpu_count(constraints: dict) -> int:
    gpu = str(constraints.get("gpu", "1x"))
    m = re.match(r"\s*(\d+)\s*x", gpu.lower())
    return int(m.group(1)) if m else 1


def _workload_weeks(topic: str, constraints: dict) -> float:
    """Workload estimate (person-weeks) -- complexity keywords + training regime + compute discount."""
    low = topic.lower()
    weeks = 6.0
    weeks += 4.0 * sum(1 for t in COMPLEXITY_TERMS if t in low)
    if "from scratch" in low or "pretrain" in low:
        weeks += 12.0
    if any(t in low for t in ("benchmark", "evaluation", "dataset")):
        weeks += 2.0
    # insufficient compute -> the same workload takes longer (discount factor)
    if _gpu_count(constraints) < 4 and any(t in low for t in ("large", "billion", "pretrain")):
        weeks *= 1.3
    return round(weeks, 1)


def _novelty(topic: str, lit_gaps: list = None) -> tuple:
    """Return (score, source, verified, evidence)."""
    low = topic.lower()
    hits = sum(1 for t in NOVELTY_TERMS if t in low)
    score = _clamp(0.45 + 0.10 * hits, 0.0, 0.95)
    source, verified, evidence = "heuristic-keyword", False, []
    if lit_gaps:
        toks = {w for w in re.findall(r"[a-z]{4,}", low)}
        for g in lit_gaps:
            gt = {w for w in re.findall(r"[a-z]{4,}", str(g).lower())}
            if toks and len(toks & gt) >= 3:
                evidence.append(str(g)[:120])
        if evidence:
            score = _clamp(score + 0.20, 0.0, 0.95)
            source, verified = "lit-review", True
    return round(score, 3), source, verified, evidence


def _impact(topic: str) -> float:
    low = topic.lower()
    score = 0.5
    if any(t in low for t in ("benchmark", "evaluation", "dataset")):
        score += 0.15
    if any(t in low for t in ("safety", "robustness", "generalization", "efficiency")):
        score += 0.15
    if any(t in low for t in ("theory", "analysis")):
        score += 0.10
    return round(_clamp(score), 3)


def _buildability(topic: str) -> float:
    low = topic.lower()
    score = 0.6
    if any(t in low for t in BUILDABLE_TERMS):
        score += 0.20
    if "from scratch" in low or "pretrain" in low:
        score -= 0.25
    return round(_clamp(score), 3)


def evaluate_topic(topic: str, constraints: dict = None, lit_gaps: list = None) -> dict:
    constraints = constraints or {}
    deadline = _deadline_weeks(constraints)
    workload = _workload_weeks(topic, constraints)
    feasibility = round(_clamp(1.0 - workload / max(deadline, 1.0)), 3)

    novelty, n_src, n_verified, n_evidence = _novelty(topic, lit_gaps)
    impact = _impact(topic)
    buildability = _buildability(topic)

    total = round(WEIGHTS["novelty"] * novelty + WEIGHTS["feasibility"] * feasibility
                  + WEIGHTS["impact"] * impact + WEIGHTS["buildability"] * buildability, 3)

    if feasibility < 0.35 or total < 0.40:
        recommendation = "reject"
        reason = (f"feasibility {feasibility} (workload {workload}w vs {round(deadline,1)}w)"
                  if feasibility < 0.35 else f"total score {total} below 0.40")
    elif feasibility >= 0.60 and total >= 0.65:
        recommendation, reason = "go", "feasible within budget and scores above thresholds"
    else:
        recommendation, reason = "risky", "borderline — verify gap with lit-review before committing"

    return {
        "topic": topic,
        "scores": {"novelty": novelty, "feasibility": feasibility, "impact": impact,
                   "buildability": buildability},
        "total": total,
        "weights": WEIGHTS,
        "recommendation": recommendation,
        "reason": reason,
        "novelty_source": n_src,
        "novelty_verified": n_verified,
        "novelty_evidence": n_evidence,
        "workload_weeks": workload,
        "deadline_weeks": round(deadline, 1),
        "gpu_count": _gpu_count(constraints),
        "constraints": constraints,
        "next": ("Verify the gap with lit-review (Semantic Scholar) before committing"
                 if not n_verified else
                 "Gap corroborated by lit-review output — proceed to experiment planning"),
    }


def rank(candidates: list, constraints: dict = None, lit_gaps: list = None,
         top_n: int = 5) -> dict:
    scored = [evaluate_topic(c, constraints, lit_gaps) for c in candidates]
    rejected = [s for s in scored if s["recommendation"] == "reject"]
    ranked = sorted((s for s in scored if s["recommendation"] != "reject"),
                    key=lambda s: -s["total"])[:top_n]
    for i, s in enumerate(ranked, 1):
        s["rank"] = i
    return {
        "ranked_topics": ranked,
        "rejected": [{"topic": s["topic"], "reason": s["reason"],
                      "scores": s["scores"], "total": s["total"]} for s in rejected],
        "n_candidates": len(candidates),
        "novelty_source": ("lit-review" if any(s["novelty_verified"] for s in scored)
                           else "heuristic-keyword"),
        "weights": WEIGHTS,
        "honesty_note": ("Novelty is a keyword heuristic unless --lit-review-json supplied; "
                         "never cite an unverified novelty score as a literature claim."),
    }


def main():
    parser = argparse.ArgumentParser(description="Evaluate & rank research topics (SOTA)")
    parser.add_argument("--topic", action="append", help="Research topic (repeatable)")
    parser.add_argument("--candidates", help="JSON file: list or {candidates:[...]}")
    parser.add_argument("--constraints", help="JSON constraints: time / gpu / venue")
    parser.add_argument("--lit-review-json", help="lit-review output JSON to verify gaps")
    parser.add_argument("--top-n", type=int, default=5)
    parser.add_argument("--output", help="Output file")
    args = parser.parse_args()

    try:
        constraints = json.loads(args.constraints) if args.constraints else {}
    except json.JSONDecodeError as e:
        print(json.dumps({"status": "error", "error": f"invalid --constraints JSON: {e}"},
                         ensure_ascii=False, indent=2))
        return 2

    candidates = list(args.topic or [])
    if args.candidates:
        p = Path(args.candidates)
        if not p.exists():
            print(json.dumps({"status": "error", "error": f"Not found: {args.candidates}"},
                             ensure_ascii=False, indent=2))
            return 1
        data = json.loads(p.read_text(encoding="utf-8"))
        items = data.get("candidates", []) if isinstance(data, dict) else data
        for it in items:
            candidates.append(it if isinstance(it, str) else str(it.get("topic", "")))
        if isinstance(data, dict) and data.get("constraints") and not constraints:
            constraints = data["constraints"]

    if not candidates:
        print(json.dumps({"status": "error",
                          "error": "provide --topic (repeatable) and/or --candidates FILE"},
                         ensure_ascii=False, indent=2))
        return 2

    lit_gaps = None
    if args.lit_review_json:
        lp = Path(args.lit_review_json)
        if not lp.exists():
            print(json.dumps({"status": "error", "error": f"Not found: {args.lit_review_json}"},
                             ensure_ascii=False, indent=2))
            return 1
        lr = json.loads(lp.read_text(encoding="utf-8"))
        lit_gaps = (lr.get("summary") or {}).get("gaps_identified") or []

    result = rank(candidates, constraints, lit_gaps, args.top_n)

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    sys.exit(main())
