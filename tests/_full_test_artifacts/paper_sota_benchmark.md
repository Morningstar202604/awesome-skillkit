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
