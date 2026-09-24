# Methodology sources and design trade-offs

> When to read: when adding a conversion pipeline, tweaking dependency probing, or understanding "why cross-pipeline conversion is rejected". CLI flags are in SKILL.md; this file only covers the design rationale.


## Idea sources (distilled from public methodology; no code copied)

| This script's approach | Idea distilled from |
|--------------|--------------|
| Probe dependencies first, give install command if missing | The Unix `autoconf`/`./configure` tradition of "probe capability then decide"; modern CLI's actionable-error philosophy (the error message directly gives the fix) |
| One command, multiple subcommands | The `git` / `docker` / `ffmpeg` subcommand organization: fewer top-level entries for users to remember, differences tucked into subcommands |
| Reject same input/output path | The explicitization of `mv`/`cp` protection; "source and target are the same file" is a classic data-loss accident |
| Batch mode dry-run by default | Consistent operation contract with the same-domain file-organizer (see that skill's `references/`) |
| Infer pipeline by extension | `pandoc`'s automatic format recognition, `ImageMagick`'s output-format inference—but this script **explicitly prints** the inference, avoiding silent wrong guesses |

## Key trade-offs

**Why reject cross-pipeline conversion?** `.mp4 → .jpg` is actually **frame extraction** (need to pick a time point, pick which frame),
`.md → .jpg` is actually **rendering** (needs a layout engine). The semantics of these two are completely different from "change the container format":
the former has infinitely many reasonable results, the latter depends on a browser/LaTeX environment. Putting them in the same `batch` produces garbage the user doesn't want.
Rejecting beats guessing wrong—the error message directly gives the right approach (`ffmpeg -frames:v 1`).

**Why pass `-f`/`-t` explicitly to pandoc?** pandoc's automatic recognition of `.tex`, `.rst` is inconsistent across versions,
and `-t latex` vs `-t pdf` behave very differently (the latter needs an external LaTeX engine). Explicit parameters make
script behavior stable across versions, and make the printed command directly copy-pasteable by the user.

**Why doesn't a single failure abort batch mode?** In batch scenarios the user cares about "how many of 100 files broke,"
not "the 3rd broke so the whole run was wasted." Failed items are printed one by one and counted at the end; the user can rerun only the failed ones.

**Why does `--kind` manual override exist?** The extension→pipeline mapping table is a hardcoded closed set: encountering an unregistered new format
(e.g. different implementations of `.avif`, `.heic`), the user can force a pipeline with `--kind image` without modifying the script.

## Official documentation

- pandoc user guide (`-f`/`-t`, `--pdf-engine`): <https://pandoc.org/MANUAL.html>
- pandoc supported formats list: <https://pandoc.org/MANUAL.html#option--list-input-formats>
- Pillow `Image.resize` (`LANCZOS` resampling): <https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.resize>
- Pillow `Image.save` and the `quality` parameter: <https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#jpeg>
- Pillow mode conversion (RGBA → RGB): <https://pillow.readthedocs.io/en/stable/handbook/concepts.html#concept-modes>
- FFmpeg official docs: <https://ffmpeg.org/ffmpeg.html>
- FFmpeg codec selection guide: <https://trac.ffmpeg.org/wiki/Encode/H.264>
