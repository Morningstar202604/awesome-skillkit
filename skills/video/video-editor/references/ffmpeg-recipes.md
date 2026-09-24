# FFmpeg Editing Cheat Sheet (video-editor)

Copy-pasteable commands for this skill's seven scene categories: **concatenation / transitions /
audio mixing / vertical packaging / silence detection / frame extraction / subtitles**. Works with
generic syntax across ffmpeg 4.x–7.x; filter parameters change between versions, so anything uncertain
is marked `VERIFY BEFORE USE` with the verification command—better to omit one parameter than to write
a fake parameter that won't compile.

Conventions: `in.mp4` / `out.mp4` in examples are always **relative paths**; `cd` into the working
directory before running. `-y` is included by default (overwrite output, to avoid "Overwrite? [y/N]"
hanging non-interactive runs); when calling from a shell loop / cron, also add `-nostdin`, otherwise
ffmpeg eats the script's stdin.

## Table of Contents

0. Pre-flight self-check / 1. concat demuxer concatenation / 2. concat filter fallback / 3. xfade transitions / 4. BGM audio mixing
5. Vertical 1080x1920 / 6. Silence detection and trimming / 7. Frame extraction / 8. Subtitle burning and soft-muxing / 9. Error-handling table

## 0. Pre-flight self-check

```bash
ffmpeg -version | head -1                                        # expected: version line
ffprobe -v error -show_entries format=duration -of default=nw=1 in.mp4   # expected: seconds
ffmpeg -filters 2>/dev/null | grep -E " (xfade|amix|subtitles|silencedetect) "
ffmpeg -encoders 2>/dev/null | grep -E " (libx264|aac) "
```

The last two lines must respectively list `xfade`/`amix`/`subtitles`/`silencedetect` and
`libx264`/`aac` for the feature set to be complete. Missing `subtitles` = not compiled with libass
(subtitle burning unavailable); missing `libx264` = no H.264 encoder (switch to `-c:v mpeg4` or
install a build with x264).

## 1. Concatenation: concat demuxer (lossless, fastest)

Use when all clips share **identical encoding parameters** (produced by the same pipeline) and you
just want them end-to-end.

```bash
printf "file 'scene_1.mp4'\nfile 'scene_2.mp4'\nfile 'scene_3.mp4'\n" > clips.txt
ffmpeg -y -nostdin -f concat -safe 0 -i clips.txt -c copy combined.mp4
```

`-f concat` enables the concat demuxer; `-safe 0` allows absolute paths, `..`, spaces, or special
characters in the list (without it you get `Unsafe file name`); `-c copy` copies the bitstream,
finishing in seconds with no quality loss. Expected: duration equals the sum of clips (±1 frame).

Failure branches: `Unsafe file name` → add `-safe 0` or switch to relative paths; `Non-monotonous DTS`,
audio/video out of sync → clips are encoded differently, use Section 2 instead; a clip is missing →
`cat clips.txt` to check quotes and newlines.

## 2. Concatenation: concat filter (fallback when encodings differ)

```bash
ffmpeg -y -nostdin -i scene_1.mp4 -i scene_2.mp4 -filter_complex \
  "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]" \
  -map "[v]" -map "[a]" -c:v libx264 -crf 20 -preset medium -c:a aac -b:a 192k combined.mp4
```

`concat=n=2:v=1:a=1` = 2 inputs, output 1 video 1 audio; inputs must be listed in pairs as
`[v0][a0][v1][a1]`. The cost is a full re-encode. Failure branch: `Stream specifier ':a' ... matches
no streams` → one clip has no audio track; first add a silent track with
`ffmpeg -i v.mp4 -f lavfi -i anullsrc=r=44100:cl=stereo -shortest -c:v copy -c:a aac v_a.mp4`.

## 3. Transition: xfade cross-dissolve

```bash
# clip_a duration D1, transition duration T, then offset = D1 - T (this example D1=5s, T=0.5s)
ffmpeg -y -nostdin -i clip_a.mp4 -i clip_b.mp4 -filter_complex "\
[0:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,settb=AVTB,fps=30[va];\
[1:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,settb=AVTB,fps=30[vb];\
[va][vb]xfade=transition=fade:duration=0.5:offset=4.5[v]" \
  -map "[v]" -c:v libx264 -crf 20 -pix_fmt yuv420p out.mp4
```

