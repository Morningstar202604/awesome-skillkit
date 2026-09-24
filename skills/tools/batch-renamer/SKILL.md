---
name: batch-renamer
description: >-
  Batch-rename files with a preview-first contract: template patterns, regex
  substitution, prefix/suffix, case folding, and EXIF-shooting-date prefixes,
  plus a JSON change log for one-command rollback. Use when the user asks to
  batch rename / rename files / rename photos by date / regex replace filenames /
  strip prefix from filenames / file renaming utility / batch processing. Do NOT
  use for moving or sorting files into folders, editing file contents, or
  renaming directories.
license: Apache-2.0
compatibility: "Python 3.8+; stdlib for all modes. EXIF date mode additionally uses Pillow (optional, falls back to file mtime if absent). Preview is the default; disk writes require the --yes flag."
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: tools
  pattern: single-task
  tier: standard
  verified-date: "2026-09-17"
---

# Batch Renamer (Batch File Renaming)

Solves the problem of "a pile of files needs consistent renaming, doing it
manually is maddening."

**Core judgment: renaming is destructive, so preview first, act second, and
leave a trail.** `preview` is the default action; `apply` refuses without
`--yes` (exit code 2); each real execution appends a JSON record to
`rename-log.txt`, which `undo` uses for one-command rollback. Conflicts are
always **skipped and reported**, never silently overwritten.

## Input Checklist

| Input | Required | Notes |
|------|:---:|------|
| Target directory | yes | Positional argument. Only regular files inside the directory are processed; symlinks and `.git`/`node_modules` are skipped |
| Renaming rule | yes | At least one: `--pattern` / `--regex` / `--prefix` / `--suffix` / `--exif-date` / `--lower` / `--upper` |
| Execution flag | no | `apply` requires `--yes`; `preview` and `undo` preview modes don't need it |
| `--start` | no | `{n}` starting index, default 1 |

When inputs are missing, ask all at once: "Please provide: 1) directory path;
2) target naming rule (an example is enough); 3) whether to use shooting date;
4) whether to preview first. Defaults: sequence starts at 1, conflicts are
skipped."

## Pre-flight Checks

```bash
python3 --version                                    # expected >= 3.8
test -f scripts/rename.py && echo SCRIPT_OK          # expected prints SCRIPT_OK
test -d "$TARGET_DIR" && echo DIR_OK                 # expected prints DIR_OK
python3 -c "import PIL; print('EXIF_OK', PIL.__version__)" 2>/dev/null || echo "Pillow only needed with --exif-date"
find "$TARGET_DIR" -maxdepth 1 -type f | wc -l       # check scale first; >10k discuss batching
```

Missing Pillow doesn't block: `--exif-date` automatically falls back to file
mtime and notes the source in output.

## Workflow

### Step 1: Preview Renaming Result

```bash
python3 scripts/rename.py preview assets/sample-files --pattern "IMG_{n:03d}.{ext}"   # bundled sample directory (preview is read-only)
```

Expected: line-by-line `old -> new`, ending with "will rename N items, skip M".
Reading key: **read every line**—this is the only chance to catch a wrong rule.

If it fails: `ERROR: unknown placeholder {x}` → template only accepts `{n}`,
`{ext}`, `{stem}`, `{date}`; fix and rerun.

### Step 2: Handle Conflicts

Expected: conflicts listed separately in a "conflict skipped" block with reason
(`target already exists` or `collides with batch item X`).

| Conflict Reason | Meaning | Action |
|----------|------|------|
| `target exists: <name>` | A file with that name already exists in the directory | Change rule or handle that file first; script won't overwrite it |
| `collides with batch <name>` | Two planned renames produce the same target name | Add `{n}` index to template for uniqueness |

If it fails: conflict count near total → likely template missing `{n}`, making
all files want the same name.

### Step 3: Execute After Confirmation

```bash
# python3 scripts/rename.py apply "$TARGET_DIR" --pattern "IMG_{n:03d}.{ext}" --yes
```

