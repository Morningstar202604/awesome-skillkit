---
name: file-organizer
description: >-
  Audit and reorganize a messy directory with a dry-run-first planner:
  extension/date/size statistics, fast duplicate detection (size + first-1KB
  hash), and a reviewable move plan before anything touches disk. Use when the
  user asks to organize my files / file cleanup / find duplicate files / sort
  downloads folder / tidy directory / file archiving / batch organize. Do NOT
  use for deleting files, renaming in place, syncing between machines, or
  touching system/VCS directories.
license: Apache-2.0
compatibility: "Python 3.8+ stdlib only (no third-party packages). Reads and moves files inside the directory you pass; apply is dry-run unless --yes is given."
metadata:
  author: "awesome-skillkit"
  version: "1.1"
  category: tools
  pattern: single-task
  tier: standard
  verified-date: "2026-09-21"
---

# File Organizer (File Organization)

Solves the problem of "Downloads/Desktop/project directory is a mess": first
audit, then plan, then act.

**Core judgment: organizing is irreversible, so the order can never be
reversed.** `scan` and `plan` are read-only, `apply` defaults to dry-run—only
after the user sees the complete "will move X to Y" list and confirms does
`--yes` write to disk. This script **never deletes files**: duplicates only get
a keep suggestion; deletion is a human decision.

## Domain Tacit Knowledge (Four Things to Know Before Acting)

**1. mtime is not "creation time"—the #1 source of misunderstanding for
`--by date`.** Whether copy/unzip/sync preserves mtime **depends on the tool**:
Windows Explorer and macOS Finder copies usually preserve original timestamps;
mainstream unzip tools restore archive timestamps; common failures are Linux
`cp` without `-p`, some cloud-drive client re-syncs, cross-machine transit—
these rewrite mtime to "that moment in time". So before choosing `date`
dimension, state the definition: mtime = last time the file appeared/changed on
this disk, not business time. Important photo/document directories should switch
to `type`, or confirm with user "is bucketing by appearance time on this disk OK".

**2. Downloads folder geography: three junk types dominate volume, clean those
first.** A real Downloads directory is usually bloated by three things—duplicate
downloads (same invoice/installer clicked three times), partial downloads
(`.crdownload`/`.part`/`.tmp` breakpoint leftovers), expired installer caches.
After `scan` report, look at these three first; the volume hog is usually them,
not real documents. Handle those first and organizing pressure halves. Partial
download leftovers can be listed separately as a group in plan stage.

**3. The duplicate fingerprint blind spot is bidirectional—it both false-positives
and false-negatives.** "Size + first 1KB hash" will false-positive files with
identical headers (same-template PDFs, videos from the same muxer) and
**false-negative** files that are identical in content but differ in header
(same video with different mux params, before/after stripping EXIF from images).
So this script only suggests, doesn't delete; `cmp` is the human gate (step 2);
when reporting duplicate groups, explain both directions of blind spot—"cleared
X GB" must leave room for `cmp` review.

**4. Extension buckets can tear apart one photo album / one project.** `--by type`
separates `.heic` and `.jpg` into two buckets, which for "photos are photos"
users is tearing the album in half—same for `.m4a`/`.mp3` mixed music libraries,
`.docx`/`.pdf` mixed bid packages. Look at `scan` distribution before choosing
dimension: extensions highly mixed but semantically one category (album/project),
suggest keeping `type` only as catch-all for odd files, or switch to a user-custom
plan; don't let the default dimension make semantic decisions for the user.

## Input Checklist

| Input | Required | Notes |
|------|:---:|------|
| Target directory | yes | Positional, e.g. `~/Downloads`. Script operates only inside this directory; symlinks and `../` are blocked |
| Organize dimension `--by` | no | `type` (default, by extension) / `date` (by mtime `YYYY-MM`) / `size` (plan only) |
| Execution flag | no | `--yes` actually moves; `--dry-run` is default behavior, can be written explicitly for self-documentation |

When inputs are missing, ask all at once: "Please provide: 1) directory path to
organize; 2) by type or by date; 3) whether you already have a backup. I'll use
defaults: `--by type`, dry-run preview."

## Pre-flight Checks

```bash
python3 --version                                   # expected >= 3.8
test -f scripts/organize.py && echo SCRIPT_OK       # expected prints SCRIPT_OK
test -d "$TARGET_DIR" && echo DIR_OK                # expected prints DIR_OK
python3 -c "import os;print(len(os.listdir('$TARGET_DIR')))"   # check scale first; discuss huge directories first
```

Any of three failing → STOP and report what's missing; empty directory → `scan`
will directly say "no files to organize", no need to continue.

## Workflow

### Step 1: Audit Current State

```bash
python3 scripts/organize.py scan assets/sample-files   # bundled sample directory (scan is read-only)
```

Expected: prints extension distribution table (count + volume), size-tier
counts, duplicate file groups. Reading key: first use tacit knowledge 2 to find
the three volume-bloating junk types (duplicate downloads/partial downloads/
installer caches); duplicate group count × redundant volume decides whether to
run `dedupe` first before organizing; extensions highly mixed but semantically
one category (album/bid/project) → watch out for tacit knowledge 4's tearing
trap, confirm dimension with user before choosing `--by`; file count > 5000 →
confirm batching with user first.

