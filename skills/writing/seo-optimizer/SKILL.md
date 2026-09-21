---
name: seo-optimizer
description: "Optimize article for search: extract keywords, generate meta tags, score SEO quality, and adapt titles/captions per platform. Use after editing, before publishing to specific platforms. Use when the user asks to 做 SEO 优化 / 选关键词 / 优化标题 / 检查关键词密度 / 生成 meta 描述 / optimize SEO / extract keywords / SEO score / meta description / platform title limits. Do NOT use for paid advertising strategy, ad bidding, or writing the article itself."
license: Apache-2.0
compatibility: Pure Python analysis. No API keys required.
metadata:
  version: "2.0"
  author: awesome-skillkit
  category: writing
  pattern: single-task
  tier: sota
  verified-date: "2026-09-21"
---

# SEO 优化器：评估文章 SEO 就绪度并按平台适配标题与 meta

## 按任务选路径

| 你要做什么 | 直接去 | 关键动作 |
|---|---|---|
| 给已写完的文章出标题 + meta | 步骤 1-4 | 跑脚本 → 按平台文化改标题 → 复评 |
| 判断这篇文章能不能被搜到 | 先读「搜索意图匹配」再跑脚本 | 对齐搜索意图，别先调关键词 |
| 标题改了反而流量更差 | 先读「平台标题文化」 | 检查是否踩了平台限流红线 |
| 关键词选不出来 | [references/keyword-research.md](references/keyword-research.md) | 人工指定 `target_keywords` |

## 领域暗知识（跑脚本前先建立判断）

### 1. 关键词密度是过时迷信，位置一致性才是现代 SEO

关键词密度 1-3% 这类规则来自 2010 年代的 TF-IDF 时代。百度 2019 年上 BERT、Google 更早——
**搜索引擎现在判断的是"这篇回答了什么搜索意图"，不是"这个词出现了几次"**。堆砌密度反而触发
垃圾内容判定（百度飓风算法打击的就是采集与关键词堆砌）。

现代 SEO 真正起作用的三处位置一致性：

| 位置 | 为什么 | 怎么做 |
|---|---|---|
| 标题 | 搜索结果点击率的第一因素，点击率反过来影响排名 | 主关键词放在标题**前半段**（截断安全区） |
| 首段前 100 字 | 搜索摘要直接截取这段；读者 3 秒决定去留 | 主关键词自然出现一次 + 直接回答标题承诺 |
| 至少一个 H2 | 长文的锚点跳转和精选摘要（featured snippet）来源 | 用读者会搜的问句形式写 H2（"为什么…" / "如何…"） |

本脚本的密度检查（权重 15）**保留但降权使用**：它的真实作用是抓"一个关键词都没有"的极端漏题，
不是把 1.8% 调到 2.2%。

### 2. 搜索意图三型，标题句式跟着意图走

| 意图 | 用户在搜什么 | 标题句式 | 反例 |
|---|---|---|---|
| 信息型 | "怎么做 / 为什么 / 是什么" | 疑问句或 How-to：「为什么你的 Redis 总是超时」 | ❌「Redis 超时问题的研究」 |
| 对比型 | "A vs B / 哪个好 / 值不值" | 明确给出比较双方+立场：「SQLite vs PostgreSQL：小项目到底选哪个」 | ❌「两种数据库介绍」 |
| 解决型 | "报错 / 优化 / 修复 + 具体症状" | 症状前置+结果前置：「从 200ms 到 30ms：FastAPI 接口优化实录」 | ❌「FastAPI 性能分析」 |

跑脚本前先判断文章属于哪型——**标题句式与意图错配，是"关键词都对了但没流量"的第一原因**。

### 3. 平台标题文化（同一个标题在五个平台是五种命运）

| 平台 | 流量来源 | 标题文化 | 红线（踩了限流/扣分） |
|---|---|---|---|
| CSDN | 站内搜索 + SEO 引流 | 技术关键词前置 + 具体数字；搜索用户扫的是技术栈词 | 标题党判定（"惊！""必看"）降曝光；标签与内容无关会被举报 |
| 掘金 | 编辑推荐 + 关注流 | 口语化、场景化、"我"视角；【】修饰前缀有辨识度但别滥用 | 纯营销外链文会被下沉 |
| 微信公众号 | 社交转发 | 情绪 + 悬念 + 身份标签（"做后端的都懂"）；30 字内必须完成钩子 | **标题党明文打击**：「震惊/必看/99% 的人不知道」这类词触发限流；诱导分享（"不转不是"）直接处罚 |
| 百家号 | 百度搜索 + 信息流 | 数字 + 痛点，审核极严 | 极限词、医疗/财经夸大表述直接不过审；标题与正文不符扣信用分 |
| 头条 | 信息流推荐，完读率导向 | 疑问句 + 数字效果好；标题承诺正文必须兑现，否则完读率崩 → 推荐腰斩 | 「标题党」机器审核：标题含正文没有的概念即判 |

