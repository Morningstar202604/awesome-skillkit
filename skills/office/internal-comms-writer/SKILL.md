---
name: internal-comms-writer
description: >-
  Draft company internal communications in four standard genres — recurring
  team updates, all-hands announcements, FAQ answers, and cross-team request
  emails — after pinning down audience, event, expected action and deadline.
  Use when the user asks to write a team update / internal notice / company
  announcement / reply to employee FAQ / send a cross-team coordination email /
  team update / company announcement / internal comms / company newsletter /
  FAQ answer / cross-team request. Do NOT use for external customer-facing copy,
  marketing material, or legal/PR statements that require sign-off from comms
  or legal teams.
license: Apache-2.0
compatibility: Pure prompt-based; no runtime deps.
metadata:
  author: awesome-skillkit
  version: "1.0"
  category: office-productivity
  pattern: single-task
  tier: standard
  verified-date: "2026-09-16"
---

# Internal Comms Writer (Internal Communications)

The #1 killer of internal comms isn't bad writing—it's unclear information:
readers don't know what to do, by when, or whom to ask. This skill collapses
internal writing into four genre templates plus a self-check checklist—ask
first, write second, ask everything in one batch so the user isn't interrogated
over three rounds.

## Input Checklist

| Input | Required | Notes |
|---|---|---|
| Audience | yes | Team members / all employees / a collaborating team; audience size and familiarity set how much background to include |
| What happened | yes | The facts: progress, change, policy, problem, ask |
| Expected reader action | yes | Just be aware / switch systems / fill a form / reply to confirm; if you can't state this, confirm with user first |
| Timing | yes | Deadline, effective date, next update time; an action item with no date is worthless |
| Supporting material | no | Data, links, owner list, historical FAQ entries |

When required inputs are missing, ask once—all four together:

> Before I start, please confirm four things: 1) who is this for? 2) what's the
> core thing? 3) what do you want them to do after reading (or just be aware)?
> 4) what timing applies (deadline / effective / next update)? Send any
> supporting material (data, links, owners) as well.

## Pre-flight Checks

- Are the four Ws present? Missing any → use the combined question above to ask
  all at once, not drip-fed follow-ups.
- Determine genre: is it a "regular sync" / "change notice" / "Q&A" / "ask for
  help"? Unsure → ask user "which scenario does this most closely match" and
  give four examples to choose from.
- Sensitive content scan: involves layoffs, performance, compensation, org
  changes, incident blame → warn that such comms usually need HR/legal/management
  review; this skill's output is draft-only.
- Internal jargon? Abbreviations outsiders won't get (system names, project
  codenames) → add a parenthetical explanation on first appearance in the draft.

## Workflow

### Step 1: Determine Genre

- **Action:** Map the request to one of four genres per the table below, and
  pull the corresponding template from references/templates.md.

| Scenario | Genre | Skeleton |
|---|---|---|
| Regular sync (weekly / biweekly / project standup) | Team update | Progress → Plan → Issues |
| All-hands notice of change/policy/system | All-hands announcement | Conclusion → Impact → Action → Deadline |
| Same question employees repeatedly ask | FAQ answer | Question → Direct answer → Background → Follow-up channel |
| Ask another team for help or resource alignment | Cross-team request email | Context → Request → Deadline → Alternative |

- **Expected:** genre uniquely determined; if one comms mixes two (e.g.
  announcement with embedded FAQ) → write separately, main genre as body,
  secondary as appendix section.
- **If it fails:** none of the four fit (e.g. incident postmortem, executive
  address) → say honestly it's outside template scope, write freely with
  "conclusion first + timing + action items" three elements, and note the draft
  didn't go through template self-check.

