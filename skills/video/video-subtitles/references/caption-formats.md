# Caption Format Reference (video-subtitles)

Four common subtitle carriers: **SRT** (most universal), **ASS** (use it when you want styling),
**VTT** (Web), **JSON word-level timestamps** (programmatically generated / animated captions).
Each gets a minimal runnable example + field explanation + pitfalls + ffmpeg burn/soft-mux command.

## Table of Contents

0. Choosing a format and general rules / 1. SRT / 2. ASS / 3. WebVTT / 4. JSON word-level timestamps
5. Encoding and BOM / 6. ffmpeg burning and soft-muxing / 7. Chinese line-breaking rules

## 0. Choosing a format and general rules

| Format | Use case | Styling capability | Notes |
|---|---|---|---|
| SRT | Platform upload, soft-muxed subtitle tracks | None | Best compatibility; do this first |
| ASS | Hard burn, effects captions | Strong (font/color/position/animation) | Usually unsupported on platform upload; only for burning into the picture |
| VTT | Web players, web side | Weak (limited cue settings) | The header must be `WEBVTT` |
| JSON word-level | "Karaoke-style" word-by-word highlight | Up to the renderer | No universal standard; the schema is whatever your tool uses |

General rules: the timeline must be **monotonically increasing**, adjacent cues must not overlap (when
overlapping, some players show only the later one); precision to the millisecond with start < end;
files are UTF-8 throughout (BOM tradeoff in Section 5); one Chinese cue ≤15 characters, at most two
lines; English one line ≤42 characters (guideline values, not hard standards).

## 1. SRT

```
1
00:00:00,000 --> 00:00:03,000
Guess how much I spent?

2
00:00:03,000 --> 00:00:08,000
8900! For this?
```

| Element | Syntax | Notes |
|---|---|---|
| Sequence number | `1`, `2`… | Increment from 1; some parsers ignore it, but don't omit it |
| Time line | `HH:MM:SS,mmm --> HH:MM:SS,mmm` | **The millisecond separator is a comma**, not a dot |
| Text | 1–2 lines | Most players ignore a third line |
| Separator | Blank line | There must be exactly one blank line between cues, and a trailing newline at file end |

Common pitfalls: writing `00:00:00.000` (a dot) → it's parsed as VTT or errors outright; no blank
line after the last cue → some parsers drop the last cue; writing a literal `\n` doesn't wrap—you must
use a real newline.

## 2. ASS

```
[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Noto Sans CJK SC,64,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,3,1,2,60,60,120,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:03.00,Default,,0,0,0,,Guess how much I spent?
Dialogue: 0,0:00:03.00,0:00:08.00,Default,,0,0,0,,8900! For this?
```

| Field | Meaning |
|---|---|
| `PlayResX/Y` | Logical resolution; coordinates and font size are based on it; set to `1080` / `1920` for vertical |
| `Fontsize` | Size based on PlayRes; 56–72 is common for a 1080-wide vertical (guideline) |
| `PrimaryColour` | Main color, format `&HAABBGGRR` (**channels reversed vs. `#RRGGBB`**) |
| `Outline` / `Shadow` | Outline/shadow width in pixels; for white-on-black start at `3` / `1` |
| `Alignment` | Numpad position: 1=bottom-left 2=bottom-center 3=bottom-right 5=center; vertical usually uses `2` |
| `MarginV` | Vertical margin; leave 200+ pixels at the bottom for platform UI on vertical |
| `Start` / `End` | `H:MM:SS.cc`, **centiseconds (two digits)**, not milliseconds |

Common pitfalls: writing milliseconds with three digits (`0:00:03.000`) → ASS only reads two
centiseconds, so it parses wrong; missing `[V4+ Styles]` or `Format:` line → parsing fails outright;
a font name that doesn't exist on the system → Chinese turns to boxes; use `fc-list :lang=zh` to get
the real name.

## 3. WebVTT

```
WEBVTT

1
00:00:00.000 --> 00:00:03.000 line:85% align:center
Guess how much I spent?

2
00:00:03.000 --> 00:00:08.000 line:85% align:center
8900! For this?
```

| Element | Syntax | Notes |
|---|---|---|
| File header | `WEBVTT` (first line) | **Required**; without it the whole file is inert |
| Time | `HH:MM:SS.mmm` or `MM:SS.mmm` | **The millisecond separator is a dot** (opposite of SRT) |
| Cue settings | Appended to the end of the time line | Common: `line:85%`, `position:50%`, `align:center` |
| Sequence number | Optional | Harmless if present |

Common pitfall: renaming an SRT to `.vtt` and using it → comma milliseconds + missing `WEBVTT` header;
the player silently shows nothing.

## 4. JSON word-level timestamps

**There is no universal standard.** Below is one common form; field names must match your ASR /
rendering tool (**VERIFY BEFORE USE**: first run your tool once to see what it actually outputs, then
copy its schema).

