---
name: meeting-notes
description: >
  Turn raw meeting transcripts or rough notes into structured minutes:
  decisions, action items with owners and deadlines, open questions, and a
  circulation-ready summary. Use when the user asks to 整理会议纪要 /
  会议记录 / notes from this transcript / summarize this meeting /
  把录音转的文字整理一下. Do NOT use for live transcription, audio-to-text
  conversion, or project status reports without meeting content.
license: Apache-2.0
compatibility: No special environment; accepts pasted transcript or notes.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: office-productivity
  verified-date: "2026-08-26"
---

# Meeting Notes (transcript → minutes)

Machine-first rule: never invent an owner, date, or decision. If the
transcript does not state it, mark it `<未明确>` and list it in open questions.

## Inputs

| Input | Required | Default | Notes |
|---|---|---|---|
| transcript / raw notes | yes | — | pasted text; speaker labels help but optional |
| meeting meta | no | — | date, attendees, purpose |
| audience | no | 全体相关人 | shapes how blunt the summary is |

If the transcript is missing, ask ONCE:

> 请粘贴会议文字记录（语音转写稿即可）。可选告知：日期、参会人、
> 会议目标，以及纪要发给谁。

## Workflow

### Step 1: Segment before summarizing

Split the transcript chronologically into议题块 (one block per topic shift),
numbering them T1…Tn with a one-line topic label each.
Expected: block count matches discussion flow; merge fragments of the same topic.

### Step 2: Extract decisions vs discussions

For each block classify every exchange as:
- **决议**：有明确结论且无人反对（记录原话关键句作为证据）
- **讨论**：有交换但无结论 → 归入 open questions
- **行动**：有人说"我来/你去/下周前" → 进入 Step 3
Expected: zero unclassified exchanges; when ambiguous, quote the sentence in
open questions instead of guessing intent.

### Step 3: Action table (the deliverable's core)

| 行动项 | Owner | 截止 | 来源议题 | 状态 |
|---|---|---|---|---|

Rules: Owner 必须是 transcript 里点名的人，否则写 `<待指派>`;
deadline 缺失写 `<待定>`；每行必须能在 T 编号中找到出处。

### Step 4: Compose minutes in fixed structure

```
# 会议纪要 YYYY-MM-DD <主题>
参会：<名单或<未明确>>
## 一页结论
<3–5 条最重要的决议，每条一行>
## 决议明细
<按 T 编号，决议+证据原话>
## 行动项
<Step 3 表格>
## 待明确问题
<无主/无结论事项，含需要谁来拍板>
```

### Step 5: Consistency check before delivery

Verify: every 决议 has evidence quote; every action has owner+deadline or an
explicit placeholder; total length ≤ 1/3 of transcript. Fix violations by
returning to Steps 2–3, not by deleting items.

## Failure handling

| Symptom | Likely cause | Action |
|---|---|---|
| speakers unlabeled in transcript | raw ASR dump | infer roles from content but mark `<推断>` on uncertain attributions |
| two conflicting "decisions" same topic | later reversal missed | keep both with timestamps, flag in open questions |
| transcript truncated mid-topic | input incomplete | note cutoff point Tn explicitly at the end |
| user asks to soften a decision | political editing | deliver faithful version; edits are theirs to make |

## Delivery standard

Success = minutes following the exact Step-4 skeleton, with a complete action
table and zero invented facts. Anything else is not done — say so plainly.
