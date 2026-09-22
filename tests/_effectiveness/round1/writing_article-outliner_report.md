# 效能对照报告 — writing/article-outliner

- 旧版来源：`HEAD` ｜ 新版来源：工作区 SKILL.md
- 判定法：二元 rubric 清单 + 成对盲评（顺序互换，不一致记平局）
- 诚实边界：单一评委模型、与生成方同家族（自偏好偏差）、样本量小 —— 方向性信号，非统计结论

| 任务 | 最终裁决 | old/new/tie/invalid |
|---|---|---|
| tech-2000w | **new** | 0/1/0/0 |
| opinion-zhihu | **new** | 0/1/0/0 |
| listicle-mece | **tie** | 0/0/0/1 |

**汇总：新版胜 2 ｜ 旧版胜 0 ｜ 平局 0 ｜ 无效 1**

结论：新版在多数任务上占优（方向性证据支持改写有效）。

## 明细
### 任务 tech-2000w
- sample 1: verdict=**new** (换序 ['new', 'new']) ｜ gate old=OK / new=OK ｜ chars=[1263, 2239]
### 任务 opinion-zhihu
- sample 1: verdict=**new** (换序 ['new', 'new']) ｜ gate old=OK / new=OK ｜ chars=[1310, 3131]
### 任务 listicle-mece
- sample 1: verdict=**invalid** (换序 ['invalid', 'new']) ｜ gate old=OK / new=OK ｜ chars=[2692, 3836]