---
name: motion-effects-designer
description: "Design motion graphics and visual effects for AI video: kinetic typography, lower thirds, animated charts, particles, overlays, subtitle animation styles, and easing/timing specs. Produces a motion spec that video-editor executes. Use when the user asks to design motion graphics / add animated text / animate a chart / add particles / style captions / choose easing / add lower thirds / plan VFX overlays / make text bounce. Do NOT use for cutting between scenes (use transition-designer), for executing the actual edit (use video-editor), or for generating background footage (use video-generation)."
license: Apache-2.0
compatibility: Pure prompt-based design skill; no scripts required. Outputs a motion spec consumed by video-editor.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: video
  pattern: planning
  tier: standard
  verified-date: "2026-09-24"
---

# Motion Effects Designer

Plan motion graphics and visual effects overlays for AI video. This skill does not render effects; it produces a **motion spec** — a per-overlay table with type, timing, easing, on-screen position, and parameters that downstream `video-editor` (or CapCut / After Effects) executes.

The core principle: motion should **direct attention, not decorate**. Every animated element must earn its screen time. If a static text plate would do the job, animate only the entrance and exit, not the whole duration.

## Applicability Decision Table

| Your Situation | Use This Skill? | Go To |
|---|---|---|
| Need animated text, lower thirds, titles, logo anim | yes, this skill | here |
| Need charts/counters/progress bars animated | yes, this skill | here |
| Need particles, light leaks, grain, vignette overlays | yes, this skill | here |
| Need to plan how two scenes cut together | out of scope | transition-designer |
| Need to actually run FFmpeg / AE and render | out of scope | video-editor |
| Need to write on-screen text content itself | out of scope | video-subtitles (captions) / video-script-writer |
| Need a static thumbnail | out of scope | video-thumbnail |
| Talking-head video with no B-roll | caution: minimal motion only; read "When Motion Hurts" | here, with restraint |

## Input Checklist

| Input | Required | Default if Missing |
|---|---|---|
| Shot list / scene list with timestamps | yes | ask |
| On-screen text content (titles, captions, labels) | yes | ask — cannot design animation without content |
| Platform target | no | assume Douyin vertical 9:16 |
| Brand style guide (colors, fonts, logo) | no | generic sans-serif, white text |
| Music / BPM | no | 120 BPM; animations sync to beats |
| Audio / voice-over timing | no | animate on sentence boundaries |

When required inputs are missing, ask once: "Please provide: (1) the shot list with timestamps; (2) all on-screen text to animate (titles, captions, labels); (3) target platform; (4) brand colors/logo if any."

## Pre-flight Checks

- Inventory every on-screen element that moves: titles, lower thirds, captions, logos, charts, particles, overlays. If an element is static on screen for the whole video, it is not motion graphics.
- Identify the attention moments: which frame is the punchline? Which number must the viewer read? Motion should peak at those moments.
- Check safe areas: for 9:16 vertical, keep critical text inside the central 80% horizontally and 85% vertically (platform UI overlays the bottom ~15% and right ~10%).
- Note platform format: vertical 9:16 tolerates bolder, larger, bouncier motion than horizontal 16:9.
- For talking-head videos, count planned motion elements: budget is **at most 2 animated elements per 30 seconds**. Anything more distracts from the speaker.

## Motion Graphics Types Catalog

### Kinetic Typography (Animated Text)

| Style | Typical Timing | Use Case | Adds Value When | Clutters When |
|---|---|---|---|---|
| Typewriter reveal | 0.05-0.1s per character, 0.5-1.5s total | Quotes, code, intimate text | Monospace font; tech / writing content | Long sentences (too slow) |
| Fade-up (opacity + y-offset) | 0.3-0.5s in, hold, 0.2s out | Section titles, clean captions | Minimalist content; YouTube | Used for every word (muddy) |
| Slide-in (from left/right) | 0.2-0.4s in | Lower thirds, name plates | Direction matches content flow | Multiple texts slide from same side (flat) |
| Scale pop (0->110%->100%) | 0.15-0.3s | Punchwords, keywords, CTA | Emphasizing 1-2 words per beat | Every word pops (comic, unreadable) |
| Text mask reveal (wipe through a mask) | 0.4-0.8s | Stylish title sequences, brand intros | Fashion / beauty / aesthetic | Explainer content (slows reading) |
| Text-on-path (text follows a curve) | 1-3s duration | Playful, artistic titles; brand logos | Short phrases only | Body text (unreadable while moving) |

### Lower Thirds and Titles

