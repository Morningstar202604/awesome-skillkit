---
name: sound-designer
description: "Design and mix the audio bed for a podcast or short video: select and place sound effects (SFX), choose a background music (BGM) bed matched to the content mood, set per-platform loudness targets (LUFS), plan EQ and compression for speech clarity, and design ducking curves so music automatically drops under the voice. Use when the user asks to add sound effects / mix audio / make audio louder / level audio / add background music / BGM selection / audio ducking / EQ voice / compression / loudness / LUFS / podcast mix / video sound design / ambient sound. Do NOT use for writing the spoken script (podcast-producer), voice casting or TTS synthesis parameters (tts-voice-director), publishing metadata (episode-publisher), or video clip assembly (video-editor)."
license: Apache-2.0
compatibility: Pure prompt-based; the bundled loudness_check.py needs Python 3.8+ stdlib only. No audio processing is performed by this skill — it outputs a mixing plan the user or their DAW/ffmpeg executes.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: audio
  pattern: single-task
  tier: standard
  verified-date: "2026-09-24"
---

# Sound Designer

The missing middle layer between a synthesized voice track and a finished, publishable audio file. Upstream you have a clean TTS recording (from tts-voice-director); downstream you hand off a mixing plan ready for ffmpeg or a DAW. The core discipline: **speech must stay intelligible above everything else** — music, SFX, and ambient beds are supporting actors, never the lead.

## Applicability Decision Table

| Situation | Use this skill? | Reason |
|---|---|---|
| User has a raw voice track and wants it to sound professional | Yes | Loudness normalization, EQ, compression, ducking are exactly this skill |
| User wants to add a whoosh / ding / transition SFX at a timestamp | Yes | SFX selection and placement plan |
| User asks "what BGM should I use under my podcast?" | Yes | BGM mood matching + level guidance |
| User is writing the script or choosing voices | No | Wrong step — go to podcast-producer or tts-voice-director |
| User is stitching video clips together | No | video-editor handles clip assembly; this skill only outputs the audio mixing plan |
| User needs shownotes or chapter markers | No | episode-publisher |
| User wants to generate a new music track from scratch | No | music-generation creates the track; this skill decides how to place and level it |

## Input Checklist

| Input | Required | Notes |
|------|------|------|
| Voice / narration audio | Yes | The TTS or recorded speech track (file path or description of the audio) |
| Content type | Yes | Podcast interview / podcast monologue / short video voiceover / tutorial narration |
| Target platform | No | Defaults to Xiaoyuzhou + Bilibili dual target; affects loudness LUFS target |
| Existing music or SFX | No | If the user already has tracks, list them; otherwise plan selections |
| Mood / genre | No | E.g. "calm tech podcast", "energetic Douyin short", "documentary voiceover" |

When inputs are missing, ask for all at once: "Please provide: ① the voice / narration audio (or a description of what you have); ② the content type (podcast / short video / tutorial); ③ the target platform (defaults to Xiaoyuzhou + Bilibili); ④ any existing BGM or SFX files (optional); ⑤ the mood or genre (optional)."

## Pre-flight Self-check

This skill is planning-only — it does not render audio. Self-check:

```bash
test -f references/loudness-standards.md && echo LOUDNESS-OK
```

Expected: `LOUDNESS-OK` printed. Failure means the reference table is missing — STOP and prompt for reinstall. No other environment checks are needed; the mixing plan it produces can be executed by ffmpeg or any DAW on the user's side.

## Tacit Knowledge (Domain Dark Information)

**1. LUFS is the loudness standard, not peak dB.** Platforms measure integrated loudness in LUFS (Loudness Units relative to Full Scale), not peak volume. Cranking the peak to 0 dBFS makes the podcast sound loud but distorted, and platforms will reject or normalize it anyway. The correct target is an **integrated loudness** number, plus a true-peak ceiling. See [loudness-standards.md](references/loudness-standards.md) for per-platform targets.

**2. Speech sits in the 1 kHz–4 kHz band; music masks it everywhere else.** Human intelligibility depends almost entirely on the 1–4 kHz range. A music bed with strong presence in that band (bright piano, vocal chops, cymbals) will bury the voice even at −20 dB. When choosing BGM, prefer tracks with a hollow mid-range (ambient pads, soft synth, low-end kick only) so the voice cuts through without aggressive ducking.

**3. Duck the music, don't just lower it.** A static music level that is quiet enough during speech is also too quiet during intro/outro. The professional pattern is a **ducking curve**: music is at full volume between segments, and automatically drops by 6–12 dB the moment speech starts, then fades back up when speech pauses. In ffmpeg this is the `sidechaincompress` filter; in a DAW it is an automation track triggered by the voice channel.

**4. SFX are punctuation, not decoration.** A whoosh under a transition, a subtle riser before a reveal, a single "ding" when mentioning a key point — each SFX serves a narrative function. Sprinkling SFX every 10 seconds makes a 5-minute podcast sound like a game show. Rule of thumb: ≤3 SFX per 5-minute episode, each under 1 second, at −18 to −24 dB relative to the voice.

