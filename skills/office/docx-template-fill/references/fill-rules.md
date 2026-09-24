# Placeholder Fill Rules

## Naming convention
- Placeholder: `{{KEY}}`, where KEY is `[a-zA-Z0-9_]+`; recommend all-caps with underscores (`EMP_NAME`, `AMOUNT`).
- JSON key **exact match** (case-sensitive); missing key → leave `{{KEY}}` as-is and list it in `[NOTICE]`.

## Degradation and boundaries
- `python-docx` not installed: the script only prints "data keys that could be filled", rc=3, no file written.
- Comments: this skill approximates with an "end-of-document [Comment·Author] italic paragraph"; a true Word comment
  (w:comment part) requires modifying document.xml + comments.xml + the relationship table, beyond the script's scope—do manual OXML as needed.
- Tables: `doc.tables[].rows[].cells[].paragraphs` are all covered; merged-cell text only changes the first cell.

## Verification
- The source template's `md5sum` before and after filling should match (source is never written to).
- Output opens in Word/WPS; paragraph styles are preserved (the script clears runs and writes back to the first run, does not rebuild paragraph styles).