| Type | Typical Timing | Use Case | Adds Value When | Clutters When |
|---|---|---|---|---|
| Name plate (lower third) | 0.3s in, hold 2-4s, 0.3s out | Introducing a person / interviewee | Name + role; fades in once | Reappears every sentence |
| Section title (full-screen or center) | 0.4s in, hold 1.5-3s, 0.4s out | Chapter breaks, topic shifts | Signals a new section | Between every short shot (feels choppy) |
| Animated logo | 0.5-1.5s | Intro / outro | Once at start, once at end | Mid-video watermark animation |
| Lower-third bug (persistent) | static after entrance | Channel watermark | Branded, unobtrusive | Animated continuously (distracting) |

### Data Visualization Animation

| Type | Typical Timing | Use Case | Adds Value When | Clutters When |
|---|---|---|---|---|
| Line/bar chart drawing | 1-3s draw-on | Explaining trends | Data story has a "reveal" beat | Static chart would be fine |
| Number counter | 0.8-2.0s count up | Stats, results, money amounts | Number is the punchline | Small numbers (no impact) |
| Progress bar fill | 1-3s fill | Loading, ranking, steps | Linear process content | Already know the result |
| Map reveal (region lights up) | 0.5-1s per region | Geography / logistics / market share | Multiple regions compared | Single location (just show a pin) |
| Pie chart sweep | 0.8-1.5s | Composition breakdown | Comparing slices | Single slice (just show the number) |

### Particle and Atmospheric Effects

| Type | Typical Timing | Use Case | Adds Value When | Clutters When |
|---|---|---|---|---|
| Dust / floating particles | continuous loop | Dreamy, atmospheric, product shots | Warm / cinematic tone | Corporate explainer |
| Bokeh (out-of-focus lights) | continuous | Night, romance, lifestyle | Shallow-depth aesthetic | Text-heavy content (muddies readability) |
| Light rays (god rays) | subtle, continuous | Sunrise, holy, hopeful | Key emotional beat | Every scene (over-saturated) |
| Rain / snow overlay | continuous loop | Mood, weather mood-set | Matches scene tone | Dialogue scene (distracts from face) |
| Sparkles | 0.5-1s burst on beat | Beauty, fashion, CTA | Highlight a product / keyword | Every beat (cheap looking) |
| Confetti | 1-2s burst | Celebration, win, CTA hit | Once per celebratory moment | Repeated (loses impact) |

### Overlays and Accents

| Type | Typical Timing | Use Case | Adds Value When | Clutters When |
|---|---|---|---|---|
| Light leak | 0.5-1.5s warm flash | Filmic, nostalgic, transition | Between scenes; warm grade | Clean tech content |
| Film grain | continuous subtle layer | Film texture, cinematic | Matching a film look | Digital / screen-recorded content |
| Vignette | static (or subtle pulse) | Focus attention to center | Portrait / talking head | Already dark scene (too dark) |
| Lens flare | 0.5-1.5s on light source | Photorealism, sunny scene | Natural light source exists | Artificial flare added everywhere |
| Scan lines | continuous | Retro / CRT / tech aesthetic | Gaming / cyberpunk theme | Modern lifestyle |
| Glitch artifacts | 0.2-0.5s | Error, beat drop, cyberpunk | On music drops / transitions | Gentle content |

### Transitions-as-Motion (overlapping with transition-designer)

| Type | Typical Timing | Use Case |
|---|---|---|
| Morphing shape (circle expands to new scene) | 0.5-1.0s | Creative scene change |
| Liquid transition (warp/water) | 0.6-1.2s | Playful, brand-style |
| Page flip | 0.5-1.0s | Journal / book / scrapbook aesthetic |

These overlap with transition-designer; coordinate so motion-effects-designer owns the visual treatment and transition-designer owns the boundary timing.

## Animation Principles for AI Video

Adapted from the 12 basic principles of animation, applied to motion graphics:

1. **Slow in / slow out (ease curves)**: Nothing starts or stops instantly. Use ease-out on entrances (fast start, settle), ease-in on exits (slow start, accelerate). Avoid linear motion for anything organic.
2. **Follow-through and overlapping action**: When a text box stops moving, its shadow / underline / accent finishes slightly after. When a character stops, hair/clothing trails.
3. **Staging**: The viewer's eye must land on the most important thing first. If everything moves, nothing moves.
4. **Anticipation**: A 0.1-0.2s small backward movement before the main motion (text pulls down slightly before popping up) makes motion feel physical.
5. **Timing**: 12 frames (0.5s at 24fps) is the minimum readable entrance. Faster than 0.2s feels like a flicker; slower than 1.5s feels sluggish.
6. **Keyframe spacing**: Motion should decelerate at the end — keys spaced wide apart at start, close together at end. Bezier handles: ease-out = ease in 0, ease out 1 (cubic-bezier(0, 0, 0.2, 1) in CSS).
7. **Motion blur**: Fast moving elements need motion blur; static elements do not. AI-generated footage often lacks natural motion blur — add subtle direction blur on fast overlays.
8. **Secondary action**: Small supporting motions (a bounce under a title, a twinkle near a number) add life without competing.