`transition` takes `fade`/`wipeleft`/`slideup`/`circleopen` etc. (full list: `ffmpeg -h filter=xfade`);
`duration` is the overlap length; `offset` is the time point on the **first input** where the
transition starts. For three clips, feed the previous result as the next input and accumulate offsets:
`[0][1]xfade=duration=0.5:offset=4.5[v01];[v01][2]xfade=duration=0.5:offset=9.0[v]`.

Failure branches: `First input link main timebase ... do not match` → the two inputs have different
timebases; prepend `settb=AVTB`; width/height/SAR mismatch → prepend
`scale=...:force_original_aspect_ratio=decrease,pad=...,setsar=1` to unify; the last segment is
missing → `offset` was miscalculated; re-derive durations with `ffprobe`.

## 4. Audio mixing: BGM + voiceover, volume and ducking

```bash
ffmpeg -y -nostdin -i video.mp4 -stream_loop -1 -i bgm.mp3 -filter_complex "\
[1:a]volume=0.25[bgm];\
[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -shortest final.mp4
```

`-stream_loop -1` loops a short BGM (must go **before** the `-i` it modifies); `volume=0.25` is a
linear gain multiplier (not dB); `duration=first` uses the first input's length; `-shortest` truncates
as a safety net.

**Volume pitfall**: `amix` default scales each channel by 1/n, which pushes the voice down. To turn
that off, first verify whether this build has the parameter: `ffmpeg -h filter=amix` must show
`-normalize` (VERIFY BEFORE USE); if present, write `amix=inputs=2:duration=first:normalize=0`.

Voiceover ducking (auto-lower BGM while speaking):
`[0:a][bgm]sidechaincompress=threshold=0.05:ratio=6:attack=20:release=250[a]`
—parameter names and defaults vary by version; must confirm with `ffmpeg -h filter=sidechaincompress`
before running (VERIFY BEFORE USE).

Failure branches: silent output → forgot `-map "[a]"`; filter outputs must be explicitly mapped;
`Could not find tag for codec mp3` → MP4 doesn't store MP3; this example already transcodes with
`-c:a aac`; audio/video drift → sample-rate mismatch; prepend `aresample=44100`.

## 5. Vertical: 1080x1920 scaling and padding

```bash
# 5a) Keep black bars
ffmpeg -y -nostdin -i in.mp4 -vf \
  "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1" \
  -c:v libx264 -crf 20 -preset medium -c:a aac vertical.mp4

# 5b) Blurred-background fill (no black bars)
ffmpeg -y -nostdin -i in.mp4 -filter_complex "\
[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:2[bg];\
[0:v]scale=1080:1920:force_original_aspect_ratio=decrease[fg];\
[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1[v]" \
  -map "[v]" -map 0:a -c:v libx264 -crf 20 -preset medium -c:a aac vertical_blur.mp4
```

`decrease` scales proportionally to fit inside the box (no cropping); `increase` fills the box then
`crop` cuts the overflow; the pad offset `(ow-iw)/2:(oh-ih)/2` centers it; `boxblur=20:2` =
luma radius:strength; `setsar=1` normalizes the pixel aspect ratio, otherwise some platforms stretch
according to SAR.

Expected: `ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 vertical.mp4`
outputs `1080,1920`. Failure branch: `Invalid too big or non positive size` → the source width/height
is abnormal; confirm with `ffprobe` first.

## 6. Silence detection and trimming

```bash
ffmpeg -nostdin -i in.mp4 -af silencedetect=noise=-35dB:d=0.4 -f null - 2> silence.log
grep -E "silence_(start|end)" silence.log
```

Expect paired lines: `silence_start: 3.204` / `silence_end: 5.881 | silence_duration: 2.677`.
Results go to **stderr**, so you must redirect; `-f null -` is required, otherwise it actually
generates an output file; `noise` is the detection threshold (lower = stricter), `d` is the minimum
duration to qualify as silence.

Trim leading/trailing silence (keep the middle):

```bash
ffmpeg -y -nostdin -i in.wav -af "\
silenceremove=start_periods=1:start_duration=0.2:start_threshold=-40dB:detection=peak,areverse,\
silenceremove=start_periods=1:start_duration=0.2:start_threshold=-40dB:detection=peak,areverse" trimmed.wav
```

`silenceremove` can only remove from the **start**; using `areverse` lets you run it once to trim the
tail, then `areverse` back. Parameter names vary by version; check with
`ffmpeg -h filter=silenceremove` before running (VERIFY BEFORE USE).

