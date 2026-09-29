---
name: handoff
description: >-
  Compact the current conversation into a handoff document for another agent to pick up. Use when the user asks to 交接 / hand off / write a session summary for the next agent or session. Do NOT use for commit messages, changelogs, or status reports.
description_zh: "把当前对话压缩成一份交接文档，方便另一个代理快速接手继续工作。"
license: MIT
compatibility: 纯提示型，任意支持 SKILL.md 的工具可用；无外部依赖。
metadata:
  author: "mattpocock/skills 上游（MIT）"
  version: "1.0.0"
  category: programming
  pattern: single-task
  tier: standard
  verified-date: "2026-09-27"
  source: "https://github.com/mattpocock/skills/tree/main"
---

Write a handoff document summarising the current conversation so a fresh agent can continue the work. Save to the temporary directory of the user's OS - not the current workspace.

Include a "suggested skills" section in the document, naming which skills the next agent should call the Skill tool for.

Do not duplicate content already captured in other artifacts (specs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.

Redact any sensitive information, such as API keys, passwords, or personally identifiable information.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly.

---

## 来源与署名 / Source & Attribution

本技能收录自上游开源仓库 mattpocock/skills（MIT，见该仓库 LICENSE 与版权声明，作者：mattpocock/skills 上游（MIT））。
awesome-skillkit 保留上游正文与参考文件，仅补齐本仓库 frontmatter 元数据、为长参考文档增补目录、按本仓库链接口径归一化相对路径；同步上游时以官方仓库为准。
