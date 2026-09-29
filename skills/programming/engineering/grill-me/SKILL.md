---
name: grill-me
description: >-
  A relentless interview to sharpen a plan or design.
description_zh: "通过持续追问的犀利访谈，反复打磨并完善你的计划或设计方案。"
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

## How to grill (self-contained protocol)

The upstream `grilling` skill is not bundled in this pack — run the interview yourself, in this order:

1. **Restate the plan in one sentence.** Ask the user to confirm your restatement before any questioning. If they can't confirm it, that is the first finding.
2. **One question at a time.** Never batch questions. Wait for the answer, reflect it back in one line, then ask the next.
3. **Probe in this sequence** — go down the list; skip only what the plan genuinely doesn't touch:
   - Assumption: "What are you taking for granted here that could be false?"
   - Failure: "What does this look like when it goes wrong in production / in front of a user?"
   - Edge: "What input or scale breaks this first?"
   - Alternative: "What did you decide NOT to do, and why is that the right call?"
   - Cost: "What does this cost in the worst case — money, time, trust?"
4. **Don't accept vague answers.** If the answer is "it depends" or "we'll figure it out", that's a finding — record it and re-ask with a concrete scenario.
5. **Converge.** After ~5-8 questions (or when answers stop changing the plan), stop. Output three lists:
   - **Sharpened**: claims that survived questioning (with the evidence given)
   - **Changed**: claims the user revised mid-interview
   - **Open**: unanswered risks, each with a suggested owner and deadline

Success criterion: the user can state the plan's weakest point without your help.

---

## 来源与署名 / Source & Attribution

本技能收录自上游开源仓库 mattpocock/skills（MIT，见该仓库 LICENSE 与版权声明，作者：mattpocock/skills 上游（MIT））。
awesome-skillkit 保留上游正文与参考文件，仅补齐本仓库 frontmatter 元数据、为长参考文档增补目录、按本仓库链接口径归一化相对路径；同步上游时以官方仓库为准。
