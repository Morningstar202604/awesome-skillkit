# paper 域 SOTA 加强 before/after 基准（2026-09-21）

> 标杆块：按 `docs/SKILL-SOTA-STRENGTHENING.md` 模板，对 paper 域 3 个最高杠杆技能做内容深度加强。
> 度量口径：SKILL.md 行数、脚本行数、引入的 SOTA 工具、方法学缺口消除、测试强度。

## 量化对照

| 技能 | SKILL.md (前→后) | 脚本行数 (前→后) | 关键方法学缺口 | 加强后 SOTA 工具 |
|------|------------------|------------------|----------------|-----------------|
| experiment-runner | 96 → 108 | ~91 → 318 | 「显著」= 均值超阈值（假 t-test） | scipy Welch t-test（p/Cohen's d/95%CI）+ 多后端 seed + env 指纹 + mlflow 钩子（缺 scipy 时纯 stdlib 回退） |
| lit-review | 95 → 99 | ~172 → 313 | 顺序连接引用图 + 硬编码趋势/空白 | Semantic Scholar 真实引用/被引 + 共同引用图（co-cited）+ LLM/关键词共现合成 + 诚实来源标注 |
| pub-plotter | 99 → 108 | ~195 → 205 | 手拍 figsize、无字体嵌入、非色盲安全色板 | 真实期刊物理宽度（Nature/Science/IEEE/ACM）+ `pdf.fonttype=42` 字体嵌入 + 色盲安全色板 + 可选官方 scienceplots |

## 诚实性 / 可复核性增强（核心改进）

- **experiment-runner**：`stats` 现在含 `test/method/statistic/p_value/alpha/effect_size_cohens_d/ci95_diff/significant`。
  显著性 = `p_value < 0.05`，不再用阈值冒充；`method` 如实标 `scipy`/`stdlib-fallback`；`seed_backends`/`env` 支撑复现。
- **lit-review**：`data_source` ∈ {s2, arxiv, mock}，任何回退写进 `warning`；`citation_graph.method` 说明边类型可信度；`retrieval_date` 支撑「存 DOI 不存查询」复现。
- **pub-plotter**：`--data` 不存在时报错退出（不再静默用演示数据）；`font_embedded`/`colorblind_safe`/`width_inches` 写入产物，可核验。

## 测试强度升级（弱冒烟 → 手搓强测试）

| 技能 | 前 | 后 |
|------|----|----|
| experiment-runner | `test_smoke_all.py`（import + `--help`） | `test_smoke_experiment_runner.py` 6 断言（Welch 字段、显著/不显著、模拟模式、seed 确定性、CLI） |
| lit-review | `test_smoke_all.py` | `test_smoke_lit_review.py` 5 断言（mock 诚实标注、co-cited 图、网络回退、关键词合成、CLI） |
| pub-plotter | `test_smoke_all.py` | `test_smoke_pub_plotter.py` 5 断言（真实期刊宽度、nature 预设、字体嵌入 PDF、色盲默认、CLI） |

三个强测试合计 **16 passed**；全库 `run_skill_smoke.py` 复跑 **121/121 pass（offline=0、dep=0、0 警告）**，门禁未退化。

## 遗留项（非阻塞）

- paper 域其余 10 技能（tex-cleaner / latex-formatter / neural-net-draw / self-reviewer / journal-adapt / ai-humanizer / anti-defensive / paper-topic-selector / arch-diagram / 等）仍为第一代方法学，按本模板逐域推广。
- lit-review 的 Semantic Scholar 真实调用需网络；CI 走 mock，已诚实标注。
- experiment-runner 的 scipy 为可选依赖；无 scipy 时走 stdlib 回退（p 值正态近似，小样本略保守，已如实标注）。

---

## 第二批 before/after（2026-09-21，本提交）

按同一模板续推 paper 域第二批 3 技能：neural-net-draw / latex-formatter / self-reviewer。

### 量化

