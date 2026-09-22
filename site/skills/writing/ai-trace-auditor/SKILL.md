---
name: ai-trace-auditor
description: "Audit a text for AI-writing fingerprints: scan built-in Chinese/English AI高频词 lists, measure sentence-length variance (std/mean), list/parallelism density and structural cliches, then report a 0-100 score with per-finding locations as machine-parseable JSON. Use when the user asks to 检测AI味 / AI痕迹检测 / 查一下这段像不像AI写的 / 体检AI率 / audit AI traces / detect AI writing / scan for AI style / de-AI check. Do NOT use as an official AI detector for academic-integrity arbitration — heuristic self-check only."
license: Apache-2.0
compatibility: Needs Python 3.8+ (stdlib only) for scripts/trace_scanner.py; if Python is unavailable, degrade to the manual checklist and mark the report manual_mode.
metadata:
  version: "2.0"
  author: awesome-skillkit
  category: writing
  pattern: single-task
  tier: standard
  verified-date: "2026-09-21"
---

# AI Trace Auditor（AI 痕迹体检）

AI 味不是玄学，它有可测量、可定位的特征。本技能对文本做一次"体检"：跑词表、算句长方差、数列表密度，产出 0-100 分与逐条 findings——只诊断，不动刀，改写交给下游 humanize-rewriter。

## 适用决策表（先判断，再体检）

| 你的目的 | 用不用本技能 | 预期效用 |
|---|---|---|
| 发布/交付前，自查"这稿 AI 味重不重" | 用 | findings 逐条定位，可直接转 humanize-rewriter 消痕 |
| 内部 review，比较两版稿子的机器腔程度 | 用 | 同一文本分数可横向对比（确定性脚本） |
| 追问"这是不是 AI 写的"（作者归因） | **别用** | 本技能测风格特征，测不出作者身份（暗知识 1） |
| 学术诚信仲裁 / 要"官方 AI 率" | **拒绝** | 启发式自检无任何官方效力（红线 2） |
| 文本少于 3 句 / 大量代码表格 | 降级用 | cv 不可判定，只有词表命中可用 |

## 领域暗知识（体检前必须懂的四件事）

**1. 商业检测器测什么，词表法只是"土法近似"。** 主流商业检测器的底层是两类信号：困惑度（perplexity，模型对文本的"惊讶度"——AI 文本太可预测所以偏低）和爆发度（burstiness，句长节奏的波动——人类忽长忽短，AI 均匀工整）。本技能的词表 + cv + list_ratio 是这两个信号的手工近似：**测的是风格与 AI 产出的相似性，不是 AI 的作者身份**。score 90 的套路文可能是人写的，score 30 的模仿机器腔可能是人改的——体检结论永远是"像不像 AI 的风格"，不是"是不是 AI 写的"。

**2. 假阳性有明确的高发人群，比假阴性更需要警惕。** 三类人写的原文极易被统计特征误伤：非母语写作者（教学环境的固定句式天然"均匀"）、公文/法律/医学等程式化文体（人类规范本来就要求工整）、刻意模仿"高级感"的初学者（堆排比恰是学来的修辞）。所以步骤 3 的语境复核不是可选项——**uniform ≠ AI，工整 ≠ 机器**。历史上最著名的翻车就是把非母语学生的作文误判为 AI 生成，这也是本技能坚持只做自检不做仲裁的原因。

**3. 假阴性来自改写与混合文本，词表测不到它们。** 逐句改写（paraphrase）可绕过任何词表；最常见且最难判的真实场景是"人写初稿 + AI 润色"的混合文本——它一段像人一段像机器，整篇分数取平均后落在"说不清"区间。遇到混合嫌疑（段落间风格断裂明显），逐段体检分段报告，比全文一个分数诚实得多。

