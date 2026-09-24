# Duration and Timing Parameter Table (video-script-writer)

**All values in this document are guideline ranges, not hard platform standards, nor any vendor's
promise.** Their only use: provide a workable initial value when you have no measured data. Once you
have real TTS audio durations or platform backend data, **use the measured values and write them back.**

## Table of Contents

0. Confidence tiers of the numbers / 1. Recommended platform durations / 2. Speech rate and character-count conversion / 3. Shot-duration allocation
4. Pauses and breath gaps / 5. Timing validation: write measured values back

## 0. Confidence tiers of the numbers

| Tier | Meaning | Examples in this doc | How to use |
|---|---|---|---|
| A Measured | What you ran yourself | Actual TTS audio duration, `ffprobe` output | Use directly, overriding this doc's guidelines |
| B Guideline | Common industry practice (the bulk of this table) | Speech rate 4–6 chars/sec, shots 3–6s | As initial values; calibrate after one run |
| C Volatile | Platform rules, change anytime | Per-platform duration caps, tag-count caps | **VERIFY BEFORE USE**, must check before publishing |

How to tell whether a Tier-C value is outdated (don't rely on memory):

1. Open the platform's creator center / upload page; the upload page directly shows the current max duration and file size;
2. Check the platform's official help docs "video specs" / "upload requirements" pages;
3. Actually upload a 1-second test video and see whether it errors—the error message states the current limit.

## 1. Recommended platform durations

| Platform | Cap (Tier C, verify) | Recommended finished length (Tier B) | Notes |
|---|---|---|---|
| Douyin | 60s (short) / 15min (long) | 15–45s | Caps from this repo's SKILL.md notes, **verify before publishing**; shorter is safer under completion-rate pressure |
| TikTok | 10min | 15–60s | Same; the first 3 seconds decide everything |
| Bilibili | No hard cap | 60s–5min | Higher tolerance for medium-long content, but the first 15 seconds still need a hook |
| YouTube Shorts | — | 15–60s | This repo has no recorded cap; **don't guess**, verify with the Section 0 method |

Platforms not listed = this repo has no reliable record; **don't fill in from memory**. It's better
to leave it blank and let the user check than to write a fake number that looks professional.

Finished-length selection logic (works independent of platform caps):

- Single-point information → 15–30s (one hook + one twist)
- List/tutorial with 3 items → 45–60s
- Explainer with mechanism walkthrough → 60–90s

## 2. Speech rate and character-count conversion

**Conversion formulas** (Tier B guideline values, calibrate to your voice):

```
Estimated duration (sec) = characters / speech rate (chars/sec) × pause factor
Writable characters      = target duration (sec) × speech rate (chars/sec) / pause factor
```

| Parameter | Guideline value | Notes |
|---|---|---|
| Speech rate (Chinese) | 4–6 chars/sec | Fast-paced character voiceover uses 6; steady narration uses 4; news-broadcast style ≈5 |
| Speech rate (English) | 2.2–2.5 words/sec | ≈130–150 wpm, also a guideline range |
| Pause factor | 1.10–1.25 | Amplification for inter-sentence breath gaps and emphasis pauses; the choppier the sentences, the larger the value |

Example (30 seconds, Chinese fast-paced voiceover, rate 6, factor 1.15):

```
Writable characters = 30 × 6 / 1.15 ≈ 156 chars
```

Split into 4 shots per Section 3, averaging ≈39 chars per shot; but a talking-head single line must
be ≤15 chars, so a 39-char shot should be split into 2–3 short lines plus one action pause.

**Calibration method (strongly recommended once)**: take 30 Chinese characters, synthesize audio
with your actual voice, read the real duration with `ffprobe`, and back out your true speech rate:

```bash
ffprobe -v error -show_entries format=duration -of default=nw=1 scene_1.wav
# true speech rate (chars/sec) = characters / measured duration
```

Record this value and use it for all later estimates; the error will be noticeably smaller than the
generic range.

## 3. Shot-duration allocation

| Form | Single-shot length (Tier B) | Shot count (30s / 60s) | Cut rhythm |
|---|---|---|---|
| Talking-head (character to camera) | 3–6s | 5–7 / 10–14 | Cut at emotional turns, don't wait for the line to finish |
| Narrated (voiceover + B-roll) | 5–12s | 4–6 / 8–12 | One information point per shot |
| Tutorial/list | 10–18s | 2–3 / 4–6 | One step per shot; cut at step boundaries |
| Meme/reaction | 1.5–4s | 8–15 / 20+ | Fast cuts; the last shot loops back to the first frame |

Three-act proportions (Tier B):

| Act | Share | 30s video | 60s video |
|---|---|---|---|
| Hook | 10% | 3s | 6s |
| Body | 75% | 22s | 45s |
| CTA | 15% | 5s | 9s |

Hard constraint: **`sum(scenes[].duration_sec)` must strictly equal `total_duration`**, difference 0.
After allocating, do an addition check before delivering.

Allocation steps:

1. Set Hook / CTA values per the table above (30s video: 3s / 5s);
2. Divide the remaining 22s evenly across the Body shots by number of information points;
3. Round each shot to 0.5s, and add/subtract all rounding error to/from the **longest** shot (smallest change, least rhythm impact);
4. Add it all up again to confirm it equals the total duration.

## 4. Pauses and breath gaps

| Situation | Suggested pause (Tier B) | Why |
|---|---|---|
| Between sentences | 0.2–0.4s | Shorter than 0.2s TTS runs them together; longer than 0.5s drags |
| After the hook (asking a question, awaiting the answer) | 0.5–0.8s | Gives viewers reaction time; a low-cost way to raise completion |
| Before a twist/punchline | 0.3–0.5s | Silence builds expectation |
| Between points (list type) | 0.4–0.6s | Lets the "first/second" structure be heard |
| At shot cuts (visual already changed) | 0.3–0.5s | The visual switch itself consumes attention |

Note: pauses **count toward duration**. When writing dialogue, count characters from the body text,
then scale up the total duration by the pause factor; don't write pauses as separate "silence shots,"
or the subtitle timeline will have empty cues.

## 5. Timing validation: write measured values back

The duration calculated at the script stage is only an estimate. Once in TTS you must close the loop:

```bash
# Get the actual duration of each shot's audio
for f in scene_*.wav; do
  printf "%-14s " "$f"
  ffprobe -v error -show_entries format=duration -of default=nw=1 "$f"
done
```

| Deviation | Verdict | Action |
|---|---|---|
| Measured ≤ planned | Audio shorter than picture | The tail of the shot goes empty: shrink that shot's `duration_sec` to the measured value, or add B-roll |
| Measured > planned (<0.5s) | Acceptable | Just change `duration_sec` to the measured value |
| Measured > planned (≥0.5s) | Line too long | Cut characters and re-synthesize, or split that shot into two |
| Whole video measured >10% longer than planned | Wrong speech-rate assumption | Recalibrate speech rate with the Section 2 method and re-layout the whole thing |

After validation, write the measured values back into the script JSON so downstream lip-sync and
subtitles line up.
