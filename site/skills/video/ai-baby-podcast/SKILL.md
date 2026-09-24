---
name: ai-baby-podcast
description: >
  Produce viral "AI baby podcast / talking baby" entertainment shorts:
  character design, script with adult-voice contrast, TTS audio, lip-sync
  generation, and platform-compliant publishing. Use when the user asks to
  make a baby podcast video / AI baby video / talking baby / baby podcast /
  baby streamer / funny AI-kid short video, or wants meme-style
  talking-character shorts. Do NOT use for real-child footage editing,
  deepfakes of real people, or news-style content presented as factual.
license: Apache-2.0
compatibility: Uses web creation tools (image gen, TTS, lip-sync) in a browser workflow; no local install needed.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: viral-entertainment
  verified-date: "2026-08-26"
---

# AI Baby Podcast (Viral Talking-Character Shorts)

The recipe for this format: a baby (or toddler)'s face + an adult voice delivering deadpan opinions — the contrast itself is the joke. The mature pipeline splits into four stages: character image -> script -> adult-voice TTS -> lip-sync -> edit & publish. This skill orchestrates the whole chain and enforces the two disciplines that separate viral accounts from flash-in-the-pan ones: character locking and platform compliance.

## Red Lines — Read Before You Touch Anything

1. **You MUST declare AI-generated content**: at publish, tick the platform's "AI-generated content" declaration, and add an explicit notice on the video's opening frame
   (text height >= 5% of the shortest frame edge, held for >= 2 seconds). Basis: the
   Measures for Labeling AI-Generated Synthetic Content (effective 2025-09-01);
   failing to label -> the platform detects it, tags it "suspected AI", and throttles / removes it.
2. **Use purely AI-generated fictional baby images only**. Real children's photos — even your own kid — are not recommended; never lip-sync a real minor to "say things they never said". Reasons: portrait rights + the platform's heightened review of minor-related content.
3. **Do NOT clone celebrities' voices or likenesses** (star timbres, celebrity baby-ification) unless you have authorization — double risk on both platform and legal fronts.
4. **Do NOT do misleading "AI toddler expert parenting class" themes** — this is explicitly named as a remediation target in the regulatory documents.

## Input Checklist

| Input | Required | Default | Notes |
|---|---|---|---|
| topic / trending meme | yes | — | The opinion the baby delivers |
| persona | no | new character | Reuse an existing character card or create one |
| format | no | single monologue | single / two-person dialogue |
| target_platform | no | douyin | Determines aspect ratio and labeling details |

When topic is missing, ask everything at once:

> Please give this episode's topic (which trending meme to ride / what opinion to discuss). Optional: reuse an existing character or create a new one, single or two-person dialogue, which platform to post to (default douyin vertical).

## Pre-flight Checks

- Series mode (reusing an existing character): is `character_bible.md` and the locked reference images on disk?
  (`ls <character-card-directory>/`) If not -> treat it as a new character and follow Step 1; do not redraw from memory.
- Before running a series account, confirm the drift-discipline doc is on disk: `test -f references/character-consistency.md`;
  if missing -> STOP and report the repo is incomplete.
- Is a lip-sync tool available (Jimeng "lip-sync" / Hedra, either one)? If neither works -> Step 4 cannot be completed,
  tell the user the blocker in advance and STOP.

## Character-Locking Discipline (Do It Once, Reuse Forever)

Create `character_bible.md` containing:

- ① The original prompt text used to generate the reference image;
- ② Reference image files (front + left/right side + mid-speech expression, 4-6 images total, generated from the same seed);
- ③ The locked TTS voice ID and parameters;
- ④ 3-5 "do not" rules (e.g., "always wears black-rimmed glasses", "never changes clothing color").

From then on, drive every episode only from the reference images; **never regenerate the character from text**. Every 10 videos, compare the latest frame side by side with the reference image (eye spacing / nose shape / hairline), and if drift appears, restart from the original reference image immediately.
Reason: drift is the #1 killer of followers — viewers recognize one face.

## Workflow

### Step 1: Character Image

