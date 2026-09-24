---
name: transition-designer
description: "Design a transition plan for AI video: choose the right transition type at every scene boundary, set durations, sync to music beats, and hand off an executable transition spec to video-editor. Covers hard cuts, match cuts, dissolves, wipes, J/L-cuts, whip pans, speed ramps, glitch and more. Use when the user asks to design transitions / plan a cut / decide how scenes connect / beat-sync editing / pacing a montage / choose between cut and dissolve / fix a jarring cut. Do NOT use for executing the actual edit (that is video-editor), for motion graphics or animated text (use motion-effects-designer), or for writing the script itself (use video-script-writer)."
license: Apache-2.0
compatibility: Pure prompt-based design skill; no scripts required. Outputs a transition plan consumed by video-editor.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: video
  pattern: planning
  tier: standard
  verified-date: "2026-09-24"
---

# Transition Designer

Plan how two shots or scenes meet at the cut point. This skill does not edit video; it produces a **transition plan** — a per-boundary table that downstream `video-editor` executes with FFmpeg `xfade` / `xfade` audio filters. Good transitions are invisible: they carry the viewer across a boundary without drawing attention to themselves. A transition that calls attention to itself is usually a mistake unless it is intentionally stylized.

The deliverable is a table with one row per scene boundary, naming the transition type, duration, audio behavior, and the beat it lands on.

## Applicability Decision Table

| Your Situation | Use This Skill? | Go To |
|---|---|---|
| Have a shot list / scene list and need to decide how each scene connects | yes, this skill | here |
| Only need to stitch clips back-to-back with default cuts | no — default hard cut is fine | video-editor directly |
| Need animated text, lower thirds, particles, chart animations | out of scope | motion-effects-designer |
| Need to actually run FFmpeg and produce the file | out of scope | video-editor (consumes this plan) |
| Need to write dialogue or beat sheet | out of scope | video-script-writer |
| Need to choose camera angles per shot | out of scope | storyboard-designer |
| User says "just make it look cool" with no pacing intent | ask for genre + platform first | Input Checklist |

## Input Checklist

| Input | Required | Default if Missing |
|---|---|---|
| Shot list / scene list | yes | ask — cannot plan without knowing boundaries |
| Scene list with durations | yes | derive from storyboard beat sheet |
| Music track / BPM | no | 120 BPM assumed; off-beat transitions allowed |
| Platform target | no | assume Douyin/TikTok vertical (9:16) |
| Pacing intent | no | assume genre default (see Rhythm section) |
| Genre | no | assume short-form entertainment |
| Audio track (voice-over / dialogue) | no | no J/L-cuts planned; audio bridge skipped |

When required inputs are missing, ask once: "Please provide: (1) the shot/scene list in order with per-shot durations; (2) target platform (Douyin / Bilibili / YouTube / WeChat Channels / Xiaohongshu); (3) music BPM if known; (4) pacing intent (fast / medium / cinematic)."

## Pre-flight Checks

- Count the boundaries: if there are N shots, there are N-1 internal boundaries plus an optional opening (fade in) and closing (fade out). Confirm the list is ordered.
- Total duration = sum of shot durations. Cross-check against target platform length (Douyin <=60s, YouTube 5-15min, Xiaohongshu 30-90s).
- If music is provided, note BPM: beat interval = 60 / BPM seconds. At 120 BPM, a beat is 0.5s; at 90 BPM, 0.67s; at 140 BPM, 0.43s. Transitions should land on or just off a beat.
- Identify emotional beats: moments where holding longer matters (reveal, punchline, reaction). Mark these in the shot list before choosing transitions.
- Flag any boundary where two adjacent shots share the same color / motion / subject — these are natural match-cut candidates.

## Transition Type Catalog

For each boundary, pick exactly one transition. Default to hard cut unless a deliberate reason exists.

### Basic Cuts

