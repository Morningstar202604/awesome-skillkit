---
name: humanize-rewriter
description: "Rewrite AI-flavored text into natural human writing: inject burstiness (long-short sentence rhythm), upgrade abstractions to concrete details, add first-person reaction and controlled imperfection, while freezing all facts, numbers, terms and conclusions. Use when the user asks to 去AI味 / 人性化改写 / 改得像人写的 / 降AI率重写 / humanize this text / make it sound human / rewrite the AI draft. Do NOT use for legal, medical or academic-submission texts, and never invent facts the source does not contain."
license: Apache-2.0
compatibility: Needs Python 3.8+ (stdlib only) for the baseline/rescan step via the ai-trace-auditor bundle scanner; if unavailable, degrade to its manual checklist and mark the report manual_mode.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: writing
  pattern: workflow
  tier: powerful
  verified-date: "2026-09-16"
---

# Humanize Rewriter（人性化重写）

AI 代笔的文字工整但冷冰冰。本技能把它的表达层拆掉重装——节奏、具体性、情绪、适度的不完美——信息层一根手指都不碰。每一步可验证：改写前有基线分，改写后必须显著下降。

## 输入清单

| 输入 | 必需 | 说明 |
|---|---|---|
| 待改写文本 | 是 | AI 生成的初稿或 AI 味明显的成稿；太短（<100 字）没有重写空间 |
| voice profile | 否 | personal-voice-profile 产出的 voice-profile.json；缺省时用通用人味策略并声明 |
| 改写强度 | 否 | 轻度去痕（只消体检命中项）/ 深度人格化（默认）；用户没说就按深度 |
| 保护清单 | 否 | 用户点名不可动的表述；与红线 1 的默认冻结项合并执行 |

缺必填项时，只问一次：

> 请提供：① 待改写的文本全文；② 可选——你的 voice profile 文件（没有就用通用策略）、改写强度（轻度去痕 / 深度人格化）、有特别不能动的句子吗？

## 前置自检

需要探测一项环境：复检依赖 ai-trace-auditor 技能目录内的 trace_scanner.py（纯标准库脚本，随该技能 bundle 交付）。

```bash
python3 --version && python3 <ai-trace-auditor目录>/scripts/trace_scanner.py --help 2>/dev/null; echo "check=$?"
```

脚本能跑 → 走标准流程；不能跑（无 python3 / 脚本缺失）→ 全程用人工清单（见步骤 1 若失败），交付时标注 `manual_mode: true`。输入侧自检：文本拿到了吗？低于 100 字 → 如实告知改写空间不足，不建议开工。改写强度未声明 → 按深度人格化执行并在首条回复中说明，不等用户第二轮确认。

## 红线（硬性禁令，不可协商）

1. 不改事实与结论：数字、术语、引用、论断、因果关系全部冻结——本技能只动表达层。禁改项在改写前先提取成清单，交付时逐条核对。
2. 不加原文没有的信息：尤其数字。"从 3 小时压到 40 分钟"这种具体性升维，只能来自原文已有事实或向用户确认，绝不凭空造一个。
3. 正式法律、医疗、学术提交文本不适用本技能：这类文本的措辞即合规边界，表达层的"人味"会引入风险；只可建议用户人工润色。
4. 不承诺绕过任何平台或机构的 AI 检测：本技能提升可读性与真实感，改写结果与任何检测系统的结论无关——被问到时明确说明。

## 工作流

### 步骤 1：体检基线

- **动作：** 先用 ai-trace-auditor 的扫描器拿基线分（脚本在该技能目录内，先 cd 过去或写全路径）：

```bash
python3 scripts/trace_scanner.py 待改写文本.md     # 脚本在 ai-trace-auditor 技能目录内
                                                   # 也支持 cat 文本 | python3 scripts/trace_scanner.py -
```

