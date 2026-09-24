# TTS Voice Parameters (video-voice-synth)

**Parameter names and value ranges depend heavily on the TTS engine you actually use.** The names
given here (`speed` / `pitch` / `emotion` / `break`) are common conventions, not a standard.
Anything not confirmed in your engine's documentation must be marked `VERIFY BEFORE USE`,
along with how to verify it.

## Table of Contents

0. Verify your engine first / 1. Speech rate speed / 2. Pitch / 3. Emotion / 4. Pauses and phrasing
5. Chinese polyphonic characters and number reading / 6. Voice selection by scene / 7. Parameter presets / 8. Pre-delivery self-check

## 0. Verify your engine first

Before tuning any parameter, run a probe call to find out exactly what this engine accepts:

```bash
# 1) Check whether there is a voices/capabilities endpoint (path names depend on your gateway, VERIFY BEFORE USE)
curl -sS -m 10 -H "Authorization: Bearer ${GATEWAY_API_KEY}" "$GATEWAY_BASE_URL/v1/voices"

# 2) Run a parameter sweep with the same sentence, listen/measure the differences (speed from 0.8 to 1.4)
for s in 0.8 1.0 1.2 1.4; do
  curl -sS -m 30 -o "probe_$s.wav" -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${GATEWAY_API_KEY}" \
    -d "{\"text\":\"Nice weather today\",\"voice\":\"baby_f01\",\"speed\":$s,\"format\":\"wav\"}" \
    "$GATEWAY_BASE_URL/v1/tts"
  printf "speed=%s  " "$s"
  ffprobe -v error -show_entries format=duration -of default=nw=1 "probe_$s.wav"
done
```

