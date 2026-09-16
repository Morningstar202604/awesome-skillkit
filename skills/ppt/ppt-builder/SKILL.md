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

# PPT Builder（需求简报 → 演示文稿）

产出两件东西：逐页内容规格（JSON），以及——在 python-pptx 可用时——由它渲染出的真实 .pptx。规格是唯一事实源；渲染只是机械执行。

## 输入清单

| 输入 | 必填 | 默认 | 说明 |
|---|---|---|---|
| 主题 | 是 | — | 这套 PPT 要论证或解释什么 |
| 受众 | 否 | 通用商务 | 决定语气和深度 |
| slide_count | 否 | `10` | 含封面和结尾页 |
| 风格 | 否 | 简洁商务 | 如：学术答辩 / 融资路演 / 教学课件 |

缺主题时，只问一次：

> 请给出 PPT 主题与用途（汇报对象是谁）。可选告知：页数（默认 10）、
> 风格（默认简洁商务）、是否已有大纲或素材文件。

## 前置自检

```bash
python -c "import pptx; print('pptx-ok')"
```

- 打印 `pptx-ok` → 启用 .pptx 导出（步骤 3a）。
- ModuleNotFoundError → 走 markdown 路径（步骤 3b）。用一句话告知用户：
  `pip install python-pptx` 下次即可直接导出 .pptx。除非用户明确同意，否则不要自行安装。

## 工作流

### 步骤 1：搭大纲

按此顺序组织论证（不是罗列话题）：钩子开场（一个问题或反直觉
事实）→ 全局地图 → 核心论点 2–3 个（每个配证据/案例）→ 反驳或边界 → 行动号召。

预期：带编号的大纲，每页只陈述一个论点。

### 步骤 2：逐页规格

写 `slides_spec.json`：

```json
{
  "deck_title": "...",
  "slides": [
    {"title": "...", "bullets": ["<=18字/条, 最多5条"], "notes": "讲稿口语版", "visual": "图表/截图/留白提示"}
  ]
}
```

规则：title ≤ 16 字并含观点（不是"介绍"这种空词）; notes 必须是能照着说的
完整句子。

### 步骤 3a：渲染 .pptx（pptx 可用）

```bash
python "<skill-dir>/scripts/make_pptx.py" slides_spec.json deck.pptx
```

预期：exit 0 加 `wrote deck.pptx (N slides)`。exit 3 表示缺 python-pptx
→ 转步骤 3b 并告知用户原因。exit 2 表示规格无效——读打印出的错误，
修 slides_spec.json 后重跑。

### 步骤 3b：兜底交付物

输出 `deck_outline.md`：H1 为演示文稿标题，每页一个 H2，含 bullets 和该页讲稿。用户可粘贴进任何工具。

### 步骤 4：交付前自审

检查：每页只讲一个论点；无超过 5 条 bullet；每页 visual 有具体提示；
notes 总词量支撑目标时长（约 1 分钟/页）。发现违规就改规格重渲染，不要手工补 prose。

## 失败处置表

| 现象 | 可能原因 | 处置 |
|---|---|---|
| 脚本 exit 2 并指出第 N 页 | 规格违反 schema | 按步骤 2 的结构修该页字段 |
| 脚本 exit 3 | 缺 python-pptx | 转步骤 3b，给出 pip 提示 |
| bullet 反复超 18 字 | 大纲太密 | 把该页拆成两页，重渲染 |
| 用户要求套公司模板 | v1 不含样式定制 | 交付 spec + outline.md 供手工改样式 |

## 交付标准

成功 = `deck.pptx`（可打开，页数与规格一致）或 `deck_outline.md`，加上 `slides_spec.json`，三个路径都回报并附页数。缺任何一项即未完成——如实说明。

## 参考

- `scripts/make_pptx.py` — 直接运行（执行，不要读）；先校验规格再渲染
- [layout-and-chart-rules.md](references/layout-and-chart-rules.md) — 版式与图表规则词库：字号层级表、信息密度三档、图表选择决策树（什么数据配什么图）、对齐网格、配色对比度基准、负面清单（排版规格与图表选型时查）