- **预期：** 输出 `{stats, findings[]}` JSON、退出码 0；记录基线 score 与 findings 清单——这是后面每一步的靶子。
- **若失败：** python3 不可用 → 改用人工三查（词表逐词过 / 目测句长是否均匀 / 数列表行占比），把命中项手工记成对照清单，报告标注 manual_mode；用户直接粘贴的文本未落盘 → 先存临时文件再扫，或直接走 stdin——脚本支持 `-` 参数读取标准输入（用法见步骤 1 代码块注释）。

### 步骤 2：锁定禁改清单

- **动作：** 从原文提取四类冻结项：全部数字与单位、专有名词与术语、直接引语、结论句。逐条编号列出。
- **预期：** 禁改清单完整可核对；有歧义的表述（如"约 30%"算不算可动）当面向用户确认一次。清单样例：

```text
禁改清单 #1 数字与单位：3 小时 / 40 分钟 / 12 人 / 2026 年 Q2
禁改清单 #2 术语与专名：Kubernetes、HPBX 协议、A/B 测试
禁改清单 #3 直接引语："用户告诉我们，加载慢一秒就走人。"
禁改清单 #4 结论句：所以缓存层必须保留，砍掉它就是砍掉首屏体验。
```

- **若失败：** 用户补充了保护清单 → 合并进本清单；提取不出来（全文皆结论）→ 告知本技能只宜做轻度去痕。

### 步骤 3：加载 voice profile

- **动作：** 有 voice-profile.json → 读出四层参数（lexical 口头禅与高频动词、syntactic 句长与段落习惯、tonal 语气与称呼、structural 开头结尾套路），改写时向其对齐；没有 → 用通用策略，并告知用户"先跑 personal-voice-profile 会更像你本人"。
- **预期：** 改写基调确定——后续每段都问一句"这样写像不像 profile 里那个人"。对齐读法示例：

```text
profile.syntactic.median_sentence_len = 22  → 改写稿句长中位数控制在 20-25
profile.tonal.habit = "爱用反问收段"        → 每段结尾最多一个反问，宁缺勿滥
```

- **若失败：** profile 文件损坏或字段缺失 → 缺哪层补哪层的通用默认，不整个弃用。

### 步骤 4：逐段重写

- **动作：** 逐段执行"保信息、换表达、注情绪"，四个手法按优先级使用：
  - **burstiness 注入：** 连续两个长句后接一个 ≤8 字短句；把一个 60 字长句拆成一个 40 字句加一个 12 字句。目标 cv ≥ 0.5（与体检阈值对齐）。
  - **具体性升维：** 抽象概括换成具体名词、数字、场景——"效率显著提升"→"同样一批稿件，从 3 小时压到 40 分钟"（数字必须来自原文或用户确认，见红线 2）。
  - **情绪注入：** 加第一人称反应、犹豫、吐槽——"说实话我一开始也不信"，一个就够，不堆砌。
  - **不完美允许：** 口语插入语、破折号岔路、偶尔的反问；允许一处不算华丽的表达保留原样。
- 同时对照步骤 1 的 findings 逐条消痕：ai_word 命中换具体表达，parallelism 拆句，enumerator_chain 改小标题或直接展开，list_density 把非并列列表揉回段落。
- 手法优先级：先消 findings 命中项（可验证），再上四手法（可感知）——只做后者体检分会骗人，只做前者读者会觉得没改。
- **预期：** 每段改完能在原文与改写稿之间逐句对应；禁改清单项零变化。改写前后对照示例：

```text
原文：综上所述，缓存优化显著提升了系统性能，不仅降低了延迟，而且提高了吞吐量。
改后：缓存这一刀下去，接口延迟从 800ms 掉到 90ms，吞吐也跟着上来了——数字不会说谎。
手法：删"综上所述/不仅…而且"（体检 L3 命中）→ burstiness：长句后补一个短句收尾
      → "800ms→90ms"为原文已有事实（红线 2：数字未新增）
```

- **若失败：** 某段怎么改都干瘪 → 保留原样并注明"该段信息密度高，未强行注入"，不硬造情绪。

### 步骤 5：复检