```json
{
  "duration": 8.0,
  "cues": [
    {
      "index": 1,
      "start": 0.0,
      "end": 3.0,
      "text": "Guess how much I spent?",
      "words": [
        {"word": "Guess", "start": 0.10, "end": 0.42},
        {"word": "how",   "start": 0.42, "end": 0.58},
        {"word": "much",  "start": 0.58, "end": 0.70}
      ]
    }
  ]
}
```

`start`/`end` use floating-point seconds (don't write `HH:MM:SS` strings; floats are easier to
compute); `words[].start/end` are per-word timings for word-by-word highlighting; for Chinese,
segmenting by **word** feels more natural than by single character.

Post-generation self-check (to prevent a broken timeline; if it fails, don't continue downstream):

```bash
python3 - <<'PY'
import json
d, prev = json.load(open("subs.json")), -1.0
for c in d["cues"]:
    assert prev <= c["start"] < c["end"], f"timeline anomaly: {c}"
    prev = c["end"]
print("OK cues =", len(d["cues"]))
PY
```

Expected output: `OK cues = N`.

## 5. Encoding and BOM

**Prefer UTF-8 without BOM.** The BOM is the main source of compatibility issues: some parsers treat
the BOM as part of the first cue, which shows up as "the first subtitle doesn't display" or "garbled
first line."

```bash
# Detect: the first 3 bytes EF BB BF mean BOM present
head -c 3 subs.srt | xxd
file subs.srt            # contains "with BOM" means BOM present

# Strip the BOM (back up first, rewrite in place)
cp subs.srt subs.srt.bak
python3 -c "
import pathlib
p = pathlib.Path('subs.srt')
write_bytes(p.read_bytes().lstrip(b'\xef\xbb\xbf'))"

# If the source is GBK, transcode: iconv -f GBK -t UTF-8 subs_gbk.srt > subs.srt
```

Exception: a few old Windows-side tools actually require a BOM to recognize Chinese—try without BOM
first, and add a BOM only if the first cue doesn't display or the first line is garbled.

## 6. ffmpeg burning and soft-muxing

```bash
# Hard burn (visible on any platform)
ffmpeg -y -i in.mp4 -vf "subtitles=subs.srt" -c:v libx264 -crf 20 -c:a copy burned.mp4

# Hard burn and override style (works on SRT too; force_style uses ASS fields)
ffmpeg -y -i in.mp4 -vf \
  "subtitles=subs.srt:force_style='FontName=Noto Sans CJK SC,FontSize=64,PrimaryColour=&H00FFFFFF,Outline=3,MarginV=200'" \
  -c:v libx264 -crf 20 -c:a copy burned_zh.mp4

# Soft-mux into MP4 (toggleable; mov_text does not support ASS styling)
ffmpeg -y -i in.mp4 -i subs.srt -c:v copy -c:a copy -c:s mov_text \
  -metadata:s:s:0 language=chi soft.mp4

# Soft-mux into MKV (use -c:s ass to keep ASS styling, -c:s srt for plain text; for WebM use -c:s webvtt)
ffmpeg -y -i in.mp4 -i subs.ass -c:v copy -c:a copy -c:s ass soft.mkv
```

Pre-check (missing either means burning fails or produces boxed glyphs):

```bash
ffmpeg -filters 2>/dev/null | grep " subtitles "   # output present = compiled with libass
fc-list :lang=zh | head -5                          # output present = Chinese fonts available
```

Failure branches: `No such filter: 'subtitles'` → missing libass; switch to soft-muxing or a different
build; `Unable to open subs.srt` → wrong path (relative paths are relative to the **current
directory**); the container doesn't support that subtitle codec → MP4 uses `mov_text`, MKV uses
`srt`/`ass`.

Format conversion (always check the header and actual playback after converting; tools don't guarantee
zero timeline drift): `ffmpeg -y -i subs.srt subs.vtt` / `ffmpeg -y -i subs.srt subs.ass`.

## 7. Chinese line-breaking rules

| Rule | Value (guideline) | Reason |
|---|---|---|
| Characters per cue | ≤15 chars | A vertical line can't fit more; split into two cues if longer |
| Lines per cue | ≤2 lines | Three lines cover the subject |
| Minimum display time | ≥0.8s | Shorter than 0.8s isn't readable, equivalent to no caption |
| Maximum display time | ≤6s | Longer means it should have been split |
| Gap between adjacent cues | 0.1–0.3s | Leave a gap to avoid "flickering together" without hurting readability |

Where to break: prefer breaking at punctuation (commas/periods/exclamation/question marks), then
between subject-predicate or verb-object; **don't** split a word in the middle (e.g. splitting the
number phrase "eight-thousand-nine" across a break is wrong; breaking after a complete clause is right).
