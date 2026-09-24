# Short Video Script Templates (video-script-writer)

Three-act skeleton: **Hook → Body → CTA**. Brackets `[...]` are required slots;
replace them and delete the brackets after filling. This is for machine fill-in—don't improvise the structure.

## Table of Contents

0. Universal skeleton and hard rules / 1. Template 1: talking-head review/roast / 2. Template 2: narrated explainer
3. Template 3: tutorial/list / 4. Bad examples and line-by-line diagnosis / 5. Pre-delivery checklist

## 0. Universal skeleton and hard rules

```
[HOOK 0-3s]      Create a question/conflict/contrast → decides whether viewers swipe away
[BODY 3-75%]     Deliver on the hook's promise, advance step by step through [N] shots
[CTA  last 15%]  One action: rhetorical question / comment / save / next-episode tease
```

Hard rules (violation means rework):

1. **The hook must be directly provable by a visual.** "Did you know" is empty; "I spent 8900 on this"
   paired with the action of holding up the phone is a hook.
2. **One line of dialogue ≤ one breath**: for talking-head Chinese, a single line ≤15 characters
   (fast-paced character ≤10); for narrated, ≤30 characters.
3. **One shot carries only one information point.** Cramming two selling points = viewers remember neither.
4. **The CTA leaves only one action.** Asking for follows, likes, AND comments = viewers do nothing.
5. Suggested three-act proportions (guideline, not hard standard): Hook 10%, Body 75%, CTA 15%.
   For second conversion, see the timing-guide doc in this skill's SKILL.md References.

## 1. Template 1: talking-head review/roast (30 seconds, 4 shots)

Use for: baby / mascot / virtual character talking to camera. Dialogue-driven, the character is the
visual; cuts happen at emotional turns.

```json
{
  "title": "[Character] reviews [product]: I regret it",
  "video_type": "talking_character",
  "duration_seconds": 30,
  "platform": "douyin",
  "hook": "I spent [price] on this—guess whether it's worth it?",
  "scenes": [
    {
      "id": 1, "duration_sec": 4,
      "dialogue": "I spent [price] on this—guess whether it's worth it?",
      "visual": "[Character] holds [product] up with both hands right to the lens, background blurred",
      "camera": "close-up, front-facing", "sfx": "[unboxing chime]"
    },
    {
      "id": 2, "duration_sec": 8,
      "dialogue": "There's only one upside: [the upside].",
      "visual": "[Character] nods; cut to a close-up of [the upside demo]",
      "camera": "medium shot, slight tilt", "sfx": "[bright ding]"
    },
    {
      "id": 3, "duration_sec": 10,
      "dialogue": "But [the fatal flaw]! [price] for this? I don't get it.",
      "visual": "[Character] frowns and shakes the head; [product] pushed to the edge of frame",
      "camera": "close-up, slight push-in", "sfx": "[comic slide-down tone]"
    },
    {
      "id": 4, "duration_sec": 8,
      "dialogue": "Would you buy it? Tell me in the comments.",
      "visual": "[Character] tilts head looking at camera; leave room for the comment area at the bottom",
      "camera": "medium shot, locked off", "sfx": null
    }
  ],
  "caption": "#[product] #[complaint tag] #[character]",
  "total_duration": 30
}
```

Fill-in tips: `[the fatal flaw]` must be filmable ("charge two hours for 40 minutes of use"); don't
write abstract verdicts like "mediocre experience" that can't be visualized.

## 2. Template 2: narrated explainer (45 seconds, 4 shots)

Use for: science explainers, roundups, vlogs. Visual first, dialogue explains the picture; leave
0.3–0.5s of air between sentences for inserting B-roll.

```json
{
  "title": "Why [phenomenon]? 90% of people don't know the real reason",
  "video_type": "short",
  "duration_seconds": 45,
  "platform": "bilibili",
  "hook": "You think [common misconception]? It's actually the opposite.",
  "scenes": [
    {
      "id": 1, "duration_sec": 5,
      "dialogue": "You think [common misconception]? It's actually the opposite.",
      "visual": "Open with the result: footage or animation of [the counter-intuitive phenomenon]",
      "camera": "start on a wide shot", "sfx": "[suspense drumbeat]"
    },
    {
      "id": 2, "duration_sec": 12,
      "dialogue": "First, the background: [one-sentence setup].",
      "visual": "[diagram or archive footage], leave a title bar in the top-left",
      "camera": "static, mainly graphics", "sfx": null
    },
    {
      "id": 3, "duration_sec": 18,
      "dialogue": "The real reason is [the core mechanism]. Remember this one point and you're set.",
      "visual": "[mechanism animation or comparison graphic], hold the key frame for at least 2 seconds",
      "camera": "zoom in to the key area", "sfx": "[emphasis hit]"
    },
    {
      "id": 4, "duration_sec": 10,
      "dialogue": "Next time you hit [the situation], just [the actionable step].",
      "visual": "[hands-on demo], on-screen step number labels",
      "camera": "medium shot", "sfx": null
    }
  ],
  "caption": "#[topic] #science #[keyword]",
  "total_duration": 45
}
```