## 7. Frame extraction

```bash
ffmpeg -y -nostdin -ss 00:00:03 -i in.mp4 -frames:v 1 -q:v 2 frame.png   # single frame (fast)
ffmpeg -y -nostdin -i in.mp4 -vf "fps=1,scale=480:-2" thumb_%04d.jpg      # 1 per second
```

`-ss` placed **before** `-i` is fast seek (keyframe-accurate); after `-i` it's accurate but slow;
`-frames:v 1` takes only 1 frame; `-q:v 2` is JPEG/PNG quality (2 ≈ high); `scale=480:-2` uses `-2`
(not `-1`) to keep the height even—H.264 requires even dimensions.

Expected: `frame.png` or `thumb_0001.jpg`, `thumb_0002.jpg`… appear in the current directory.
Failure branch: extracting an all-black frame → the timestamp landed on the opening black frame;
increase `-ss` to 1–3 seconds and retry.

## 8. Subtitles: hard burn and soft muxing

```bash
# 8a) Hard burn (baked into the picture, displays on any platform)
ffmpeg -y -nostdin -i in.mp4 -vf "subtitles=subs.srt" -c:v libx264 -crf 20 -c:a copy burned.mp4

# 8b) Specify Chinese glyphs and outline
ffmpeg -y -nostdin -i in.mp4 -vf \
  "subtitles=subs.srt:force_style='FontName=Noto Sans CJK SC,FontSize=22,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2,Shadow=1,MarginV=60'" \
  -c:v libx264 -crf 20 -c:a copy burned_zh.mp4

# 8c) Soft mux (toggleable; MP4 uses mov_text, MKV uses -c:s srt)
ffmpeg -y -nostdin -i in.mp4 -i subs.srt -c:v copy -c:a copy -c:s mov_text \
  -metadata:s:s:0 language=chi soft.mp4
```

`subtitles=` uses libass; `force_style` uses ASS fields, with colors as `&HAABBGGRR` (opposite of the
common `#RRGGBB`); `MarginV` is pixels from the bottom; `mov_text` is the only widely supported
subtitle codec in MP4.

Pre-check for Chinese burning (either being empty means failure or boxed glyphs):

```bash
ffmpeg -filters 2>/dev/null | grep " subtitles "   # output present = compiled with libass
fc-list :lang=zh | head -5                          # output present = Chinese fonts installed
```

Failure branches: `No such filter: 'subtitles'` → missing libass; `Unable to open subs.srt` → wrong
path (relative paths are relative to the **current directory**); Chinese boxes → the `FontName`
doesn't exist; replace it with a name actually output by `fc-list :lang=zh`; filename contains spaces
or a colon → use the form `subtitles=filename='my subs.srt'`, or rename the file.

## 9. Error-handling table

| Error text (key fragment) | Cause | Action |
|---|---|---|
| `Unsafe file name` | concat list uses absolute paths/special chars without `-safe` | Add `-safe 0` or switch to relative paths |
| `Could not find tag for codec ... in stream #0` | The container doesn't support that codec | MP4 uses `-c:a aac -c:v libx264` |
| `Unknown encoder 'libx264'` | This build has no x264 | `ffmpeg -encoders \| grep 264` to see what's available |
| `Automatic encoder selection failed` | No encoder specified and no default | Explicitly set `-c:v` / `-c:a` |
| Audio track missing after `Stream mapping:` | Used a filter but didn't `-map` | Explicitly `-map 0:v -map "[a]"` |
| xfade `timebase ... do not match` | Two inputs have different timebases | Prepend `settb=AVTB` |
| `Invalid data found when processing input` | File missing/corrupt/extension mismatch | `ls -l` + `ffprobe -v error -show_format in.mp4` |
| `Too many packets buffered for output stream` | Broken timestamps or large rate differences | Add `-max_muxing_queue_size 1024` as a fallback; prioritize checking source timestamps |
| `silencedetect` produces no output | Results are on stderr and you missed `-f null -` | Redirect with `2> silence.log` |
| Subtitle Chinese boxes/garbage | Missing Chinese fonts or subtitles aren't UTF-8 | Install `fonts-noto-cjk`; save subtitles as UTF-8 (prefer without BOM) |
| Command skipped in a loop | ffmpeg eats stdin | Add `-nostdin` |
