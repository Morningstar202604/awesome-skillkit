#!/usr/bin/env python3
"""Topic Selector — 评估研究方向的可行性。

用法:
  python3 topic_selector.py --topic "LLM agent coordination"
  python3 topic_selector.py --topic "..." --constraints '{"time":"3mo","gpu":"1xA100"}'
"""
import argparse
import json
import sys
from pathlib import Path


def evaluate_topic(topic: str, constraints: dict = None) -> dict:
    """Score a research topic on feasibility/novelty/impact."""
    constraints = constraints or {}
    time_budget = constraints.get("time", "6mo")
    gpu = constraints.get("gpu", "1x")

    # Heuristic scoring
    complexity_words = ["large", "multi", "distributed", "real-time", "end-to-end"]
    novelty_words = ["first", "novel", "unexplored", "without", "zero-shot"]

    text_lower = topic.lower()
    complexity_score = sum(1 for w in complexity_words if w in text_lower)
    novelty_score = sum(1 for w in novelty_words if w in text_lower)

    # Feasibility decreases with complexity, increases with resources
    feasibility = max(0, 0.9 - complexity_score * 0.1)
    if "8" in gpu or "A100" in gpu or "H100" in gpu:
        feasibility = min(1.0, feasibility + 0.1)

    return {
        "topic": topic,
        "scores": {
            "novelty": min(1.0, 0.5 + novelty_score * 0.2),
            "feasibility": round(feasibility, 2),
            "impact": 0.6 + (1 if "benchmark" in text_lower or "evaluation" in text_lower else 0) * 0.2,
        },
        "constraints": constraints,
        "recommendation": "go" if feasibility >= 0.7 else "risky",
        "next": "Run lit-review to verify gap exists",
    }


def main():
    parser = argparse.ArgumentParser(description="Evaluate research topic")
    parser.add_argument("--topic", required=True)
    parser.add_argument("--constraints", help="JSON constraints")
    parser.add_argument("--output", help="Output file")
    args = parser.parse_args()

    try:
        constraints = json.loads(args.constraints) if args.constraints else None
    except json.JSONDecodeError as e:
        print(json.dumps({"status": "error", "error": f"invalid --constraints JSON: {e}"},
                         ensure_ascii=False, indent=2))
        return 2
    result = evaluate_topic(args.topic, constraints)

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    sys.exit(main())
