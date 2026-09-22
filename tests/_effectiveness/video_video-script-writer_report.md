# 效能对照报告 — video/video-script-writer

- 旧版来源：`HEAD` ｜ 新版来源：工作区 SKILL.md
- 判定法：二元 rubric 清单 + 成对盲评（顺序互换，不一致记平局）
- 诚实边界：单一评委模型、与生成方同家族（自偏好偏差）、样本量小 —— 方向性信号，非统计结论
- 长度混淆：新版在 3/3 个样本上更长（中位 1086 vs 2187 字符）——评委指令禁止按篇幅加分，但该混淆不可完全排除

| 任务 | 最终裁决 | old/new/tie/invalid |
|---|---|---|
| douyin-30s-oral | **tie** | 0/0/1/0 |
| bilibili-60s-tutorial | **tie** | 0/0/1/0 |
| meme-15s-loop | **old** | 1/0/0/0 |

**汇总：新版胜 0 ｜ 旧版胜 1 ｜ 平局 2 ｜ 无效 0**

结论：⚠️ 旧版占优——改写效果未兑现，需复盘（不许粉饰）。

## 明细
### 任务 douyin-30s-oral
- sample 1: verdict=**tie** (换序 ['old', 'new']) ｜ gate old=OK / new=OK ｜ chars=[1086, 2270]
### 任务 bilibili-60s-tutorial
- sample 1: verdict=**tie** (换序 ['old', 'new']) ｜ gate old=OK / new=OK ｜ chars=[1802, 2187]
### 任务 meme-15s-loop
- sample 1: verdict=**old** (换序 ['old', 'old']) ｜ gate old=OK / new=OK ｜ chars=[844, 1169]