| Type | Typical Duration | Emotional Effect | When It Works | When It Fails |
|---|---|---|---|---|
| Hard cut | 0 frames (instant) | Neutral, sharp | Most cuts; dialogue; when action continues | Between two visually similar frames (becomes a jump cut) |
| Soft cut (half-frame dissolve ~2-4 frames) | 0.03-0.07s | Gentle, unnoticeable | Between similar angles; smoothing jump cuts | Already has a natural motion match — wastes the match |
| Jump cut | 0 frames, same framing, time jump | Energetic, restless, vlog-style | Talking-head compression; comedic pacing; music videos | Dramatic narrative (looks like a mistake); same wardrobe/position with no time indicator |
| Cross-cut (parallel action) | 0 frames, alternates | Tension, simultaneity | Two stories converging; chase vs. clock; "meanwhile" | Audiences not tracking both threads yet (confusing) |
| Match cut (graphic / action / eyeline) | 0 frames (cut on match) | Elegant, seamless, memorable | Shape/color/motion/eyeline matches across scenes; time or place jump | No real match exists — forced match cuts draw attention |
| Smash cut | 0 frames, abrupt audio/visual contrast | Shock, comedy, whiplash | After a slow build; reveal; comedic punchline | Overused; in subtle content feels jarring |
| Cutaway | 0 frames, inserts B-roll | Explains, relieves tension | Show what speaker is talking about; reaction shot | B-roll unrelated to dialogue |
| Cut-in (insert) | 0 frames, close-up detail | Emphasizes a detail | Hand on a doorknob, text on screen, object close-up | Used too often (frantic, no wide shot) |

### Optical Transitions

| Type | Typical Duration | Emotional Effect | When It Works | When It Fails |
|---|---|---|---|---|
| Cross-dissolve | 0.3-1.0s (shorts) / 1.0-2.0s (cinematic) | Time passage, memory, softness | Scene change in time; dream/memory; warm tone | Modern fast-paced shorts (feels slow); back-to-back dissolves = transition fatigue |
| Dip to black | 0.5-1.5s | Act break, chapter end, death | Hard scene separation; end of a chapter; title card | Between every short scene (feels choppy) |
| Dip to white | 0.3-0.8s | Flash, overexposure, heavenly | Flashback start; bright reveal; memory wipe | Overused in vlogs; looks cheap if repeated |
| Fade in (from black) | 0.5-1.5s | Opening, calm | Video opening; first shot | Opening of every segment |
| Fade out (to black) | 0.5-2.0s | Ending, finality | Video ending; outro | End of every short clip |
| Wipe (left/right/up/down/circle) | 0.3-0.8s | Playful, retro, stylized | Retro / 80s / cartoon aesthetic; Bilibili meme cuts | Cinematic drama; feels dated unless intentional |
| Iris (circle open/close) | 0.4-1.0s | Old film, storybook, focus isolation | Fairytale; revealing a detail within a circle | Modern documentary; feels gimmicky |

### Audio-Led Transitions

| Type | Typical Duration | Emotional Effect | When It Works | When It Fails |
|---|---|---|---|---|
| J-cut (audio leads video) | audio starts 0.5-1.5s before video cut | Anticipation, smooth handoff | Next scene's sound (door, laughter, music) heard before we see it; dialogue across cuts | Audio bleed competes with current scene's dialogue |
| L-cut (video leads audio) | audio ends 0.5-2.0s after video cut | Reflection, lingering emotion | Reaction shot holds voice-over; someone speaks as we leave them | Mismatched tone; audio from old scene contradicts new visual |
| Audio bridge (sound effect or music carries across cut) | full crossfade over boundary | Unity, energy | Whoosh / riser / beat drop masks the cut; music under both scenes | No bridge sound designed; cut still audible |

### Creative Transitions