| 技能 | SKILL.md | 脚本 | 测试 | 引入的 SOTA 能力 |
|------|---------|------|------|------------------|
| neural-net-draw | 1.0→2.0（102行） | 206行（前 ~106） | 7 断言 | PlotNeuralNet 层类型（conv/pool/residual/linear/attention）typed-blocks + per-neuron 兼容；层高封顶 3cm；未知类型硬报错 |
| latex-formatter | 1.0→2.0（102行） | 174行（前 ~104） | 8 断言 | 按名环境配对（Counter，非粗计数）；跨文件 undefined `\cite`（`--refs`）；可选 chktex 真实 lint；method 诚实标注（stdlib-fallback/external-lint） |
| self-reviewer | 1.0→2.0（101行） | 199行（前 ~130） | 7 断言 | ML 可复现性 rubric（p值/CI、ablation、baselines、seeds/code/data）；每项带可复核 evidence；LLM 证据双轨（`--llm-evidence`）+ 关键词回退；ready 必须 uncertain 为空 |

### 测试强度升级

三个弱 `test_smoke_all.py` 升级为 22 断言手搓强测试（7+8+7），全绿；全库 `run_skill_smoke.py` 复跑 **121/121 pass（offline=0、dep=0、0 警告）**，门禁未退化。

### 经验
- 「内容加强」的第三批已证明可复用：审计四轴定位缺口 → 挑最高杠杆技能 → 脚本 SOTA 化（留离线回退 + 诚实 method/source）→ SKILL.md 1.0→2.0 → 弱测试换强测试（断言 SOTA 行为本身）→ 全库门禁复跑。
- neural-net-draw 暴露的通用坑：f-string 内嵌 TikZ 花括号必须转义/提变量；逐神经元层高需封顶，否则大层失控。
- latex-formatter / self-reviewer 证明「外部工具可选 + 离线兜底 + 诚实 method 标注」是脚本可移植性的核心范式。

### 遗留项更新（非阻塞）
- paper 域剩余未加强技能：tex-cleaner / journal-adapt / ai-humanizer / anti-defensive / paper-topic-selector / arch-diagram。
- 第三批（本次 3 技能）均离线可复现，无新增网络/外部依赖门禁风险。

---

## 第三批 before/after（2026-09-21，收尾：paper 域 13/13 全覆盖）

按同一模板收尾 paper 域最后 6 个技能：tex-cleaner / journal-adapt / ai-humanizer / anti-defensive / paper-topic-selector / arch-diagram。

### 量化

| 技能 | SKILL.md | 脚本 | 测试 | 引入的 SOTA 能力 |
|------|---------|------|------|------------------|
| tex-cleaner | 1.0→2.0（109行） | 243行（前 ~125） | 8 断言 | 注释剥离改为**转义 + verbatim 感知**（旧版只认行首 `%`，漏掉全部行尾注释）；未用宏包改**命令→宏包映射**（旧版硬编码 3 条）；新增**资源清单** `assets{groups,missing}`（`\input`/`\bibliography`/`\includegraphics` 存在性）；`--clean` 缺 `--output` 改为 rc=1（旧版静默无操作） |
| journal-adapt | 1.0→2.0（107行） | 216行（前 ~95） | 12 断言 | 页数从 `words/500` 一刀切 → **分栏感知模型**（NeurIPS 1 栏 600 词/页 vs IEEE/ACM 2 栏 950–1000）+ **参考文献页扣减**（venue 是否计 refs，按 `\bibitem` 45 条/页）+ 摘要字数上限 + venue 必填章节（含 NeurIPS/ACL 的 Limitations）+ 引用风格 + **双盲匿名检查** + venue 别名 + `--template-year` |
| ai-humanizer | 1.0→2.0（104行） | 234行（前 ~124） | 9 断言 | 纯词表 → 叠加**结构层**：句长 burstiness、句首重复（连续 ≥3 同开头）、TTR 词汇多样性、重复 5-gram；全部命中带 `line:col`；新增 `llm_verb_spam`（delve/leverage/pivotal…）；固化的**诚实声明**（检测器不可靠、不得用于指控） |
| anti-defensive | 1.0→2.0（104行） | 178行（前 ~98） | 9 断言 | 从「所有限定都扣分」→ **retain/tighten 分类器**：命中落在统计不确定语境（CI/p 值/方差/样本量/分布漂移）附近时标 `retain` 且**不扣分**（删掉它是学术错误）；新增**对冲密度**（每百词）；命中定位 |
| paper-topic-selector | 1.0→2.0（136行） | 239行（前 ~69） | 10 断言 | 单题关键词打分 → **多候选排序**（`--topic` 可重复 + `--candidates`）配 SKILL.md 的四因子权重 40/30/20/10；**真实可行性模型** `1 - workload_weeks/deadline_weeks`（工期单位解析 + 复杂度词 + from-scratch 惩罚 + 少卡折扣）；**诚实 novelty 来源**（`novelty_source: heuristic-keyword` 默认未查新；给了 `--lit-review-json` 且 gap 命中才升 `lit-review` + `novelty_verified=true`）；输出 `ranked_topics[]` + `rejected[]`（带 reason） |
| arch-diagram | 1.0→2.0（106行） | 244行（前 ~139） | 11 断言 | 修两个**编译/渲染硬伤**：`\sffootnotesize`（非法 LaTeX 命令）→ `\footnotesize`；SVG `url(#arrow)` 无 marker 定义 → 补 `<defs><marker>`（旧版箭头根本不显示）；新增布局 `row/wrap/stack` + `--per-row`；色盲安全配色（与 pub-plotter 同源）；标签自动 **LaTeX + XML 转义** |

