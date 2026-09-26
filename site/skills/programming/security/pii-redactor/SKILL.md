---
name: pii-redactor
description: >
  Detect and redact personally identifiable information (PII) in logs, chat
  transcripts, files, and structured data before sharing or logging. Use when
  the user asks to redact PII / scrub sensitive data / PII detection / mask data /
  privacy cleanup / compliant logging / GDPR redaction / anonymize logs / mask PII /
  redact personal data / scrub PII / ID card / phone number / email redaction.
  Do NOT use for encryption at rest, key management, or secret
  rotation (use secrets-vault-manager / env-secrets-manager); this skill
  redacts already-visible text and structured fields.
license: Apache-2.0
compatibility: Pure Python 3 stdlib (no third-party deps). Read-only scan by default; redaction writes a NEW output file, never mutates the source. Credentials not required.
metadata:
  version: "1.1"
  author: awesome-skillkit
  category: security
  pattern: script
  tier: powerful
  verified-date: "2026-09-21"
---

# PII Redactor

PII detection and redaction for logs, chat transcripts, tickets, and structured data (CSV/JSON).
Covers 8 PII classes: ID card / phone number / email / bank card / name / address / license plate / unified social credit code.
Core principle: **default to a read-only dry-run scan; redaction produces a new file; the source file is never rewritten.**

**Distinct from secrets-vault-manager**: that one manages secret infrastructure. This skill manages redaction of personal data in "already-visible text" —
it does not touch keys, does no encryption, and does not go online.

## Input Checklist

| Input | Required | Description |
|------|------|------|
| Target file / directory | Yes | The path to scan; a directory is scanned recursively for text files |
| PII classes | No | All 8 by default; a subset can be specified (e.g. only redact `id_card` + `phone`) |
| Redaction strategy | No | `mask` (keep first/last 1-4 chars) / `hash` (first 8 chars of SHA-256) / `replace` (substitute a placeholder), default `mask` |
| Output file | No | Path for the redacted result; defaults to `<original>.redacted` |
| Dry run | No | On by default: only report hits, write no file. Pass `--execute` to persist; `--dry-run` is kept as an explicit no-op |

(Missing-input prompt template: "Please provide: (1) the file or directory path to scan; (2) the PII classes to redact (default all 8); (3) the redaction strategy (mask / hash / replace, default mask). Everything else uses defaults: dry-run on, output `<original>.redacted".)

## Pre-flight Checks

```bash
python3 -c "import sys; sys.exit(0 if sys.version_info>=(3,8) else 1)" \
  && echo "python>=3.8 OK" || echo "Python 3.8+ required"
```
Expected: prints `python>=3.8 OK`. On failure → prompt to upgrade Python or switch to a compatible environment and stop.
No network, no environment-variable credentials needed (red line: this skill does not read any secrets).

## Workflow

### Step 1: Determine the input shape
Decide whether it is a single file or a directory.
Expected: get a file list (for a directory, recurse over `*.log *.txt *.json *.csv *.md`, skipping binary and hidden files).
On failure: the path does not exist → report `PATH NOT FOUND: <path>` and stop.

### Step 2: Dry-run scan (default)
Run `scripts/pii_scan.py <path> [--categories phone,id_card]`.
Expected: stdout prints one hit per line `L<line>\t<category>\t<redacted preview of original>\t<file>`; the last line is `SUMMARY: N hits across M files`.
On failure: the script reports `SYNTAX` or a missing dependency → see the failure-handling table.

### Step 3: Review hits
Manually spot-check 3-5 hits to confirm there isn't a flood of false positives (e.g. `1001234` misread as a phone number).
Expected: false-positive rate <10%; if a class has high false positives → tighten rules with `--no-heuristics` or exclude that class.
On failure: severe false positives → use `--categories` to keep only high-confidence classes, then rerun Step 2.

### Step 4: Persist the redaction (non-dry-run)
After confirmation, run `scripts/pii_scan.py <path> --strategy mask --out <output file> --execute`.
Expected: stdout shows `REDACTED: <output file> (N hits masked)`, and the source file's bytes are unchanged (verify with `diff` or `git status`).
On failure: the output directory is not writable → report `PERM` and suggest changing `--out` to a writable path.

## Detection Rules Cheat Sheet

