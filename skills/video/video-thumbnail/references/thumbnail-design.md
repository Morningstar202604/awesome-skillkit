# Thumbnail Design Parameters (video-thumbnail)

The thumbnail decides click-through rate. **Dimension values are volatile information**—platform
limits and specs change with versions; composition, safe zones, and minimum font sizes are
relatively stable human-factor heuristics that can be used long-term.

## Table of Contents

0. Data credibility and how to verify / 1. Platform size reference / 2. Composition: rule of thirds and subject proportion
3. Text safe zone / 4. Minimum font size and contrast / 5. Copy rules / 6. Common click-through mistakes
7. Implementation: frame extraction + overlay / 8. Pre-delivery self-check

## 0. Data credibility and how to verify

| Tier | Examples | How to use |
|---|---|---|
| Volatile (platform specs) | Thumbnail dimensions, file size limits, format | **Must verify before publishing**, see method below |
| Stable (human-factor heuristics) | Rule-of-thirds composition, minimum font size, contrast | Use directly, fine-tune with your own measured data |

Three ways to verify the platform's current spec (pick one; don't rely on memory):

1. Open the platform's creator center / upload page; the upload page shows the currently allowed thumbnail size and file size;
2. Check the platform help docs' "thumbnail/video specs" entry;
3. Upload a test image; the error message will state the current limit.

**Treat all dimension values as "common values as of 2026; verify the platform's latest spec before publishing."**

## 1. Platform size reference

The values below come from this repo's SKILL.md notes + common practice; **they are volatile information—verify before publishing**:

| Platform | Common thumbnail size | Aspect ratio | File size limit (common value) | Notes |
|---|---|---|---|---|
| Douyin | 1080 × 1920 | 9:16 | 2 MB | Vertical; defer to the publish-page prompt |
| TikTok | 1080 × 1920 | 9:16 | 2 MB | Vertical |
| Bilibili | 1920 × 1080 | 16:9 | 2 MB | Landscape cover |
| YouTube | 1280 × 720 | 16:9 | 2 MB | Landscape cover |

Platforms not listed = this repo has no reliable record; **don't fill in from memory**.

General export principles:

- First export PNG at the size in the table above; if over size, convert to JPG and lower quality
  (PNG keeps text sharp; JPG keeps file size down).
- After outputting, always check the actual dimensions—don't trust "I set it to 1080":

```bash
ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 thumb.png
ls -l thumb.png        # is the file over the platform limit?
```

## 2. Composition: rule of thirds and subject proportion

- **Rule of thirds**: divide the frame into thirds horizontally and vertically; place the subject
  (face / product) near the intersections of the four dividing lines. For vertical thumbnails, place
  the subject at the **upper-half** intersections, because the lower half is covered by titles and UI.
- **Subject proportion** (guideline): the person or product occupies 40%–60% of the frame height.
  Below 30% it's unrecognizable on a mobile thumbnail; above 70% there's nowhere to put the text.
- **Gaze direction**: having the person's eyes look toward frame center or toward the title text
  naturally draws the viewer's attention to the copy.
- **Single subject**: one visual center. Two subjects = visual conflict = a muddy blob on the thumbnail.
- **Simplify the background**: lower background saturation / add blur so the subject and text pop.

## 3. Text safe zone

Platforms overlay their own UI on top of the thumbnail (title, author name, play button, bottom
copy). Text pushed into these areas will be covered.

