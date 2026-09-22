# 效能对照报告 — design/image-prompt-engineer

- 旧版来源：`HEAD` ｜ 新版来源：工作区 SKILL.md
- 判定法：二元 rubric 清单 + 成对盲评（顺序互换，不一致记平局）
- 诚实边界：单一评委模型、与生成方同家族（自偏好偏差）、样本量小 —— 方向性信号，非统计结论

| 任务 | 最终裁决 | old/new/tie/invalid |
|---|---|---|
| write-photo-hero | **new** | 0/1/0/0 |
| audit-bad-prompt | **new** | 0/1/0/0 |
| poster-with-text | **tie** | 0/0/1/0 |

**汇总：新版胜 2 ｜ 旧版胜 0 ｜ 平局 1 ｜ 无效 0**

结论：新版在多数任务上占优（方向性证据支持改写有效）。

## 明细
### 任务 write-photo-hero
- sample 1: verdict=**new** (换序 ['new', 'new']) ｜ gate old=OK / new=OK ｜ chars=[1463, 1709]
### 任务 audit-bad-prompt
- sample 1: verdict=**new** (换序 ['new', 'new']) ｜ gate old=OK / new=OK ｜ chars=[2821, 3951]
### 任务 poster-with-text
- sample 1: verdict=**tie** (换序 ['old', 'new']) ｜ gate old=OK / new=OK ｜ chars=[1443, 3467]