Expected: duration should monotonically decrease as speed increases. If all four durations are identical,
the engine **does not recognize the `speed` field**—rerun using the actual parameter name from its
documentation (don't assume "setting it means it took effect").

## 1. Speech rate speed

There are two common forms; **first confirm which one your engine uses**:

| Form | Range | Meaning |
|---|---|---|
| Multiplier (most common) | `0.5` – `2.0`, `1.0` = original speed | Multiple of the original speech rate |
| Percentage | `50` – `200`, `100` = original speed | Same meaning, different unit (VERIFY BEFORE USE) |

Guideline values (Tier B, not hard standards):

| Scene | Recommendation | Reason |
|---|---|---|
| Fast-paced character voiceover (baby, mascot) | 1.15 – 1.35 | Short video needs density; too slow feels dragging |
| Regular narration | 1.0 – 1.1 | Balances clarity and rhythm |
| Tutorial/instructional | 0.9 – 1.0 | Viewers must follow along; too fast loses them |
| Emotional peak/twist | +0.1 over baseline | Local speedup creates urgency |
| Emphasis sentence | −0.15 over baseline | Local slowdown feels more natural than simply stressing |

Hard boundary: **above 1.5, clarity drops noticeably**, especially in Chinese (syllables get crushed).
Judgment criterion: blind-listen once after synthesis; if unclear, back off.

## 2. Pitch

Again two forms; **confirm the unit first**:

| Form | Range | Notes |
|---|---|---|
| Semitone shift | commonly `-12` – `+12`, `0` = original | Each ±1 is one semitone, ±12 is one octave |
| Multiplier / Hz (some engines) | varies by engine | VERIFY BEFORE USE, don't guess |

Guideline values:

| Goal | Suggested shift | Notes |
|---|---|---|
| Toddler feel (baby) | `+3` – `+7` | Higher distorts and sounds shrill |
| Adult female | `0` – `+2` | Minor tweak only |
| Adult male | `-2` – `0` | Minor tweak only |
| Narrator/neutral | `0` | Leaving it alone is safest |
| Villain/deep | `-4` – `-8` | Lower gets muddy |

**pitch and speed are often coupled**: raising pitch without speed sounds like "slow screaming,"
not like a child. When making a toddler voice, adjust both together (pitch +4 with speed 1.2 is a
common starting point, a guideline value).

## 3. Emotion

**This is the most variable item**: some engines use an `emotion` string, some use `style`, some
have none at all, and some can only express emotion through a reference audio / voice clone.
**VERIFY BEFORE USE**: check your engine docs for what it's actually called and what valid values are;
sending a value the engine doesn't recognize usually doesn't error—it **silently falls back to the
default emotion**, which is more dangerous than an error because you'll think the setting took effect.

Common values (only use when the engine explicitly supports them; don't assume):

| Value (example) | Suitable for | Notes |
|---|---|---|
| `neutral` | Narration, explanation | Safe default |
| `happy` / `cheerful` | Product promos, unboxing, mascot | Pair with `+speed` |
| `sad` | Setbacks, transition buildup | Pair with `−speed` |
| `angry` | Roasts, conflict | Use sparingly; fatiguing on long listens |
| `excited` | Climax, twist | Usually with `+pitch` |
| `serious` | Science conclusions, warnings | Pair with `−speed` |

Workaround for engines without emotion support: simulate with a speed + pitch + pause combination,
or change it at the copy level (add filler words, change punctuation)—this is the most reliable approach.

## 4. Pauses and phrasing

| Mechanism | Common syntax (VERIFY BEFORE USE) | Notes |
|---|---|---|
| Implicit punctuation pauses | `，` short pause, `。` long pause | Supported by almost all engines, most reliable |
| SSML `<break>` | `<break time="500ms"/>` | Requires engine to enable SSML support (**many gateways leave it off by default**) |
| Custom markers | `[break:500]`, `|` and the like | Completely engine-dependent, must test |
| Blank-line segmentation | Leave a blank line in the text | Some engines treat it as a paragraph pause |

**Recommended approach: prefer punctuation to control pauses**, don't rely on engine-private markers.
Reason: punctuation works on any engine; private markers break when you switch engines, and the
failure is usually silent (no error).

Guideline pause values (Tier B): 0.2–0.4s between sentences; 0.5–0.8s after a hook; 0.3–0.5s
before a twist; 0.4–0.6s between list items. Pauses **count toward duration**, so include them when
estimating total length (rule of thumb: total duration ≈ characters / speech rate / pause factor,
pause factor 1.10–1.25).

## 5. Chinese polyphonic characters and number reading

This is the most common failure point of Chinese TTS. Processing order: prevent first, then fix.

**Prevention (at the copy level, most effective)**:

| Problem | Example | Fix |
|---|---|---|
| Polyphonic character | The word for "bank" (háng) misread as yín xíng | Rephrase with a synonym: say "this branch" instead of "this bank" |
| Polyphonic character | zhòng-yào ("important") vs. chóng-xīn ("again") | When context can't disambiguate, swap words: use the clearer "once more" instead of the ambiguous "chóngxīn" |
| Numbers | "8900" read as "eight-thousand-nine-hundred" or "eight-nine-zero-zero" | Write amounts as a compact grouping; write serial numbers digit-by-digit |
| Years | "2026" | Usually read digit-by-digit ("two-zero-two-six"); don't write it as a big round number unless you want that reading |
| Percent sign | "30%" | Writing "thirty percent" out is safest |
| Decimal point | "3.5" | Write it out as "three point five" |
| Units | "5G" "iPhone 16" | In Chinese context spell out the digit ("five G", "iPhone sixteen") or annotate per engine docs |
| English abbreviations | "AI" "CPU" | Write uppercase for letter-by-letter reading; confirm engine behavior if you want it read as a word |
| Long digit strings | Phone numbers, order IDs | Add spaces/separators for digit-by-digit reading |

**Fixes (at the engine level, capabilities vary by engine, VERIFY BEFORE USE)**:

- SSML `<phoneme>` / `<say-as>`: the standard approach, but requires the engine to enable SSML.
- Custom lexicon / phoneme table: some engines support uploading a `word<TAB>pronunciation` lexicon file.
- Inline pinyin markup: some Chinese engines support annotating each character with tone-numbered pinyin (e.g. ni3-hao3).

**How to verify**: after synthesis, use `ffprobe` to check whether the duration is abnormal
(mispronounced polyphonic characters usually have normal duration, so **you must listen manually**),
or run a regression test on 10 error-prone words and record the results.

Small regression-test sample (run every time you switch engine/voice):
the word for "bank" (háng), "important" (zhòng), "again" (chóng), year "2026", "30%", "3.5 seconds",
"iPhone 16", "5G", "one third", and "8900" as an amount.

## 6. Voice selection by scene

The voice IDs below come from the Voice Catalog in this skill's SKILL.md; they are **only valid
if your gateway has registered a voice with the same name**. How to verify:
`curl -sS "$GATEWAY_BASE_URL/v1/voices"` and inspect the returned list (path depends on your
gateway, VERIFY BEFORE USE); if there's no such endpoint, test-synthesize a short sentence per voice.

| Voice ID | Characteristics | Best scenes | Not suited for |
|---|---|---|---|
| `baby_f01` | High pitch, fast | Baby podcasts, cute roasts, funny twists | Serious science, long explanatory sentences |
| `baby_f02` | Slightly lower, slower | Children's education, bedtime stories | Fast-paced roundups |
| `adult_m01` | Male voice, steady | Tutorials, vlogs, reviews | Cute characters, highly emotional segments |
| `adult_f01` | Female voice, warm | Product promos, reviews, lifestyle sharing | Villain/conflict characters |
| `mascot_01` | Enthusiastic, slightly mechanical | Mascots, animated characters | Realistic human narration |
| `narrator_01` | Neutral, clear | Voiceover, explanation, knowledge content | Content needing strong emotion |

Selection logic (use this when the table above doesn't apply):

1. First decide the **content type** (comedy / education / promo / explanatory);
2. Then decide **whether a character exists** (with a character → the voice should sound like that character; no character → pick a neutral narrator);
3. Finally decide **rhythm** (fast-paced content pairs with a fast voice, slow content with a steady voice);
4. **Don't switch voices frequently within one video**, except in dialogue scenes (in dialogue, fix one voice per character).

## 7. Parameter presets

| Goal | speed | pitch | emotion | Notes |
|---|---|---|---|---|
| Cute kid roast (30s short video) | 1.25 | +5 | happy/cheerful (if supported) | This repo's `baby_f01` defaults to speed 1.3 / pitch 5, usable as a starting point |
| Children's education | 1.0 | +4 | neutral | Slower for read-along |
| Knowledge narration | 1.0 | 0 | neutral / serious | Focus on clarity; don't add emotion |
| Product promo review | 1.1 | +1 | happy | Slightly faster feels energetic |
| Tutorial steps | 0.95 | 0 | neutral | Viewers must follow along |
| Twist/climax sentence | baseline +0.15 | baseline +2 | excited | Change only this sentence, not the whole video |

Use one consistent parameter set across the whole video, with only local tweaks on **individual
sentences**; an erratic speed across the whole video will be noticed.

## 8. Pre-delivery self-check

- [ ] Parameter names have been confirmed to **actually take effect** via the Section 0 sweep (duration changes with speed)
- [ ] The voice ID exists in the current gateway's voice list
- [ ] Each audio's duration deviates from the script `duration_sec` by < 0.5s
- [ ] The audio is not silent (`ffprobe -af volumedetect` shows `mean_volume` well above -91 dB)
- [ ] The error-prone regression sample has been listened through item by item; polyphonic characters/number readings are correct
- [ ] No reliance on private markers the engine doesn't support (when unsure, switch to punctuation)
- [ ] The result JSON does not have `mock` set to `true`