| Type | Typical Duration | Emotional Effect | When It Works | When It Fails |
|---|---|---|---|---|
| Freeze frame | hold 0.5-2.0s | Pause, emphasis, punchline | Punchline reveal; "wait for it"; title card over freeze | Overused; kills momentum |
| Speed ramp transition | 0.5-1.5s ramp (slow-mo to real time or vice versa) | Energy, emphasis, stylized | Action reveal; hit moment; sports; music video | Dialogue scenes (distracting); AI-generated footage where motion blur looks fake |
| Whip pan / flash pan | 0.2-0.4s motion blur between shots | High energy, disorientation, speed | Fast cuts; high-energy montage; chase | Slow narrative; two shots with no motion direction to match |
| Zoom through (push into object / out of object) | 0.5-1.5s | Spatial jump, discovery | Push into a door frame and out the other side; zoom into a photo and into the scene | Object has no clear center; AI-generated zoom looks warped |
| Morph / shape morph | 0.5-1.2s | Surreal, magical, branded | Logo morph; object morphs into another (apple -> Earth) | Narrative realism; morph artifacts in AI footage |
| Glitch | 0.2-0.5s digital glitch | Cyberpunk, error, energy | Tech / gaming / EDM content; beat drop | Gentle lifestyle content; overdone |
| Light leak | 0.5-1.5s warm overlay | Filmic, nostalgic, romantic | Wedding / travel / lifestyle; warm grade | Corporate / clean explainers |
| Overlay transition (hand pass, object passes lens) | 0.3-0.6s | Seamless, invisible | Person walks past camera -> cut to next scene with same motion | No foreground motion in either shot |

## Transition Rhythm and Pacing

### Transitions Per Minute by Genre

| Genre | Avg Shot Length | Transitions (cuts) per Minute | Notes |
|---|---|---|---|
| Talking head / interview | 4-8s | 8-15 cuts/min | Prefer hard cuts; cut on dialogue pauses |
| Fast-cut shorts (Douyin/TikTok) | 0.5-1.5s | 40-120 cuts/min | Whip pans, jump cuts, beat-synced |
| Vlog / lifestyle | 2-4s | 15-25 cuts/min | Mix of hard cuts, J-cuts, dissolves |
| Cinematic / short film | 3-6s | 10-20 cuts/min | Match cuts, dissolves, L-cuts |
| Explainer / tutorial | 2-5s | 12-20 cuts/min | Cutaways to B-roll; kinetic text overlays |
| Music video | 0.5-2s | 30-90 cuts/min | Beat-synced; speed ramps; creative transitions |

### Beat-Syncing

- **On-beat cut**: cut lands exactly on a beat (downbeat or accent). Feels powerful, deliberate. Use for drops, reveals, punchlines.
- **Off-beat cut**: cut lands between beats (on the "and" of 1). Feels natural, conversational. Use for dialogue, organic moments.
- Rule of thumb: action/energy cuts on the beat; emotional/narrative cuts slightly off-beat.
- If BPM = 120, beat = 0.5s. Snap transition midpoint to the nearest beat grid line.

### The 30-Degree Rule for Cuts

When cutting between two shots of the same subject, the camera angle should change by at least 30 degrees or the shot size should jump a tier (e.g., medium -> close-up). Violating this produces a visible "jump." If you cannot change angle/size, use a cutaway or J-cut to mask it.

### Avoiding Transition Fatigue

- **Max 1 creative transition per 30 seconds**. If every boundary is a whip pan or glitch, none land.
- **Dissolves should not exceed 20% of all boundaries** in a single video.
- Reserve the most elaborate transition for the most important beat (the reveal / twist / CTA).
- If two adjacent boundaries both want a creative transition, drop one — let it be a hard cut.

## Scene Connection Logic

Before assigning a transition, answer: **why do these two scenes belong next to each other?** Pick the connection dimension:

| Connection Dimension | How | Transition That Serves It |
|---|---|---|
| By motion | Scene A ends with motion in direction X; Scene B begins with motion in direction X | Whip pan, match-on-action, overlay pass |
| By color | Dominant color in A matches dominant color in B | Cross-dissolve, dip to that color |
| By shape | A round object in A -> round object in B | Shape morph, match cut on graphic |
| By sound | A's audio bridges into B's sound world | J-cut, L-cut, audio bridge with whoosh/riser |
| By thematic match | A shows a gun; B shows a flower — cut on thematic contrast | Smash cut, match cut on contrast |
| By eyeline | A looks off-screen right; B is what they see | Eyeline match cut (hard cut) |

The decision framework, per boundary:

1. What is the emotional job of this boundary? (time jump / location jump / same place continuous / punchline / chapter break)
2. What shared element exists between shot N and shot N+1? (motion, color, shape, sound, subject)
3. If there is a shared element, prefer a match/motion transition. If not, default to hard cut unless emotional job calls for dissolve/dip.
4. Does music have a beat near the boundary? If yes, snap the transition midpoint to that beat.

## Platform-Specific Transition Norms

