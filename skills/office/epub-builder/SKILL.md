---
name: epub-builder
description: >-
  Convert a Markdown manuscript into a valid EPUB 3 e-book with correct
  mimetype/container.xml/content.opf/toc.ncx/nav.xhtml structure, then read the
  EPUB back to verify metadata and chapter order. Uses only the Python standard
  library because EPUB is just a zip plus XML. Use when the user asks to build
  an epub / make an e-book from markdown / convert to epub / inspect an epub
  file / split ebook chapters / generate ebook / epub from markdown. Do NOT use
  for Word documents (use docx-writer) or PDF generation (use pdf-pipeline).
license: Apache-2.0
compatibility: Requires python3 3.8+; script uses stdlib only (zipfile + ElementTree), no third-party dependencies.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: office
  pattern: single-task
  tier: standard
  verified-date: "2026-09-17"
---

# EPUB Builder (E-book Generation)

Package a Markdown manuscript into an EPUB 3 that **readers will accept**.
EPUB is essentially "a zip + a set of XML", so this skill uses only the Python
standard library: `zipfile` for packaging, hand-written OPF/NCX/NAV, and a
built-in lightweight parser for Markdown conversion.

Core judgment: **spec details decide success or failure**. EPUB has one hard
requirement—the `mimetype` must be the **first** entry in the zip and
**uncompressed** (`ZIP_STORED`), with content exactly `application/epub+zip`
and no trailing newline. Get this wrong and most readers will reject the file
outright, even though it "generated successfully". This skill therefore builds
validation into `build` and makes it re-checkable in `inspect`.

This skill does **not** do Word (use `docx-writer`), **not** PDF (use
`pdf-pipeline`), and **not** typographic beautification (EPUB styling is
controlled by the reader; over-specifying styles causes breakage across
devices).

## Input Checklist

| Input | Required | Default | Notes |
|---|---|---|---|
| Markdown source file | yes | — | First H1 becomes book title and first chapter heading |
| Book title | no | First H1 or filename | Written to `dc:title` |
| Author | no | Anonymous | Written to `dc:creator` |
| Language | no | `zh` | Written to `dc:language`, affects hyphenation and TTS |
| Output path | no | `book.epub` | Single-file artifact |

When inputs are missing, ask all at once:

> Please provide: 1) where is the Markdown file? 2) book title and author (if
> not given I'll use the first H1 and "Anonymous")? 3) output filename (default
> book.epub)? 4) do you have a cover image (this skill doesn't embed images;
> say so if you need one)?

## Pre-flight Checks

Run each in order; any failure → follow the action, then STOP:

```bash
# 1. Python version (needs 3.8+)
python3 --version
# Expected: Python 3.8+. Failure → STOP.

# 2. Script available
# Self-check: python3 scripts/epub_build.py --help should print build/inspect usage (lines starting with # are not executed as scenario commands)
# Expected: script ok. Failure → verify scripts/ path.

# 3. Source file exists and is non-empty
test -s <input.md> && head -3 <input.md>
# Expected: content visible. Failure → script will report "empty file"; ask user for the manuscript first.

# 4. Chapter structure usable (how many H1s?)
grep -c '^# ' <input.md>
# Expected: ≥1. Zero → script treats whole thing as a single "body" chapter; no error but TOC has one entry.
```

## Workflow

### Step 1: Confirm Chapter Structure

**Level-1 headings (H1) are chapter boundaries**—this is the splitting
convention:

| Markdown | Becomes |
|---|---|
| `# Title` | New chapter; becomes chapter filename and TOC entry |
| `## / ###` | Sub-sections within chapter (kept as h2/h3) |
| Content before the first H1 | "Front matter" chapter (if non-empty) |
| No H1 at all | Whole document as single "body" chapter |
| H1 inside a chapter | Dropped (chapter name is already H1, avoid duplication) |

- **Expected**: can list chapter names suitable for filenames.
- **If it fails**: only one H1 but content is long → suggest user split with H2
  or into multiple H1s; **don't** restructure the user's content unilaterally.

### Step 2: Generate EPUB

```bash
python3 scripts/epub_build.py build references/sources-and-methodology.md --out book.epub --title "Book Title" --author "Author Name"   # Real input example: bundled sources-and-methodology.md; replace with your input.md
```

Output structure (compliant with EPUB 3 spec):

