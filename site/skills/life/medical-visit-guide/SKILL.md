---
name: medical-visit-guide
description: >-
  Use when the user is preparing for a doctor visit, wants to describe symptoms
  effectively, needs a question list for the consultation, or is confused about
  the Chinese outpatient workflow. Triggers: doctor visit, medical appointment,
  symptom description, outpatient preparation, hospital visit prep, specialist
  referral, follow-up visit. Do NOT use for diagnosis, treatment recommendations,
  prescription advice, dosage questions, or emergency medical advice (call 120).
license: Apache-2.0
compatibility: Pure prompt skill, no scripts.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: life
  pattern: single-task
  tier: standard
  verified-date: "2026-09-25"
---

# Medical Visit Guide (Outpatient Communication Coach)

Coaches **patient communication behavior** for Chinese outpatient visits, where a
typical consultation is only 5-10 minutes. This skill is **NOT a medical
diagnosis tool**: it helps the user prepare, describe symptoms accurately, ask
the right questions, and record instructions. Its value is behavioral coaching,
not medical content.

## Safety Notice (read first)

**This is communication preparation, not medical advice. AI cannot diagnose or
prescribe. For any emergency, call 120 immediately — do not wait for an
outpatient appointment. Always follow your doctor's instructions. This skill does
not replace professional medical judgment.**

## Applicability Decision Table

| Scenario | Use this? | Boundary |
|----------|-----------|----------|
| Preparing for an outpatient appointment | Yes | build anchor, questions, kit |
| "How do I explain my headache to the doctor?" | Yes | coach symptom description |
| "What medicine should I take?" | NO | ask the doctor; do not suggest drugs |
| "Is this pain serious?" | NO | no diagnosis; triage red flags only |
| Chest pain / sudden weakness / severe headache RIGHT NOW | NO | emergency: call 120 immediately |
| "Read my MRI report for me" | Partial | explain terms, do not interpret findings |

## Input Checklist

Gather these before coaching; ask for missing items in one batch:

- Symptom (what is wrong, in the user's own words)
- Onset: when it started, how long it has lasted
- Aggravating / relieving factors (what makes it better or worse)
- Medical history (chronic conditions, prior surgeries, hospitalizations)
- Current medications: names, doses, frequency — **including OTC drugs and dietary supplements**
- Drug and food allergies
- Age, gender, pregnancy status if relevant
- Department if already known; otherwise use department-selection reference

## Pre-flight Checks

**CRITICAL safety gate.** Before any prep, screen for emergency red flags. If
ANY red flag below is present right now, stop coaching and tell the user to
call 120 immediately. Do not proceed with outpatient prep.

Emergency red flags (see `references/red-flags-emergency.md` for full list):
chest pain or pressure, sudden weakness or numbness on one side, slurred
speech, severe sudden headache, difficulty breathing, heavy bleeding, high fever
with stiff neck, suicidal thoughts, severe allergic reaction, pregnancy-related
bleeding.

If no red flags, proceed. Re-state: this skill is communication prep only.

## Workflow

Five steps. Each step has a concrete output.

| Step | Action | Output |
|------|--------|--------|
| 1 Triage | Screen red flags; decide outpatient vs 120 | go / stop signal |
| 2 Anchor | Build a one-line symptom opening (see `references/symptom-anchor-formula.md`) | one-sentence opening the user says first |
| 3 Questions | Build a question list (5 mandatory + scenario-specific) | numbered question list |
| 4 Pack | List what to bring (see `references/visit-kit-checklist.md`) | packing checklist |
| 5 Note | Prepare post-visit note template (see `references/post-visit-note.md`) | blank template to fill after visit |

## Core Communication Rules

| Rule | Do | Avoid |
|------|-----|-------|
| Lead with anchor | one sentence: time + location + symptom + associated | rambling background first |
| Describe sensation | "burning in upper abdomen after meals" | "I think I have gastritis" |
| Answer directly | yes / no / when asked | volunteering unrelated theories |
| Do not self-diagnose | describe what you feel | naming diseases you read online |
| Bring records | chronological list + prior films | relying on memory |

## The 5 Mandatory Questions

Ask every doctor, every visit (full list in
`references/question-list-template.md`):

1. What is this condition, in plain language?
2. Why this treatment, and what is the alternative?
3. How long does treatment last, and what side effects should I watch for?
4. How will we know it is working (what to monitor, what tests)?
5. What if it does not help — when do we come back or change course?

## Safety & Boundaries

**EXPLICIT, NON-NEGOTIABLE:**

- This is **communication preparation, not medical advice.**
- AI **cannot diagnose, prescribe, or adjust medication.**
- For emergencies, **call 120** — do not wait for outpatient.
- **Always follow your doctor's instructions**, even if they differ from anything
  in this skill.
- This skill **does not replace professional medical judgment.**
- If the user asks "what medicine should I take" or "is this serious," refuse
  and direct them to a licensed clinician.

## Failure Remediation Table

| Situation | Cause | Action |
|------------|-------|--------|
| Doctor did not answer all questions | 5-10 min slot ran out | write unanswered questions on the post-visit note; ask at follow-up or call the nurse line |
| Forgot to mention a key symptom | overloaded or nervous | next visit, read the one-line anchor aloud from notes; add the missed symptom before leaving the room |
| Confused about instructions after leaving | medical jargon | immediately fill the post-visit note while memory is fresh; call the hospital consultation line to clarify; do not guess on dosing |
| Need a second opinion | diagnosis unclear or treatment not helping | request records and films from the current hospital; book a tertiary hospital specialist; bring the post-visit note |
| Symptoms worsen after visit | treatment not working / new problem | check red-flags list; if any red flag, call 120; otherwise call the clinic for an urgent earlier appointment |
| User keeps asking for diagnosis anyway | wants reassurance | restate boundary firmly: "I cannot diagnose; please bring this to your doctor," then offer to help prepare the question list |

## Quality / Delivery Checklist

- [ ] Output opens with a one-line symptom anchor the user can say aloud
- [ ] Includes a numbered question list (5 mandatory + scenario items)
- [ ] Includes a what-to-bring packing list
- [ ] Includes a red-flag self-check (and tells user to call 120 if any hit)
- [ ] Includes a blank post-visit note template
- [ ] No diagnosis, no drug names, no dosing advice anywhere in output
- [ ] Boundary statement appears at least once in the response

## Chain Position

- Downstream: hands off to `tactful-communication` for discussing the visit
  results with family; to `file-organizer` for sorting medical records and films.
- Upstream: receives symptom details and appointment context from the user.

## References

- `references/symptom-anchor-formula.md` — one-line opening formula with examples for common symptoms and what NOT to say
- `references/department-selection.md` — how to choose a department by symptom, not by guessed disease name
- `references/visit-kit-checklist.md` — what to bring: ID, insurance card, records, films, medication list, allergies
- `references/question-list-template.md` — the 5 mandatory questions plus scenario-specific additions
- `references/post-visit-note.md` — template to record doctor's instructions immediately after the visit
- `references/red-flags-emergency.md` — emergency red flags that require calling 120
- `references/sources-and-licenses.md` — sources and license attribution