**4. 词表是移动靶，会随模型版本漂移。** "综上所述""深入探讨"是上一代模型的高频套话，新一代模型的套话隔半年就换一批——今天没命中不代表干净。所以 score 的语义是"已知特征命中了多少"，不是"还有多少未知的 AI 味"。报告里给结论时永远带一句词表覆盖盲区的说明，不给"体检通过 = 无 AI 味"的暗示。

## 输入清单

| 输入 | 必需 | 说明 |
|---|---|---|
| 待体检文本 | 是 | 纯文本或 markdown 文件路径；不接受"我大概是这么写的"转述 |
| 用途声明 | 否 | 发布前自检 / 内部 review / 交付前抽检；涉及学术提交时必填，用于触发红线 2 提示 |

缺必填项时，只问一次：

> 请提供：待体检的文本全文（直接粘贴或给文件路径）。
> 可选：这份文本的用途（发布 / 内部 review / 学术提交）。

## 前置自检

本技能依赖内置扫描脚本，先探测再动手：

```bash
python3 --version                       # 预期打印 3.8+；失败 → 走手工降级
test -f scripts/trace_scanner.py && echo OK   # 预期打印 OK，否则脚本缺失 STOP
```

输入侧自检：文本拿到了吗？少于 3 个句子的文本无法计算句长方差——可以照常跑词表，但报告必须标注 `cv_evaluable: false`。用途声明缺失 → 按"发布前自检"处理并继续，不要为此追问第二轮。文本超过 2 万字 → 先按章节切成 3000 字左右的分段逐段体检，最后汇报各段分数与全文最低分段，不分段直接扫会让定位信息失真。

## 红线（硬性禁令，不可协商）

1. 本技能是启发式自检，不是官方 AI 检测器：报告必须附带一句边界声明——"分数基于词表与统计特征，命中不等于 AI 所写，未命中不等于人所写"（原理见暗知识 1）。
2. 不用于学术欺诈：不得向用户担保"AI 率已降为 0"、不得把体检报告当作原创性证明，更不得以此协助规避学校的学术诚信审查——被问到时明确拒绝并解释。对非母语写作者等假阳性高发人群（暗知识 2），主动提示误伤风险。
3. 只读不改：审计过程禁止顺手改文本；发现问题的修复属于下游 humanize-rewriter 的职责。
4. 体检在本机完成：不得把用户文本粘贴到任何在线检测网站——发布前的草稿常有未公开信息。
5. 分数不可单独外传：脱离 findings 的裸分数没有定位信息，禁止只报一个数字了事；也不得暗示"分数高 = 无 AI 味"（词表覆盖盲区，暗知识 4）。

## 工作流

### 步骤 1：运行扫描器

- **动作：** 对待体检文本执行（脚本随本技能 bundle 交付）：

```bash
python3 scripts/trace_scanner.py assets/sample-article.md        # 随包样例；或 cat 文本 | python3 scripts/trace_scanner.py -
```

- **预期：** stdout 输出单个 JSON 对象 `{stats, findings[]}`，退出码 0。stats 含 sentences、mean_sentence_len、std_sentence_len、cv、list_ratio、enumerator_count、ai_word_hits、score、verdict 十余字段；findings 每条含 pos/type/evidence/fix_hint 四字段。
- **若失败：** python3 缺失或脚本不可跑 → 降级为手工模式：打开 `scripts/trace_scanner.py` 里的 `AI_PATTERNS` 词表逐词核对、目测句长是否均匀、数列表行占比，报告整体标注 `manual_mode: true`，score 字段填 null 并说明原因。

### 步骤 2：解读 stats

- **动作：** 按三轴读数：句长方差比 cv（< 0.5 = 句长过均匀，机器腔核心特征）；列表密度 list_ratio（> 0.4 = PPT 腔）；综合分 score。
- **预期：** verdict 分段结论：

| score | verdict | 含义 |
|---|---|---|
| ≥ 80 | human_like | 统计特征在人类写作的正常区间 |
| 60–79 | light_ai_traces | 少量痕迹，微调即可 |
| 40–59 | obvious_ai_style | 明显机器腔，需系统性改写 |
| < 40 | heavy_ai_style | 重度模板腔，建议整篇重写 |

