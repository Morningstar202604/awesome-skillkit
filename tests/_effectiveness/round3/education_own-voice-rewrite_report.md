# 效能对照报告 — education/own-voice-rewrite

- 旧版来源：`HEAD` ｜ 新版来源：工作区 SKILL.md
- 判定法：二元 rubric 清单 + 成对盲评（顺序互换，不一致记平局）
- 诚实边界：单一评委模型、与生成方同家族（自偏好偏差）、样本量小 —— 方向性信号，非统计结论
- 长度混淆：新版在 3/3 个样本上更长（中位 702 vs 1287 字符）——评委指令禁止按篇幅加分，但该混淆不可完全排除

| 任务 | 最终裁决 | old/new/tie/invalid |
|---|---|---|
| junior-high-downgrade | **tie** | 0/0/1/0 |
| voice-profile-match | **new** | 0/1/0/0 |
| edge-florid-style | **new** | 0/1/0/0 |

**汇总：新版胜 2 ｜ 旧版胜 0 ｜ 平局 1 ｜ 无效 0**

结论：新版在多数任务上占优（方向性证据支持改写有效）。

## 明细
### 任务 junior-high-downgrade
- sample 1: verdict=**tie** (换序 ['old', 'new']) ｜ gate old=OK / new=OK ｜ chars=[1171, 1287]
### 任务 voice-profile-match
- sample 1: verdict=**new** (换序 ['new', 'new']) ｜ gate old=OK / new=OK ｜ chars=[702, 1477]
### 任务 edge-florid-style
- sample 1: verdict=**new** (换序 ['new', 'new']) ｜ gate old=OK / new=OK ｜ chars=[278, 389]