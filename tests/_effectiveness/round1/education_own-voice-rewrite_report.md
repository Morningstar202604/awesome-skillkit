# 效能对照报告 — education/own-voice-rewrite

- 旧版来源：`HEAD` ｜ 新版来源：工作区 SKILL.md
- 判定法：二元 rubric 清单 + 成对盲评（顺序互换，不一致记平局）
- 诚实边界：单一评委模型、与生成方同家族（自偏好偏差）、样本量小 —— 方向性信号，非统计结论

| 任务 | 最终裁决 | old/new/tie/invalid |
|---|---|---|
| junior-high-downgrade | **tie** | 0/0/1/0 |
| voice-profile-match | **tie** | 0/0/0/1 |
| edge-florid-style | **old** | 1/0/0/0 |

**汇总：新版胜 0 ｜ 旧版胜 1 ｜ 平局 1 ｜ 无效 1**

结论：⚠️ 旧版占优——改写效果未兑现，需复盘（不许粉饰）。

## 明细
### 任务 junior-high-downgrade
- sample 1: verdict=**tie** (换序 ['old', 'new']) ｜ gate old=OK / new=OK ｜ chars=[856, 1403]
### 任务 voice-profile-match
- sample 1: verdict=**invalid** (换序 ['new', 'invalid']) ｜ gate old=OK / new=OK ｜ chars=[267, 2120]
### 任务 edge-florid-style
- sample 1: verdict=**old** (换序 ['old', 'old']) ｜ gate old=OK / new=['长度不足（179 < 250）'] ｜ chars=[2676, 179]