If it fails: `ERROR: not a directory` → wrong path or points to a file; verify
with `ls -ld`.

### Step 2: Review Duplicates

```bash
python3 scripts/organize.py dedupe assets/sample-files
```

Expected: each duplicate group lists "keep" and "cleanable" columns, keep item
sorted by **oldest mtime → shortest path** (if mtime was rewritten by a tool,
this sort is reference only—keeping which is ultimately the user's call).

If it fails: no duplicates found → file contents differ, skip this step and
organize directly. Note: duplicate fingerprint is "size + first 1KB hash",
blind spot is bidirectional (tacit knowledge 3)—large files with same header but
different content will **false-positive**, files with same content but different
header (video remux, image EXIF strip) will **false-negative**. Therefore script
only suggests, doesn't delete; before cleaning, `cmp` to confirm; false-negative
duplicates rely on user's volume-proportion intuition for manual spot-check.

### Step 3: Generate Organize Plan

```bash
python3 scripts/organize.py plan assets/sample-files --by type
```

Expected: line-by-line `will move <relative path> to <relative path>`, ending
with next-step command. Hand the list to the user for line-by-line review—this
is the only human gate in the whole flow.

If it fails: plan is empty → files already in target positions; `apply --by size`
errors → apply doesn't support size dimension (volume is an attribute not
semantic; archiving makes files hard to retrieve), `plan --by size` is only
for volume-tier reports; for organizing switch to `type` or `date`.

### Step 4: Dry-Run Review

```bash
python3 scripts/organize.py apply assets/sample-files --by type --dry-run
```

Expected: each line prefixed `[dry-run]`, ending prints "no disk changes made".
Use `find "$TARGET_DIR" -type f | wc -l` before/after; counts must match exactly.

If it fails: `[skip] target exists` → disk state changed during planning; rerun
step 3 to regenerate plan (script auto-adds `_1`, `_2` suffixes to avoid
collisions).

### Step 5: Execute After Confirmation

```bash
# python3 scripts/organize.py apply "$TARGET_DIR" --by type --yes
```

Expected: each line prefixed `[ok]`, ending prints "done: moved N items, skipped
M". **Must have explicit user consent before executing**; suggest `cp -r` or
`rsync` backup first.

If it fails: `[skip] ... move failed: Permission denied` → target directory not
writable; check permissions and retry; skipped items show in ending count;
troubleshoot line by line.

## Target Directory Structure Example

```
$TARGET_DIR/
├── pdf/          # .pdf
├── jpg/          # .jpg
├── txt/          # .txt
├── csv/          # .csv
└── (no-ext)/     # files without extension
```

With `--by date`, directory names are `YYYY-MM` form like `2026-09`, from file mtime.

## Parameter Quick Reference

| Parameter | Values | Notes |
|------|------|------|
| `scan <dir>` | path | read-only audit |
| `plan <dir> --by` | `type`/`date`/`size` | print plan only |
| `apply <dir> --by` | `type`/`date` | execute; default dry-run |
| `apply --yes` | flag | the only switch that changes disk |
| `dedupe <dir>` | path | read-only duplicate report |

## Failure Handling Table

| Symptom | Cause | Action |
|------|------|------|
| `ERROR: not a directory` | path points to file or doesn't exist | verify with `ls -ld`, rerun |
| `escaped directory boundary` | target resolves outside directory | normal protection; check symlinks pointing outside; script refuses cross-boundary writes |
| `[skip] target exists, skipping` | disk changed between plan and execute | rerun `plan` to regenerate (script auto-adds suffixes on collision) |
| Duplicate group obvious false-positive | large files with same header (e.g. same-template PDFs) | `cmp -s a b` to double-confirm; `dedupe` only suggests, doesn't delete |
| Photos/music split into two buckets | extension tears album/project apart (tacit knowledge 4) | move back to same bucket or restore original structure; reconfirm dimension before organizing |
| `--by date` results don't match file age | mtime rewritten by some tool (`cp` without `-p`, cloud re-sync, tacit knowledge 1) | explain the definition honestly: bucketing by "appearance time on this disk"; important directories switch to `--by type` and replan |
| Too many files, output floods screen | directory too large | batch: handle subdirectories first, or redirect output to file and read in sections |
| Can't find files after `apply` | archived by extension | look up via `plan` output mapping, or `find "$TARGET_DIR" -name "<original filename>"` |

## Delivery Criteria

**Success definition**: after `apply --yes`, ending prints "done: moved N
items", and `scan` re-check shows each extension bucket's file count matches
plan.

**Artifacts**: organized directory tree, subdirectory names = lowercase
extension (or `YYYY-MM`); extension-less files go to `(no-ext)/`.

**Location**: all inside original directory; no external copies.

**Integrity verification**:

```bash
find "$TARGET_DIR" -type f | wc -l    # count must be equal before/after moving
find "$TARGET_DIR" -type f -exec du -cb {} + | tail -1   # total volume must be equal
```

## References

- `scripts/organize.py` — run it for four subcommands; `_resolve_within` is the boundary gate.
- `references/sources-and-methodology.md` — design trade-offs for duplicate strategy, conflict naming, and irreversible operations.
