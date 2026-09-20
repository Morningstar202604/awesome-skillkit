# 第二代 · 真实技能冒烟测试全量报告

> 生成时间：2026-09-20 17:59:20 UTC
> 口径：**直接运行真实技能自带的 `test_smoke_*.py`**（pytest），取代第一代手搓代理 task。
> 这是真正意义上的「技能质量门禁」——测的是仓库里 117 个真实技能中 ship 了冒烟测试的 28 个。

## 总览
- 真实技能目录总数（skills/ 下）：117
- 带可执行脚本的技能：56（其中 ship 冒烟测试的：121）
- 本轮跑冒烟测试的技能数：**121**
- 判定分布：**pass=121 / fail=0**
- 失败分类：需网络/API（离线不可测）=0，缺失依赖=0，其它=0

## 与第一代测试的关系（重要纠正）
- 第一代 `full_skill_test.py`：20 个**合成技能名**的代理实现 → 19 pass/1 warn。**它不测真实技能。**
- 第二代 `run_skill_smoke.py`：28 个**真实技能自带冒烟测试** → 见上。这才是技能包质量的真指标。
- 结论：第一代的高 pass 率有「自嗨」成分；第二代才是硬指标。两者互补：第一代验证「交付物可生成」，第二代验证「技能脚本真能跑」。

## 逐技能结果