**通用红线词表**（各平台共通打击）：震惊、必看、秒懂、99% 的人、惊呆了、不转不是、
刚刚传出、内部消息。脚本抓不到这些——**这 8 个词出现任何一个，手动改标题**。

### 4. 诚实声明：这个分数是什么、不是什么

`score` 是**自检启发式**，用途是把 20 篇草稿排序、找出漏做的基础项。
它**不是**搜索引擎的真实排名预测——真实排名由站点权重、外链、用户行为信号决定，任何本地
脚本都无法计算。不要对用户说"score 85 = 能排前三"；要说"基础项 8/9 已就位，缺 X"。

## 工作流

### 前置自检

```bash
python3 --version                                   # 预期 >= 3.8
test -f scripts/seo_optimizer.py && echo OK         # 预期 OK；失败 → cd 到技能目录
python3 scripts/seo_optimizer.py --title "smoke" --content "smoke content" | head -c 20
# 预期：以 { 开头的 JSON；失败 → 见失败处置表
```

### 步骤 1：判断搜索意图 + 跑基线

先按「搜索意图三型」判断文章类型（这决定步骤 2 的标题句式），再跑：

```bash
python3 scripts/seo_optimizer.py \
  --title "FastAPI 性能优化" \
  --content article.md \
  --platform csdn \
  --output seo_result.json
```

预期：退出码 0，JSON 含 `title`（`issues`/`suggestions`）与 `meta`（`meta_description`/`tags`/`keywords`/`score`）。

### 步骤 2：按平台文化重写标题（人工环节，脚本只提建议）

按「平台标题文化」表 + 搜索意图句式改写，硬约束三条：主关键词在前半段、长度 ≤ 平台上限、
数字或对比至少其一。**红线词表逐词过一遍**——脚本抓不到标题党词，这是人工闸门。

### 步骤 3：meta description 与标签

- meta description：80-160 字符（搜索结果约 155 字符截断），主关键词出现一次会被搜索结果加亮；
  写"用户点进来能看到什么"，不写口号。
- 标签：`meta.tags` 去重后按平台上限截取（CSDN ≤5、掘金 ≤3）；**标签必须是正文真实覆盖的主题**，
  挂热门无关标签是举报高发区。

### 步骤 4：复评 + 真实验证

1. 优化后的标题重跑脚本，`score` 不降（降了 = 挤掉了主关键词，回滚）。
2. **真实验证（脚本测不出的部分）**：把最终标题放到目标平台的搜索框里搜一遍主关键词，
   对比现有前三名——你的标题有没有提供它们都没有的角度？没有的话，流量不会来，改角度而不是改字。

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| `--title` | 字符串 | 文章标题原文 |
| `--content` | 路径或文本 | 正文全文，两者皆可 |
| `--platform` | `csdn`（默认）/`juejin`/`wechat`/`baijiahao`/`toutiao` | 决定标题长度规则 |
| `--output` | JSON 文件路径 | 缺省打印 stdout |

## 评分因子（含权重理由）

| 因子 | 权重 | 理由 |
|------|------|------|
| 标题含关键词 | 20 | 搜索结果点击率第一因素 |
| Meta description | 15 | 摘要截取区，影响点击不直接影响排名 |
| 关键词密度 | 15 | 只用于抓"零关键词"极端漏题（见暗知识 1） |
| 标题长度 | 10 | 平台截断保护 |
| 标题结构 | 10 | H1>H2>H3 层级 = H2 锚点与精选摘要资格 |
| 正文字数 | 10 | <800 词难以完整回答一个意图 |
| 内部链接 | 10 | 站内权重流动 |
| 可读性 | 10 | 短段落影响完读，完读影响推荐 |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|-------------|------|------|
| `ModuleNotFoundError` / `python3: command not found` | Python 未装或不在 PATH | 安装 Python 3.8+ 后重跑前置自检 |
| `FileNotFoundError` | `--content` 路径错误 | 改绝对路径；或直接把正文文本传给 `--content` |
| `unrecognized arguments` | 参数名拼错 | 只用速查表里 4 个参数 |
| `score` 恒 50 且 `keywords` 空 | 正文太短或全为无实义词 | 补正文 >800 词后重跑 |
| `tags` 为空但正文正常 | 词频未命中 | 人工传 `target_keywords`，或接受空标签手动补 |

## 交付标准

- 产物：`seo_result.json`（优化后标题 + meta + tags + score），`python3 -m json.tool` 校验通过。
- 完整性：最终标题过红线词表、意图句式匹配、平台长度合规三项全绿。

## 参考

- [references/keyword-research.md](references/keyword-research.md) — 主关键词选不出或想换更优关键词时的选词方法
- [references/platform-rules.md](references/platform-rules.md) — 各平台 SEO 细则（标签上限、审核尺度）