- **若失败：** sentences < 3 → cv 不可判定，只依据词表与结构项给结论，并在报告中写明数据不足。

解读示例：

```text
stats: sentences=18, cv=0.42 (<0.5 报警), list_ratio=0.55 (报警), ai_word_hits=13
→ 读法：句长过均匀 + 列表过密是结构层问题，词表命中是表层问题；
   按公式验算 100 - 13×6 - 20 - 15 = -13 → score 触底 0，verdict 必然 heavy_ai_style，
   这类文本直接建议整篇重写，逐词修补意义不大。
```

- **解读纪律：** cv 与 list_ratio 低分但词表零命中 → 先想暗知识 4（词表移动靶）而不是直接宣布"干净"；词表命中但 cv 达标 → 先想暗知识 2（程式化文体误伤）而不是直接定罪。

### 步骤 3：逐条核对 findings

- **动作：** 对每条 finding 做语境复核：ai_word 命中要看语境——"赋能"出现在互联网行业分析里可能是有意为之的行话；parallelism 与 enumerator_chain 命中基本可坐实；evidence 里的原文引用用于向用户定位。同时自查作者画像：作者若是非母语写作者或文体本属程式化（合同、公告、病历），uniform 类 finding 一律降级为"待议"。
- **预期：** 每条 finding 标注 保留（语境合理）/ 确认（真 AI 痕迹）/ 待议（两可）三态之一。复核示例：

```text
L3 ai_word "抓手"      → 确认（空泛黑话，无实指）
L7 ai_word "robust"   → 保留（技术语境下描述容错能力，属正常术语）
L9 parallelism        → 确认（三个分句同头，纯修辞填充）
```

- **若失败：** 某条 evidence 无法在原文中定位 → 以 pos 行号重新核对；仍定位不到则删除该条并说明。

### 步骤 4：脚本测不到的语义层检查

- **动作：** 人工补查四类：每段开头是否都是总结句（AI 的"总-分"强迫症）；是否滥用三点式罗列（刚好三条、长度相近）；结论是否空洞回环（说了一圈等于没说）；**段落间风格是否断裂**（一段人味十足一段机器工整——混合文本嫌疑，暗知识 3）。
- **预期：** 语义层问题以同样四字段结构追加进 findings，pos 填所在行号，type 用 `semantic_pattern`；发现风格断裂 → 建议逐段体检而不是只给全文分数。
- **若失败：** 文本过短无从判断结构 → 跳过本步并注明。

### 步骤 5：输出报告

- **动作：** 汇总为报告 JSON 并向用户陈述：

```json
{
  "score": 34,
  "verdict": "heavy_ai_style",
  "manual_mode": false,
  "disclaimer": "启发式自检，非官方检测器",
  "findings": [
    {"pos": "L3", "type": "ai_word", "evidence": "……综上所述，深入探讨……", "fix_hint": "总结改成一个具体结论"}
  ]
}
```

- **预期：** JSON 可被 `json.loads` 直接解析；score 与脚本输出一致（semantic_pattern 追加项不改 score，人工分项单独陈述）。
- **预期（陈述话术）：** 用三句话向用户收口——第一句给结论："score 34，heavy_ai_style，主要问题是词表命中 13 处 + 列表密度 67%"；第二句给去向："逐条 findings 已定位到行，可直接转 humanize-rewriter 按条消痕"；第三句给边界："本报告测的是风格特征与已知词表覆盖（暗知识 1/4），不是作者身份，也不是任何官方结论。"
- **若失败：** JSON 序列化失败 → 修复转义后重出，禁止交付半结构化文本。

## 参数速查表

