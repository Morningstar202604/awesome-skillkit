# Scoring Dimensions and Weights

Five dimensions (0-1) are weighted into an overall, then ×5 to get a 0-5 score:

| Dimension | Default weight | Meaning | Source |
|---|---|---|---|
| requirement_match | 0.35 | Per-requirement hit rate (A=1/B=0.7/C=0.4) | automated by script |
| level_fit | 0.20 | Level match (detected level gives 0.6, otherwise 0.4) | automated by script |
| comp_band | 0.15 | Salary band match | **human-filled** |
| domain_match | 0.20 | Domain match | **human-filled** |
| stability | 0.10 | Company/role stability | **human-filled** |

- `score_5 >= 4` → STRONG (recommend applying)
- `3 ≤ score_5 < 4` → OK (applicable; mind filling gaps)
- `score_5 < 3` → WEAK (skip)

## Weight override
Pass `--weights ./weights.json`, format `{"requirement_match":0.5,...}`; missing dimensions keep defaults.

## Boundaries
- Scoring is **heuristic surface matching**, not LLM semantic understanding—terms must match literally.
- The three human dimensions default to 0.5; be sure to fill them in before making a final decision.
