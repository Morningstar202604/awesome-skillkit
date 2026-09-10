---
name: ppt-builder
description: >
  Build presentation decks: structured outline, per-slide content spec, and a
  real .pptx file via bundled script (with graceful markdown fallback). Use
  when the user asks to 做 PPT / 做个演示文稿 / 写个幻灯片 / create slides /
  make a deck / prepare a presentation about X. Do NOT use for Word documents,
  spreadsheets, or PDF forms.
license: Apache-2.0
compatibility: Optional python3 with python-pptx for .pptx export; fallback needs nothing.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: office-productivity
  verified-date: "2026-08-26"
---

# PPT Builder (brief → deck)

Produce a deck in two artifacts: a per-slide content spec (JSON) and — when
python-pptx exists — a real .pptx rendered from it. The spec is the source of
truth; rendering is mechanical.

## Inputs

| Input | Required | Default | Notes |
|---|---|---|---|
| topic | yes | — | what the deck argues or explains |
| audience | no | 通用商务 | shapes tone and depth |
| slide_count | no | `10` | including cover and closing |
| style | no | 简洁商务 | e.g. 学术答辩 / 融资路演 / 教学课件 |

If topic is missing, ask ONCE:

> 请给出 PPT 主题与用途（汇报对象是谁）。可选告知：页数（默认 10）、
> 风格（默认简洁商务）、是否已有大纲或素材文件。

## Preflight self-check

```bash
python -c "import pptx; print('pptx-ok')"
```

- Prints `pptx-ok` → .pptx export enabled (Step 3a).
- ModuleNotFoundError → markdown path (Step 3b). Tell the user one line:
  `pip install python-pptx` enables direct .pptx export next time. Do NOT
  install it yourself unless the user explicitly says yes.

## Workflow

### Step 1: Outline

Structure the argument (not topics) in this order: 钩子开场（一个问题或反直觉
事实）→ 全局地图 → 核心论点 2–3 个（每个配证据/案例）→ 反驳或边界 → 行动号召。
Expected: numbered outline where every slide states ONE claim.

### Step 2: Per-slide spec

Write `slides_spec.json`:

```json
{
  "deck_title": "...",
  "slides": [
    {"title": "...", "bullets": ["<=18字/条, 最多5条"], "notes": "讲稿口语版", "visual": "图表/截图/留白提示"}
  ]
}
```

Rules: title ≤ 16 字并含观点（不是"介绍"这种空词）; notes 必须是能照着说的
完整句子。

### Step 3a: Render .pptx (pptx available)

```bash
python "<skill-dir>/scripts/make_pptx.py" slides_spec.json deck.pptx
```

Expected: exit 0 plus `wrote deck.pptx (N slides)`. Exit 3 means python-pptx
missing → fall back to 3b and tell the user why. Exit 2 means spec invalid —
read the printed error, fix slides_spec.json, rerun.

### Step 3b: Fallback deliverable

Emit `deck_outline.md`: H1 deck title, H2 per slide with bullets and the
speaker note under each. User pastes into any tool.

### Step 4: Self-review before handing over

Check: 每页只讲一个论点；无超过 5 条 bullet；每页 visual 有具体提示；
notes 总词量支撑目标时长（约 1 分钟/页）。Fix violations in the spec and
re-render rather than patching prose.

## Failure handling

| Symptom | Likely cause | Action |
|---|---|---|
| script exits 2 listing slide N | spec schema violation | fix that slide's fields per Step 2 shape |
| script exits 3 | python-pptx absent | switch to Step 3b, offer the pip hint |
| bullets keep exceeding 18 字 | outline too dense | split the slide into two, re-render |
| user wants their company template | styling out of scope for v1 | deliver spec + outline.md for manual restyle |

## Delivery standard

Success = either `deck.pptx` (openable, N slides matching spec) or
`deck_outline.md`, PLUS `slides_spec.json`, all three paths reported with
slide count. Anything else is not done — say so plainly.

## References

- `scripts/make_pptx.py` — run it (execute, not read); validates spec then renders
