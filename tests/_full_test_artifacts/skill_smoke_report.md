# 第二代 · 真实技能冒烟测试全量报告

> 生成时间：2026-09-20 16:52:44 UTC
> 口径：**直接运行真实技能自带的 `test_smoke_*.py`**（pytest），取代第一代手搓代理 task。
> 这是真正意义上的「技能质量门禁」——测的是仓库里 117 个真实技能中 ship 了冒烟测试的 28 个。

## 总览
- 真实技能目录总数（skills/ 下）：117
- 带可执行脚本的技能：56（其中 ship 冒烟测试的：28）
- 本轮跑冒烟测试的技能数：**28**
- 判定分布：**pass=28 / fail=0**
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
| `design\layout-spec-auditor` | pass | 8 | 0 | 0 | 0 | — |
| `education\exercise-generator` | pass | 5 | 0 | 0 | 0 | — |
| `marketing\channel-adapter` | pass | 6 | 0 | 0 | 0 | — |
| `meta\skill-finder` | pass | 8 | 0 | 0 | 0 | — |
| `meta\skill-linter` | pass | 6 | 0 | 0 | 0 | — |
| `paper\paper-topic-selector` | pass | 1 | 0 | 0 | 0 | — |
| `programming\data` | pass | 1 | 0 | 0 | 0 | — |
| `programming\data` | pass | 1 | 0 | 0 | 0 | — |
| `programming\debug` | pass | 1 | 0 | 0 | 0 | — |
| `programming\math` | pass | 1 | 0 | 0 | 0 | — |
| `programming\math` | pass | 1 | 0 | 0 | 0 | — |
| `programming\math` | pass | 1 | 0 | 0 | 0 | — |
| `programming\math` | pass | 1 | 0 | 0 | 0 | — |
| `programming\ml` | pass | 1 | 0 | 0 | 0 | — |
| `video\storyboard-designer` | pass | 1 | 0 | 0 | 0 | — |
| `video\video-editor` | pass | 1 | 0 | 0 | 0 | — |
| `video\video-lip-sync` | pass | 1 | 0 | 0 | 0 | — |
| `video\video-prompt-engineer` | pass | 3 | 0 | 0 | 0 | — |
| `video\video-script-writer` | pass | 1 | 0 | 0 | 0 | — |
| `video\video-subtitles` | pass | 1 | 0 | 0 | 0 | — |
| `video\video-thumbnail` | pass | 1 | 0 | 0 | 0 | — |
| `video\video-voice-synth` | pass | 1 | 0 | 0 | 0 | — |
| `writing\article-drafter` | pass | 1 | 0 | 0 | 0 | — |
| `writing\article-outliner` | pass | 1 | 0 | 0 | 0 | — |
| `writing\content-editor` | pass | 1 | 0 | 0 | 0 | — |
| `writing\seo-optimizer` | pass | 1 | 0 | 0 | 0 | — |

## 失败明细（供修复排期）

- （无失败）

## 改进清单（对应自审 P0/P1）
- P0：未 ship 冒烟测试的 28 个脚本化技能，补 `test_smoke_*.py`（复用本驱动器）。
- P0：失败中「缺失依赖」类 → 补进 CI 依赖清单（如 scikit-learn 已补）。
- P1：失败中「需网络/API」类 → 为生成式/外部调用技能加离线兜底（model_route 模式），使其离线可冒烟。
- P2：61 个纯 prompt 型技能（无脚本）→ 设计 LLM 沙箱冒烟（需网关恢复）。