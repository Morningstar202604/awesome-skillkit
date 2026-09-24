# Loudness Standards Reference

Per-platform integrated loudness targets in LUFS (Loudness Units relative to Full Scale), true-peak ceilings, and short-term loudness limits. Use this table to set the master loudness normalization target.

## Why LUFS, not peak dB

Platforms normalize audio based on integrated loudness (the average over the whole track), not peak volume. Cranking peaks to 0 dBFS sounds loud but distorts, and platforms will re-normalize anyway. Always target the integrated LUFS number below, and respect the true-peak ceiling.

## Chinese Platforms

| Platform | Integrated LUFS | True Peak Ceiling | Short-term Max | Notes |
|---|---|---|---|---|
| Xiaoyuzhou (小宇宙) | −16 LUFS | −1.5 dBTP | −10 LUFS | Podcast standard; follows Apple Podcasts spec |
| Ximalaya (喜马拉雅) | −16 LUFS | −1.5 dBTP | −10 LUFS | Same as Xiaoyuzhou |
| Apple Podcasts | −16 LUFS | −1.5 dBTP | — | Global podcast reference |
| WeChat MP audio | −14 LUFS | −1.0 dBTP | −8 LUFS | Slightly louder; WeChat player does not normalize |
| Bilibili (B站) | −16 LUFS | −1.5 dBTP | −10 LUFS | Audio-only; video follows YouTube spec |
| Douyin (抖音) | −14 LUFS | −1.0 dBTP | −8 LUFS | Short video; platform expects punchier audio |
| Kuaishou (快手) | −14 LUFS | −1.0 dBTP | −8 LUFS | Same as Douyin |
| WeChat Channels (视频号) | −14 LUFS | −1.0 dBTP | −8 LUFS | Short video |

## International Platforms

| Platform | Integrated LUFS | True Peak Ceiling | Notes |
|---|---|---|---|
| YouTube | −14 LUFS | −1.0 dBTP | Video platform standard |
| Spotify | −14 LUFS | −1.0 dBTP | Music streaming |
| SoundCloud | −14 LUFS | −1.0 dBTP | |
| Twitch | −14 LUFS | −1.0 dBTP | Live streaming |

## ffmpeg loudnorm Two-Pass Procedure

For accurate loudness normalization, run ffmpeg's loudnorm filter in two passes:

**First pass (measure):**

```bash
ffmpeg -i input.wav -af loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json -f null -
```

This outputs JSON with `input_i`, `input_tp`, `input_lra`, `input_thresh`, and `target_offset` values.

**Second pass (apply):**

```bash
ffmpeg -i input.wav -af loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=<input_i>:measured_TP=<input_tp>:measured_LRA=<input_lra>:measured_thresh=<input_thresh>:offset=<target_offset>:linear=true -c:a libmp3lame -b:a 192k output.mp3
```

Replace the `<...>` placeholders with the values from the first pass. The `linear=true` flag ensures accurate (not just approximate) normalization.

## LUFS Cheat Sheet for Quick Decisions

- **Podcast (Xiaoyuzhou / Ximalaya / Apple):** target −16 LUFS, ceiling −1.5 dBTP
- **Short video (Douyin / Kuaishou / Channels):** target −14 LUFS, ceiling −1.0 dBTP
- **WeChat MP article audio:** target −14 LUFS (no platform normalization)
- **When in doubt:** use −16 LUFS; it is the safest middle ground

## Dynamic Range (LRA)

LRA (Loudness Range) is the spread between quiet and loud parts. For speech, LRA of 8–11 LU is natural — not too compressed (sounds flat) and not too wide (loud parts clip, quiet parts are inaudible). Compression settings in the main skill target this range.
