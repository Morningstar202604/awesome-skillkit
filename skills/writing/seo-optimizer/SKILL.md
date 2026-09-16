---
name: seo-optimizer
description: "Optimize article for search: extract keywords, generate meta tags, score SEO quality, and adapt titles/captions per platform. Use after editing, before publishing to specific platforms. Use when the user asks to 做 SEO 优化 / 选关键词 / 优化标题 / 检查关键词密度 / 生成 meta 描述 / optimize SEO / extract keywords / SEO score / meta description / platform title limits. Do NOT use for paid advertising strategy, ad bidding, or writing the article itself."
license: Apache-2.0
compatibility: Pure Python analysis. No API keys required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: writing
  pattern: single-task
  tier: basic
  verified-date: "2026-09-09"
---

# SEO Optimizer: score article SEO-readiness and adapt titles/meta per platform

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| `--title` | 是 | 文章标题原文 |
| `--content` | 是 | 正文全文：传文件路径或直接传文本 |
| `--platform` | 否 | 目标平台 ID（`csdn`/`juejin`/`wechat`/`baijiahao`/`toutiao`，默认 `csdn`） |
| `--output` | 否 | 结果写入的 JSON 文件路径；缺省打印到 stdout |
| `target_keywords` | 否 | 人工指定的主关键词；缺省时脚本用词频分析自动提取 |

缺输入时一次性问齐（不要分多轮追问）：
"请提供：① 文章标题；② 正文文件路径（或直接粘贴全文）；③ 目标平台（默认 csdn）。"

## 前置自检

依次执行，任一失败 → 按提示修复后 STOP，不要继续：

```bash
# 1. Python 3 可用（脚本为纯标准库实现）
python3 --version
# 预期：输出 Python 3.x；失败 → 安装 Python 3.8+

# 2. 脚本文件存在
test -f scripts/seo_optimizer.py && echo OK
# 预期：OK；失败 → 你不在技能目录内，cd 到本技能目录

# 3. 脚本可运行（冒烟）
python3 scripts/seo_optimizer.py --title "smoke" --content "smoke content" | head -c 20
# 预期：输出以 { 开头的 JSON；失败 → 看"失败处置表"第 1 行
```

## 工作流

### 步骤 1：运行 SEO 分析

```bash
python3 scripts/seo_optimizer.py \
  --title "FastAPI 性能优化" \
  --content article.md \
  --platform csdn \
  --output seo_result.json
```

- **动作**：`--content` 传正文文件路径（或直接传文本）；`--platform` 按目标平台传；`--output` 落盘结果。
- **预期**：退出码 0，stdout/输出文件包含 JSON，含 `title`（含 `issues`/`suggestions`）与 `meta`（含 `meta_description`/`tags`/`keywords`/`score`）字段；`score` 为 0-100 整数。
- **若失败**：报 `FileNotFoundError` → `--content` 路径写错，改用绝对路径重跑；报 `unrecognized arguments` → 对照"参数速查表"修正参数名。

### 步骤 2：按 suggestions 优化标题

- **动作**：读取 JSON 中 `title.suggestions` 列表逐条落实——标题补数字（如 "从 200ms 到 30ms"）、补主关键词、压到平台长度限制内（见"平台标题限制"表）。
- **预期**：改写后的标题满足三条：含主关键词、长度 ≤ 平台上限、带具体数字或对比。
- **若失败**：脚本 suggestions 为空但标题明显过长 → 以"平台标题限制"表为准人工压缩。

### 步骤 3：生成 meta description 与标签

- **动作**：取 `meta.meta_description`（正文前 150 字符改写，含主关键词，80-160 字符）；`meta.tags`/`meta.keywords` 作为发布平台标签与关键词候选，人工去重后按平台标签数上限截取。
- **预期**：meta description 长度 80-160 字符且含主关键词；标签数 ≤ 平台限制（如 CSDN ≤ 5）。
- **若失败**：`meta.tags` 为空数组 → 正文太短或关键词密度不足，先按 `title.issues` 补正文关键词，重跑步骤 1。

### 步骤 4：复评并输出结果

- **动作**：把优化后的标题代入重跑步骤 1，对比 `score`；将最终 JSON（优化标题 + meta + score + platform）交付给发布类技能使用。
- **预期**：复评 `score` 不低于首次得分；交付物包含完整 JSON 与最终版标题。
- **若失败**：复评分下降 → 回滚到上一次标题，检查是否挤掉了主关键词。

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| `--title` | 字符串 | 文章标题原文 |
| `--content` | 路径或文本 | 正文全文，两者皆可 |
| `--platform` | `csdn`（默认）/`juejin`/`wechat`/`baijiahao`/`toutiao` | 决定标题长度规则 |
| `--output` | JSON 文件路径 | 缺省打印 stdout |

## SEO Score Factors

| Factor | Weight | Check |
|--------|--------|-------|
| Title has keyword | 20 | Primary keyword in title |
| Title length | 10 | Within platform limit |
| Meta description | 15 | 80-160 chars, has keyword |
| Keyword density | 15 | 1-3% (not stuffed) |
| Heading structure | 10 | H1 > H2 > H3 hierarchy |
| Word count | 10 | > 800 words |
| Internal links | 10 | At least 1 |
| Readability | 10 | Short paragraphs, lists |

## Platform Title Limits

| Platform | Max Title | Max Tags | Caption Style |
|----------|----------|----------|---------------|
| CSDN | 50 chars | 5 | 关键词 + 数字 |
| 掘金 | 60 chars | 3 | 【标题】 |
| 微信 | 30 chars | 0 | 短 + 悬念 |
| 百家号 | 30 chars | 3 | 数字 + 痛点 |
| 头条 | 30 chars | 3 | 数字 + 疑问 |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|-------------|------|------|
| `ModuleNotFoundError` / `python3: command not found` | Python 未安装或不在 PATH | 安装 Python 3.8+ 后重跑前置自检 |
| `FileNotFoundError` | `--content` 文件路径错误 | 改用绝对路径；或直接把正文文本传给 `--content` |
| `unrecognized arguments` | 参数名拼写错误 | 对照"参数速查表"，只使用表中列出的 4 个参数 |
| 输出 JSON 中 `score` 为 50 且 `keywords` 为空 | 正文太短或全为无实义词 | 补充正文（> 800 词）后重跑 |
| `tags` 为空但正文正常 | 词频分析未命中 | 在输入中人工指定 `target_keywords`，或接受空标签人工补齐 |

## 交付标准

- **成功定义**：产出一份 JSON（优化后标题 + meta description + tags/keywords + score），且复评 score ≥ 首次 score。
- **产物命名**：`seo_result.json`（步骤 1 的 `--output` 默认名；已存在时加平台后缀如 `seo_result_csdn.json`）。
- **保存位置**：当前工作目录（与被优化的文章同目录）。
- **完整性验证**：`python3 -m json.tool seo_result.json` 退出码 0，且含 `title`、`meta`、`meta.score` 三个字段。

## 参考

- [references/keyword-research.md](references/keyword-research.md) — 步骤 2/3 中主关键词选不出或想换更优关键词时读：关键词选择方法。
- [references/platform-rules.md](references/platform-rules.md) — 步骤 3 按平台截取标签、适配标题前读：各平台 SEO 细则。