**Default easing cheatsheet**:
- Pop / punch: `cubic-bezier(0.2, 1.4, 0.4, 1)` (overshoot, bouncy)
- Smooth entrance: `cubic-bezier(0.2, 0, 0, 1)` (standard ease-out)
- Smooth exit: `cubic-bezier(0.4, 0, 1, 1)` (ease-in)
- Spring / elastic: use physics spring (stiffness 200-300, damping 15-20)

## Subtitle and Caption Animation Styles

| Style | Timing | Platform Norm | Readability |
|---|---|---|---|
| Pop-in (scale 0->1 with overshoot) | 0.15-0.25s per word | Douyin / TikTok default: bold, big, centered | High if bold outline |
| Karaoke highlight (word fills in on beat) | per syllable, 0.05-0.1s | Music / lyric videos | High when synced to voice |
| Word-by-word reveal | 0.1-0.2s per word | YouTube / Instagram captions | High, clean |
| Bouncing emoji captions | emoji bounces 0.3s | Bilibili / playful vlogs | Medium (emoji distracts) |
| Static caption with subtle fade | 0.2s fade | YouTube / WeChat Channels | Highest for long-form |
| Text shadow / outline | permanent | All platforms: 2-4px black outline or 50% shadow | Required over busy footage |

Platform norms:
- **Douyin**: bold, large, pop-in, centered, with thick outline. Captions are a primary delivery channel, not secondary.
- **Bilibili**: playful, meme-friendly, emoji accents, danmaku-style (subtitles that feel chatty, like scrolling bullet comments).
- **YouTube**: clean, smaller, lower-third, minimal animation. Viewers read; don't distract.
- **WeChat Channels**: subtle, conservative, small outline.
- **Xiaohongshu**: aesthetic, softer font, fade-up, warm color accents.

## When Motion Hurts (Red Lines)

1. **Motion sickness from fast zooms/pans**: Keep continuous zoom speed under 10% per second; whip pans only >=0.3s with motion blur. Avoid rapid back-and-forth motion.
2. **Text unreadable**: If text moves during reading, the viewer cannot read it. Text must be on screen and stable for at least 1.5x the reading time (roughly 0.5s per word) before animating out.
3. **Brand inconsistency**: If a brand guide exists, do not introduce random fonts/colors/animation styles. Lock the typeface and color palette.
4. **Over-animation on talking-head**: Max 2 animated elements per 30s. The speaker's face is the content; motion around it competes.
5. **Particles over dialogue**: Floating dust/confetti over a speaker's face reads as noise. Keep overlays away from the face region.
6. **Animated watermarks**: A logo that continuously bounces/rotates is a bug, not a feature. Enter once, stay static.
7. **More than 3 colors on screen at once** in kinetic typography. Limit to brand palette + one accent.

## Workflow

### Step 1: Identify Moments Needing Motion

Go through the shot list. For each shot, ask: does the viewer need to look at something specific that is not already in the footage? If yes, that moment gets a motion element. Output a list:

```
| Timestamp | Element Type | Content (text/data) | Why motion is needed |
```

Expected: every motion element has a reason. If "because it looks cool," drop it.

### Step 2: Choose Motion Type Per Element

Pick from the catalog. One element = one primary motion style. Do not stack 3 animations on the same text block.

### Step 3: Set Timing and Easing

For each element, specify:
- Entrance duration (s)
- Hold duration (s)
- Exit duration (s)
- Easing curve (use the cheatsheet)
- On-screen position (safe area)
- Font size / color / weight (if text)

### Step 4: Specify Parameters

Output a per-element spec table:

```
| # | Type | Timestamp In/Out | Position | Size/Color | Easing | Tool |
```

### Step 5: Write the Motion Spec

Combine into a single handoff document. Note overlaps with transition-designer (if motion overlays a transition boundary). This spec goes to video-editor for execution.

## Parameter Quick Reference

