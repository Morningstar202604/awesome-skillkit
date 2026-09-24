# Sources & Methodology (pdf-pipeline)

## Methodology sources

This skill's design thinking is distilled from the **task-division ideas reflected in the public
description of the pdf skill** in Anthropic's official public skills repository (subtask decomposition of merge/split/extract/metadata/rotate,
the routing judgment of "scans go through OCR"). No text passages, script code, or documentation content was copied;
all text and code in this directory are original. Upstream content is proprietary-licensed and redistribution is prohibited.

- Anthropic skills repository (read only as conceptual reference):
  https://github.com/anthropics/skills/tree/main/skills/pdf
  https://github.com/anthropics/skills/tree/main/skills/docx

## Technical basis

- pypdf official docs (PdfReader / PdfWriter / append / add_metadata /
  get_fields / rotate):
  https://pypdf.readthedocs.io/
- AcroForm field dictionaries and the /Rotate page attribute in the PDF spec (ISO 32000):
  form-field detection (/FT type) and rotation-flag read-back directly correspond to the standard structures.
- No-text-layer determination: extract_text() returns an empty string for image pages; based on this, prompt the OCR
  route (ocrmypdf / tesseract are common external tools; this skill does not bundle them).
