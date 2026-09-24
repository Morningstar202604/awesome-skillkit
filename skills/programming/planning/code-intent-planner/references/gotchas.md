# Common Pitfalls

## L1 rule pitfalls

1. **Keyword ambiguity**: "Help me review this document" may be recognized as code review. Rule: only match review when "code/PR" is present, otherwise degrade to L2.

2. **Multi-intent override**: "fix the bug and add a captcha" hits both fix and implement. Rule: rank by priority (fix > implement), output with primary/secondary labels.

3. **Colloquial omissions**: "How do I build this feature?" was not matched. Rule: add the L1 rule `"how|how to|what's the approach"` → plan (confidence 0.80).

## L2 LLM pitfalls

4. **Confidence inflation**: L2 outputs 0.82 but it may actually be wrong. Rule: calibrate via multi-signal fusion (rule match + vector similarity + historical accuracy).

5. **Slot hallucination**: infers target=auth though the user never mentioned it. Rule: slots with no explicit evidence are set to provisional and flagged.

6. **Over-clarification**: asking follow-ups on every small point. Rule: only clarify key information that affects the decision; record non-key info as an assumption and proceed.

## Cross-turn accumulation pitfalls

7. **Slot override loss**: a new value in turn 2 overwrites a key constraint from turn 1. Rule: latest-wins applies only to newly added slots; existing slots need conflict detection.

8. **Session leakage**: `_session_*.json` files committed to git. Rule: `.gitignore` must include `_session_*.json`.

## Task-breakdown pitfalls

9. **Tasks too fine-grained**: breaking down 50+ subtasks, where coordination cost exceeds execution cost. Rule: a single task is at most 4 hours; merge if larger.

10. **Missing dependencies**: T3 depends on T1 but doesn't declare it. Rule: every task must have an explicit depends_on; declare an empty array when there are no dependencies.

11. **Critical-path misjudgment**: a non-critical-path task labeled P0. Rule: P0 = on the critical path AND no parallel alternative exists.

## Security pitfalls

12. **Destructive false positive**: "delete temp files" triggers a high-risk confirmation. Rule: only trigger the high-risk flow when it involves project code/database/config.

13. **Hard constraint softened**: the user explicitly said "must use PostgreSQL" but it was downgraded to a soft constraint. Rule: constraints the user explicitly specifies must be marked hard.

## Cache pitfalls

14. **Cache pollution**: different intent types share a cache key. Rule: the cache key must include intent_type.

15. **Cache expiry**: long sessions make the cache stale. Rule: session expiry of 24h, or explicit clearing.
