---
name: gws-calendar-agenda
description: >-
  Google Calendar: Show upcoming events across all calendars.
description_zh: "通过 gws CLI 汇总展示所有 Google 日历中即将到来的日程活动安排。"
license: Apache-2.0
compatibility: 需要 Google Workspace CLI（gws）与 OAuth 凭据。
metadata:
  author: "googleworkspace/cli 上游（Apache-2.0）"
  version: "1.0.0"
  category: integrations
  pattern: single-task
  tier: standard
  verified-date: "2026-09-27"
  source: "https://github.com/googleworkspace/cli/tree/main"
---

# calendar +agenda

> **PREREQUISITE:** Read `../gws-shared/SKILL.md` for auth, global flags, and security rules. If missing, run `gws generate-skills` to create it.

Show upcoming events across all calendars

## Usage

```bash
gws calendar +agenda
```

## Flags

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--today` | — | — | Show today's events |
| `--tomorrow` | — | — | Show tomorrow's events |
| `--week` | — | — | Show this week's events |
| `--days` | — | — | Number of days ahead to show |
| `--calendar` | — | — | Filter to specific calendar name or ID |
| `--timezone` | — | — | IANA timezone override (e.g. America/Denver). Defaults to Google account timezone. |

## Examples

```bash
gws calendar +agenda
gws calendar +agenda --today
gws calendar +agenda --week --format table
gws calendar +agenda --days 3 --calendar 'Work'
gws calendar +agenda --today --timezone America/New_York
```

## Tips

- Read-only — never modifies events.
- Queries all calendars by default; use --calendar to filter.
- Uses your Google account timezone by default; override with --timezone.

## See Also

- [gws-shared](../gws-shared/SKILL.md) — Global flags and auth
- [gws-calendar](../gws-calendar/SKILL.md) — All manage calendars and events commands

---

## 来源与署名 / Source & Attribution

本技能收录自上游开源仓库 googleworkspace/cli（Apache-2.0，见该仓库 LICENSE 与版权声明，作者：googleworkspace/cli 上游（Apache-2.0））。
awesome-skillkit 保留上游正文与参考文件，仅补齐本仓库 frontmatter 元数据、为长参考文档增补目录、按本仓库链接口径归一化相对路径；同步上游时以官方仓库为准。
