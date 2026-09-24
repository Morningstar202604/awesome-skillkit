---
name: pdf-pipeline
description: >-
  Page-level PDF processing: merge multiple PDFs, split by page ranges, extract
  text with page tags, read/write metadata, rotate pages, and probe AcroForm
  fields or detect scanned (no text layer) files. Use when the user asks to
  merge PDFs / split a PDF / extract PDF text / rotate pages / merge pdfs /
  pdf metadata / page extraction / PDF manipulation. Do NOT use for generating
  Word documents (use docx-writer), editing slide decks, or image editing.
license: Apache-2.0
compatibility: Requires python3 + pypdf (pip-installable); without it only operational guidance and command lists can be given.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: office-productivity
  pattern: single-task
  tier: standard
  verified-date: "2026-09-16"
---

# PDF Pipeline (Page-Level PDF Processing)

Five page-level operations on existing PDFs: merge, split, extract text,
modify metadata, rotate. Core judgment: **first determine PDF type**—text type
processes directly; scanned type (no text layer) goes through OCR first; form
type probes fields to confirm structure before acting.

## Input Checklist

| Input | Required | Notes |
|---|---|---|
| PDF file path | yes | One or more; relative paths based on current working directory |
| Operation to perform | yes | merge / split / extract / meta / rotate |
| Output filename | no | merge/rotate require `--output`; meta defaults to in-place write |
| Page range | no | 1-based like `1-3,5`, defaults to all pages |

When inputs are missing, ask all at once:

> Please provide: 1) PDF file path; 2) what to do (merge/split/extract
> text/edit metadata/rotate); 3) output filename; 4) if splitting or
> extracting: page range (default all pages).

## Pre-flight Checks

```bash
python3 -c "import pypdf; print('pypdf ok')"
test -f scripts/pdf_ops.py && echo "script ok"
```

- Both pass → proceed per workflow.
- First reports `ModuleNotFoundError` → prompt user `pip install pypdf`;
  don't install without consent—only output operational plan, no file.
- Second fails → use inline equivalent code from pypdf docs linked in
  `references/sources-and-methodology.md`.

## Workflow

### Step 1: Determine PDF Type (Which Branch to Take)

```bash
python3 scripts/pdf_ops.py meta assets/sample.pdf   # bundled sample PDF; replace with your input.pdf
```

Expected output: three sections—page count, metadata, `form fields: ...`.
Interpret:

- `form fields` lists fields → form PDF: first confirm with user whether to
  "only read field structure" or "fill values"; filling values is out of scope,
  give the field list then tell user to use a dedicated form tool, don't guess
  values and fill.
- When extracting text, first run step 4 `extract` to probe the text layer.

Expected: a clear conclusion (text / scanned / form).
If it fails (file won't open): likely encrypted or corrupt, see failure table.

### Step 2: Text Type — Merge / Split / Rotate

```bash
python3 scripts/pdf_ops.py merge a.pdf b.pdf --output merged.pdf
python3 scripts/pdf_ops.py split merged.pdf --ranges "1-2,3" --outdir split_out
python3 scripts/pdf_ops.py rotate assets/sample.pdf --degrees 90 --pages 1-2 --output rotated.pdf   # bundled sample; use merged.pdf from previous step for your real scenario
```

Expected: merge prints per-file page count and total; split lists output paths
per file; rotate prints rotated page numbers.
If it fails: page range out of bounds reports `out of bounds`; first verify
range against meta's page count.

### Step 3: Scanned Type — OCR Route Prompt

`extract` on a file with no text layer outputs `[warn] no text layer ...` to
stderr. After confirming it's a scan, the script stops here and switches to OCR
route (prompt user):

- `ocrmypdf in.pdf out.pdf` (generates searchable text layer, then return to
  step 2/4)
- For pure text extraction use `tesseract in.pdf out -l chi_sim+eng`
- OCR quality depends on scan resolution; below 300dpi it's poor, explain to
  user.

Expected: only after user confirms do you run external OCR commands; this skill
doesn't install OCR tools for you.
If it fails: user's machine lacks `ocrmypdf`/`tesseract` → give install commands
(`pip install ocrmypdf`, `brew install tesseract tesseract-lang`) and note this
skill doesn't install them; OCR result still garbled → scan resolution
insufficient or missing language pack; return to step 2 with "screenshot then
OCR".

### Step 4: Extract Text (With Page Tags)

```bash
python3 scripts/pdf_ops.py extract merged.pdf --pages 1-2 --output out.txt
```

Expected: each page starts with `=== page N/M ===`; stdout direct or written to
`out.txt`.
If it fails: extracted garbled text is usually embedded fonts missing ToUnicode
mapping (see failure table).

### Step 5: Read/Write Metadata

```bash
python3 scripts/pdf_ops.py meta assets/sample.pdf                          # read-only (bundled sample)
python3 scripts/pdf_ops.py meta merged.pdf --set Title="Q3 Report" \
    --set Author="Team Name" --output final.pdf                        # write
```

Expected: after writing, prints per-key list; can rerun read-only to verify.
If it fails: key names limited to Title/Author/Subject/Keywords/Creator/Producer.

### Step 6: Deliver

Report each artifact path + page count, and one sentence on provenance (which
file, which pages). Write operations default to not overwriting original
(rotate/split/merge all require explicit `--output`); in-place write (meta
default) requires warning user about backup or confirmation first.

Expected: every artifact path has had page count verified via `meta` read-back;
user can spot-check against source page numbers.
If it fails: artifact path can't be written (e.g. user only wants stdout result)
→ deliver stdout content directly as artifact, note "not saved to disk"; user
disputes page count → return to corresponding step and rerun with `meta` read-back.

## Delivery Criteria

- Artifacts: new PDF or text files, all in user-visible paths.
- Verification: after page operations, read back page count with `meta`; text
  extraction spot-checks first/last page content against page tags; after rotate,
  read `/Rotate` flag to confirm.
- When merging multiple files, report source page count per file for reconciliation.

## Failure Handling Table

| Symptom | Cause | Action |
|---|---|---|
| Garbled or blank extraction but not a scan | Embedded fonts missing ToUnicode mapping | Suggest pdfminer.six re-extraction, or screenshot pages and OCR |
| Open reports "not decrypted / password protected" | PDF has user password or permission restrictions | Ask user for password; forcing without password is non-compliant, refuse |
| Wrong page order after merge | Input file order differs from expected | Check filename order on command line; merge concatenates in argument order |
| Split reports page out of bounds | Range exceeds actual pages | First `meta` to see page count, use `1-N` format |
| Large file merge slow | Page objects copied one by one | Normal; report progress; over 10 minutes suggest batch merging |
| Rotated but viewer shows no direction change | Some viewers cache old render | Reopen file; read back `/Rotate` flag to confirm write |

## References

- Methodology and source attribution: `references/sources-and-methodology.md`
- Script help: `python3 scripts/pdf_ops.py --help`
