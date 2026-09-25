# Decision Record Template

A decision record (sometimes called an ADR, Architecture Decision Record, adapted
here to any consequential choice) makes the call auditable. Without it, hindsight
rewrites history: six months later the user "knew all along" it would work, or
"knew all along" it was a mistake. The record freezes the reasoning at the moment of
choice so the user can learn from outcomes, not from nostalgia.

## When to write one

Mandatory for any hard-to-reverse (reversibility 4-5) decision. Optional but useful
for medium-stakes calls. Never skip it on a decision the protocol ran in full.

## Template

```markdown
# Decision Record — <short title>

Date: YYYY-MM-DD
Time horizon: <when we will know if this worked>
Stakes: <what is gained / lost>
Reversibility: <1-5>   (1 = cheaply undoable, 5 = locked in, large sunk cost)

## Context
<The situation that forced the decision. What was happening? What made now the
moment to decide?>

## Options considered
- Option A: <one line>
- Option B: <one line>
- Option C: <one line>

## Decision
Chosen: <which option>

## Rationale
<Why this one won. What the pre-mortem and red-team surfaced, and why they did not
kill this option.>

## Rejected options, and why
- Rejected X: <why it lost>
- Rejected Y: <why it lost>

## Key assumptions the decision rests on
1. <assumption — the thing most likely to be wrong>
2. <assumption>
3. <assumption>

## Triggers that would make me revisit
- If <X measurable condition happens>, I will re-open this decision.
- If <Y assumption is contradicted by data>, I will re-open this decision.

## Second opinion
<Who independent I consulted, or "required but not yet obtained" if pending>

## Review date
YYYY-MM-DD (set a future calendar reminder)
```

## Notes on each field

- **Context** is the scene at the time. Do not write it after the outcome; hindsight
  contaminates it.
- **Rejected options with rationale** is the highest-value field. It prevents the
  user from later pretending they never considered the alternative, and it records
  the trade-offs they consciously gave up.
- **Key assumptions** must be falsifiable. "Things will go well" is not an
  assumption; "we will close the pilot within 90 days" is.
- **Triggers** convert the pre-mortem into an early-warning system. Each past-tense
  failure reason suggests a trigger: "if pilot conversion trails target by 30% at
  day 45, revisit."
- **Review date** closes the loop. Without a scheduled revisit, the record rots in a
  drawer.

## Worked mini-example

> Decision: hire a contractor for 6 months instead of a full-time hire.
> Chosen: contractor.
> Rejected: full-time (too slow to hire, too much fixed cost for an unproven need).
> Assumptions: scope stays contained; contractor is available for the full 6 months;
> no long-term knowledge transfer needed.
> Revisit triggers: if scope grows past the original contract, or if the contractor
> becomes unavailable, reopen.
> Review date: +90 days.