Genre determination examples (user's words → verdict):

| User says | Verdict | Basis |
|---|---|---|
| "Send a Friday team sync on what we did this week and next" | Team update | Recurring + three-part ask |
| "New approval system goes live Monday, everyone must switch entry" | All-hands announcement | Change + all-employee audience + action item |
| "Safety training questions keep coming, write a unified reply" | FAQ answer | Repeated Q&A on same topic |
| "Need data team to export a report, by Friday" | Cross-team request email | Cross-team + explicit request + deadline |

### Step 2: Write Draft

- **Action:** Fill template, obey three writing disciplines:
  1. One information point per paragraph; if you need "also" or "by the way"
     between paragraphs, that usually means split the paragraph or the piece.
  2. Conclusion first: the first sentence of each paragraph is its entire point;
     details come after.
  3. Every action item must carry an owner (specific person or role, not
     "everyone") and a deadline (specific date, not "ASAP" or "soon").
- **Expected:** draft length proportional to reader attention—team update
  200-400 words, all-hands announcement 300-500 words, FAQ single entry
  100-200 words, request email 200-400 words.
- **If it fails:** user supplied too much material → move details to
  "background details" or links, keep only what's relevant to this piece's
  purpose in the body, and list what was cut for the user to decide.

Revision comparison example (how checklist items 2, 3, 5 land):

```text
Draft (failing):
  Everyone will be switching to the new VPN soon; please log in at the new
  entry ASAP. If you hit issues, maybe check with IT, ideally before next month.

Problem diagnosis:
  - "everyone" "ASAP" "before next month" → no owner, no specific date (items 2, 5)
  - "maybe" "a bit" → vague, reader can't tell when done (item 3)

Revised (passing):
  All employees (owner: every colleague) please log in once at the new entry
  vpn.example.com by end of day Friday March 15 and keep the session open for
  5 minutes. If login fails, file a ticket in the #it-help channel the same
  day; IT will follow up within 1 business day.
```

### Step 3: Run Self-Check Checklist

- **Action:** Check item by item; any fail → return to step 2:

| # | Check | Typical Failing Symptom |
|---|---|---|
| 1 | One information point per paragraph? | "Also", "by the way" appears |
| 2 | Every action item has owner + deadline? | "Everyone", "ASAP", "try by next week" appears |
| 3 | Defensive or vague wording? | "might/maybe/possibly", "for some reason", "can't share more" |
| 4 | Reader can state "what do I do" within 10 seconds? | Conclusion buried after third paragraph |
| 5 | Timing specific to a date? | "Next month", "later in Q4" with no anchor date |
| 6 | FAQ avoids defensive tone? | "As we previously stated", "actually that's not the case" |
| 7 | Request email gives alternative or concession room? | Only one demand, no flexibility |

- **Expected:** all seven pass.
- **If it fails:** item 3 repeatedly fails (user insists on vague wording) → keep
  user's original phrasing but flag the risk in delivery notes: "this phrasing
  may be read by readers as ...; recommend confirming with user whether
  intentional."

FAQ defensive wording comparison (how checklist item 6 lands):

```text
Defensive (failing):
  As stated in last quarter's announcement, the reimbursement process has not
  become more complex; everyone may simply not have read the notice carefully.

Direct (passing):
  One thing changed in reimbursement: invoice attachments move from email to
  system upload. The old email channel closes in March. Steps are in the
  internal link; expect about 2 extra minutes. We didn't send a separate
  all-employee notice before—that was our oversight—and this entry is the
  official explanation.
```

### Step 4: Deliver

- **Action:** Output the finished piece + three-line delivery note: genre type,
  assumptions about unconfirmed info, suggested send channel and timing.
- **Expected:** user can send as-is; if unconfirmed assumptions remain (e.g.
  deadline was guessed), must state them explicitly in delivery notes, don't
  slip through silently.
- **If it fails:** user requests major rework → only fix the called-out issues,
  don't opportunistically rewrite the whole piece; rerun checklist items 1-3
  after.

## Delivery Criteria

| Item | Requirement |
|---|---|
| Body | One of four genres, paragraphs ≤ 5 lines, all action items carry owner + date |
| Structure | Conclusion first; announcements include "impact + action + deadline" trio |
| Tone | Direct, specific, no defensive wording; FAQ doesn't justify, requests don't grovel |
| Delivery note | Genre type + unconfirmed assumptions + suggested send channel, all required |

## Failure Handling Table

| Symptom | Action |
|---|---|
| User answers only half of the four Ws | Write placeholder draft with known parts, mark gaps with `[TBD: xx]`, never fabricate dates or owners |
| Comms involves negative event (incident / outage / personnel change) | State only facts and next steps, no blame or emotional judgment, flag that management review is needed |
| User asks for "more formal / more lively" tone | Adjust salutation and sentence density only, keep genre skeleton |
| Same piece for multiple reader groups | Layer and split: all-hands version keeps only conclusion and actions, detailed version for directly affected teams, both pass self-check |
| User has only verbal material, no data | Don't invent numbers; put `[add data here]` placeholder and list as pending in delivery notes |
| Content exceeds four genres | Write freely with three elements, explicitly state template self-check was skipped |

## References

- references/templates.md — original templates for four genres (department
  weekly / all-hands email / FAQ entry / cross-team request); consult when
  drafting.
- references/sources-and-methodology.md — methodology sources and license.
