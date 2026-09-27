---
name: gws-gmail-triage
description: >-
  Gmail: show an unread inbox summary (sender, subject, date) via the gws
  CLI. Use when the user wants to scan or triage unread email.
description_zh: "Gmail：快速分诊收件箱——未读邮件摘要（发件人/主题/日期）。"
license: Apache-2.0
compatibility: 需要 Google Workspace CLI（gws）与 OAuth 凭据。
metadata:
  author: "googleworkspace/cli 上游（Apache-2.0）"
  version: "1.0.0"
  category: integrations
  pattern: single-task
  tier: standard
  verified-date: "2026-09-27"
  source: "https://github.com/googleworkspace/cli/tree/main/skills/gws-gmail-triage"
---

# gmail +triage

> **PREREQUISITE:** Read `../gws-shared/SKILL.md` for auth, global flags, and security rules. If missing, run `gws generate-skills` to create it.

Show unread inbox summary (sender, subject, date)

## Usage

```bash
gws gmail +triage
```

## Flags

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--max` | — | 20 | Maximum messages to show (default: 20) |
| `--query` | — | — | Gmail search query (default: is:unread) |
| `--labels` | — | — | Include label names in output |

## Examples

```bash
gws gmail +triage
gws gmail +triage --max 5 --query 'from:boss'
gws gmail +triage --format json | jq '.[].subject'
gws gmail +triage --labels
```

## Tips

- Read-only — never modifies your mailbox.
- Defaults to table output format.

## See Also

- [gws-shared](../gws-shared/SKILL.md) — Global flags and auth
- [gws-gmail](../gws-gmail/SKILL.md) — All send, read, and manage email commands

---

## 来源与署名 / Source & Attribution

本技能收录自 [googleworkspace/cli](https://github.com/googleworkspace/cli/tree/main/skills/gws-gmail-triage)（Apache-2.0）；awesome-skillkit 仅做规范化（frontmatter 归一、补中文描述、路径与链接清理）与署名，内容与更新以上游为准。