- **动作：** 对改写稿再跑一次步骤 1 的扫描命令，参数与基线一致。
- **预期：** score 相比基线下降 ≥20 分（经验值，可调），且 cv 升到 0.5 以上；若加载了 voice profile，句长与段落形态应与 profile 的 syntactic 层接近。对比记录样例：

```text
基线：score 34，heavy_ai_style，ai_word_hits=13，cv=0.38
复检：score 71，light_ai_traces，ai_word_hits=2， cv=0.61
结论：降幅 37 ≥ 20，达标；残余 2 处命中在对照表中给出处理说明
```

- **若失败：** 分数不降反升 → 多半是把长句全改成了等长短句，回步骤 4 重做长短句交错；只差一点 → 只针对残余 findings 做点状修补，不整篇重写。

### 步骤 6：交付

- **动作：** 输出两件产物：① 改写稿全文；② 修改对照表，每条 `原文 → 改后 ← 手法/依据`，附基线分与复检分对比、禁改清单核对结果。
- **预期：** 用户能逐条接受或拒绝每处改动；边界声明随交付走（红线 4）。
- **若失败：** 对照表与改写稿对不上 → 以改写稿为准重算对照表，禁止交付两张皮。

## 产出规格

| 产物 | 结构 | 说明 |
|---|---|---|
| 改写稿 | 连贯正文 | 与原文逐段对应；禁改项逐字未动 |
| 修改对照表 | 每条：原文 / 改后 / 手法 / 依据 | 依据指向体检 findings 的 pos 或 voice profile 字段 |
| 复检结果 | `{score, verdict, findings[]}` | 与 ai-trace-auditor 报告同构；基线分与复检分并列展示 |

## 失败处置表

| 现象 | 原因 | 处置 |
|---|---|---|
| 复检分不降反升 | 短句堆成新的均匀节奏 | 回步骤 4 重做长短句交错；验证 cv |
| 禁改内容被改动 | 重写时手滑 | 对照禁改清单逐条回滚，重跑复检 |
| 用户要求补细节编数字 | 触碰红线 2 | 拒绝；提示插入 `<待你确认：具体数值>` 占位 |
| 改完像另一个人写的 | 没加载 profile 或强度过大 | 退回轻度去痕：只消 findings 命中项，不做情绪注入 |
| 全文都是结论没得改 | 信息层与表达层不可分 | 如实说明本技能适配性差，建议重写而非改写 |
| 改写稿超长/缩水超过 20% | 情绪注入或删减失控 | 以原文长度为锚回调，偏差计入对照表说明 |
| 情绪句与全文气质打架 | 强度选错或 profile 缺失 | 逐句回滚违和的注入句，保留结构层改动 |
| 破折号/省略号用得比原文多一倍 | "不完美允许"被当成了标点堆料 | 修辞标点回撤到每段最多一处；对照表记录回撤项 |
| 用户拿来的是合同/病历等正式文本 | 触碰红线 3 | 拒绝改写并说明理由；只提供人工润色的方向性建议 |

## 交付标准

- 复检 score 相比基线下降 ≥20（经验值，可调），禁改清单逐条核对零改动。
- 修改对照表完整：每处改动可追溯手法与依据，无未记录的改动。
- 改写稿不含原文没有的数字与事实；含一句检测边界声明。
- 改写稿可直接交 content-editor 或发布技能接手：无未确认的占位符残留（`<待你确认：…>` 必须已在步骤 4 向用户问明或保留为显式占位）。
- 用户读完改写稿能说出"这句像我"或指出"这句不像"——后者进下一轮点状修补。

## 参考

- `references/sources-and-methodology.md` —— 需要说明 burstiness 与具体性原则的来源、四手法的依据、如何对外署名时读。

## 链路位置

- 上游：ai-trace-auditor（体检报告是本技能的靶子清单）；personal-voice-profile（voice profile 让"人味"对齐到具体的人）。
- 下游：content-editor（终稿润色）、各平台发布技能（wechat-mp-publisher、zhihu-content-manager、juejin-publisher 等）。
- 平行：own-voice-rewrite（education 域学生作文的克制的版本；写作域通用场景用本技能）。