| Class | Regex signature | Default mask form |
|------|---------|---------------|
| `id_card` | 18 digits `\d{17}[0-9Xx]`, checksum passes | `1101***********123` |
| `phone` | `1[3-9]\d{9}` (incl. `+86`) | `138****5678` |
| `email` | Standard email | `j***@example.com` |
| `bank_card` | 13-19 digits passing Luhn | `6222********0123` |
| `plate` | Chinese license plate: one CJK province-abbreviation char, `[A-Z]`, `\d{5,6}`, optional suffix CJK char | `A*****1` |
| `credit_code` | 18-digit unified social credit code | `91110000***` |
| `address` | Province/city/district/road-number combos (heuristic) | `[ADDR MASKED]` |
| `name` | Heuristic only (context contains a "name/contact" key) | `[NAME MASKED]` |

> `name` and `address` are heuristic classes with the highest false-positive rate; they are not enabled standalone by default and require explicit `--categories name,address`.

## Redaction-Strategy Dark Knowledge (picking the wrong strategy = redacting for nothing)

1. **The three strategies have completely different security semantics; pick by data sensitivity, not habit**:
   - `mask` (`138****5678`): keeps the head and tail. Suits **human-verification scenarios** (customer callbacks need to recognize the number segment), but the last 4 digits + segment combo can still narrow the population in real-name scenarios.
   - `hash` (first 8 chars of SHA-256): **is not anonymization**. The Chinese phone-number space is only ~10^10, so an attacker can offline-enumerate all numbers and build a rainbow table for reverse lookup (compute cost is very low); the same applies to bank cards/ID cards. hash only defends against "naked-eye reading", not "deliberate reverse lookup".
   - `replace` (`[REDACTED:phone]`): zero residual, **the only safe choice before external publication / public sharing**. The trade-off is lost format information and no ability to trace back.
2. **Checksum digits are the first false-positive gate**: ID cards go through a mod11 check, bank cards through Luhn — random digit strings are mostly caught. But `phone` only validates the leading digit (1[3-9]), so long digit strings like ticket numbers and order numbers easily false-match; the review step cannot be skipped.
3. **The dry-run stdout reports only the first hit per line**; a line with multiple PII classes isn't reported repeatedly; rely on the final `SUMMARY` line for totals.
4. **Re-scan verification is part of delivery**: rerun dry-run on the redacted artifact; strong-check classes (id_card/bank_card/credit_code) must have 0 hits; under the `replace` strategy, all classes should be 0.

## Red Lines (crossing these defeats the skill's purpose)

1. **Never rewrite the source file** — redaction writes only a new file; the source bytes are unchanged (verifiable with `git status`).
2. **Do not call mask/hash artifacts "anonymized data"** — in compliance contexts (GDPR/PIPL) they are still personal data, merely "de-identified"; true anonymization requires replace-level + irrecoverability.
3. **Do not enable name/address heuristics by default** — high false-positive rate, and names in free text can't be exhaustively covered, so enabling them doesn't fully catch them anyway.
4. **Do not promise "detection completeness"** — this skill reduces the exposure surface, it is not a compliance certification; unrecognized PII (e.g. colloquial nicknames, indirect identifiers) always exists.
5. **Multi-file merged output must preserve the `===== filename =====` boundary lines** (the script adds them automatically since v1.1) — losing file attribution after redaction is just creating new data chaos.

## Failure Handling Table

| Symptom / error code | Cause | Action |
|---|---|---|
| `PATH NOT FOUND` | The input path doesn't exist or is misspelled | Double-check the path with `ls`; for a directory, drop the filename |
| `PERM` | The output path isn't writable | Change `--out` to a directory the user can write to |
| 0 hits but PII is visible to the eye | A class wasn't enabled / text is escaped | Add all via explicit `--categories`; check for URL-encoding or JSON escaping (`\u00XX`) that needs decoding first |
| Flood of false positives | Digit strings coincidentally match | Add `--no-heuristics` to keep only strong-regex check classes (id_card/phone/bank_card/credit_code/plate) |
| `SYNTAX` | Python version too old | Rerun the Step 1 pre-flight check; upgrade to 3.8+ |

## Delivery Criteria

- dry-run: stdout hit list + `SUMMARY` line, nothing persisted.
- with `--execute`: produce `<output file>` (default `<original>.redacted`), stdout `REDACTED: <file> (N hits)`.
- Verification method: rerun dry-run on the output file; hit count should be 0 (strong-check classes); the source file shows no `git diff`.

## References

- `references/pii-rules.md` — the full regex set for the 8 PII classes, checksum algorithms (Luhn / ID-card mod11), false-positive case comparisons, and JSON/escaped-text preprocessing.
- `scripts/pii_scan.py` — the execution entry point: reports hits by default (dry-run), `--execute` persists redaction to `--out`, `--categories` selection, `--no-heuristics` tightening. Run it rather than hand-copying the algorithms.
