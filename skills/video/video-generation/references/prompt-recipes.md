# Video Prompt Recipes

Formulas for composing generation prompts (Step 2 of SKILL.md). The gateway
renders what the prompt describes; vague prompts produce vague footage.

## Contents

- [The formula](#the-formula)
- [Worked examples](#worked-examples)
- [Image-to-video notes](#image-to-video-notes)

## The formula

One paragraph, four slots, in this order:

```
[Subject] in [Scene] [Action], [Mood], [Shot hint]
```

- **Subject**: concrete noun with 1–2 attributes ("a barista in a blue apron")
- **Scene**: place + time + light ("a corner shop in the early morning, warm light")
- **Action**: one continuous motion, not a montage ("slowly pours latte art and pushes the cup toward the lens")
- **Mood**: adjectives the renderer can lean on ("cozy, healing, cinematic")
- **Shot hint** (optional): "close-up", "slow push-in", "orbit" — one camera idea max

Rules of thumb:

1. One scene, one action per video. Six seconds cannot hold a story arc.
2. Physical verbs beat abstract verbs: "pick up, turn, hand over" over "show, convey".
3. Put the most important visual FIRST — early tokens weigh more.
4. No text-in-video requests; rendered text is unreliable across engines.

## Worked examples

Strong prompt (product intro, 16:9):

> A white ceramic mug on a raw-wood table; morning light slants through the window casting soft
> patches; coffee pours slowly into the cup, steam rising gently; the camera pushes slowly in from
> the side to a close-up of the latte art; a warm, professional, trustworthy cinematic mood.

Weak prompt (same brief) and why it fails:

> Coffee video, make it look nice.

- No subject detail → the engine picks a random cup; no scene → random backdrop;
  "look nice" is not renderable; no motion → a frozen first-frame feel.

Strong prompt (vertical short, knowledge clip):

> A young lecturer in black-framed glasses stands in front of a bookshelf, smiles at the camera and
> raises the notebook in hand; a bright daytime office background; a light-paced, clear, bright
> science-communication mood; medium shot on a locked-off camera.

## Image-to-video notes

The reference image fixes the SUBJECT and SCENE; your prompt then only needs
to specify MOTION and MOOD. Do not re-describe what the image already shows.

Good image-to-video prompt for a portrait photo:

> The person holds the pose; the hair is lifted by a gentle breeze, the corners of the mouth slowly
> rise into a smile; the background light patches flicker subtly; the overall mood is soft and natural.
