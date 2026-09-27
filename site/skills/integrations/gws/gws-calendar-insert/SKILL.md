---
name: gws-calendar-insert
description: >-
  Google Calendar: create a new event via the gws CLI. Use when the user
  wants to add an event or schedule a meeting on Google Calendar.
description_zh: "Google 日历：新建日程（时间、参会人、会议室与提醒）。"
license: Apache-2.0
compatibility: 需要 Google Workspace CLI（gws）与 OAuth 凭据。
metadata:
  author: "googleworkspace/cli 上游（Apache-2.0）"
  version: "1.0.0"
  category: integrations
  pattern: single-task
  tier: standard
  verified-date: "2026-09-27"
  source: "https://github.com/googleworkspace/cli/tree/main/skills/gws-calendar-insert"
---

# calendar +insert

> **PREREQUISITE:** Read `../gws-shared/SKILL.md` for auth, global flags, and security rules. If missing, run `gws generate-skills` to create it.

create a new event

## Usage

```bash
gws calendar +insert --summary <TEXT> --start <TIME> --end <TIME>
```

## Flags

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--calendar` | — | primary | Calendar ID (default: primary) |
| `--summary` | ✓ | — | Event summary/title |
| `--start` | ✓ | — | Start time (ISO 8601, e.g., 2024-01-01T10:00:00Z) |
| `--end` | ✓ | — | End time (ISO 8601) |
| `--location` | — | — | Event location |
| `--description` | — | — | Event description/body |
| `--attendee` | — | — | Attendee email (can be used multiple times) |
| `--meet` | — | — | Add a Google Meet video conference link |

## Examples

```bash
gws calendar +insert --summary 'Standup' --start '2026-06-17T09:00:00-07:00' --end '2026-06-17T09:30:00-07:00'
gws calendar +insert --summary 'Review' --start ... --end ... --attendee alice@example.com
gws calendar +insert --summary 'Meet' --start ... --end ... --meet
```

## Tips

- Use RFC3339 format for times (e.g. 2026-06-17T09:00:00-07:00).
- The --meet flag automatically adds a Google Meet link to the event.

> [!CAUTION]
> This is a **write** command — confirm with the user before executing.

## See Also

- [gws-shared](../gws-shared/SKILL.md) — Global flags and auth
- [gws-calendar](../gws-calendar/SKILL.md) — All manage calendars and events commands

---

## 来源与署名 / Source & Attribution

本技能收录自 [googleworkspace/cli](https://github.com/googleworkspace/cli/tree/main/skills/gws-calendar-insert)（Apache-2.0）；awesome-skillkit 仅做规范化（frontmatter 归一、补中文描述、路径与链接清理）与署名，内容与更新以上游为准。