```
mimetype                    ← first entry, STORED uncompressed
META-INF/container.xml      ← points to OPF
OEBPS/content.opf           ← manifest + spine (chapter order follows spine)
OEBPS/toc.ncx               ← EPUB2-compatible TOC (old readers)
OEBPS/nav.xhtml             ← EPUB3 native TOC
OEBPS/style.css             ← minimal styles
OEBPS/chap01-*.xhtml …      ← one file per chapter
```

- **Expected**: prints title, author, chapter count, per-chapter list, and ends
  with `mimetype : first entry=True storage=STORED ✓`. This line is the spec
  self-check and must be ✓.
- **If it fails**: if `✗ violates EPUB spec` appears, packaging order or
  compression was broken—don't deliver that file; check whether `write_epub()`
  writes mimetype first.

### Step 3: Read Back to Verify

```bash
python3 scripts/epub_build.py inspect examples/sample.epub   # bundled sample (real artifact); verify your book.epub the same way
```

Check metadata, chapter list **in spine order**, and whether `toc.ncx` /
`nav.xhtml` are both present. Chapter order is read from spine rather than
manifest because manifest order has no spec guarantee; spine is the reader's
actual reading order.

- **Expected**: all four metadata fields present; chapter count matches step 2;
  both TOCs present.
- **If it fails**: chapter count is 0 → OPF spine is empty; check itemref
  generation in `content_opf()`.

### Step 4: Independent Cross-Verification (Recommended)

Don't trust your own script's conclusion; verify the spec directly with
`zipfile`:

```bash
python3 -c "
import zipfile
z = zipfile.ZipFile('book.epub'); i = z.infolist()[0]
print('1 first entry is mimetype :', i.filename == 'mimetype')
print('2 uncompressed (ZIP_STORED) :', i.compress_type == zipfile.ZIP_STORED)
print('3 exact content match        :', z.read('mimetype') == b'application/epub+zip')
print('4 entry count                :', len(z.namelist()))
"
```

- **Expected**: first three all `True` (byte string in 3 has no trailing newline).
- **If it fails**: any is `False` → EPUB is non-compliant; handle per step 2's
  failure branch.

### Step 5: Deliver

State: file **absolute path**, title/author/language, chapter count, mimetype
compliance conclusion, and a reminder—**this skill doesn't embed images or
add covers**; if you need a cover, do it separately (use an image-capable
solution, or append after EPUB generation with a dedicated tool).

## Delivery Criteria

- Artifact: one `.epub` file openable in mainstream readers (Calibre / Apple
  Books / Duokan).
- Location: user-specified `--out` path; defaults to `book.epub` in current
  directory.
- Integrity verification (all required):
  - `build` ending mimetype self-check shows `✓`;
  - `inspect` chapter count equals H1 count in source (1 when no H1);
  - cross-verification "first entry is mimetype", "uncompressed", "exact
    content match" all `True`.
- Delivery notes must explain chapter splitting basis (H1) so the user follows
  the same rule for future edits.

## Failure Handling Table

| Symptom / Error | Cause | Action |
|---|---|---|
| `Markdown file not found: ...` | Wrong path | Verify path; note it's `.md` not `.docx` |
| `... is an empty file` | Source is zero bytes | Confirm manuscript was saved with content |
| `No chapters parsed` | No valid chapters after split | Rare; check if source is blank |
| `... is not a valid zip/EPUB` | File passed to inspect isn't an EPUB | Confirm extension matches content (renamed txt won't pass) |
| Reader says "can't open" | mimetype order or compression wrong | Run three cross-verification checks; script writes per spec; failure means packaging logic was altered |
| TOC empty but chapters have content | Spine missing itemrefs | Check spine generation in `content_opf()` |
| Chapter order unexpected | Relied on manifest order | Manifest order has no spec guarantee; chapter order follows spine |
| Duplicate chapter names overwrite files | Two H1s with same name | `slugify` adds number prefix (`chap01-`, `chap02-`), no overwrite; but warn user to rename |
| CJK titles garbled in old readers | Missing encoding declaration | Every XHTML carries `<meta charset="utf-8"/>`; if still garbled it's a reader issue |
| Need cover/illustration | Script has no image support | Say clearly; suggest generating HTML then processing with a dedicated tool; don't fake support |
| Tables/code break in reader | Reader overrode styles | EPUB styling is reader-driven, expected; only text structure is guaranteed correct |

## References

- `references/sources-and-methodology.md` — the three hard requirements of EPUB
  3 spec, Markdown parser trade-offs, and why stdlib only.
- `scripts/epub_build.py --help` — build / inspect subcommands.
- Related skills: `docx-writer` (Word documents), `pdf-pipeline` (PDF processing),
  `article-drafter` (write the manuscript first, then book).