### 测试强度升级

6 个弱 `test_smoke_all.py` 升级为 **59 断言**手搓强测试（8+12+9+9+10+11），全绿；全库 `run_skill_smoke.py` 复跑 **121/121 pass（offline=0、dep=0、0 警告）**，门禁未退化。

### 经验（第三批新增）
- 修「老脚本」最高杠杆的往往不是加功能，而是**修正错误断言/无效语法**：`\sffootnotesize` 与未定义 SVG marker 都是「跑得通、编译/渲染必炸」的隐性硬伤。
- 「所有 X 都是坏事」的单向规则（anti-defensive 的限定语）必须加**语境分类器**，否则会把统计上必须保留的限定删成裸断言——这是学术错误而非风格问题。
- 涉及伦理的检测类工具（ai-humanizer）必须在**输出结构里**固化免责声明（`detector_note`），而不是只写在 SKILL.md。
- 估算类指标（页数、工作量）应把**中间量暴露出来**（`workload_weeks`/`deadline_weeks`/`ref_pages`）供人工复核，而不是只给一个最终分。

### 遗留项（收尾后）
- **paper 域 13 个技能已全部 SOTA 化**（3+3+3+3 共四批，含 figure-maker 合并入 pub-plotter）。
- paper 域剩余可选项：给 `figure-maker` 是否仍独立存在做一次去重审计（与 pub-plotter 职责重叠）。
- 横向推广：writing / programming / meta 等域尚未开始，`docs/SKILL-SOTA-STRENGTHENING.md` 可直接复用。

---

## 第五批：figure-maker ↔ pub-plotter 去重审计（2026-09-21）

收尾时挂起的**去重审计**结论与执行记录。

### 审计结论：pub-plotter 是 figure-maker 的严格超集

| 维度 | figure-maker (v1) | pub-plotter | 判定 |
|------|-------------------|-------------|------|
| `line`/`bar`/`boxplot` | 自实现，手拍 figsize，无字体嵌入 | ✅ 同款数据 JSON | 重叠 |
| `heatmap` | **永远返回 `status:"unsupported"`**（宣传了但从未实现） | ✅ 真实渲染（cividis / RdBu_r） | pub-plotter 胜 |
| 期刊真实物理宽度 | ❌ | ✅ `JOURNAL_WIDTHS`（Nature 89mm / Science 4.76" …） | pub-plotter 胜 |
| 字体嵌入 | ❌ | ✅ `pdf.fonttype=42`（arXiv/LaTeX 可收录） | pub-plotter 胜 |
| 色盲安全色板 | ❌ | ✅ Okabe-Ito 默认开 | pub-plotter 胜 |
| `--data` 路径不存在 | **静默用演示数据** | rc=2 报错 | pub-plotter 胜 |

→ 保留两个实现毫无价值，但**直接删会打断消费者**。选择**去重实现 + 保留弃用薄壳**。

### 顺带挖出并修掉的真 bug（静默错误）

