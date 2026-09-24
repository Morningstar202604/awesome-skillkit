---
name: nailong-laugh-shorts
description: >
  Produce "laughing Nailong"-style laughing dragon meme videos: generate the
  chubby yellow dragon character image, animate belly-laugh actions or swap
  actions from human footage, add processed giggle audio, batch skin
  variants, and publish with probability-bait captions. Use when the user
  asks to make a Nailong video / laughing Nailong / belly-laughing Nailong /
  Nailong emoji come alive / absurd funny little-dragon meme video, or
  wants a meme-style talking-character short. Do NOT use for harassing
  specific real persons, or political/factual disinformation contexts.
license: Apache-2.0
compatibility: Uses web AI tools (text-to-image, image-to-video, action transfer); no local install needed.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: viral-entertainment
  verified-date: "2026-08-26"
---

# Nailong Laughing Shorts ("Laughing Nailong" Production Manual)

Risk notice (one sentence, then get to work): publicly posting with this commercial IP character is unauthorized use; for non-commercial personal accounts the realistic consequences are usually throttling/removal/account penalties rather than lawsuits, but commercial use will definitely draw a claim — weigh it yourself; ticking "AI-generated content" at publish noticeably lowers the probability of action.

The character elements that make people laugh, in order of importance:
① small-head / big-body distorted proportions ② head-tilted-back, belly-holding shake ③ high-saturation bright yellow ④ the cute-vs-unhinged expression contrast.

## Input Checklist

| Input | Required | Default | Notes |
|---|---|---|---|
| pipeline | no | A | A = emoji come alive (image -> video); B = real-human action shell |
| skin/theme | no | original yellow | Holiday / occupation / color-shift variant themes |
| episode_count | no | `1` | For series, recommend >= 5 at a time |

Only when the user gave nothing at all, ask everything at once:

