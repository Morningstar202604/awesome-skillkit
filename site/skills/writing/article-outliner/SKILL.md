---
name: article-outliner
description: "Create article outlines: structure, section hierarchy, key points, and reading flow. Supports blog posts, technical articles, news, and listicles. Use when the topic is defined but structure is needed before drafting. 当用户要求 搭文章大纲 / 列提纲 / 规划结构 / 帮我理一下文章框架 时使用。 Do NOT use for writing full prose (outline only — use article-drafter for that)."
license: Apache-2.0
compatibility: Pure prompt-based structuring; LLM may assist generation. Optional helper scripts/outliner.py requires Python 3.8+ (stdlib only). No API keys required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: writing
  pattern: single-task
  tier: standard
  verified-date: "2026-09-09"
---

# Article Outliner（在动笔前搭建文章结构）

主题已定、需要先行规划章节层级、关键要点与阅读流时，产出可交付的大纲对象。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| `topic` | 是 | 文章主题，如 `FastAPI 性能优化` |
| `type` | 否 | `technical` / `blog` / `news` / `listicle` / `opinion` / `tutorial`，默认 `technical` |
| `target_length` | 否 | `short(800)` / `medium(2000)` / `long(5000)`，默认 `medium` |
| `audience` | 否 | `beginner` / `intermediate` / `expert`，默认 `intermediate` |
| `key_points` | 否 | 要点列表，如 `["async","caching","DB indexing"]` |
| `platforms` | 否 | 目标平台，如 `["csdn","juejin","wechat"]` |

缺失时一次性问齐：「请提供：① 主题 topic；② 文章类型 type（technical/blog/news/listicle/opinion/tutorial）；③ 目标长度 target_length；④ 目标受众 audience；⑤ 关键要点 key_points（可空）。其余默认：type=technical、target_length=medium、audience=intermediate。」

## 前置自检

1. 校验脚本可用性（可选，确定性骨架）：
   ```bash
   python3 scripts/outliner.py --topic "FastAPI 性能优化" --type technical --output outline.json
   ```
   预期：退出码 `0`，生成 `outline.json` 含 `sections[]`。
   若失败：`需要 --topic 或 --json-input` → 补 `--topic` 后重跑。
2. 确认 `type` 取值在 `technical|blog|news|listicle|opinion|tutorial` 内；否则回退 `technical`。
3. 纯提示词模式可跳过第 1 步，直接进入工作流。

## 工作流

### 步骤 1：分析主题与受众

判定主题复杂度与受众层级（beginner/intermediate/expert）。
预期：明确 `audience` 与复杂度档位。
若失败：`audience` 不明 → 用 `intermediate` 并在交付时标注。

### 步骤 2：选择结构模式

按 `type` 选骨架（见「结构模式表」）：technical→problem-solution，listicle→list，tutorial→linear，news→inverted-pyramid，opinion→argumentative。
预期：选定一种 `pattern` 与对应章节数。

### 步骤 3：定义章节

大多数文章 3–7 个主章节，每节 `level:2`，编号 `id` 自增。
预期：`sections` 数组长度 ∈ [3,7]。

### 步骤 4：填充关键要点

每节 2–5 个 `points`；若提供了 `key_points`，按顺序分配到前 N 节。
预期：每节至少 1 个 `point`。

### 步骤 5：设定字数目标

`total_words_target` 由 `target_length` 映射（short=800/medium=2000/long=5000），`reading_time_min` = 总字数 / 250，并分摊到每节 `word_count_target`。
预期：各节 `word_count_target` 之和 ≈ `total_words_target`。

### 步骤 6：写 hook 与 CTA

`hook` 为开头 2 句抓注意力；`conclusion` 含总结 + 行动号召（关注/收藏/评论）。
预期：`hook` 与 `conclusion` 非空。

### 步骤 7：产出大纲对象

整合为完整 `outline` JSON（示例见下）。

## 输入输出示例

输入：
```json
{
  "topic": "FastAPI 性能优化",
  "type": "technical",
  "target_length": "medium",
  "audience": "intermediate",
  "key_points": ["async", "caching", "DB indexing"],
  "platforms": ["csdn", "juejin", "wechat"]
}
```

输出：
```json
{
  "title": "FastAPI 性能优化：从 200ms 到 30ms 的 5 个关键步骤",
  "hook": "你的 FastAPI 接口为什么慢？",
  "sections": [
    {"id": 1, "heading": "为什么你的 FastAPI 慢", "level": 2,
     "points": ["同步 I/O 阻塞事件循环", "N+1 查询", "缺少缓存"], "word_count_target": 300},
    {"id": 2, "heading": "5 个优化技巧", "level": 2,
     "points": [
       {"sub": "使用 async/await", "detail": "替换同步数据库调用"},
       {"sub": "Redis 缓存", "detail": "热点数据 5min TTL"},
       {"sub": "数据库索引", "detail": "EXPLAIN 分析慢查询"},
       {"sub": "连接池", "detail": "pgBouncer / SQLAlchemy pool"},
       {"sub": "批量查询", "detail": "IN 查询替代循环"}
     ], "word_count_target": 1200}
  ],
  "conclusion": "总结 + CTA (关注/收藏/评论)",
  "total_words_target": 2000,
  "reading_time_min": 8
}
```

## 结构模式表

| Pattern | Best For | Sections |
|---------|----------|----------|
| Problem → Solution | Technical articles | 3-5 |
| Listicle | Tips, tricks, resources | N items + intro + outro |
| Tutorial | How-to guides | Steps 1-N + prerequisites + result |
| News | Announcements, updates | What → Why → How → Impact |
| Opinion | Essays, commentary | Thesis → Arguments → Counter → Conclusion |

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| `--topic` | 字符串 | 文章主题，必需之一 |
| `--type` | technical/blog/news/listicle/opinion/tutorial | 默认 `technical` |
| `--length` | short/medium/long | 默认 `medium` |
| `--audience` | beginner/intermediate/expert | 默认 `intermediate` |
| `--points` | 多值 | 关键要点列表 |
| `--platforms` | 多值 | 目标平台 |
| `--json-input` | 文件路径 | 完整 JSON 输入（含 topic） |
| `--output` | 文件路径 | 写出大纲 JSON |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|-------------|------|------|
| `需要 --topic 或 --json-input` | 缺主题 | 补 `--topic` 或在 `--json-input` 提供 topic |
| `type` 取值非法 | 拼写错误 | 回退 `technical` 并提示 |
| 章节数 <3 或 >7 | 结构失衡 | 合并/拆分章节至 [3,7] |
| 各节字数之和偏离目标 | 分配不均 | 按总长度重分摊 `word_count_target` |

## 交付标准

- 成功定义：产出 `outline` 对象，含 `title`/`hook`/`sections[]`/`conclusion`/`total_words_target`。
- 产物命名：`outline.json`。
- 保存位置：用户指定目录，脚本用 `--output` 指定，默认标准输出。
- 完整性验证：`sections` 每项含 `id`/`heading`/`level`/`points`/`word_count_target`；`word_count_target` 之和 ≈ `total_words_target`；`reading_time_min` == 总字数/250。

## 参考

- `references/outline-templates.md` —— 各类型现成模板，步骤 2–3 时按需读取。
- `references/flow-guide.md` —— 阅读流与过渡句写法，步骤 6 写 hook/CTA 时读取。
