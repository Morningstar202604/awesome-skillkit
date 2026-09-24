---
name: docx-writer
description: >-
  Generate and audit real Word (.docx) files from a markdown-ish draft or
  structured JSON, with correct heading levels, lists, tables, bold spans, and
  CJK font setup. Use when the user asks to write a document / create a Word
  file / generate a docx report / create document / make a Word report / export
  to docx / format a document, or wants to inspect or restyle an existing
  .docx. Do NOT use for PDF manipulation (use pdf-pipeline), spreadsheets, or
  slide decks.
license: Apache-2.0
compatibility: Requires python3 + python-docx (pip-installable); degrades to markdown-only output without it
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: office-productivity
  pattern: single-task
  tier: standard
  verified-date: "2026-09-16"
---

# DOCX Writer (Word Document Generation and Review)

Turn a structured draft into a real .docx: heading hierarchy, lists, tables,
and bold spans all handled in one pass, with CJK body fonts (SimSun/SimHei)
applied consistently. Core judgment: **the content source must be structured**—
establish an outline before rendering, no impromptu layout.

## Input Checklist

| Input | Required | Notes |
|---|---|---|
| Document topic and purpose | yes | What to write, for whom (report/notes/notice/manual) |
| Content draft or bullets | yes | User-provided material; if absent, confirm outline section by section |
| Target filename | no | Default `output.docx`, saved in current working directory |
| Cover title needed | no | Default adds a Title paragraph |
| CJK font preference | no | Default body SimSun, headings SimHei |

When inputs are missing, ask all at once (don't drip-feed follow-ups):

> Please provide: 1) document topic and purpose; 2) content material or let me
> draft from your outline; 3) target filename (default output.docx). Any font
> preference (default SimSun body / SimHei headings)?

## Pre-flight Checks

```bash
python3 -c "import docx; print('python-docx ok')"
test -f scripts/docx_ops.py && echo "script ok"
```

- Both pass → proceed through full workflow (from step 2).
- First reports `ModuleNotFoundError` → tell user `pip install python-docx`
  enables .docx export; don't install without consent—degrade to markdown draft
  and note it in delivery.
- Second fails (script missing) → use equivalent inline python-docx code in the
  current working directory (see step 3 equivalent).

## Workflow

### Step 1: Establish Outline and Content Source

Organize content into a markdown-ish draft (conventions in table below), save
as `content.md`. This is the single source of truth; rendering is mechanical.

| Draft Syntax | Maps To |
|---|---|
| `# / ## / ###` | Heading 1 / 2 / 3 |
| `- ` or `* ` prefix | Bullet list |
| `1. ` prefix | Numbered list |
| `\|\|`-delimited row blocks | Table (first row is header) |
| `**text**` | Bold run |
| Other plain lines | Body paragraph |

Expected: `content.md` covers all sections with no empty sections.
If it fails (insufficient material): return to input checklist and ask for
missing sections in one batch.

### Step 2: Generate .docx

```bash
python3 scripts/docx_ops.py create --input content.md --output output.docx --title "Document Title"
```

Structured sources (e.g. program pipelines) can use JSON: each block
`{"type": "h1|h2|h3|para|bullet|number|table", "text": "...", "rows": [[...]]}`,
also via `create --input content.json`.

Expected output: `created: output.docx`.
If it fails: check whether draft syntax mixed in full-width `＃`, or table rows
don't start with `|`; fix and rerun.

### Step 3: Apply CJK Styles

```bash
python3 scripts/docx_ops.py styles output.docx --body-font SimSun --heading-font SimHei
```

Expected output: `saved: output.docx` plus per-style list, each line like
`Heading 1 -> eastAsia=SimHei`.
If it fails: font names must be CJK font names Word recognizes
(SimSun/SimHei/KaiTi/FangSong), not English names; empty style list means the
document has no modifiable paragraph styles.

### Step 4: Read Back to Verify

After generation, must read back and check—don't just trust exit code:

```bash
python3 scripts/docx_ops.py inspect output.docx --preview 12
```

Expected: paragraph/table counts match draft; style statistics show headings
and lists in place; preview text has no garbled characters or dropped paragraphs.
If it fails: see failure table below; fix `content.md` and return to step 2.

### Step 5: Deliver

Tell the user the file's absolute path, section structure (restate the inspect
style stats in a paragraph), and note: content source is `content.md`; future
changes should edit the draft first then re-render.

Expected: user gets a directly openable .docx plus reusable `content.md`.
If it fails: layout doesn't match on open → don't edit .docx; return to step 1
to fix `content.md` then rerun steps 2-4. `inspect` disagrees with what user
sees → trust user's view, troubleshoot row by row per failure table.

## Delivery Criteria

- Artifact: a .docx file openable in Word/WPS.
- Location: current working directory (or user-specified path).
- Integrity verification (at least inspect, pick one):
  - `inspect` style stats match draft outline;
  - `unzip -l output.docx` contains `word/document.xml` and `word/styles.xml`;
  - User can open it and heading navigation shows hierarchy.
- No leftover temp files from script; draft file is mentioned in delivery notes, not deleted.

## Failure Handling Table

| Symptom | Cause | Action |
|---|---|---|
| CJK shows as boxes/garbled on open | Styles lack eastAsia font, Word used default Latin font | Run step 3 `styles`; verify `w:eastAsia` value in `word/styles.xml` |
| Headings don't appear in navigation pane | Headings used bold normal paragraphs instead of Heading styles | Draft must use `#` syntax; no manual bold-as-heading |
| Tables lost or squeezed into one column | Table rows don't start with `\|`, or separator row malformed | Every table row starts with `\|`; separator row uses `\|---\|` |
| Large document slow or hangs | Tens of thousands of paragraphs, per-paragraph API overhead | Split by section into files then merge manually; or trim draft |
| Images missing | Script has no image insertion | Use python-docx `add_picture` as a separate step, or tell user images need post-insertion |
| Open prompts file corrupt | Generation interrupted, ZIP incomplete | Delete and regenerate from step 2; don't hand-patch |

## References

- Methodology and source attribution: `references/sources-and-methodology.md`
- Script help: `python3 scripts/docx_ops.py --help`