> Which approach? A: generate a belly-laughing character image and animate it (simple, fast);
> B: take a real-person absurd-action video and swap in this character (closer to the meme's warped feel).
> Optional: how many episodes, and whether to do a costume-change series.

## Pre-flight Checks

- Is a text-to-image tool available (this repo's `image-generation` skill or any web tool)? If not -> STOP.
- Pipeline B: is the action source video on disk? (`test -f <action-video>`) If not -> shoot or source it first, STOP.
- Series (episode_count >= 5): are the previous episode's character image and prompt archived on disk? If not ->
  first rebuild the character archive (rerun pipeline A Step 1 and archive), so every episode has the same face.

## Workflow

1. **Pick the route**: based on available assets, choose pipeline A (static-image emoji come alive, fastest) or pipeline B (real-human action shell, closer to the warped feel) — see the corresponding section.
2. **Lock the character**: pull that character's description block from the character description library and **reuse it verbatim across shots** to ensure consistency.
3. **Write hooks and body**: produce per the series formula; each clip <= 15 seconds, and the first 2 seconds must grab attention.
4. **Output validation**: check each clip against the delivery standard for proportions, duration, and character consistency.
5. **Exception handling**: when the character drifts / duration exceeds limit / audio-video sync is off, consult the failure table.

## Character Description Library (Ready-to-Copy Prompts)

Base body (close to the official look):

> A round, chubby yellow cartoon little dragon, big white oval belly, short limbs and tail,
> cute big eyes, chibi 3D cartoon render, high-saturation bright yellow, solid-color background, full body front view.

Laughing variant (the meme's signature scene):

> The same yellow little dragon laughing uproariously with head tilted back, both short hands hugging its belly,
> belly shaking violently, eyes squeezed shut into two slits, mouth wide open, exaggerated body proportions —
> small head, huge belly, motion-blurred shaking feel.

Warped proportions (the funnier "nail-frog" distortion):

> Same character but deliberately off-balance proportions: shrunken head, elongated enlarged body, thin short legs kicking wildly,
> facial features clustered in the lower half of the face, distorted and comical, rubber-textured shake.

Series skin-matrix ideas: golden-armor version / suit-and-office version / Spring-Festival-red-lantern version / watermelon-rind version / late-night-emo-lights-out version. Each skin = base prompt + one skin description line.

## Pipeline A: Emoji Come Alive (Fastest Output)

### Step 1: Generate the Static Laughing Image

Run the laughing-variant prompt above with any text-to-image tool.
Expected: single character, front or slightly side view, large belly proportion, no extra limbs.
Failure branch: multiple characters / broken limbs -> add "single character, simple pose" and regenerate.

### Step 2: Image-to-Video

Feed the image into an image-to-video tool (Jimeng / Kling, etc.), with the action instruction:

> The character stays in place, laughing head-tilted-back, belly shaking and bouncing violently, body swaying forward and back,
> looping animation.

Expected: a 3-5 second seamless-loop feel clip. Failure branch: stiff motion -> revise the instruction to emphasize
"rubber-hose wobble, exaggerated squash and stretch" and roll the dice 1-2 more times.

### Step 3: Add Laughter & Subtitles

Making the laugh: record your own belly laugh on a phone -> process it with a voice changer (pitch up 20-30% + slight robotic feel + break into 4/4 beats), cut a 3-8 second loopable version. **Do NOT directly rip the original audio from someone else's video** — platform duplicate detection flags it as reposting and throttles it; a self-made equivalent is your own asset.
Editing: the laugh hits within the first 0.5 seconds -> loop the video 2-3 times -> overlay a big title on screen.

## Pipeline B: Real-Human Action Shell (Closer to the Original Meme's Warped Feel)

### Step 1: Action Source

Find an absurd real-human action (military boxing, social dance, square dance, wrestling fall). Shooting it yourself is most reliable; if using web footage, only take the action as reference — keep no recognizable faces.
Expected: an action video with a clear silhouette and exaggerated rhythm. Failure branch: footage has identifiable faces ->
crop or reshoot, keep only the action (silhouette / long shot), no faces going into the next step.

### Step 2: Action Transfer

Use a tool supporting video-to-video / action transfer (Jimeng, Kling, etc.): use pipeline A Step 1's
character image as the reference + the action video as the driver. Expected: the character copies the action and the AI warps the proportions — **this loss of control is exactly what makes the original meme funny; don't fix it**.
Failure branch: doesn't resemble the original action at all -> switch to a simpler-silhouette action and rerun; looks too much like normal animation and isn't funny ->
add "distorted proportions, head shrinking, belly expanding" to the prompt.

### Steps 3-4: Same as Pipeline A Step 3, then move into series production.

## Series Formula (Batch-Produce Hooks + Body)

One body shell x N skins x a fixed caption template = five clips stocked up in one evening:

| Template | Example |
|---|---|
| Blessing style | "Congratulations, you scrolled onto the Laughing Nailong" + "everyone who sees this is chosen" |
| Rare probability | "Golden Nailong, appearance probability only 0.01%, good luck to all who see it" |
| Dialogue meme | Two identical ones yelling at each other "I'm Nailong!" "No, I'm Nailong!" |
| Contrast daily-life | Office version / class version / foodie version, one each |

Publishing: tick "AI-generated content"; put #Nailong-style hashtags in the title to enter the traffic pool.

## Failure Remediation Table

| Symptom | Cause | Remedy |
|---|---|---|
| Image looks like a frog/lizard, not a fat dragon | White belly omitted from prompt | Add "big white oval belly" and regenerate |
| Belly doesn't shake in the video | Action instruction too flat | Emphasize the triple shake/jiggle/wobble words and reroll |
| Laugh feels awkward, not catchy | No rhythm processing | 4/4-beat phrasing + second voice-changer pass |
| Platform flags it as reposted | Used someone else's original audio/footage | Make everything yourself: self-recorded laugh, self-shot action source |
| Flagged as suspected AI, undeclared | Missed the declaration | Tick it, check next time's checklist |

## Delivery Standard

Success = finished mp4 (9:16, laugh at the opening, subtitles complete) + the character image/prompt used archived
(archiving is mandatory for a series, so every episode keeps the same face) + a screenshot confirming the AI declaration is ticked.
Anything else counts as incomplete — say so plainly.

## References

- This skill is pure prompt-based; no external reference files needed.
