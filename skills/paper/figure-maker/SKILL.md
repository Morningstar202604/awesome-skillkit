---
name: figure-maker
description: "DEPRECATED — use `pub-plotter` instead. This skill is kept only as a compatibility shim: it preserves the original CLI (--data / --type bar|line|boxplot|heatmap / --output) and delegates to pub-plotter, adding `deprecated: true` / `superseded_by: \"pub-plotter\"` to its output. Kept for repo indexes (manifest/packs/skill_chains) and external callers that pinned the old CLI; the in-repo consumer (`paper_pipeline.py`) has already migrated to pub-plotter. Use when the user asks 画实验结果图 / 论文图表 / results plot / 把实验数据画成图 / 画柱状图 — but prefer pub-plotter for anything new (it adds real journal widths, font embedding, and full heatmap support). Do NOT use for neural-network structure diagrams (use neural-net-draw) or architecture diagrams (use arch-diagram)."
license: Apache-2.0
compatibility: DEPRECATED. Requires matplotlib (only indirectly, via pub-plotter). Delegates to `../pub-plotter/scripts/pub_plotter.py`.
metadata:
  version: "3.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: deprecated
  verified-date: "2026-09-21"
  superseded-by: pub-plotter
---

# Figure Maker (DEPRECATED → pub-plotter)

> **本技能已弃用**。它与 `pub-plotter` 职责完全重叠，而 `pub-plotter` 是严格超集：
> 同样支持 `line`/`bar`/`boxplot`（+ 本技能从未真正实现的 `heatmap`），并额外提供
> **期刊真实物理宽度、Type-42 字体嵌入、色盲安全色板、scienceplots 集成**。
>
> 现在 `figure_maker.py` 的正文实现已删除，改为**薄壳委托**：CLI 与 JSON 契约不变，
> 内部调用 `pub-plotter`，并在输出里打上 `deprecated: true` / `superseded_by: "pub-plotter"`。

## 为什么保留而不是直接删

**仓库内消费者已迁移**：paper 域编排器 `paper_pipeline.py` 的 figures 阶段原先指向本技能（这是当初不删的唯一硬理由），现已改为直接调用 `pub-plotter`（`--journal ieee`）。所以保留薄壳的原因变成：

1. **目录内兼容**：仓库根 `manifest.json`、`packs` 下 ai-research-writing 的 `pack.json`、`skill_chains.json` 与生成站点 `site/` 仍按名字引用本技能；直接删会打断这些索引，需要一次协同改动。
2. **外部已固定 CLI 的调用方**：本仓库是面向使用者的技能集，可能已有人把 `figure_maker.py --type ... --data ...` 写进脚本；薄壳让他们不炸。

薄壳 = 去掉重复实现 + 不破坏既有消费者 + 输出里显式暴露弃用状态。**下一轮大版本可直接删除**（届时同步 `manifest.json` / packs / `skill_chains.json` 并重建 `site/`）。

## 迁移方式（推荐）

把调用改指向 pub-plotter：

```bash
# 旧（仍可用，但有弃用开销与少一层转发）
python3 scripts/figure_maker.py --type bar --data results.json --output fig.pdf

# 新（推荐）
python3 ../pub-plotter/scripts/pub_plotter.py --type bar --journal ieee --data results.json --output fig.pdf
```

## 行为契约（与 v1 的差异）

| 项目 | v1 | 现在（薄壳） |
|------|----|--------------|
| `line`/`bar`/`boxplot` | 自实现、手拍 figsize、无字体嵌入 | 委托 pub-plotter → 期刊宽度 + 字体嵌入 + 色盲安全 |
| `heatmap` | **永远是 `status:"unsupported"`**（从未实现） | **真实渲染**（委托 pub-plotter，cividis / RdBu_r） |
| 输出 JSON 额外字段 | — | `deprecated: true`、`superseded_by`、`deprecation_note` |
| `--data` 路径不存在 | 静默用演示数据 | **报错退出（rc=2）** |
| 退出码 | 恒 0 | 0 成功；2 参数/数据问题；1 委托目标缺失 |
| 新增透传参数 | — | `--journal`、`--no-colorblind` |

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 数据 JSON | 建议 | `--data results.json`；不存在则 rc=2 |
| 图型 | 否 | `--type bar\|line\|boxplot\|heatmap`（默认 `bar`，保持 v1 默认） |
| 期刊版面 | 否 | `--journal nature_single\|science\|ieee\|acm\|neurips`（透传） |
| 色板 | 否 | 默认色盲安全；`--no-colorblind` 关闭（透传） |
| 输出路径 | 否 | `--output fig.pdf`；缺省由 pub-plotter 决定 |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------------|------|------|
| rc=1，`delegation target missing` | `../pub-plotter/scripts/pub_plotter.py` 不存在 | 本仓库不完整；改用 pub-plotter 路径或恢复目录结构 |
| rc=2，`--data 文件不存在` | 数据路径错 | 先 `test -f` 修路径（v1 会静默用演示数据，别依赖该行为） |
| rc=2，`未知 --journal` | 版面名不在 `JOURNAL_WIDTHS` | 用 `nature_single`/`science`/`ieee`/`acm`/`neurips` |
| `status:"mock"` | matplotlib 未安装 | `pip install matplotlib` 后重跑 |

## 交付标准

成功定义：`status:"success"` + `rendered:true`，且 `output` 文件存在非空。
产物命名：由 `--output` 决定。
验证方法：`python3 -c "import json;d=json.load(open('<out>'));assert d['deprecated'] is True"` 能确认走的是弃用薄壳。
**新代码请直接交付 pub-plotter**，不要新增对本技能的依赖。

## 参考

本技能无自有绘图实现；全部行为委托 `../pub-plotter/scripts/pub_plotter.py`（`JOURNAL_WIDTHS` / `STYLES` / `setup_style` / `plot_*`）。

## 链路位置

兼容占位。paper 域绘图正典为 **pub-plotter**，且 `paper_pipeline.py` 的 figures 阶段**已经**迁到 pub-plotter；本技能当前只服务仓库内索引（manifest/packs/skill_chains/site）与外部已固定 CLI 的调用方，可在下一轮大版本随索引一起删除。