| 字段/规则 | 取值 | 说明 |
|---|---|---|
| score | 0-100，越高越像人写 | 初始 100：每个 ai_word 命中 -6；cv<0.5 再 -20；list_ratio>0.4 再 -15；排比每处 -10；枚举链每处 -8（经验值，与脚本常量一致，可调） |
| verdict 分段 | 80/60/40 三条界 | human_like / light_ai_traces / obvious_ai_style / heavy_ai_style |
| cv 报警线 | 0.5 | 句长标准差/均值；经验值，可调 |
| list_ratio 报警线 | 0.4 | 列表行/非空行；经验值，可调 |
| findings[].type 枚举 | ai_word / uniform_sentence_length / parallelism / enumerator_chain / list_density / semantic_pattern | 前五类由脚本产出，semantic_pattern 仅人工步骤追加 |
| pos 格式 | L行号（如 L3） | 统计类发现（cv、列表密度）固定记 L1 |

## 失败处置表

| 现象 | 原因 | 处置 |
|---|---|---|
| python3 不可用 | 环境缺失 | 走手工降级清单，报告标注 manual_mode，score 置 null |
| 文本少于 3 句 | 样本太短 | 只出词表 findings，说明 cv 不可判定；建议合并全文再检 |
| 文本含大量代码/表格 | 词表误报（如注释里的 robust） | 先剥离代码块与表格再扫，剔除的命中在报告注明 |
| 非母语/公文文体被高分误伤 | 假阳性高发人群（暗知识 2） | uniform 类 finding 降级为待议；主动提示误伤风险 |
| 段落间风格断裂明显 | 混合文本（暗知识 3） | 改为逐段体检分段报告，不给单一全文分数定调 |
| 词表零命中但用户坚信是 AI 写的 | 词表覆盖有限（暗知识 4） | 承认盲区：语义层特征（步骤 4）与词表外的新型套话不在覆盖范围 |
| 用户要"官方 AI 率"截图 | 触碰红线 1/2 | 拒绝；重申启发式边界与作者归因不可行（暗知识 1） |
| score 直接为 0 | 重度模板腔 | 如实报告 verdict，直接建议转入 humanize-rewriter 重写而非逐词修补 |
| 同一文本两次跑分数不同 | 不应发生（脚本确定性） | 检查是否传入了不同文件/版本；确认后重跑 |
| 命中集中在引号内的人名/产品名 | 词表误伤专名 | 按步骤 3 标注保留；必要时建议用户加书名号或引号消歧 |
| 用户只关心"能不能过学校检测" | 触碰红线 2 | 明确回答：本报告与任何检测系统无关，不提供规避担保 |
| 文本为中英混排 | 句长按字符数统计，英文长句会抬高均值 | 正常扫描并照常解读；报告注明 cv 以字符为单位的口径局限 |
| 文本来自 OCR 或语音转写 | 断句缺失导致句子被并成长句 | 先人工修断句再扫；修不动就声明句子切分不可信，只看词表命中 |

## 交付标准

- 报告 JSON 可被 `json.loads` 解析；findings 每条含 pos/type/evidence/fix_hint 四字段。
- 每条 finding 可凭 pos 行号在原文定位；evidence 为原文片段。
- 报告含边界声明与（如适用）manual_mode 标注；score 与脚本输出一致。
- 语境复核完成：每条 finding 带三态标注，没有"无脑全改"的默认结论；假阳性高发人群已自查（暗知识 2）。
- 用户能拿着 findings 逐条决定"改 or 不改"，且明确知道 score 是风格相似度而非作者证据——这是体检的最终效用标准。

## 参考

- `references/sources-and-methodology.md` —— 需要说明 AI 高频词表出处、perplexity/burstiness 检测原理的来源、评分权重依据或对外署名时读。

## 链路位置

- 上游：任何写作成稿——article-drafter、ai-humanizer 产出的文本都在本技能的体检范围内。
- 下游：humanize-rewriter（接收本技能的 findings 逐条改写，改后回到本技能复检）。
- 平行：own-voice-rewrite（education 域的学生作文链路，其终稿复检同样调用本技能）。
