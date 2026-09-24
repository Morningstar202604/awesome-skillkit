# Emotion Delivery Lexicon: Giving TTS Warmth (emotion-delivery-lexicon)

> Most TTS models don't have an "emotion slider"—**emotion lives in the script, not in the parameters**. This table translates emotion labels into executable script techniques + parameter settings.
> Iron rule: first change punctuation and sentence length (zero cost, guaranteed to work), then adjust speech rate (mild effect), and only finally consider switching to an engine that supports emotion parameters.

## 1. Emotion → Script Technique Mapping

| Emotion label | Script technique (edit the script) | Speech rate | Pause design |
|----------|-------------------|------|---------|
| Composed/authoritative | Medium-long sentences; avoid filler words; terms upfront | 0.95-1.0 | 400-600ms after periods (implement by splitting segments) |
| Excited/promotional | Extremely short sentences in a row ("Fast. Faster. Fastest."); numbers and exclamations upfront | 1.1-1.2 | No long pauses between short sentences |
| Whisper/intimate | Ellipses at sentence ends; use low-threshold openers like "look," "honestly" | 0.85-0.95 | Leave 800ms after ellipsis segments |
| Suspense/tension | Dash cuts ("He opened the door—"); delayed information release | 0.9-1.0 | 600ms after the dash before continuing |
| Sorrowful/nostalgic | Slow long sentences; repeat keywords ("That year. That winter.") | 0.85-0.9 | 500-700ms between sentences |
| Humorous/light | Colloquial filler words; self-ask-self-answer | 1.0-1.1 | Pause 300ms before the punchline |

## 2. Punctuation as Pauses (punctuation hierarchy = pause length)

TTS has a rough hierarchy of pause handling for punctuation; choose as needed when writing scripts:

| Punctuation | Pause feel | Use |
|------|--------|------|
| Enumeration comma 、 | almost none | list read-through |
| Comma ， | short | half-sentence breath |
| Period 。 | medium | complete pause within a segment |
| Dash —— | medium-long + suspended feel | cut-offs, suspense |
| Ellipsis …… | long and descending | whispers, wistfulness |
| Question mark ？ | medium + rising | interactive feel |
| Line break (segment split) | longest (controlled by concatenation gap) | chapter/topic switches |

**The concatenation gap is the biggest pause controller**: 500ms between segments is conversational rhythm, 800-1200ms is chapter feel, >1.5s is scene change.

## 3. Stress Position (information at sentence end, hooks at sentence start)

- TTS stress naturally falls on the **sentence end**—put the most important word at the end: "Today we're talking about something **that changes your perspective**" (where "something" is stressed → not ideal) → change to "What changes your perspective is **this thing**"
- Numbers, negatives, and transition words (but/actually) should be placed upfront—TTS clarity is highest for sentence-initial words
- To emphasize a word: make it a standalone short sentence ("Remember three words. **Slow down.**")

## 4. Dialogue Rhythm (for two-person podcasts only)

| Technique | Script writing | Effect |
|------|---------|------|
| Interjection | One person's sentence cut off mid-way ("So I think—" "Right, exactly") | Realism |
| Hesitation | Add "um…" "how should I put it" | Thinking, avoiding broadcast tone |
| Affirmation | "No way?" "Really?" as standalone short segments | Two-person anchor points |
| Argument escalation | Sentences get shorter and shorter | Conflict tension |

- Dialogue lines **each become their own segment** (the concatenation plan is laid out by line); adjacent lines crossfade 300-500ms
- Set the speech-rate difference between the two voices to 0.05+ (e.g. host 1.05 / guest 0.95), and the listening feel immediately separates

## 5. Parameter Quick Reference (Kokoro family / universal)

| Parameter | Setting | Notes |
|------|------|------|
| speed | 0.85 slow whisper / 1.0 baseline / 1.1 narration / 1.2 fast-paced | Outside 0.8-1.3, distortion likely |
| stability (supported engines) | high = steady but flat / low = lively but wandering | Narrative 0.7, dialogue 0.4-0.5 |
| voice design description | "scene + gender + texture": "low male voice in a library," "bright female voice like a subway station announcement" | Only for descriptive-generation models |

## 6. Failure Modes and Fixes

| Symptom | Root cause | Fix |
|------|------|------|
| Broadcast tone | All long sentences + all periods + rate 1.0 | Short sentences in a row + dashes + rate ±0.1 |
| Overwrought emotion (AI moaning feel) | Too many filler words ("Ah! Wow! Oh my god!") | Max 1 filler per segment; rely on rhythm for the rest |
| Machine-gun | No pause markers | Split segments + 500ms minimum between segments |
| Chanting feel | Parallel sentences all the same structure | Break up: alternate short-long-short |
| Key point eaten | Keywords mid-sentence | Make the keyword a standalone sentence or move to the end |
