# 效能对照报告 — design/image-prompt-engineer

- 旧版来源：`HEAD` ｜ 新版来源：工作区 SKILL.md
- 判定法：二元 rubric 清单 + 成对盲评（顺序互换，不一致记平局）
- 诚实边界：单一评委模型、与生成方同家族（自偏好偏差）、样本量小 —— 方向性信号，非统计结论
- 长度混淆：新版在 2/3 个样本上更长（中位 1964 vs 1975 字符）——评委指令禁止按篇幅加分，但该混淆不可完全排除

| 任务 | 最终裁决 | old/new/tie/invalid |
|---|---|---|
| write-photo-hero | **new** | 0/1/0/0 |
| audit-bad-prompt | **new** | 0/1/0/0 |
| poster-with-text | **new** | 0/1/0/0 |

**汇总：新版胜 3 ｜ 旧版胜 0 ｜ 平局 0 ｜ 无效 0**

结论：新版在多数任务上占优（方向性证据支持改写有效）。

## 明细
### 任务 write-photo-hero
- sample 1: verdict=**new** (换序 ['new', 'new']) ｜ gate old=OK / new=OK ｜ chars=[2664, 836]
### 任务 audit-bad-prompt
- sample 1: verdict=**new** (换序 ['new', 'new']) ｜ gate old=OK / new=OK ｜ chars=[1964, 2795]
### 任务 poster-with-text
- sample 1: verdict=**new** (换序 ['new', 'new']) ｜ gate old=OK / new=OK ｜ chars=[426, 1975]