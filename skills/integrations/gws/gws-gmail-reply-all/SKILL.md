---
name: gws-gmail-reply-all
description: >-
  Gmail: reply-all to a message, handling threading automatically, via the
  gws CLI. Use when the user wants to answer the whole recipient list.
description_zh: "Gmail：全部回复，自动处理会话串。"
license: Apache-2.0
compatibility: 需要 Google Workspace CLI（gws）与 OAuth 凭据。
metadata:
  author: "googleworkspace/cli 上游（Apache-2.0）"
  version: "1.0.0"
  category: integrations
  pattern: single-task
  tier: standard
  verified-date: "2026-09-27"
  source: "https://github.com/googleworkspace/cli/tree/main/skills/gws-gmail-reply-all"
---

# gmail +reply-all

> **PREREQUISITE:** Read `../gws-shared/SKILL.md` for auth, global flags, and security rules. If missing, run `gws generate-skills` to create it.

Reply-all to a message (handles threading automatically)

## Usage

```bash
gws gmail +reply-all --message-id <ID> --body <TEXT>
```

## Flags

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--message-id` | ✓ | — | Gmail message ID to reply to |
| `--body` | ✓ | — | Reply body (plain text, or HTML with --html) |
| `--from` | — | — | Sender address (for send-as/alias; omit to use account default) |
| `--to` | — | — | Additional To email address(es), comma-separated |
| `--attach` | — | — | Attach a file (can be specified multiple times) |
| `--cc` | — | — | CC email address(es), comma-separated |
| `--bcc` | — | — | BCC email address(es), comma-separated |
| `--html` | — | — | Treat --body as HTML content (default is plain text) |
| `--dry-run` | — | — | Show the request that would be sent without executing it |
| `--draft` | — | — | Save as draft instead of sending |
| `--remove` | — | — | Exclude recipients from the outgoing reply (comma-separated emails) |

## Examples

```bash
gws gmail +reply-all --message-id 18f1a2b3c4d --body 'Sounds good to me!'
gws gmail +reply-all --message-id 18f1a2b3c4d --body 'Updated' --remove bob@example.com
gws gmail +reply-all --message-id 18f1a2b3c4d --body 'Adding Eve' --cc eve@example.com
gws gmail +reply-all --message-id 18f1a2b3c4d --body '<i>Noted</i>' --html
gws gmail +reply-all --message-id 18f1a2b3c4d --body 'Notes attached' -a notes.pdf
gws gmail +reply-all --message-id 18f1a2b3c4d --body 'Draft reply' --draft
```

## Tips

- Replies to the sender and all original To/CC recipients.
- Use --to to add extra recipients to the To field.
- Use --cc to add new CC recipients.
- Use --bcc for recipients who should not be visible to others.
- Use --remove to exclude recipients from the outgoing reply, including the sender or Reply-To target.
- The command fails if no To recipient remains after exclusions and --to additions.
- Use -a/--attach to add file attachments. Can be specified multiple times.
- With --html, the quoted block uses Gmail's gmail_quote CSS classes and preserves HTML formatting. Use fragment tags (<p>, <b>, <a>, etc.) — no <html>/<body> wrapper needed.
- With --html, inline images in the quoted message are preserved via cid: references.
- Use --draft to save the reply as a draft instead of sending it immediately.

## See Also

- [gws-shared](../gws-shared/SKILL.md) — Global flags and auth
- [gws-gmail](../gws-gmail/SKILL.md) — All send, read, and manage email commands

---

## 来源与署名 / Source & Attribution

本技能收录自 [googleworkspace/cli](https://github.com/googleworkspace/cli/tree/main/skills/gws-gmail-reply-all)（Apache-2.0）；awesome-skillkit 仅做规范化（frontmatter 归一、补中文描述、路径与链接清理）与署名，内容与更新以上游为准。
