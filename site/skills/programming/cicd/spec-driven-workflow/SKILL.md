---
name: spec-driven-workflow
description: "Use when the user asks to write a spec before code, write specifications, define acceptance criteria, do spec-driven development, plan features before implementation, generate tests from specifications, or follow spec-first development practices. Do NOT use for free-form coding without a written spec."
license: Apache-2.0
compatibility: Requires network access. No API keys required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: cicd
  pattern: single-task
  tier: powerful
  verified-date: "2026-09-09"
---

# Spec-Driven Workflow

Enforces spec-first: write the spec before any code, extract test stubs from acceptance criteria after validation passes, then implement one item at a time. Every line of code traces back to a requirement in the spec.

**Iron Law:**

```text
NO CODE WITHOUT AN APPROVED SPEC.
NO EXCEPTIONS. NO "QUICK PROTOTYPES." NO "I'LL DOCUMENT IT LATER."
```

Why spec-first: resolving ambiguity in a spec takes minutes; discovering it in production takes days; the spec *is* the definition of "done"; acceptance criteria translate 1:1 into test cases.

## Input Checklist

| Input | Required | Description |
|---|---|---|
| Feature name and description | Yes | The seed for generating the spec template, e.g. `--name "User Authentication" --description "OAuth 2.0 login flow"` |
| Requirements source | Yes | User-interview notes, existing code, constraints (performance budget/security/compatibility) |
| Test framework | No | pytest / jest / go-test (test_extractor's `--framework`); defaults to pytest |
| Spec storage path | No | e.g. named by feature under specs/ (see delivery criteria); defaults to project convention |
| Spec status | Required at the implementation stage | Draft / In Review / **Approved** (no implementation before Approved) |

When inputs are missing, ask for all at once: "Please provide: (1) feature name and one-line description; (2) key requirements/constraints/explicit non-goals; (3) test framework (pytest/jest/go-test)."

## Pre-flight Checks

Run line by line; on any failure → fix per the remediation and STOP:

```bash
# 1. Python 3 is available
python3 --version
# Expected: Python 3.8+.

# 2. Both tool scripts exist
ls scripts/spec_generator.py scripts/test_extractor.py
# Expected: both filenames (run inside the skill directory). On failure: cd to the skill directory; still missing → STOP and report.
# Note: this skill has no spec_validator.py — spec completeness is validated manually by the Step 3 checklist.

# 3. The reference templates are in place
ls references/spec_format_guide.md references/acceptance_criteria_patterns.md references/bounded_autonomy_rules.md
# Expected: all three filenames. Missing → STOP and report an incomplete repo.
```

## Workflow

### Step 1: Collect requirements

- **Action**: interview the user (what problem it solves, who the user is, what success looks like, what is explicitly not being built); read existing code to understand the current state; record constraints and all unknowns.
- **Expected**: you can explain the feature in 2 minutes to someone unfamiliar with the project; unknowns are listed as a checklist.
- **On failure**: the requirement owner can't answer core questions → escalate the questioning per the bounded-autonomy rules (see references), STOP.

### Step 2: Generate and write the spec

```bash
python3 scripts/spec_generator.py --name "User Authentication" --description "OAuth 2.0 login flow" --output specs/auth.md
```

- **Action**: using the generated template as a base, fill all 9 sections (write "N/A — reason" where not applicable): Title/Metadata, Context, Functional Requirements (RFC 2119 keywords, FR-N numbering), Non-Functional Requirements (measurable thresholds), Acceptance Criteria (Given/When/Then, each AC referencing at least one FR-*/NFR-*), Edge Cases (EC-N, covering the failure mode of every external dependency), API Contracts (TS-style interfaces, including success and error responses), Data Models (tabular: field/type/constraint), Out of Scope (explicit exclusions + reasons).
- **Expected**: the spec file is generated at the `--output` path, with all 9 sections non-empty and numbering complete.
- **On failure**: the generator output is missing sections → hand-fill them per the template in `references/spec_format_guide.md`.

### Step 3: Validate the spec

Check off the manual checklist item by item (this skill has no automatic validator; this checklist is the gate):

- [ ] Every functional requirement has at least one acceptance criterion
- [ ] Every acceptance criterion is machine-verifiable (no subjective wording)
- [ ] API contracts cover every endpoint mentioned in the requirements
- [ ] Data models cover every entity mentioned in the requirements
- [ ] Edge cases cover every external dependency's failure mode
- [ ] Out of scope explicitly records things "considered but excluded"
- [ ] Every non-functional requirement has a measurable threshold

- **Expected**: all seven checked.
- **On failure**: any item unmet → revise the spec and re-check; submit for review, and only advance to Step 4 once status reaches **Approved**.

### Step 4: Generate tests from acceptance criteria

```bash
python3 scripts/test_extractor.py --file specs/auth.md --framework pytest --output tests/test_auth.py
```

- **Action**: extract test stubs from the spec's acceptance criteria and edge cases (define assertions, no implementation); `--json` emits a structured list.
- **Expected**: the test file is generated at the `--output` path, and all tests fail with "not implemented" or equivalent (TDD red).
- **On failure**: the extraction misses an AC → hand-add a test stub so every AC and EC has a corresponding test.

### Step 5: Implement one item at a time

- **Action**: pick the simplest AC → write the minimum code to make its test pass → run the full suite to prevent regressions → commit → next.
- **Expected**: each AC's test turns green one by one; no regressions in the full suite.
- **On failure**: implementation reveals a missing requirement in the spec → STOP, update the spec first and return to Step 3 for re-review; never opportunistically implement out-of-spec content.

### Step 6: Self-review

Before marking implementation done, check:

- [ ] Every AC has a passing test; every EC has a test
- [ ] No scope creep (out-of-spec content is either deleted or the spec is updated first)
- [ ] API contracts match the implementation field by field (names, types, status codes)
- [ ] Every error response defined in the spec has a test that triggers it
- [ ] NFRs have evidence of meeting them (benchmark/load test/profiling)
- [ ] The database schema matches the spec; Out of Scope hasn't leaked into the implementation

- **Expected**: all six checked.
- **On failure**: any item unmet → fix and re-review; don't declare done.

### Bounded Autonomy (throughout)

STOP and ask: scope creep (things not in the spec, even if "obviously needed"), ambiguity over 30%, a need for breaking changes, anything touching auth/encryption/PII, non-measurable performance metrics, unconfirmed cross-team dependencies.
May proceed autonomously: the spec is explicit and unambiguous, all ACs have passing tests and only refactor internals, the change is non-breaking, the implementation is a direct translation of the AC, and error handling follows existing codebase patterns.
When escalating you must provide: the blocked requirement number, the specific problem, options with Pros/Cons, a recommendation, and the impact of waiting. See `references/bounded_autonomy_rules.md`.

## Tool Quick Reference

| Script | Purpose | Key parameters |
|--------|---------|-----------|
| `spec_generator.py` | Generate a spec template from a feature name/description | `--name` (required), `--description`, `--output/-o`, `--format md\|json` |
| `test_extractor.py` | Extract test stubs from acceptance criteria | `--file/-f`, `--framework pytest\|jest\|go-test`, `--output/-o`, `--json` |

## Failure Handling Table

| Symptom / error code | Cause | Fix |
|---|---|---|
| Extracted tests miss an AC | The spec's Given/When/Then format is non-standard | Rewrite that AC per `references/acceptance_criteria_patterns.md` and re-extract |
| The spec was rejected in review but code already exists | The Iron Law was violated by coding first | Stop implementing, rewrite the spec per the review verdict, discard or redo the code |
| Implementation needs an out-of-spec change | Scope creep | STOP → update the spec → re-review; no acting first |
| An NFR can't be verified | The threshold isn't measurable | Return to Step 3 and rewrite the threshold as a measurable metric (e.g. "p95 < 500ms") |
| `spec_generator.py` reports `--name` missing | A required parameter was omitted | Add `--name` and rerun |

## Delivery Criteria

- Definition of success: an Approved spec (9 sections complete, numbering intact) + all test stubs + all tests green + the self-review checklist fully checked.
- Artifact naming: spec at `specs/<feature>.md`; tests at `tests/test_<feature>.py` (or the corresponding framework convention).
- Save location: the paths above within the project, or a user-specified location.
- Completeness verification: the AC/EC list output by `python3 scripts/test_extractor.py --file specs/<feature>.md --json` maps 1:1 to the numbering in the spec; every test name in the test file traces to an AC or EC number.

## References

- `references/spec_format_guide.md` — the full 9-section template, good/bad requirement pattern comparisons, CRUD/Integration/Migration type templates, and a complete Password Reset example; read before writing the spec in Step 2.
- `references/acceptance_criteria_patterns.md` — a Given/When/Then acceptance-criteria pattern library (auth/CRUD/search/upload/payment, etc.); read when an AC can't be written or gets bounced in review.
- `references/bounded_autonomy_rules.md` — the full decision matrix for when to stop and ask vs proceed autonomously; read when hitting edge cases during execution.

## Anti-patterns

| # | Anti-pattern | Consequence | Rule |
|---|---|---|---|
| 1 | Writing code before review passes | Post-review changes mean the code implements the rejected design | No implementation until spec status is Approved |
| 2 | Vague acceptance criteria ("fast response", "great UX") | Can't be tested | Only keep machine-verifiable ones; otherwise rewrite |
| 3 | Missing edge cases | Developers invent error handling on the fly | At least one failure scenario per external dependency |
| 4 | Backfilling the spec after the fact | That's documentation, not a spec; it can't catch design errors | Code written afterward can only be labeled documentation |
| 5 | Out-of-spec gold-plating | Bonus code without tests or review | If it's not in the spec, don't build it; write a new spec |
| 6 | An AC references no FR/NFR | An orphan criterion, either a missing requirement or redundant | Every AC must reference at least one FR-*/NFR-* |
| 7 | Skipping validation and starting work | Missing sections surface only during implementation, causing blocks | Don't enter Step 4 until the Step 3 checklist is all checked |

## Related Skills

- **`engineering-team/tdd-guide`** — red-green-refactor discipline, coverage analysis; use after Step 4.
- **`engineering/focused-fix`** — for diagnosing systematic problems that arise during spec-driven implementation.
- **`engineering/rag-architect`** — technical design when the feature involves retrieval/knowledge systems.
