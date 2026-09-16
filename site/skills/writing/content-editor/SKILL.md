---
name: content-editor
description: "Proofread, polish, and style-unify article drafts. Detects banned words, inconsistent tone, overlong sentences, and grammar issues. Scores editability. Use after drafting, before SEO and publishing. 当用户要求 润色文章 / 校对错别字 / 统一文风 / 改掉 AI 腔 / 给文章做质量检查 时使用。 Do NOT use for generating new content from scratch (editing and polishing only)."
license: Apache-2.0
compatibility: Pure Python analysis; LLM-assisted for rewriting. Optional helper scripts/editor.py requires Python 3.8+ (stdlib only). No API keys required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: writing
  pattern: single-task
  tier: standard
  verified-date: "2026-09-09"
---

# Content Editor（校对、润色与文风统一）

对已成形的草稿做质量核查：扫描禁用词、过长句、章节衔接与文风一致性，并给出 0–100 可编辑性评分。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| `draft` | 是 | 草稿对象：`title` + `sections[]`（每节 `heading`/`draft`） |
| `style` | 否 | `technical` / `casual` / `news`，默认 `technical` |
| `brand_voice` | 否 | 期望语气的文字描述，用于 LLM 改写时对齐 |

缺失时一次性问齐：「请提供：① 待润色草稿（JSON 或纯文本）；② 文风 style（technical/casual/news）；③ 品牌语气 brand_voice（可空）。其余默认：style=technical。」

## 前置自检

1. 校验脚本可用性（可选，确定性扫描）：
   ```bash
   python3 scripts/editor.py --draft draft.json --style technical --output edited.json
   ```
   预期：退出码 `0`，输出含 `score`/`issues`/`suggestions`。
   若失败：`Need --draft or --text` → 补 `--draft` 或 `--text` 后重跑。
2. 确认 `style` 取值在 `technical|casual|news` 内；否则回退 `technical`。
3. 纯提示词模式可跳过第 1 步，直接进入工作流。

## 工作流

### 步骤 1：载入草稿

读取 `draft`，提取全文与各节文本。
预期：得到可扫描的文本串与各节索引。
若失败：JSON 解析错误 → 提示用户修正 `draft` 结构后 STOP。

### 步骤 2：扫描禁用词

按 `style` 的规则集（见「文风规则表」）逐词匹配 `ban` 列表。
预期：产出 `issues[]` 中 `type:"banned_word"` 条目，含命中词与位置。
若失败：某词跨节 → 记录首个命中 `line` 即可。

### 步骤 3：检查句长

按句号切分，统计超过 `max_sentence_len` 的长句。
预期：`long_sentences` 计数准确。
若失败：无句号文本 → 按换行切分再统计。

### 步骤 4：核对章节衔接

检查相邻章节是否有过渡句/过渡短语，缺则给建议。
预期：`suggestions[]` 含衔接建议（若有缺口）。

### 步骤 5：评分

`score = 100 - issues×5 - long_sentences×2`，下限 0。
预期：输出 `score`（0–100）、`issues`、`suggestions`、`sections_edited`。

### 步骤 6：产出核查结果

整合为结果对象（示例见下）；LLM 据此改写草稿。

## 输入输出示例

输入：
```json
{
  "draft": {
    "title": "...",
    "sections": [{"heading": "...", "draft": "text..."}]
  },
  "style": "technical",
  "brand_voice": "optional: description of desired voice"
}
```

输出：
```json
{
  "score": 82,
  "issues": [
    {"type": "banned_word", "word": "我觉得", "line": 12},
    {"type": "long_sentence", "chars": 78, "limit": 40, "line": 25}
  ],
  "suggestions": ["Add transition phrase between sections 2 and 3"],
  "sections_edited": 5,
  "status": "reviewed"
}
```

## 文风规则表

| 文风 | 禁用词 | 替换用词 | 单句上限 |
|------|--------|---------|----------|
| Technical | 我觉得/应该/可能 | 根据/实测/结论是 | 40 字符 |
| Casual | 综上所述/由此可见 | 说白了/你看 | 25 字符 |
| News | 震惊/炸了/绝了 | 据悉/报道称 | 30 字符 |

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| `--draft` | 文件路径 | 草稿 JSON（见输入示例），必需之一 |
| `--text` | 字符串 | 纯文本草稿 |
| `--style` | technical/casual/news | 默认 `technical` |
| `--output` | 文件路径 | 写出核查结果 JSON |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|-------------|------|------|
| `Need --draft or --text` | 缺输入 | 补 `--draft` 或 `--text` |
| JSON 解析失败 | 草稿结构错误 | 提示用户修正 `draft` 字段 |
| `style` 取值非法 | 拼写错误 | 回退 `technical` 并提示 |
| `score` 为负 | issues 过多 | 下限截断为 0，并优先改写禁用词 |

## 交付标准

- 成功定义：产出核查结果，含 `score`、`issues`、`suggestions`、`status:"reviewed"`。
- 产物命名：`edited.json`（核查结果）或 `draft.reviewed.md`（改写后正文）。
- 保存位置：用户指定目录，脚本用 `--output` 指定，默认标准输出。
- 完整性验证：`score` ∈ [0,100]；`issues` 与 `suggestions` 非空时分别对应；`sections_edited` == 草稿章节数。

## 参考

- `references/style-guide.md` —— 家风（house style）细则，步骤 2/5 时按需读取。
- `references/grammar-checks.md` —— 中英文常见语法错误清单，步骤 2/3 时读取。
