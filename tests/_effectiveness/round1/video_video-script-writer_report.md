# 效能对照报告 — video/video-script-writer

- 旧版来源：`HEAD` ｜ 新版来源：工作区 SKILL.md
- 判定法：二元 rubric 清单 + 成对盲评（顺序互换，不一致记平局）
- 诚实边界：单一评委模型、与生成方同家族（自偏好偏差）、样本量小 —— 方向性信号，非统计结论

| 任务 | 最终裁决 | old/new/tie/invalid |
|---|---|---|
| douyin-30s-oral | **old** | 1/0/0/0 |
| bilibili-60s-tutorial | **tie** | 0/0/0/1 |
| meme-15s-loop | **old** | 1/0/0/0 |

**汇总：新版胜 0 ｜ 旧版胜 2 ｜ 平局 0 ｜ 无效 1**

结论：⚠️ 旧版占优——改写效果未兑现，需复盘（不许粉饰）。

## 明细
### 任务 douyin-30s-oral
- sample 1: verdict=**old** (换序 ['old', 'old']) ｜ gate old=OK / new=['长度不足（71 < 250）'] ｜ chars=[881, 71]
### 任务 bilibili-60s-tutorial
- sample 1: verdict=**invalid** (换序 ['invalid', 'invalid']) ｜ gate old=OK / new=OK ｜ chars=[1852, 3438]
### 任务 meme-15s-loop
- sample 1: verdict=**old** (换序 ['old', 'old']) ｜ gate old=OK / new=OK ｜ chars=[1029, 3037]