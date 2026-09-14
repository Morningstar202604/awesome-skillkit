---
name: paper-topic-selector
description: "Identify research gaps and select paper topics. Scans recent literature trends, finds underexplored areas, evaluates novelty/feasibility/impact. Outputs a ranked list of viable research directions. Use at the start of a research project. 当用户要求 选论文选题 / 找研究空白 / 投稿选刊 时使用。"
license: Apache-2.0
compatibility: Pure prompt-based; may call web-search for trend scanning. No API keys required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-09"
---

# Paper Topic Selector

Find viable research directions by identifying gaps.

## When to Use

- Starting a new research project
- Need to narrow down from broad area to specific topic
- Evaluating whether a proposed idea has novelty
- Looking for underexplored sub-problems

## Input

```json
{
  "area": "LLM agents",
  "sub_area": "multi-agent coordination",
  "constraints": {
    "time": "3 months",
    "resources": "1 GPU, no dataset budget",
    "target_venue": "ACL / NeurIPS / workshop"
  },
  "known_papers": ["paper1", "paper2"]
}
```

## Output

```json
{
  "ranked_topics": [
    {
      "rank": 1,
      "topic": "Conflict resolution in LLM agent teams without shared memory",
      "novelty": 0.85,
      "feasibility": 0.7,
      "impact": 0.8,
      "gap": "Existing work assumes shared context; zero-shot coordination unexplored",
      "baseline": "AgentBench, CAMEL",
      "contribution_angle": "Propose protocol-based coordination + evaluate with 5 benchmarks"
    },
    {
      "rank": 2,
      "topic": "Cost-aware routing for heterogeneous LLM agent pools",
      "novelty": 0.7,
      "feasibility": 0.9,
      "impact": 0.6,
      "gap": "Most work assumes single model; multi-model routing with budget constraints underexplored"
    }
  ],
  "rejected": [
    {"topic": "...", "reason": "Already covered by PaperX (2025)"}
  ]
}
```

## Scoring Criteria

| Factor | Weight | What to Check |
|--------|--------|---------------|
| Novelty | 40% | Is the specific angle unexplored? (not just the general area) |
| Feasibility | 30% | Can it be done in the time/resource budget? |
| Impact | 20% | Would reviewers care? Is there a clear evaluation? |
| Buildability | 10% | Can results build on top of existing code? |

## Workflow

1. Scan recent papers in area (last 6 months)
2. Identify what's been done
3. Find what's NOT done (gap)
4. Score each gap on 4 criteria
5. Check feasibility against constraints
6. Output: ranked list with justification

## References

- [references/gap-finding.md](references/gap-finding.md) — how to find gaps systematically
- [references/venue-matching.md](references/venue-matching.md) — which venues like what