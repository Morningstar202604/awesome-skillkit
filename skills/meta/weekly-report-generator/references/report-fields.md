# Weekly-report sections and JSON fields

## Three-section structure (works for every company)
- **What I did**: pulled automatically via `git log --since=N days`, one line per commit as `date author: subject`
- **Where I'm stuck**: defaults to `[to fill in]`, completed by hand (blockers / risks / things needing coordination)
- **Next week's plan**: defaults to `[to fill in]`, completed by hand

## `--input report.json` fields
```json
{
  "done": ["optional; overrides the auto-pulled commit list"],
  "blockers": "string",
  "next": "string"
}
```
- If `done` is not passed, the git auto result is used entirely
- If `done` is passed, **only** your list is used (git is no longer pulled)

## Aligning section names
Does your company's weekly-report template use different section names? Change the `## 1. Done this week`
headings in `TEMPLATE`, or feed `done/blockers/next` in via `--input`.
