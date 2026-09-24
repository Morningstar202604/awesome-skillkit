# Handoff JSON fields

`--input handoff.json` may contain the following keys (missing ones fall back to template placeholders):

| Key | Type | Description |
|---|---|---|
| title | str | session title |
| author | str | authoring agent name |
| goal | str | original intent |
| done | list[str] | completed items (in order) |
| next | list[str] | next steps (in order) |
| gotchas | list[str] | known pitfalls |
| files | list[str] | key file paths |
| repo | str | repository/project |
| verify | str | how to run/verify |
| blocker | str | current blocker |

Command-line arguments of the same name are overridden by the JSON (JSON wins).