| # | 症状 | 根因 | 修法 |
|---|------|------|------|
| 1 | `--journal nature_single` **悄悄回退 IEEE 3.5" 宽度**却报 success | 旧代码 `style = args.journal if args.journal in STYLES else "ieee"`——把「宽度指令」当成「风格名」查表，`nature_single`/`science` 不在 `STYLES` 里 → 静默吃默认值 | `setup_style(style, colorblind, journal)`：**style 管字号/线宽/网格，journal 只管物理宽度**，二者分离；未知 journal → rc=2；四种图型统一回报 `width_inches` |
| 2 | `--style science` 是合法选项却无 `STYLES` 条目 → 静默套 ieee 几何 | 同 #1 的同一类静默回退 | 补 `STYLES["science"] = {figure_width: 4.76, …}`；`--style` 选项集改为 `sorted(set(STYLES) + ["science"])` |
| 3 | 薄壳遇非法数据（heatmap 非二维阵）抛 traceback | 只 catch `ImportError` | 补 `except ValueError` → 干净 JSON + rc=2 |

**关键教训**：这三处都属于「跑得通、返回 0、但结果悄悄不对」的静默错误——正是「121/121 冒烟全绿」也测不出来的那一类。后续所有 SOTA 化都要专门针对**静默回退**：

> 凡「用户给了参数 A，代码静默用了默认值 B」都算缺陷，必须(a)要么真生效，(b)要么硬报错，并在输出里**回报实际生效值**供核对。

修 #1 时还差点被假绿测试骗过：早期断言用 `3.504 == 3.5` 这类比较，而 nature_single(3.504) 与 ieee(3.5) 数值极近，**媒体盒几乎一样宽**（245.9pt vs 246.1pt），无法证伪。最终用**差异显著的** `science(4.76) vs ieee(3.5)` + 直接读 PDF `/MediaBox` 做端到端铁证（实测 316.2pt vs 245.9pt，比值 1.29）。

### 量化

| 项目 | 变化 |
|------|------|
| `pub-plotter` 脚本 | 175 → 245 行（新增 `plot_heatmap` 真实实现、journal/style 职责分离、四型统一 `width_inches`、未知值 rc=2） |
| `figure-maker` 脚本 | ~139 行自实现 → 100 行**薄壳**（保留 CLI/JSON 契约，委托 pub-plotter，输出 `deprecated:true` / `superseded_by`） |
| 两技能测试 | 弱 `test_smoke_all.py`(figure-maker) + 现有 → **27 条强断言**（pub-plotter 14 + figure-maker 13），全绿 |
| `paper_pipeline.py` | figures 阶段 `figure-maker` → **pub-plotter + `--journal ieee`**（实测 6/6 步 success，产物含 `font_embedded:true`、不再带 `deprecated`） |
| 复数实现的 `line`/`bar`/`boxplot` 代码 | 2 份 → **1 份** |

### 端到端验证（不只跑测试）

```text
journal=None           -> reported 3.5  in | PDF MediaBox  245.9pt
journal=nature_single  -> reported 3.504in | PDF MediaBox  246.1pt
journal=science        -> reported 4.76 in | PDF MediaBox  316.2pt   ← 铁证
journal=acm            -> reported 6.5  in | PDF MediaBox  413.3pt
journal=neurips        -> reported 6.0  in | PDF MediaBox  385.4pt
style=science          -> reported 4.76 in | PDF MediaBox  315.2pt   ← 修 #2 后生效
paper_pipeline --topic X --json -> 6/6 步 success，figures 步 width_inches=3.5 font_embedded=true
```

### 为什么不去掉 figure-maker

仓库内**代码**消费者已迁移，但名字仍被 `manifest.json`、`packs/ai-research-writing/pack.json`、`skills/skill_chains.json`、生成站点 `site/` 引用；且本仓库面向使用者分发，外部可能已固定其 CLI。**弃用薄壳是行业标准做法**（保契约 + 暴露弃用 + 去掉重复实现）；删除留到下一轮大版本，与上述索引一起协同改动。SKILL.md 已如实写清这一状态与删除条件。

### 遗留项
- `figure-maker` 可删除，但需同步 `manifest.json` / packs / `skill_chains.json` + 重建 `site/`（下一轮大版本）。
- 横向推广 writing / programming / meta 域仍待启动。
