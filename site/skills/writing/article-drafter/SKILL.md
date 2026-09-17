---
name: article-drafter
description: "Generate article first draft from an approved outline. Fills in each section with prose based on key points, audience level, and style. Use after the outline is approved, before editing/SEO. 当用户要求 写文章初稿 / 起草正文 / 帮我写这篇 / 把大纲扩写成文章 时使用。 Also triggers on / 正文起草 / 写初稿 / 扩写大纲 / draft article / write first draft. Do NOT use for publishing the finished draft to platforms, or for building the outline itself (use article-outliner)."
license: Apache-2.0
compatibility: Pure prompt-based drafting; LLM generates prose. Optional helper scripts/drafter.py requires Python 3.8+ (stdlib only). No API keys required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: writing
  pattern: single-task
  tier: standard
  verified-date: "2026-09-09"
---

# Article Drafter（从大纲生成文章初稿）

根据已批准的大纲，按受众层级与文风把每个章节的关键点扩写成可读正文，产出待评审初稿。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| `outline` | 是 | 大纲对象：含 `title`、`sections[]`（每节 `heading`/`points`/`word_count_target`），可选 `hook`/`conclusion` |
| `audience` | 否 | `beginner` / `intermediate` / `expert`，默认 `intermediate`，决定术语密度 |
| `tone` | 否 | 文风，如 `technical` / `casual` / `news` |
| `research_notes` | 否 | 原始素材，用于补充事实与数据 |

缺失时一次性问齐：「请提供：① 大纲（标题 + 各章节要点 + 每节字数目标）；② 目标受众（beginner/intermediate/expert）；③ 文风 tone；其余我采用默认值：audience=intermediate、tone=technical、research_notes=空。」

## 前置自检

1. 确认 `outline` 存在且非空：
   ```bash
   python3 scripts/drafter.py --outline outline.json --output /tmp/draft_check.json
   ```
   预期：退出码 `0`，生成 JSON 且 `sections` 数组长度 ≥ 1。
   若失败：`FileNotFoundError` → 路径错误，请用户确认 `outline.json` 位置后 STOP。
2. 确认 `audience` 取值在 `beginner|intermediate|expert` 内；否则回退 `intermediate` 并提示。
3. 若不用脚本（纯提示词模式），跳过第 1 步，直接进入工作流步骤 2。

## 工作流

### 步骤 1：生成大纲骨架（确定性，可选）

运行脚本把大纲结构化为初稿占位骨架，正文由 LLM 在步骤 2 填充：
```bash
python3 scripts/drafter.py --outline outline.json --audience intermediate --output draft.json
```
预期：`draft.json` 含 `title`/`hook`/`sections[]`/`status:"draft"`/`needs_review:true`。
若失败：参数缺失报 `Need --outline, --topic, or --section` → 补 `--outline` 后重跑。

### 步骤 2：逐节填充正文（LLM 生成）

对 `sections[]` 每一项：
- 读取 `points`，展开为 2–4 段；
- 匹配 `audience` 术语密度（见下方「受众风格规则」）；
- 命中 `word_count_target` ±20%。
预期：每节 `draft` 字段非空，字数落在目标区间。
若失败：某节无 `points` → 用 `heading` 作为唯一要点生成，并标记该节 `needs_review`。

### 步骤 3：写开头 hook 与结论 CTA

- 用 `outline.hook`（若存在）作开头 2 句抓注意力；缺失则自写一句场景化开场。
- 写 `conclusion` + 行动号召（关注/收藏/评论，按平台口径）。
预期：`hook` 与 `conclusion` 非空。

### 步骤 4：产出完整初稿

整合为完整初稿，输出 JSON 或 Markdown。
预期：产物含全部章节、总字数、状态 `draft`、待评审标记。

## 输入输出示例

输入 `outline`：
```json
{
  "outline": {
    "title": "FastAPI 性能优化",
    "sections": [
      {"heading": "为什么慢", "points": ["同步I/O", "N+1"], "word_count_target": 300}
    ]
  },
  "audience": "intermediate",
  "tone": "technical",
  "research_notes": "optional raw material"
}
```

输出初稿：
```json
{
  "title": "FastAPI 性能优化",
  "sections": [
    {
      "id": 1,
      "heading": "为什么慢",
      "draft": "FastAPI 默认使用 async/await，但很多开发者...",
      "word_count": 320
    }
  ],
  "total_words": 1850,
  "status": "draft",
  "needs_review": true
}
```

## 受众风格规则

| 受众 | 术语密度 | 示例 | 代码 |
|------|---------|------|------|
| Beginner | 最少，全解释 | 每节 3-4 个 | 完整片段 |
| Intermediate | 适中，标准术语 | 每节 2-3 个 | 关键片段 |
| Expert | 高密度，假定已懂 | 每节 0-1 个 | 单行片段 |

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| `--outline` | 文件路径 | 大纲 JSON（见输入示例），必需之一 |
| `--topic` | 字符串 | 无大纲时的快速主题 |
| `--section` | 字符串 | 只起草单个章节 |
| `--audience` | beginner/intermediate/expert | 默认 `intermediate` |
| `--output` | 文件路径 | 写出初稿 JSON |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|-------------|------|------|
| `FileNotFoundError` on outline | 路径错误 | 确认文件存在，修正路径后重跑 |
| `Need --outline, --topic, or --section` | 缺输入 | 补 `--outline` 或改用纯提示词模式 |
| 某节字数偏离 >20% | 要点过少/过多 | 拆分或合并 `points`，重生成该节 |
| `audience` 取值非法 | 拼写错误 | 回退 `intermediate` 并提示用户 |

## 交付标准

- 成功定义：产出完整初稿，所有章节 `draft` 非空，总字数接近 `total_words_target`。
- 产物命名：`draft.json`（结构化）或 `draft.md`（Markdown）。
- 保存位置：用户指定目录；脚本用 `--output` 指定，默认标准输出。
- 完整性验证：`sections` 数量 == 大纲章节数；每节 `word_count` 落在目标 ±20%；`status=="draft"` 且 `needs_review==true`。

## 参考

- `references/drafting-tips.md` —— 分章节类型的写作技巧，撰写步骤 2 时按需读取。