**5. EQ on voice is surgical, not broad.** A high-pass filter at 80–100 Hz removes room rumble and breath thumps. A gentle presence boost (+2–3 dB at 2–3 kHz) adds clarity. A slight cut around 200–300 Hz reduces mud. Do not sweep the EQ widely — too much boost at any frequency sounds like a telephone.

## Workflow

### Step 1: Profile the Source Voice Track

First, establish what you are working with. Ask the user (or inspect the file if accessible):

- Sample rate and bit depth (44.1 kHz / 16-bit is standard; 48 kHz / 24-bit for video)
- Estimated RMS level (if the user knows; otherwise plan conservative targets)
- Any known problems: room echo, mouth clicks, breath noise, sibilance

Expected: a one-paragraph voice-track profile with any known defects listed.
On failure: the user has no audio file yet (still at script stage) → STOP and tell them to come back after tts-voice-director renders the speech. This skill cannot mix what does not exist.

### Step 2: Set the Loudness Target (per platform)

Open [loudness-standards.md](references/loudness-standards.md) and look up the target for the chosen platform. The table gives integrated LUFS, true-peak ceiling, and short-term max. Write it down:

```text
Target platform: Bilibili
Integrated loudness: −16 LUFS
True peak ceiling: −1.5 dBTP
Max short-term loudness: −10 LUFS
```

Expected: every platform target is written explicitly, not assumed.
On failure: the platform is not in the table → pick the closest analog (podcast platforms → −16 to −14 LUFS; short-video platforms → −14 to −12 LUFS; music platforms → −14 LUFS) and note the assumption.

### Step 3: Plan the EQ Chain for Speech

Apply this chain in order (output as instructions for ffmpeg or a DAW):

```text
1. High-pass filter: 80 Hz, 12 dB/octave slope — removes rumble, breath thumps
2. Cut around 200–300 Hz: −2 to −3 dB at Q=1 — reduces mud and boxiness
3. Presence boost: +2 to +3 dB at 2.5–3 kHz, Q=1.5 — adds clarity and intelligibility
4. Gentle de-essing: dynamic EQ or cut −3 dB around 6–8 kHz if sibilance is a problem
```

Do NOT add a low-pass filter on speech (it dulls the voice). Do NOT boost bass below 200 Hz (it clouds the mix).

Expected: every EQ band has a frequency, gain, and Q value written down.
On failure: the voice track sounds thin already → skip the presence boost; it will make it worse. If the voice sounds muffled → the problem is likely room echo, not EQ — recommend re-recording or adding a de-reverb plugin before any EQ.

### Step 4: Plan the Compression

Compression evens out the dynamic range so quiet parts are audible and loud parts do not clip. Settings for speech:

```text
Threshold: −18 dBFS (adjust so gain reduction is 3–6 dB on loud phrases)
Ratio: 3:1 to 4:1
Attack: 10–20 ms (slow enough to keep consonants punchy)
Release: 100–200 ms (fast enough to recover between sentences)
Makeup gain: +2 to +4 dB (to compensate for the threshold reduction)
```

Expected: threshold, ratio, attack, release, and makeup gain are all specified.
On failure: the voice sounds squashed (no dynamics) → reduce ratio to 2:1 and increase attack to 30 ms. The voice sounds uneven (whispers then shouts) → lower threshold by 2 dB and increase release to 250 ms.

### Step 5: Select and Place BGM

If the user needs background music:

1. **Mood match**: use the mood input to pick a BGM style. The [music-style-lexicon.md] in the music-generation skill is the reference for generating a track if none exists.
2. **Placement rule**: BGM appears only in three places: intro (0–15 s), between segments (5–10 s stingers), and outro (last 15–30 s). Do not run continuous BGM under the entire episode — it fatigues the listener.
3. **Level**: when BGM is under speech (ducked), it sits at −20 to −26 dB below the voice. When BGM is solo (intro/outro), it can be at the target loudness.

Expected: a timeline list showing where BGM starts, stops, and its level at each point.
On failure: the user insists on continuous BGM → compromise: use a very quiet pad (−28 dB under voice) with no rhythmic elements, and warn that it may cause listener fatigue. Do not agree to a rhythmic BGM under speech — it masks intelligibility.

### Step 6: Design the Ducking Curve

This is the difference between an amateur and a professional mix. Plan the sidechain compression:

```text
Sidechain trigger: the voice track
Reduction amount: 6–12 dB (music drops this much when speech starts)
Attack: 5–10 ms (music ducks quickly when voice starts)
Release: 200–400 ms (music fades back up gradually after speech ends)
```

In ffmpeg, this translates to:
```text
sidechaincompress=threshold=0.02:ratio=8:attack=5:release=300:makeup=1
```

Expected: the ducking parameters are written out, and the BGM timeline from step 5 accounts for the ducking behavior.
On failure: the music still pokes through between sentences → increase release to 500 ms so it does not fade back up too early. The music sounds like it is pumping (breathing in and out) → reduce ratio to 4:1 and increase attack to 15 ms.

### Step 7: Select and Place SFX

Per the tacit-knowledge rule (≤3 SFX per 5 minutes), choose from these common categories:

