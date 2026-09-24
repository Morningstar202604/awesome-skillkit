# Character Consistency Discipline (a survival manual for a series account)

Why a single viral hit is easy but a series account is hard: viewers subscribe to "the next episode
of the same character." If the face changes or the voice changes, the algorithm and your fans abandon
you at once. This document is the full expansion of `ai-baby-podcast` Step 0.

## Contents
- [The seven-piece character card](#the-seven-piece-character-card)
- [Four disciplines per-generation](#four-disciplines-per-generation)
- [Drift detection: every 10 episodes](#drift-detection-every-10-episodes)
- [Two-person / multi-character](#two-person--multi-character)

## The seven-piece character card

Create a `character_bible/` directory outside the repo (don't bundle it into the video project), containing:

1. `ref_front.png` — front reference image (the locked "official face")
2. `ref_left.png` / `ref_right.png` / `ref_talking.png` — left/right sides and a mid-speech expression,
   all generated from the front image by varying it with the same seed + same prompt (multi-angle reference set)
3. `voice.txt` — TTS voice ID, speech rate, emotion parameters (reuse it without changing a single line)
4. `prompt_locked.txt` — the verbatim appearance prompt; afterward you may only copy it, never rewrite it
5. `dont_rules.md` — 3–5 prohibitions ("don't swap the glasses," "don't change the clothing color family," "don't change the perceived age")
6. `episodes.log` — one line per episode: date / topic / finished-filename / whether it passed the drift audit

## Four disciplines per-generation

1. Only use reference images to drive lip-sync/motion; **never regenerate the character from text**—the
   most common way to die is "I think I could optimize the look a bit," after which viewers no longer recognize him.
2. Every prompt carries the locked features (glasses/headphone/clothing color).
3. Use only the voice in voice.txt; changing the voice ruins the persona even more than changing the face.
4. Archive each episode's assets under `episodes/NNN_<topic>/`, keeping finished files and intermediate products apart.

## Drift detection: every 10 episodes

Place ref_front.png side by side with the first frames of the last 3 episodes and compare three points:
eye distance (pupil spacing), philtrum length (base of nose to upper lip), and ear height.
If any point is visibly off to the naked eye, **regenerate that episode from the original reference
image**—don't keep fixing on top of the drifted image. Reason: every generation introduces a tiny
amount of random noise; after 30–50 episodes the accumulation is inevitably visible; the earlier you
roll back, the cheaper it is.

## Two-person / multi-character

- Give each character its own card and its own locked seed; if the two are often in frame together,
  additionally generate a two-shot reference image as the dedicated seed for two-shot frames.
- Always generate lip-sync one person at a time per clip, then cut and join in the edit—generating a
  two-shot always cross-contaminates the faces.
- When casting, first render a side-by-side test image of the two characters: combos with too-similar
  facial structure or the same hair color should be re-cast.