| Platform | Safe zone (per this repo's SKILL.md, volatile) |
|---|---|
| Douyin / TikTok | Keep key text out of the top 10% and bottom 15% |
| Bilibili | Full frame usable, but the bottom-right corner is often taken by a duration badge |
| YouTube | Bottom-right corner often taken by a duration badge |

Practical recommendations (guideline values, more conservative than the table above, usually safe):

- Vertical 9:16: place the title text at **55%–70% of the vertical** dimension, with 8% margins on left and right;
- Landscape 16:9: place text beside the subject, with 5% margins all around, reserve the bottom-right for a badge;
- On any platform, never put text in the bottom 10% of the frame.

## 4. Minimum font size and contrast

Minimum font sizes (guideline values, given by thumbnail width; based on 1080-wide vertical / 1280-wide landscape):

| Use | 1080 wide (9:16) | 1280 wide (16:9) | Notes |
|---|---|---|---|
| Main title | ≥ 72 px | ≥ 64 px | Any smaller turns to mush on a mobile thumbnail |
| Subtitle | ≥ 48 px | ≥ 40 px | Only supplement when the main title is under 6 characters |
| Badge / badge icon | ≥ 36 px | ≥ 32 px | Short labels like "NEW", "FULL VERSION" |

The main title should be **no more than 8 Chinese characters**. If it's longer, cut it—don't try to
shrink the font to cram it in: a thumbnail is glanced at at a few dozen pixels.

Contrast (citing a verifiable public standard, not invented):

- Body-level text vs. background contrast ≥ **4.5:1**; large text (≥18pt, or ≥14pt and bold) ≥ **3:1**
  (WCAG 2.1 AA thresholds, `VERIFY BEFORE USE`: defer to the current WCAG at w3.org).
- The easiest way to meet this isn't adjusting colors but **adding an outline or a translucent bar**:
  white text + 2–4 px dark outline, or a 30%–50% opacity dark gradient under the text.
- Forbidden: light gray text on a light background, white text on snow/white walls, colored text on a colored background.

## 5. Copy rules

| Rule | Notes |
|---|---|
| Length | Chinese main title 2–8 characters, at most two lines |
| Relationship to video title | **Complementary, not repetitive**: the thumbnail states the conflict/result, the video title states the hook |
| Verbs first | "I returned it" beats "my return-experience sharing" |
| Specific numbers | "8900 yuan" beats "very expensive"; a concrete number carries information by itself |
| Questions leave a hook | The question must be answerable by the video, otherwise it's clickbait |
| No obscure words/memes | Recognition cost is too high at thumbnail size |

## 6. Common click-through mistakes

| Mistake | Consequence | Fix |
|---|---|---|
| Thumbnail text = the video title verbatim | Zero information gain; viewers already saw the title and swipe away | Thumbnail states the conclusion/contrast, title states the hook |
| Text crammed all over the frame | It's mush on a thumbnail, equivalent to nothing | Main title ≤8 characters; leave other info to the title |
| Subject too small or off-center | Unrecognizable on a thumbnail | Subject occupies 40%–60% of frame height, placed at a rule-of-thirds intersection |
| Misleading thumbnail (content doesn't deliver) | Short-term CTR↑ but completion rate↓; long-term platform demotion | The thumbnail must be a shot/conclusion that actually appears in the video |
| No person, no expression | No emotional hook | If there's a person, show a face + an obvious expression |
| Completely different style every episode | No recognition; existing fans can't tell it's you | Fix the colors/font/position to build series recognition |
| Changing three variables at once in an A/B test | You don't know which variable worked | Change only one variable at a time (copy / subject / colors) |
| Using the video's first frame directly | Usually a black frame or a transition frame | Extract a frame after 1–3 seconds, or manually pick the frame with the fullest expression |

The right way to A/B test: prepare 2 thumbnails for the same video, **change only one variable** and
keep everything else identical; compare click-through rates over the same time window; don't conclude
when the sample is too small (views too low).

## 7. Implementation: frame extraction + overlay

Route A (when you have a source video; fastest, most faithful):

```bash
# Extract one frame at 1.5 seconds (skip the opening black frame)
ffmpeg -y -ss 1.5 -i final.mp4 -frames:v 1 -q:v 2 base.png

# Overlay the title text (font path varies by distro; confirm with fc-list :lang=zh and replace)
ffmpeg -y -i base.png -vf \
  "drawtext=fontfile=/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc:\
text='Baby Review':fontcolor=white:fontsize=88:borderw=4:bordercolor=black:\
x=(w-text_w)/2:y=h*0.60" -q:v 2 thumb.png
```

Failure branches: `No such filter: 'drawtext'` → this build wasn't compiled with drawtext (needs
freetype); font path doesn't exist → find the real path with `fc-list :lang=zh`; Chinese turns into
boxes → the font has no CJK glyphs.

Route B (AI-generated): use image generation; the prompt must hard-code the **aspect ratio** (e.g.
`9:16 vertical`), **subject proportion**, **negative-space position**, and **no text** (generated
text is usually garbled—always overlay text in post).

Both methods must end with the dimension-check command from Section 1.

## 8. Pre-delivery self-check

- [ ] Dimensions and aspect ratio match the target platform (measured with `ffprobe`, not "I think")
- [ ] File size is within the platform limit (`ls -l`)
- [ ] Subject is at a rule-of-thirds intersection, occupying 40%–60% of frame height
- [ ] Text is within the safe zone, not covered by the bottom 10% / badge position
- [ ] Main title ≤8 characters, font size no smaller than the Section 4 minimum
- [ ] Text vs. background contrast meets the bar (outline or underlay present)
- [ ] The thumbnail's promise matches the video content (not clickbait)
- [ ] Thumbnails in the same series are stylistically consistent