Expected: line-by-line `[ok] old -> new`, ending with "done: renamed N items"
and log path. **Must get explicit user consent before executing**; script uses
two-phase rename (temp name then final name), so swaps like `a→b` and `b→a`
won't collide mid-operation.

If it fails: `refusing: apply requires explicit --yes` (exit code 2) → add
`--yes`; `[skip] ... rename failed: Permission denied` → check directory write
permissions.

### Step 4: Rollback When Needed

```bash
# python3 scripts/rename.py undo "$TARGET_DIR"          # preview rollback list first
# python3 scripts/rename.py undo "$TARGET_DIR" --yes    # confirm rollback
```

Expected: prints `new -> original` in reverse order; after execution files
return to original names, rolled-back records removed from log. Unsuccessful
rollback records stay in the log for later troubleshooting.

If it fails: `[skip] original name already taken, cannot roll back` → that
original name was later occupied by another file; handle manually then rerun.

## Rule Combination Quick Reference

| Flag | Example | Notes |
|------|------|------|
| `--pattern` | `"IMG_{n:03d}.{ext}"` | Placeholders: `{n}` index, `{ext}` extension, `{stem}` original name, `{date}` date |
| `--pattern` date spec | `"{date:%Y-%m}_{stem}.{ext}"` | `{date:%...}` followed by strftime template |
| `--regex OLD NEW` | `--regex "^(.)" "doc_\1"` | Python `re.sub`, applied to stem, supports backreferences |
| `--prefix` / `--suffix` | `--prefix "2026_"` | Added around stem, before extension |
| `--exif-date` | — | Adds `YYYYMMDD_` prefix; JPEG/TIFF read EXIF, others fall back to mtime |
| `--lower` / `--upper` | — | Stem case (mutually exclusive) |
| `--start N` | `--start 100` | `{n}` starting value |

**Rule application order is fixed**: `--regex` → `--prefix`/`--suffix` →
`--lower`/`--upper`; once `--pattern` is given it replaces the result of the
above text transforms (`{stem}` already contains the transformed stem).

## Failure Handling Table

| Symptom | Cause | Action |
|------|------|------|
| Exit code 2, `refusing` | `apply` missing `--yes` | Add `--yes`; run `preview` to verify first |
| `ERROR: unknown placeholder {x}` | Template has unsupported placeholder | Use only `{n}` `{ext}` `{stem}` `{date}` |
| `ERROR: regex syntax error` | `--regex` OLD isn't valid regex | Verify first with `python3 -c "import re;re.compile(r'...')"` |
| Lots of `collision` conflicts | Template missing `{n}`, target names not unique | Add `{n:03d}` to template |
| EXIF dates all show `[mtime (Pillow not installed)]` | Pillow not installed | `pip3 install pillow`; or accept mtime result |
| EXIF shows `[mtime]` but photo definitely has date | Camera didn't write `DateTimeOriginal`, or non-standard format | Normal fallback; can `exiftool <file>` to confirm metadata |
| `undo` says log is empty | Directory never successfully ran `apply` | Nothing to roll back; check you're in the right directory |
| `.rename_tmp_*` appears in directory | Execution was force-killed mid-run | Manually rename back, or delete these leftover temp files |

## Delivery Criteria

**Success definition**: after `apply --yes`, ending prints "done: renamed N
items", and no `.rename_tmp_*` leftovers in the directory.

**Artifacts**: renamed files + `rename-log.txt` in the directory (one JSON per
line: `ts`/`from`/`to`).

**Location**: files stay in original directory (this tool doesn't move files,
only renames); log written to target directory root.

**Integrity verification**:

```bash
find "$TARGET_DIR" -maxdepth 1 -type f | wc -l    # count must be identical before/after renaming
ls "$TARGET_DIR"/.rename_tmp_* 2>/dev/null && echo "leftovers, need cleanup" || echo "no leftovers"
# python3 scripts/rename.py undo "$TARGET_DIR"      # preview rollback list to confirm one-to-one correspondence
```

## References

- `scripts/rename.py` — run it to execute preview / apply / undo; `_detect_conflicts` is the conflict gate.
- `references/sources-and-methodology.md` — design rationale for two-phase rename, EXIF fallback, and log format.
