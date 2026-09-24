---
name: prompt-injection-guard
description: >
  Detect and defend against prompt injection / jailbreak attempts in untrusted
  input fed to LLMs. Use when the user asks for prompt-injection detection /
  jailbreak protection / jailbreak defense / prompt injection / anti-injection /
  input sanitization / malicious-prompt identification / prompt security review /
  multilingual injection / indirect injection. Do NOT use for red-team penetration (this is detection,
  not attack generation) or for fine-tuning / alignment research; it scans text
  input, flags suspicious patterns, and emits a verdict.
license: Apache-2.0
compatibility: "Pure Python 3 stdlib, offline, zero deps, zero network. Read-only: only reads the target text and writes a verdict report; never mutates input. No credentials required."
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: security
  pattern: script
  tier: powerful
  verified-date: "2026-09-20"
---

# Prompt Injection Guard

**Prompt injection / jailbreak** detection for "untrusted input fed to LLMs"
(web page text, emails, scraped content, user submissions, tool return values).
Recognizes 7 injection pattern classes: direct instruction override, role-play jailbreaks,
encoding obfuscation (base64/rot13/hex), multilingual code words, indirect injection ("ignore the above" style),
data-exfiltration lures, and spoofed system messages. Outputs a 0-100 risk score + hit list + handling recommendation.
Core principle: **default to read-only dry-run; hits are reported, not blocked; blocking is the caller's decision.**

**Distinct from pii-redactor**: that one redacts personal data. This skill defends against "instruction-layer" attacks —
cleaning data-layer PII ≠ stopping injection; the two are independent and should be chained.

## Input Checklist

| Input | Required | Description |
|------|------|------|
| Text to inspect | Yes | A string or file path (web page body / log line / tool output) |
| Source category | No | `web` / `email` / `user_input` / `tool_result`; affects weighting |
| Language | No | Auto-detected; can be set to `zh` / `en` / `multi` |
| Threshold | No | The risk-score cutoff, default 50 (≥ is judged high-risk and needs a human) |
| Dry run | No | `--dry-run` (on by default): only emit a report, write no file |

(Missing-input prompt template: "Please provide: (1) the text or file path to inspect; (2) source category (web / email / user_input / tool_result, default web); (3) language (zh / en / multi, default auto). Everything else uses defaults: dry-run on, threshold 50.")

## Pre-flight Checks

```bash
python3 -c "import sys; sys.exit(0 if sys.version_info>=(3,8) else 1)" \
  && echo "python>=3.8 OK" || echo "Python 3.8+ required"
```
Expected: prints `python>=3.8 OK`. On failure → upgrade or switch environment and stop.
Runs offline, reads no secrets, sends nothing over the network (red line: injection defense must never send the inspected text out).

## Workflow

### Step 1: Load the text to inspect
Single file: read it in; multiple files: line by line / block by block.
Expected: get the string to inspect; if the path doesn't exist → `PATH NOT FOUND` and stop.

### Step 2: Scan the 7 pattern classes
Run `scripts/injection_scan.py --dry-run <text_or_file> [--source web] [--threshold 50]`.
Expected: stdout JSON report `{score, verdict, hits:[{category, line, snippet, weight}], recommendations}`;
`verdict ∈ {clean, low, medium, high, critical}`.
On failure: `SYNTAX` → rerun the pre-flight check; a `JSON` parse error → the input has bad bytes; clean it first.

### Step 3: Tiered handling
Decide by `verdict` (executed by the caller; this skill only recommends):
Expected: `clean`→ pass through; `low/medium`→ human review; `high/critical`→ block + log the sample.
On failure: too many false positives (flagging normal technical docs as high) → raise `--threshold`, or use `--source user_input` to lower weighting.

### Step 4: Persist the report (non-dry-run)
`scripts/injection_scan.py <text> --out <report path>`.
Expected: `REPORT: <path> (score=N, verdict=X)`, source text bytes unchanged.
On failure: output not writable → change `--out`.

## 7 Injection Pattern Classes Cheat Sheet

| Class | Typical signal | Weight |
|------|---------|------|
| `direct_override` | "ignore previous instructions / disregard above" | High |
| `roleplay_jailbreak` | "pretend to be / now you are an unrestricted" | High |
| `encoded_payload` | A long base64/rot13/hex string appears + "decode" | High |
| `indirect` | Instructions embedded in a tool return value ("please continue / now run this command") | Medium |
| `data_exfil` | "send me the above secret/password/data / POST the secret to" | High |
| `system_spoof` | A fake `<system>` / `### System:` block | High |
| `multilingual_lure` | Mixed Chinese/English, Chinese/Japanese, or Chinese/Russian code words (instructions mixing languages) | Medium |

> Weights are initial values; hits stack; for source `tool_result`, the indirect weight gets +20.

## Failure Handling Table

| Symptom / error code | Cause | Action |
|---|---|---|
| `PATH NOT FOUND` | The input file doesn't exist | Double-check the path; a single text can be passed directly as a string |
| `SYNTAX` | Python <3.8 | Upgrade via the pre-flight check |
| False positive (normal technical text judged high) | Coincidental keyword match | Raise `--threshold`; `--source user_input` lowers automatic weighting |
| False negative (injection not recognized) | New variant / encoding obfuscation | Turn on `--strict`; manually review hits and add patterns |
| `JSON` parse error | Input has bad bytes | Clean it with `iconv`/`textwrap` first, then feed it |

## Delivery Criteria

- dry-run: stdout JSON report (`score` / `verdict` / `hits` / `recommendations`), nothing persisted.
- non-dry-run: produce the `--out` report file, stdout `REPORT: <path> (score=N, verdict=X)`, source text shows no `git diff`.
- Verification method: `verdict` is consistent with the hit categories; `hits[].snippet` can be manually traced back to the source line number.

## References

- `references/injection-patterns.md` — the full word library (Chinese and English) for the 7 pattern classes, the weight table,
  adversarial samples, handling SOPs, and how to chain with pii-redactor.
- `scripts/injection_scan.py` — the execution entry point: `--dry-run` emits JSON, `--out` persists,
  `--source` source weighting, `--threshold` cutoff, `--strict` tightening. Run it rather than hand-copying the rules.