For narrated type, the CTA can be folded into the last point (as in this template); add a separate
8-second CTA shot only if needed.

## 3. Template 3: tutorial/list (60 seconds, 4 shots)

Use for: tutorials, Top-N roundups. Fixed structure, batch-replicable; open every point with the
**same sentence frame** so viewers can anticipate the rhythm.

```json
{
  "title": "[N] [domain] tips—the last one is the most overlooked",
  "video_type": "tutorial",
  "duration_seconds": 60,
  "platform": "douyin",
  "hook": "[N] [domain] tips; I've used the last one for three years.",
  "scenes": [
    {
      "id": 1, "duration_sec": 6,
      "dialogue": "[N] [domain] tips; I've used the last one for three years.",
      "visual": "Flash quickly through thumbnails of the [N] points, 0.5s each",
      "camera": "fast cut", "sfx": "[quick-cut rhythm hit]"
    },
    {
      "id": 2, "duration_sec": 15,
      "dialogue": "First: [tip one]. The way to do it is [one-sentence action].",
      "visual": "[screen recording or real shot], fixed number 01 at the top",
      "camera": "screen capture", "sfx": null
    },
    {
      "id": 3, "duration_sec": 15,
      "dialogue": "Second: [tip two]. The key is [the crucial detail].",
      "visual": "[screen recording or real shot], fixed number 02 at the top",
      "camera": "screen capture", "sfx": null
    },
    {
      "id": 4, "duration_sec": 24,
      "dialogue": "Last: [tip three]. [quantified before/after comparison].",
      "visual": "Before/after split screen, label the improvement on the right",
      "camera": "split screen", "sfx": "[transition stinger]"
    }
  ],
  "caption": "#[domain] #hardcore #tips",
  "total_duration": 60
}
```

Keep parallel points opening with the same frame ("first/second/last")—this is the key to whether a
list video gets watched all the way through.

## 4. Bad examples and line-by-line diagnosis

Bad example (same brief: 30-second baby reviews a phone):

```json
{
  "title": "Phone review",
  "hook": "Hi everyone, today I bring you a phone review video, hope you enjoy it.",
  "scenes": [
    {
      "id": 1, "duration_sec": 15,
      "dialogue": "This phone uses the latest processor, very powerful, smooth for both daily use and gaming, and its camera is especially good, outstanding in night mode, plus the battery life has been greatly improved.",
      "visual": "Baby holding the phone", "camera": "medium shot", "sfx": null
    },
    {
      "id": 2, "duration_sec": 15,
      "dialogue": "Overall this phone is well worth buying; if you're interested go check it out, remember to like, follow, save, and triple-tap, see you next time.",
      "visual": "Baby smiling", "camera": "medium shot", "sfx": null
    }
  ],
  "caption": "#phone #review",
  "total_duration": 30
}
```

Diagnosis:

| # | Problem | Why it's fatal | Fix |
|---|---|---|---|
| 1 | Hook is "hi everyone, today I bring you" | Zero information in the first 3 seconds; viewers are already gone, completion rate collapses | Replace with a verifiable strong claim: "I spent 8900 on this, after three days I want to return it" |
| 2 | Single line 70+ characters | More than one breath; TTS reads it as a run-on blob; talking-head needs ≤15 chars | Split into 4–5 sentences, one information point per sentence |
| 3 | One shot 15s cramming 5 selling points | Viewers remember none; no visual change causes fatigue | Cut every 3–6 seconds, one selling point per shot |
| 4 | `visual` is only "baby holding the phone" | Not executable: no shot size, action, prop, or background | Add filmable elements like "close-up / hold up to lens / background blurred" |
| 5 | CTA asks for "like, follow, save, triple-tap" | Three actions = zero actions | Leave only one: "tell me in the comments if you'd buy it" |
| 6 | Only 2 generic tags | No search value | Fill up to the platform limit with specific words (product name + complaint + audience) |
| 7 | No `sfx` throughout | Silent stretches drag; all rhythm relies on speech rate | Add sound-effect cues at key turns |

## 5. Pre-delivery checklist

- [ ] The hook is in the first 3 seconds and is directly provable by the first visual
- [ ] Each `dialogue` length meets the form's ceiling (talking-head ≤15 chars / narrated ≤30 chars)
- [ ] `sum(scenes[].duration_sec) == total_duration` (difference must be 0)
- [ ] Every `visual` contains: subject + action + shot size (missing any one = not executable)
- [ ] Number of selling points/points = number of shots; no shot carries multiple selling points
- [ ] The CTA has exactly one action
- [ ] Number of `caption` tags does not exceed the target platform's limit (platform limits are volatile; verify the latest spec before publishing)
