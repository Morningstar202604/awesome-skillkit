# 效能对照报告 — video/storyboard-designer

- 旧版来源：`HEAD` ｜ 新版来源：工作区 SKILL.md
- 判定法：二元 rubric 清单 + 成对盲评（顺序互换，不一致记平局）
- 诚实边界：单一评委模型、与生成方同家族（自偏好偏差）、样本量小 —— 方向性信号，非统计结论
- 长度混淆：新版在 1/3 个样本上更长（中位 3799 vs 3885 字符）——评委指令禁止按篇幅加分，但该混淆不可完全排除

| 任务 | 最终裁决 | old/new/tie/invalid |
|---|---|---|
| product-ad-16x9 | **new** | 0/1/0/0 |
| vertical-15s-twist | **new** | 0/1/0/0 |
| script-to-board-consistency | **tie** | 0/0/1/0 |

**汇总：新版胜 2 ｜ 旧版胜 0 ｜ 平局 1 ｜ 无效 0**

结论：新版在多数任务上占优（方向性证据支持改写有效）。

## 明细
### 任务 product-ad-16x9
- sample 1: verdict=**new** (换序 ['new', 'new']) ｜ gate old=OK / new=OK ｜ chars=[3799, 3626]
### 任务 vertical-15s-twist
- sample 1: verdict=**new** (换序 ['new', 'new']) ｜ gate old=OK / new=OK ｜ chars=[4020, 3991]
### 任务 script-to-board-consistency
- sample 1: verdict=**tie** (换序 ['old', 'new']) ｜ gate old=OK / new=OK ｜ chars=[3650, 3885]