| SFX type | When to use | Typical level | Duration |
|---|---|---|---|
| Whoosh / transition | Between major segments, scene changes | −20 dB | 0.5–1 s |
| Riser / buildup | Before a reveal or key point | −18 dB | 1–2 s |
| Ding / chime | Highlight a definition or key takeaway | −22 dB | 0.5 s |
| Ambient bed | Background room tone (cafe, rain, office) | −28 dB | Continuous, looped |

Do NOT use: laugh tracks, applause, cartoon boings, record-scratch effects (they date the audio and distract).

Expected: ≤3 SFX per 5 minutes, each with a timestamp, level, and duration.
On failure: the user wants more SFX → cap at 3 per 5 minutes and explain that over-SFXing reduces perceived quality.

### Step 8: Master and Deliver the Mixing Plan

Deliver a single mixing plan document that includes:

1. Voice track: EQ chain, compression settings
2. Loudness target: integrated LUFS, true peak, short-term max
3. BGM: track selection (or generation brief), placement timeline, levels
4. Ducking: sidechain parameters
5. SFX: list with timestamps and levels
6. Mastering step: final loudness normalization to the target (use ffmpeg `loudnorm` filter or a DAW master)

Expected: the plan is complete enough that the user (or their engineer) can execute it without asking further questions.
On failure: the user has no DAW and wants ffmpeg commands → provide the ffmpeg filter_complex string as a bonus, but note that ffmpeg's loudnorm is a two-pass process for accurate results.

## Parameter Quick Reference

| Parameter | Speech podcast | Short video voiceover | Notes |
|---|---|---|---|
| Target integrated LUFS | −16 LUFS | −14 LUFS | Per platform table |
| True peak ceiling | −1.5 dBTP | −1.0 dBTP | Never exceed |
| HPF cutoff | 80 Hz | 100 Hz | Video rooms often have more rumble |
| Presence boost | +2 dB @ 2.5 kHz | +3 dB @ 3 kHz | Video benefits from more clarity |
| Compression ratio | 3:1 | 4:1 | Video wants punchier |
| Compression attack | 15 ms | 10 ms | Video is snappier |
| Ducking reduction | 6–8 dB | 8–12 dB | Video BGM is more active |
| Ducking attack | 10 ms | 5 ms | Video needs faster ducking |
| SFX count per 5 min | ≤3 | ≤5 | Video tolerates more |

## Failure Remediation Table

| Symptom | Cause | Action |
|---|---|---|
| Voice sounds muddy / unclear | Too much bass, not enough presence | Add HPF at 80 Hz; boost 2–3 kHz by +2 dB |
| Voice sounds thin / reedy | Over-EQ'd at high end, or a bad mic | Cut 6–8 kHz by −2 dB; do not boost presence further |
| Music fights the voice even at low volume | BGM has strong mid-range (piano, vocals) | Replace BGM with ambient pads; increase ducking to 12 dB |
| Audio is too quiet on the platform | Integrated loudness not normalized | Run loudnorm to the target LUFS; do not just crank gain |
| Audio distorts / clips | True peak exceeds ceiling | Lower the master gain by 2 dB; check for inter-sample peaks |
| Ducking sounds like pumping | Attack too slow, release too fast | Increase attack to 15 ms; increase release to 400 ms |
| SFX are jarring / out of place | SFX level too high, or wrong mood | Lower to −22 dB; match SFX mood to content (no cartoon sounds in a serious interview) |
| Between-segment silence feels dead | No ambient bed or BGM fill | Add a 5-second BGM stinger or a quiet ambient bed at −30 dB |

## Delivery Standard / Quality Checklist

- Artifacts: a mixing plan document covering voice EQ, compression, loudness target, BGM placement, ducking parameters, and SFX list.
- Save location: output directly in the conversation; when saving files, name the plan `mixing-plan.md`.
- Integrity verification:
  - Every section (EQ, compression, loudness, BGM, ducking, SFX) has explicit numeric values — not "adjust by ear"
  - The loudness target matches the target platform from [loudness-standards.md](references/loudness-standards.md)
  - SFX count ≤ 3 per 5 minutes (≤5 for short video)
  - Ducking parameters specify both attack and release
  - BGM placement is timed (intro / between segments / outro), not continuous under speech

## Chain Handoff

This skill sits between tts-voice-director and episode-publisher in the audio-studio chain:

- **Upstream**: tts-voice-director produces the raw synthesized voice track and the stitching plan. Call this skill after the voice audio exists.
- **Downstream**: episode-publisher packages shownotes and metadata. Call that after the audio is mixed and exported.

Say: "The mixing plan is ready; execute it in your DAW or with the ffmpeg commands, then call episode-publisher to package the show notes and metadata."

For video creators, this skill also pairs with video-editor: this skill outputs the audio mixing plan, and video-editor handles the visual clip assembly. Run both before export.

## References

- [loudness-standards.md](references/loudness-standards.md) — per-platform loudness targets (LUFS, true peak, short-term max) for Chinese podcast and short-video platforms, plus the ffmpeg loudnorm two-pass procedure.
