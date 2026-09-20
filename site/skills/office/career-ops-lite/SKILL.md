---
name: career-ops-lite
description: >
  Score a job posting against your resume (per-requirement A-F grades + a 0-5
  holistic score), then draft a tailored cover-letter block and a tracker entry.
  Offline, human-in-the-loop: it evaluates and drafts, it never submits. Use
  when the user asks to 评估岗位 / 我该不该投 / 匹配度 / 定制简历 / 求职跟踪 /
  should I apply / job match / career pipeline. Do NOT use for scraping job
  portals or auto-applying (out of scope + compliance); this is scoring +
  drafting only.
license: Apache-2.0
compatibility: 纯文本 + Python 离线；无需网络、无需 Playwright；评分是启发式词面匹配，最终判断仍靠人
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: office
  pattern: script
  tier: standard
  verified-date: "2026-09-20"
---

# Career Ops Lite（岗位评估 + 定制 + 跟踪）

把一个 JD 文本和你的简历要点，评分成**逐条要求 A-F + 0-5 总分 + 决策建议**，
再产出定制 cover-letter 片段和跟踪条目。改造自 santifer/career-ops（MIT）的
"评估优先、人不撒网"理念，裁剪为**纯离线、不碰招聘网站登录态**的版本。

核心判断：求职系统最大的价值不是"帮你投"，是"帮你**别乱投**"。先评估、后定制、
再跟踪，人始终在回路里——**从不自动提交申请**。

> 红线：默认 dry-run 只打印评分；`--write` 才落 JSON 报告；零网络、零凭证；
> 不发任何申请。

## 输入清单

| 输入 | 必填 | 说明 |
|---|---|---|
| JD 文本文件 | 是 | 岗位描述（纯文本/.md） |
| 简历要点文件 | 是 | 你的技能/经历要点 |
| 权重 JSON | 否 | 覆盖五个维度的权重 |

## 前置自检

1. 简历要点是否"技能词可被词面匹配"？（评分是**启发式词面**，不是 LLM 语义，
   关键词要对得上：JD 写 "React"，你简历里也得有 "React"）
2. 级别信号（junior/mid/senior/staff 或 应届/初/中/高级）在 JD 里有没有？
   没有就 level_fit 给中性 0.4。
3. comp_band / domain_match / stability 三维**默认 0.5**，需你人工补值后重跑。

## 工作流

```bash
# 1. 干跑：评分 + 逐条 A-F
python3 scripts/job_scorer.py --jd ./jd.txt --resume ./me.txt

# 2. 覆盖权重（更看重匹配度）
python3 scripts/job_scorer.py --jd ./jd.txt --resume ./me.txt \
  --weights ./config/weights.json

# 3. 落 JSON 报告（喂给跟踪表 / Notion / 人工审阅）
python3 scripts/job_scorer.py --jd ./jd.txt --resume ./me.txt \
  --write -o ./report.json
```

`score_5 >= 4` 才建议投（career-ops 的"filter 不是 spray-and-pray"原则）；
< 3 直接跳过。

## 交付标准

- 每个要求都有 A-F 等级 + 可读说明（脚本输出）
- 五维权重可覆盖、可复算
- JSON 报告含 `requirements`/`grade_counts`/`dimension_scores`/`score_5`/`verdict`
- **不产生任何自动申请动作**

## 失败处置表

| 现象 | 根因 | 处置 |
|---|---|---|
| 等级全 C/F | 简历关键词与 JD 词面不符 | 对齐术语（JD "Go" 你写 "golang"） |
| level 检测不到 | JD 没写级别 | 人工补；或 JD 文本里补级别词 |
| comp/domain/stability 都 0.5 | 默认值 | 人工估后写进 `--weights` 或改 JSON |
| 权重 JSON 报错 | 格式错 | 用 `config/weights.example.json` 模板 |
| 想要"自动投" | 超出范围 + 合规风险 | 本技能只评估/定制，提交人工做 |

## 参考

- 评分维度与权重说明：[references/scoring.md](references/scoring.md)
- 权重模板：[config/weights.example.json](config/weights.example.json)

## 链路位置

- 上游：`resume-tailor`（先定制好简历要点再喂进来）
- 下游：`meeting-notes`/手工跟踪表（把 JSON 报告归档进 pipeline）
