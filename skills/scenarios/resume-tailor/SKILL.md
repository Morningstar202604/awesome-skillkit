---
name: resume-tailor
description: >
  Tailor a resume to one specific job description: extract JD requirements,
  build a gap matrix, rewrite bullets with metrics (STAR), and output an
  ATS-safe document plus an edit changelog. Use when the user asks to 改简历 /
  简历定制 / 针对这个岗位改简历 / tailor my resume for this JD /
  optimize my CV. Do NOT use for writing cover letters, LinkedIn profiles,
  or fabricating experience.
license: Apache-2.0
compatibility: No special environment needed; accepts plain text or pasted resume.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: office-productivity
  verified-date: "2026-08-26"
---

# Resume Tailor (resume + JD → tailored version)

One JD per pass. The machine-first rule: every edit must trace back to a
JD line or an evidence line in the original resume. Fabrication is a hard
ban — see red lines.

## Inputs

| Input | Required | Default | Notes |
|---|---|---|---|
| resume text/file | yes | — | plain text preferred |
| job description | yes | — | paste full JD, not just the title |
| target tone | no | 简洁量化 | e.g. 外企英文 / 国内互联网 |

If anything required is missing, ask ONCE:

> 请提供：① 现有简历全文；② 目标岗位的完整 JD（含任职要求）。
> 可选：希望中文还是英文、有无特别想突出的项目。

## Red lines (hard bans, non-negotiable)

1. 不得虚构经历、职级、证书或数字。量化只能来自原简历已有事实或向用户提问确认。
2. 不得隐瞒真实性问题的美化（如把实习写成工作）。
3. 原因：背调与面试深挖会放大任何造假，代价是 offer 作废乃至行业口碑。

## Workflow

### Step 1: Extract JD requirements

Build a two-column table: 硬性要求（学历/年限/必备技能）｜软性优先项。
Expected: 5–12 rows, each quoting the JD's own words.

### Step 2: Gap matrix

Map every JD row against the resume: 匹配(有证据) / 部分(需强化表述) /
缺失(只能诚实留白或建议用户补充真实素材)。Expected: no row left unjudged.

### Step 3: Rewrite bullets

For 部分 matches, rewrite with STAR + metric:
`动词 + 做了什么 + 方法/规模 + 可验证结果`。
Example transformation — before: "负责公众号运营";
after: "独立运营公众号（3 个月），周更 2 篇，粉丝从 1.2k 增至 4.6k（+283%）"。
If a number does not exist in the source, insert `<待你确认：具体数值>`
instead of inventing one.

### Step 4: ATS hygiene pass

Single column layout; standard headings (教育经历/工作经历/项目/技能);
no tables, text boxes, or graphics for content; keywords mirrored from JD
where honestly applicable; file naming `姓名_岗位_简历.pdf`.

### Step 5: Deliver two artifacts

① tailored resume full text; ② `edit_log.md` listing each change as
`原文 → 改后 ← JD依据`, plus a 待补充清单 of gaps only the user can fill
(numbers, projects). Expected: user can accept/reject every edit individually.

## Failure handling

| Symptom | Likely cause | Action |
|---|---|---|
| JD rows exceed resume evidence everywhere | mismatch level | say so honestly; suggest adjacent roles rather than inflating |
| user asks to inflate numbers/make up certs | red line violation | refuse that edit, restate ban, offer honest strengthening |
| resume too long after tailoring | legacy irrelevant blocks | cut by JD relevance, log every cut in edit_log |
| key skill missing entirely | true gap | add to 待补充清单 with a concrete way to gain it fast |

## Delivery standard

Success = tailored resume text + `edit_log.md` with per-edit traceability,
zero unverifiable claims. Anything else is not done — say so plainly.