| Platform | Default Cut Length | Transition Style | Notes |
|---|---|---|---|
| Douyin / TikTok (vertical 9:16) | 0.3-0.8s average shot | Fast cuts, jump cuts, beat-synced whip pans, meme overlays | Hook in first 1.5s; cut every 1-2s during energy |
| Bilibili (vertical or horizontal) | 1-3s average shot | Varied; meme transitions, fast cuts in highlights, clean in essay content | Danmaku (bullet-comment) culture: playful transitions welcome; long-form essays prefer clean |
| YouTube (16:9 horizontal) | 2-5s average shot | Cleaner, fewer flourishes; hard cuts and dissolves; J/L-cuts common | Viewer tolerance for slower pacing; avoid whip pans that cause motion sickness |
| WeChat Channels (vertical) | 1-2s average shot | Subtle, conservative; prefer hard cuts and gentle dissolves | Older audience; flashy transitions read as low-quality |
| Xiaohongshu (vertical 3:4 or 9:16) | 1.5-3s average shot | Aesthetic dissolves, warm dips to white, light leaks; soft palette | Lifestyle / beauty / food; transitions should feel pretty, not punchy |

Platform format note: vertical (9:16) platforms tolerate faster cutting and more aggressive transitions than horizontal (16:9) because the frame is a close-up and attention is shorter.

## Workflow

### Step 1: Inventory Shots

List all shots in order with durations. Output a table:

```
| # | Shot Description | Duration (s) | Scene ID |
```

Expected: N rows, total duration matches target.
If it fails: durations don't sum to target -> ask user which to adjust.

### Step 2: Group Shots by Scene

Mark scene boundaries. A new scene = location change, time change, or topic change. Same-scene shot-to-shot cuts usually default to hard cut; scene boundaries get deliberate transitions.

### Step 3: Decide Transition Type Per Boundary

For each of the N-1 boundaries, ask the four questions in "Scene Connection Logic" and pick one row from the catalog. Output:

```
| Boundary (between shot # and #) | Transition Type | Duration (s) | Audio Behavior | Beat Sync? | Rationale |
```

Expected: every boundary has a decided transition. No boundary left as "TBD."
If it fails: a boundary has no clear reason -> default to hard cut and note "default hard cut, no deliberate transition."

### Step 4: Set Durations

Apply duration guidelines from the catalog. Defaults:
- Hard cut: 0s
- Cross-dissolve: 0.5s (shorts) / 1.5s (cinematic)
- Fade/dip: 1.0s
- Whip pan: 0.3s
- Glitch: 0.3s
- Speed ramp: 1.0s

### Step 5: Map to Music Beats

If BPM is known, snap transition midpoints to nearest beat. Mark on-beat vs off-beat. If no music, skip this step and note "no music, natural rhythm."

### Step 6: Write the Transition Plan

Output the final plan as a markdown table plus a short prose note on the overall pacing intent. This is the handoff artifact for video-editor.

## Parameter Quick Reference

| Transition Type | Typical Duration | FFmpeg xfade Filter | Notes |
|---|---|---|---|
| Hard cut | 0s | (none; simple concat) | Default |
| Cross-dissolve | 0.3-1.0s | `xfade=transition=fade:duration=D:offset=O` | `fade` = crossfade |
| Fade in from black | 0.5-1.5s | `fade=t=in:st=0:d=D` | On first clip |
| Fade out to black | 0.5-2.0s | `fade=t=out:st=START:d=D` | On last clip |
| Dip to black | 0.5-1.5s | `xfade=transition=fadeblack:duration=D` | |
| Dip to white | 0.3-0.8s | `xfade=transition=fadewhite:duration=D` | |
| Wipe left | 0.3-0.8s | `xfade=transition=wiperight:duration=D` (wipe direction varies) | |
| Circle iris | 0.4-1.0s | `xfade=transition=circleopen` / `circleclose` | |
| Slide | 0.3-0.6s | `xfade=transition=slideleft` / `slideright` | |
| Wipe up/down | 0.3-0.6s | `xfade=transition=wiperight` variants | |
| Whip pan | 0.2-0.4s | Not native to xfade; use `rx="...":ry="..."` zoompan or motion-blur overlay | Plan only; execution in video-editor |
| Glitch | 0.2-0.5s | Not native; use `glitch` filter or overlay clip | Plan only |
| Speed ramp | 0.5-1.5s | `setpts` + `fps`; not an xfade | Plan only |
| J-cut | audio leads 0.5-1.5s | `adelay` on next clip's audio, or `acrossfade` | See video-editor recipes |
| L-cut | video leads, audio tails 0.5-2.0s | `apad` on previous clip's audio | |

