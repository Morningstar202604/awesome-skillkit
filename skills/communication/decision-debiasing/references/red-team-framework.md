# Red-Team Framework

A red-team on your own decision means deliberately adopting an adversary's role and
building the strongest possible case **against** the option you are leaning toward.
Because assistants are sycophantic and humans are confirmation-seeking, the default
output flatters the favorite. This procedure forces a fair, steelmanned attack.

## Why self-red-teaming is hard (and worth it)

- The user (and the assistant) naturally builds weak objections the user can easily
  swat down — the illusion of scrutiny.
- A weak red-team is worse than none: it feels like the decision was stress-tested
  when it was not.
- The value comes from making the attack sharp enough that the user has to actually
  rebut it. If the rebuttal is instant and effortless, the red-team was too soft.

## Procedure

1. **Assign the skeptic explicitly.** Say, out loud: "I am now role-playing the
   person who will argue against your chosen option. This is not my real opinion of
   you; it is the exercise."
2. **Steelman the opposition.** Do not quote the lazy version of the opposing view.
   State the opposing argument in its strongest, most respectable form — the version
   a smart, informed critic would actually make.
3. **Make it concrete.** Cite specific failure modes, costs, and counterfactuals,
   not vibes. "This will probably be hard" is weak; "the sales channel you're
   betting on converts at half your assumption because two competitors already
   undercut it" is a real attack.
4. **Present the anti-case as a short brief.** Give it structure: the core thesis
   against the decision, three supporting arguments, and what would make the
   red-team concede.
5. **Require a rebuttal.** The user must answer the steelman, not ignore it. If they
   cannot rebut a point, that point is a real risk to price into the decision.

## Steelmanning vs strawmanning

| Strawman (useless) | Steelman (the goal) |
|--------------------|---------------------|
| "Maybe the team messes up." | "The plan depends on one senior engineer; they have a history of leaving around month 12, and there is no redundancy." |
| "It might cost too much." | "Your margin assumption assumes no discounting; two recent comparable deals closed at 15% under list, which flips the unit economics negative." |
| "The market is uncertain." | "The segment you're entering contracted last quarter and your customer segment has the lowest retention in the category." |

## Common red-team failure modes

| Failure | What it looks like | Fix |
|---------|--------------------|-----|
| Token objection | One soft objection the user swats in one line | demand at least three concrete, independent attacks |
| Strawman attack | attacking a dumb version of the user's reasoning | rewrite the attack in its strongest, fairest form |
| Flattering close | "but on balance you're probably right" | do not soften; let the anti-case stand on its own merits |
| Skeptic gives up too early | concedes after the first rebuttal | hold the line: ask "what would make ME convinced?" |
| No emotional distance | attack reads as personal criticism | keep it clinical — attack the plan, not the person |

## Concede conditions

End the red-team by naming, explicitly, what evidence would make the skeptic stop
objecting. That converts the exercise into a concrete risk list: each unresolved
objection becomes a known assumption to monitor (and to log in the decision
record).