| 技能 | 判定 | passed | failed | error | skipped | 失败原因 |
|---|---|---|---|---|---|---|
| `audio\podcast-producer` | pass | 5 | 0 | 0 | 0 | — |
| `chat\chat-prompt-engineer` | pass | 6 | 0 | 0 | 0 | — |
| `dataviz\dashboard-designer` | pass | 2 | 0 | 0 | 0 | — |
| `design\frontend-component-lab` | pass | 2 | 0 | 0 | 0 | — |
| `design\layout-spec-auditor` | pass | 8 | 0 | 0 | 0 | — |
| `education\exercise-generator` | pass | 5 | 0 | 0 | 0 | — |
| `integrations\cloud-drive-manager` | pass | 2 | 0 | 0 | 0 | — |
| `integrations\feishu-dingtalk-bridge` | pass | 2 | 0 | 0 | 0 | — |
| `integrations\issue-tracker-sync` | pass | 2 | 0 | 0 | 0 | — |
| `integrations\notion-workspace` | pass | 2 | 0 | 0 | 0 | — |
| `knowledge\knowledge-graph-builder` | pass | 2 | 0 | 0 | 0 | — |
| `knowledge\personal-wiki` | pass | 2 | 0 | 0 | 0 | — |
| `marketing\channel-adapter` | pass | 6 | 0 | 0 | 0 | — |
| `meta\agent-eval-harness` | pass | 2 | 0 | 0 | 0 | — |
| `meta\session-handoff` | pass | 2 | 0 | 0 | 0 | — |
| `meta\skill-finder` | pass | 8 | 0 | 0 | 0 | — |
| `meta\skill-linter` | pass | 6 | 0 | 0 | 0 | — |
| `meta\weekly-report-generator` | pass | 2 | 0 | 0 | 0 | — |
| `office\career-ops-lite` | pass | 2 | 0 | 0 | 0 | — |
| `office\docx-template-fill` | pass | 2 | 0 | 0 | 0 | — |
| `office\docx-writer` | pass | 2 | 0 | 0 | 0 | — |
| `office\epub-builder` | pass | 2 | 0 | 0 | 0 | — |
| `office\pdf-pipeline` | pass | 2 | 0 | 0 | 0 | — |
| `paper\ai-humanizer` | pass | 2 | 0 | 0 | 0 | — |
| `paper\anti-defensive` | pass | 2 | 0 | 0 | 0 | — |
| `paper\arch-diagram` | pass | 2 | 0 | 0 | 0 | — |
| `paper\experiment-runner` | pass | 6 | 0 | 0 | 0 | — |
| `paper\figure-maker` | pass | 2 | 0 | 0 | 0 | — |
| `paper\journal-adapt` | pass | 2 | 0 | 0 | 0 | — |
| `paper\latex-formatter` | pass | 2 | 0 | 0 | 0 | — |
| `paper\lit-review` | pass | 5 | 0 | 0 | 0 | — |
| `paper\neural-net-draw` | pass | 2 | 0 | 0 | 0 | — |
| `paper\paper-topic-selector` | pass | 1 | 0 | 0 | 0 | — |
| `paper\pub-plotter` | pass | 5 | 0 | 0 | 0 | — |
| `paper\self-reviewer` | pass | 2 | 0 | 0 | 0 | — |
| `paper\tex-cleaner` | pass | 2 | 0 | 0 | 0 | — |
| `ppt\ppt-builder` | pass | 2 | 0 | 0 | 0 | — |
| `programming\ai-engineering` | pass | 2 | 0 | 0 | 0 | — |
| `programming\ai-engineering` | pass | 2 | 0 | 0 | 0 | — |
| `programming\ai-engineering` | pass | 2 | 0 | 0 | 0 | — |
| `programming\ai-engineering` | pass | 2 | 0 | 0 | 0 | — |
| `programming\api` | pass | 2 | 0 | 0 | 0 | — |
| `programming\architecture` | pass | 2 | 0 | 0 | 0 | — |
| `programming\architecture` | pass | 2 | 0 | 0 | 0 | — |
| `programming\architecture` | pass | 2 | 0 | 0 | 0 | — |
| `programming\cicd` | pass | 2 | 0 | 0 | 0 | — |
| `programming\cicd` | pass | 2 | 0 | 0 | 0 | — |
| `programming\cicd` | pass | 2 | 0 | 0 | 0 | — |
| `programming\code-quality` | pass | 2 | 0 | 0 | 0 | — |
| `programming\code-quality` | pass | 2 | 0 | 0 | 0 | — |
| `programming\code-quality` | pass | 2 | 0 | 0 | 0 | — |
| `programming\code-quality` | pass | 2 | 0 | 0 | 0 | — |
| `programming\containers` | pass | 2 | 0 | 0 | 0 | — |
| `programming\containers` | pass | 2 | 0 | 0 | 0 | — |
| `programming\data` | pass | 1 | 0 | 0 | 0 | — |
| `programming\data` | pass | 1 | 0 | 0 | 0 | — |
| `programming\database` | pass | 2 | 0 | 0 | 0 | — |
| `programming\database` | pass | 2 | 0 | 0 | 0 | — |
| `programming\debug` | pass | 1 | 0 | 0 | 0 | — |
| `programming\github` | pass | 2 | 0 | 0 | 0 | — |
| `programming\github` | pass | 2 | 0 | 0 | 0 | — |
| `programming\incident` | pass | 2 | 0 | 0 | 0 | — |
| `programming\incident` | pass | 2 | 0 | 0 | 0 | — |
| `programming\incident` | pass | 2 | 0 | 0 | 0 | — |
| `programming\infrastructure` | pass | 2 | 0 | 0 | 0 | — |
| `programming\infrastructure` | pass | 2 | 0 | 0 | 0 | — |
| `programming\infrastructure` | pass | 2 | 0 | 0 | 0 | — |
| `programming\math` | pass | 1 | 0 | 0 | 0 | — |
| `programming\math` | pass | 1 | 0 | 0 | 0 | — |
| `programming\math` | pass | 1 | 0 | 0 | 0 | — |
| `programming\math` | pass | 1 | 0 | 0 | 0 | — |
| `programming\ml` | pass | 1 | 0 | 0 | 0 | — |
| `programming\performance` | pass | 2 | 0 | 0 | 0 | — |
| `programming\planning` | pass | 2 | 0 | 0 | 0 | — |
| `programming\planning` | pass | 2 | 0 | 0 | 0 | — |
| `programming\planning` | pass | 2 | 0 | 0 | 0 | — |
| `programming\planning` | pass | 2 | 0 | 0 | 0 | — |
| `programming\security` | pass | 2 | 0 | 0 | 0 | — |
| `programming\security` | pass | 2 | 0 | 0 | 0 | — |
| `programming\security` | pass | 2 | 0 | 0 | 0 | — |
| `programming\security` | pass | 2 | 0 | 0 | 0 | — |
| `programming\testing` | pass | 2 | 0 | 0 | 0 | — |
| `programming\testing` | pass | 2 | 0 | 0 | 0 | — |
| `programming\workflow` | pass | 2 | 0 | 0 | 0 | — |
| `tools\bank-statement-reconcile` | pass | 2 | 0 | 0 | 0 | — |
| `tools\batch-renamer` | pass | 2 | 0 | 0 | 0 | — |
| `tools\file-organizer` | pass | 2 | 0 | 0 | 0 | — |
| `tools\format-converter` | pass | 2 | 0 | 0 | 0 | — |
| `tools\invoice-organizer` | pass | 2 | 0 | 0 | 0 | — |
| `tools\task-scheduler` | pass | 2 | 0 | 0 | 0 | — |
| `video\storyboard-designer` | pass | 1 | 0 | 0 | 0 | — |
| `video\video-editor` | pass | 1 | 0 | 0 | 0 | — |
| `video\video-lip-sync` | pass | 1 | 0 | 0 | 0 | — |
| `video\video-prompt-engineer` | pass | 3 | 0 | 0 | 0 | — |
| `video\video-script-writer` | pass | 1 | 0 | 0 | 0 | — |
| `video\video-subtitles` | pass | 1 | 0 | 0 | 0 | — |
| `video\video-thumbnail` | pass | 1 | 0 | 0 | 0 | — |
| `video\video-voice-synth` | pass | 1 | 0 | 0 | 0 | — |
| `writing\ai-trace-auditor` | pass | 2 | 0 | 0 | 0 | — |
| `writing\article-drafter` | pass | 1 | 0 | 0 | 0 | — |
| `writing\article-outliner` | pass | 1 | 0 | 0 | 0 | — |
| `writing\assets` | pass | 2 | 0 | 0 | 0 | — |
| `writing\blog` | pass | 2 | 0 | 0 | 0 | — |
| `writing\blog` | pass | 2 | 0 | 0 | 0 | — |
| `writing\blog` | pass | 2 | 0 | 0 | 0 | — |
| `writing\blog` | pass | 2 | 0 | 0 | 0 | — |
| `writing\community` | pass | 2 | 0 | 0 | 0 | — |
| `writing\community` | pass | 2 | 0 | 0 | 0 | — |
| `writing\community` | pass | 2 | 0 | 0 | 0 | — |
| `writing\community` | pass | 2 | 0 | 0 | 0 | — |
| `writing\content-editor` | pass | 1 | 0 | 0 | 0 | — |
| `writing\juejin` | pass | 2 | 0 | 0 | 0 | — |
| `writing\news` | pass | 2 | 0 | 0 | 0 | — |
| `writing\news` | pass | 2 | 0 | 0 | 0 | — |
| `writing\orchestrator` | pass | 2 | 0 | 0 | 0 | — |
| `writing\seo-optimizer` | pass | 1 | 0 | 0 | 0 | — |
| `writing\social` | pass | 2 | 0 | 0 | 0 | — |
| `writing\social` | pass | 2 | 0 | 0 | 0 | — |
| `writing\video` | pass | 2 | 0 | 0 | 0 | — |
| `writing\wechat` | pass | 2 | 0 | 0 | 0 | — |
| `writing\zhihu` | pass | 2 | 0 | 0 | 0 | — |

## 失败明细（供修复排期）

- （无失败）

## 改进清单（对应自审 P0/P1）
- P0：未 ship 冒烟测试的 28 个脚本化技能，补 `test_smoke_*.py`（复用本驱动器）。
- P0：失败中「缺失依赖」类 → 补进 CI 依赖清单（如 scikit-learn 已补）。
- P1：失败中「需网络/API」类 → 为生成式/外部调用技能加离线兜底（model_route 模式），使其离线可冒烟。
- P2：61 个纯 prompt 型技能（无脚本）→ 设计 LLM 沙箱冒烟（需网关恢复）。