Offset calculation: for N clips chained with xfade, the `offset` for the k-th transition = sum of previous clip durations minus (k-1) * transition_duration. This is the value video-editor computes at execution time.

## Failure Remediation Table

| Symptom | Cause | Remedy |
|---|---|---|
| Cut feels jarring / viewer notices it | Two shots too similar (same angle, same size) or no motion match | Switch to a match cut, cutaway, or J-cut; or change shot size by a tier |
| Too many dissolves, video feels slow | Dissolves used on every boundary | Replace dissolves with hard cuts except at true time/location jumps; keep <=20% dissolves |
| Transition doesn't match mood | Comedy moment got a dip-to-black; sad moment got a whip pan | Re-read emotional job of the boundary; pick from catalog by emotional effect column |
| Audio pop / click at cut | Audio waveform clicks at the edit point | Use 20-50ms audio crossfade (`acrossfade=d=0.03`) or J/L-cut to smooth |
| Beat sync feels off | Transition lands between beats but expected on beat | Move transition midpoint to nearest beat grid line; snap to downbeat for drops |
| Transition fatigue (viewer numb) | More than 1 creative transition per 30s | Strip creative transitions back to hard cuts; keep the best one |
| Whip pan causes motion sickness | Pan too fast or no motion blur | Slow to >=0.3s; add motion blur; avoid on YouTube horizontal content |
| Dissolve lingers too long | Duration >1s on shorts | Cut dissolve to 0.3-0.5s for vertical platforms |
| Jump cut looks like a mistake | Same framing with no time indicator | Add a jump cut on purpose (jump in time with wardrobe/position change) or insert a cutaway |
| Transition covers the dialogue | Dissolve over speech makes voice muddy | Move transition to a pause in dialogue; use J-cut so audio leads cleanly |

## Delivery Standard / Quality Checklist

Before handing off to video-editor, verify:

- [ ] Every one of the N-1 boundaries has a decided transition type (no "TBD").
- [ ] Every transition has a numeric duration in seconds (not just "short" / "long").
- [ ] Beat sync noted for each boundary (on-beat / off-beat / no music).
- [ ] Creative transitions <= 1 per 30 seconds of total runtime.
- [ ] Dissolves <= 20% of all boundaries.
- [ ] Opening fade-in and closing fade-out decided (or explicitly omitted).
- [ ] Platform format noted (9:16 vertical vs 16:9 horizontal) and durations match platform norms.
- [ ] Rationale written for at least the 3 most important boundaries (reveal, twist, CTA).
- [ ] No transition is planned over dialogue that needs to be heard cleanly.

## Chain Handoff

- **Downstream: video-editor** — executes this plan with FFmpeg `xfade` / `acrossfade` filters. The transition table is the input spec; durations and types map directly to filter arguments.
- **Downstream: video-subtitles** — if a transition lands on a subtitle, subtitles should shift timing accordingly; the transition plan's beat grid informs subtitle timing.
- **Downstream: video-thumbnail** — thumbnails are grabbed from hold frames; avoid placing a transition midpoint on a thumbnail source frame.
- **Upstream inputs**: storyboard-designer (shot list + scene list), video-script-writer (dialogue beats), video-voice-synth (audio timing), motion-effects-designer (if motion graphics overlay a transition).

## References

- FFmpeg xfade documentation: https://ffmpeg.org/ffmpeg-filters.html#xfade (transition names and offset math)
- Film editing grammar: 30-degree rule, 180-degree rule, match cut, J/L-cut (standard cinematography references)
- Platform editing norms: Douyin/TikTok fast-cut conventions, YouTube pacing research, Xiaohongshu aesthetic editing trends
- This skill is a planning document only; execution recipes live in `video-editor/references/ffmpeg-recipes.md`.