Prompt formula (any text-to-image tool works, including this repo's `image-generation` skill):

> A cute baby sitting in a professional podcast studio, wearing black-rimmed glasses and over-ear headphones, facing a professional microphone below the mouth, looking straight at the camera, mouth naturally closed, studio lighting and acoustic-foam background, photorealistic photo style, comedic feel.

Expected: a single clear front-facing face, the microphone not covering the lips, even lighting. Failure branch: multiple faces / side profile / hand over mouth -> add "single character, front-facing" and regenerate. Save to the character card after generation.

### Step 2: Script (15-40 seconds)

Formula: `2-second hook (contrast manifesto) -> one specific, confident opinion -> a reversal or punchline -> a fixed catchphrase ending`.

Example skeleton: "Grown-ups, you all have it wrong about <topic>. <one specific claim + reason>. <punchline reversal>. I'm XX, back in the cradle next time."

Rules:

- Short spoken phrases (each <= 15 Chinese characters);
- The more adult the opinion, the better — the contrast comes from the mismatch between content and face;
- For two-person dialogue, write alternating A/B lines and label roles.

Expected: a script readable in 15-40 seconds (at an adult speaking rate of ~4-5 Chinese chars/sec), with a 2-second hook and a fixed catchphrase ending.
If it fails: reads over 40 seconds -> cut arguments while keeping the opinion and punchline; do not force it in by doubling the speaking speed. Can't find an adult opinion (just describing a phenomenon) -> ask the user for a clear stance before writing; a stance-less contrast can't carry a video. Two-person dialogue where lines are unclear -> add A/B labels and rewrite.

### Step 3: TTS Voice-over

Use any TTS tool to generate an **adult mature voice** (low-pitched announcer tone = the classic recipe; a soft cute child voice only suits gentle parent-child content). Set the speed to 1.2-1.4x to better fit short-video pacing. Expected: dry vocal mp3/wav, no BGM no reverb — lip-sync tools need clean audio. Lock that voice into the character card; use the same voice every episode.

If it fails: the exported audio has background music or reverb -> turn off the TTS tool's music option and re-export; the lip-sync tool needs pure dry audio. Speed feels wrong -> fine-tune within 1.2-1.4 and re-export. In series mode the voice doesn't match last episode -> pull the locked voice ID from the character card and re-synthesize; don't casually swap voices.

### Step 4: Lip-sync

Feed the Step 1 reference image + Step 3 dry audio into the lip-sync tool (Jimeng "lip-sync", Hedra, etc.). First run the shortest single line to verify lip closure, then run the whole clip. Expected: lip shape matches word by word, with slight natural head movement. Failure table below. Multi-character dialogue = generate one clip per character separately, then cut between them in editing; do not generate them in the same frame.

If it fails: mouth barely moves or drifts in the second half -> per the failure table, swap in clean dry audio, or split long sentences into 2-3 chunks and generate each separately. The reference image has a microphone crossing the lips causing region distortion -> go back to Step 1 and regenerate the image. Multi-character in-frame causes face cross-contamination -> switch to per-character solo shots + cutting.

### Step 5: Editing & Compliant Publishing

In CapCut: import the lip-sync clip -> auto-generate subtitles (silent-scrollers rely on subtitles; they are mandatory) -> lay in BGM and sound effects (BGM volume at least 12dB below vocals) -> export 9:16 / 1080P.
The three-piece publishing checklist is mandatory: ① tick "AI-generated content" on the publish page; ② explicit notice text in the opening; ③ hashtags in the caption. Expected: video file + a screenshot confirming the label.

If it fails: export ratio or resolution wrong -> check the CapCut project settings (9:16 / 1080P) and re-export. BGM covers vocals -> drop BGM another 12dB+ and re-mix. Missed the AI declaration -> immediately add the declaration and republish; an unlabeled video gets judged "suspected AI" and throttled (see Red Line 1).

## Failure Remediation Table

| Symptom | Cause | Remedy |
|---|---|---|
| Mouth barely moves | Muffled audio or BGM interference | Swap in clean dry audio; retry with punctuation breaks |
| Microphone region distorted | Source image has mic crossing the lips | Regenerate the image, place the mic below the chin |
| Lip drift in second half of long sentence | Single generation too long | Split into 2-3 chunks, generate each, then edit |
| Two-person dialogue faces cross-contaminate | Generated in the same frame | Switch to per-character solo shots + cutting |
| Character looks different from last episode | Skipped the character card / regenerated from text | Roll back to the locked reference image and rerun |
| Platform flags "suspected AI", undeclared | Forgot to label | Immediately add the declaration and check Step 5 next time |

## Delivery Standard

Success = finished mp4 (9:16, with subtitles, 15-40s long) + evidence that the AI label has been added + this episode's assets archived into the character-card directory. Anything else counts as incomplete — say so plainly.

## References

- `references/character-consistency.md` — Full discipline for drift detection and multi-angle reference sets; read before running a series account.
