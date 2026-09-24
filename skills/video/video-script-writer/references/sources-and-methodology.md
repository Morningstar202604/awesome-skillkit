# Sources & Methodology — video-script-writer

Trust discipline for SKILL.md tacit knowledge 1–7: the short-video track has no academic-literature
layer; this round researched **practitioner methodology materials**. The processing rule:

> **What can be cross-validated is written as consensus; anything single-sourced or carrying
> marketing numbers is downgraded or rejected outright.**

## Sources and trust

| Tacit knowledge | Source nature | Degree of trust |
|---|---|---|
| 1. The first 3 seconds are the golden window | Short-video practitioner methodology (multiple sources agree; known in the industry as the "golden 3 seconds") | Trust the **concept**: the first 3 seconds decide retention |
| 1b. Six hook types (pain point / result-first / counter-intuitive / number / question / benefit promise) | Hook taxonomy distilled from practitioner materials | Trust it: the taxonomy is an actionable writing tool |
| 1c. **Specific numbers** like "X% drop-off in 3 seconds" / "Y% completion-rate lift" | Sources disagree and have no verifiable origin | **Rejected**: not written into SKILL.md (see trust discipline below) |
| 2. One CTA per video | Practitioner consensus (splitting attention = no CTA) | Trust: a principle-level conclusion |
| 3. Chinese voiceover speech rate 4–5 chars/sec | Common broadcast/voiceover rule of thumb (news-bulletin style is faster) | **Downgraded trust**: marked as a guideline; varies widely across hosts; only used for line-capacity budgeting |
| 4. Division of labor between voiceover and picture (show, don't say) | The migration of "Show, don't tell" into the short-video context | This group's restatement, not any one source's original text |
| 5. Loop design (meme type) | Practitioner consensus (head-tail seam raises looped replays) | Trust: a principle-level conclusion |
| 6. The thumbnail/title promise must be delivered in the first 3 seconds | Common content-operations practice | Common line: trusted as distilled from practice |
| 7. Compliance (extreme-word bans / engagement bait / efficacy promises) | Public facts from ad law and mainstream platform rules | Trust: verifiable regulatory/platform facts; specific categories defer to the platform's latest public notice |

## Trust discipline

1. **No "effect promise" carrying a percentage is ever trusted**: the short-video field circulates
   plenty of numbers like "X seconds in, 80% drop off" / "adding a hook raises completion by 45%";
   most come from course/tool marketing pages, contradict each other, and disclose no experiment →
   this skill rejects them all, and SKILL.md explicitly states "no percentages cited."
2. **Speech-rate numbers are downgraded to a range**: 4–5 chars/sec is used as a budgeting tool and
   stated as a guideline—it serves the verifiable goal of "don't overload the lines," not a precise
   phonetic parameter.
3. **Platform rules carry a time stamp**: the caps in `PLATFORM_RULES` (e.g. douyin 60s) are engineering
   constants; platform rules change, so defer to the platform's public notice at delivery time.

## Script-behavior measurement record (2026-09-22, evidence for the honesty statement)

| Fact | Measured value |
|---|---|
| Template-track dialogue | Self-describing placeholder (`[role] Attention grabber about: concept`), `dialogue_source="template"` |
| LLM-track trigger | `SKILLKIT_LLM_URL` + `SKILLKIT_LLM_KEY` (optional MODEL); on failure it falls back to the template and records `llm_note` |
| `visual` field | Always the placeholder `[role: describe visual action here]` |
| `sfx` | Only the hook/punchline/outro have values; the rest are empty strings |
| Duration invariant | Each scene ≥1s; the sum of scenes == total_duration; **a scan of 300 sets (5 types × 1–60s) found zero violations** |
| Over platform cap | Truncates and writes `duration_note` (recording `requested_duration`), not silently |
| Target < number of scenes | Raises to the scene count and writes `duration_note` |
| caption | Auto-assembled (with an emoji prefix); `caption_check` reports length/cap/tag count/compliance |
| Illegal platform | Silently falls back to douyin |
| tts speech-rate parameter | funny=1.2, everything else=1.0 (passthrough generation parameter, not a suggested speech rate) |

> Purpose of the record: let SKILL.md's "honesty statement" be independently re-checkable; whenever
> any item disagrees with the code, the code wins and the docs are revised back.