| Effect Type | Typical Duration | Easing | Executable In |
|---|---|---|---|
| Fade-up text | 0.4s in / 0.2s out | ease-out | CapCut, AE, FFmpeg (drawtext + fade) |
| Scale pop text | 0.2s | overshoot bezier | CapCut, AE |
| Typewriter | 0.05s/char | linear | CapCut, AE, FFmpeg (drawtext expansion) |
| Slide-in lower third | 0.3s | ease-out | CapCut, AE, FFmpeg (overlay + x offset) |
| Number counter | 1.0-2.0s | ease-out | AE, CapCut (number animation); FFmpeg via frame-by-frame |
| Progress bar | 1.5-3s | linear or ease-in-out | AE, CapCut |
| Particle burst (sparkles/confetti) | 0.5-1.5s | physics | AE, CapCut, stock overlays |
| Dust / bokeh loop | continuous | n/a | Stock overlay clip, blend screen |
| Light leak | 0.5-1.5s | ease in-out | Stock overlay, blend screen/add |
| Film grain | continuous subtle | n/a | FFmpeg `noise` filter, overlay |
| Vignette | static | n/a | FFmpeg `vignette` filter |
| Lens flare | 0.5-1.5s | ease in-out | Stock overlay, blend screen |
| Glitch | 0.2-0.5s | abrupt | AE, CapCut glitch effect; FFmpeg `glitch` |
| Karaoke caption | per syllable | linear sync | AE, CapCut caption tool |
| Word-by-word caption | 0.15s/word | ease-out | CapCut, AE |

Tools that can execute each: CapCut (mobile, fast, built-in templates), After Effects (desktop, full control), FFmpeg (scripted, headless — see video-editor recipes), AI overlay generators (stock footage sites for particles/light leaks).

## Failure Remediation Table

| Symptom | Cause | Remedy |
|---|---|---|
| Text is unreadable | Animation runs while reading, or no outline | Freeze text on screen for >=1.5x reading time; add 3px black outline |
| Motion feels cheap / cheesy | Too many pop/bounce effects | Replace pop with fade-up; reduce to 1 accent per 30s |
| Viewer says "makes me dizzy" | Fast repeated zoom/pan/parallax | Slow zoom to <10%/s; remove back-and-forth loops |
| Particles cover the speaker's face | Overlay centered on frame | Move overlay to corners / top third; reduce opacity to 30-50% |
| Motion doesn't sync to music | Animation timing not on beat | Shift entrance to nearest beat; for music video, snap to downbeat |
| Chart animation outlasts attention | Draw-on >3s | Speed up draw to 1-1.5s; reveal result early |
| Brand colors don't match | Freehand colors picked | Lock to brand palette; pull hex from brand guide |
| Caption animation fights with voice | Caption pops mid-word | Delay caption entrance 0.1s after word is spoken; use karaoke mode |
| Lower third covers face | Positioned bottom-center | Move to bottom-left/right; keep above platform UI safe area |
| Too many simultaneous animations | Stacked motion on same frame | Reduce to 1 active motion element per 2 seconds; sequence them |

## Delivery Standard / Quality Checklist

Before handoff:

- [ ] Every planned motion element has a reason (not "looks cool").
- [ ] Entrance + hold + exit durations specified in seconds.
- [ ] Easing curve named per element (not just "smooth").
- [ ] Text elements have font size, color, position, and outline/shadow specified.
- [ ] Text on screen long enough to read (>=0.5s per word of hold time).
- [ ] No more than 2 animated elements active at the same time.
- [ ] No motion over the speaker's face region for talking-head content.
- [ ] Platform format noted (9:16 vertical safe areas respected).
- [ ] At most 1 pop/bounce accent per 30 seconds.
- [ ] Brand colors/fonts locked if a style guide exists.
- [ ] Overlays that need stock footage are flagged (particle packs, light leaks).

## Chain Handoff

- **Downstream: video-editor** — executes the motion spec with FFmpeg drawtext/overlay/xfade, or exports to CapCut/AE for complex motion.
- **Downstream: video-subtitles** — caption animation style is decided here; subtitle timing and styling flow to that skill.
- **Downstream: transition-designer** — if a motion graphic overlaps a scene transition, coordinate so the transition timing and motion entrance do not fight.
- **Upstream inputs**: video-script-writer (on-screen text content), visual-style-anchor (brand palette/typography), storyboard-designer (shot timestamps).

## References

- 12 Basic Principles of Animation (Disney, Johnston & Thomas) — adapted to motion graphics
- FFmpeg filter documentation: drawtext, overlay, fade, vignette, noise, zoompan (https://ffmpeg.org/ffmpeg-filters.html)
- CapCut motion templates and easing presets
- Platform caption norms: Douyin bold captions, YouTube readability guidelines, Bilibili danmaku style
- Motion design easing cheatsheets (cubic-bezier reference)
