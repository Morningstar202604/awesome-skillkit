# Sources & Methodology (docx-writer)

## Methodology sources

This skill's design thinking is distilled from the **public descriptions and structural ideas** of the docx and pdf skills
in Anthropic's official public skills repository (choose the path by task, read back and verify after generation, write
error-prone points into a checklist). No text passages, script code, or documentation content was copied;
all text and code in this directory are original. Upstream content is proprietary-licensed and redistribution is prohibited.

- Anthropic skills repository (read only as conceptual reference):
  https://github.com/anthropics/skills/tree/main/skills/docx
  https://github.com/anthropics/skills/tree/main/skills/pdf

## Technical basis

- python-docx official docs (Document/Paragraph/Table API):
  https://python-docx.readthedocs.io/
- The `w:rFonts/@w:eastAsia` attribute in the OOXML / ECMA-376 standard: Chinese glyphs are rendered by the eastAsia
  font; setting only the latin font causes Chinese to fall back to the default font—this is the standards-layer cause of the
  "Chinese garbled/tofu" problem, and the `scripts/docx_ops.py` styles subcommand implements accordingly.
