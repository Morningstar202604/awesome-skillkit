# Sources & Methodology

- 技能：`skill-finder`（awesome-skillkit 原创编写，Apache-2.0）。
- 定位：本仓库元技能之一，与 `skill-author`（生成）、`skill-linter`（校验）共同组成场景包 `Skill Forge`。

## Methodology borrowed (structural level only; no text or code copied)

| Source | License | Methodology points borrowed |
|---|---|---|
| Anthropic《Skill Authoring Best Practices》公开文档 | 见原文 | 「元数据常驻、正文按需」意味着检索应当以 name/description 为主、正文为辅——本技能的三级权重由此而来 |
| agentskills.io 开放规范 | 见站点 | 技能发现依赖 name + description 的路由机制，作为打分权重的分配依据 |
| 社区 find-skills / 技能索引类工具 | 见各自仓库 | 「关键词 → 命中列表 + 所属集合 + 路径」的最小结果形态；本仓库未参考其实现，权重、排序与输出格式均为自定 |
| 本仓库的技能列表脚本（仓库根 `tools/` 目录下的 `list_skills.py`） | Apache-2.0（同仓） | 借鉴「按 category 分组罗列技能」的输出惯例；本脚本为独立实现，并额外提供检索评分与包装配 |

## Originality statement

`scripts/find_skill.py` 的三个子命令、相关度权重表（名称 5 / 名称前缀额外 3 / description 3 /
包描述 2 / 正文 1）、同分按名称升序的可复现排序、`pack` 的交集判定与顺序建议启发式
（编排类优先 → 带脚本者 → 纯提示型），以及 `references/repo-map.md` 的统计口径表，
均为本仓库从零设计。所有技能数据在运行时读自 `manifest.json` 与 `skills/**/SKILL.md`，
脚本内**不含任何硬编码技能列表**——这是本技能可与仓库同步演进而无需改代码的前提。
未翻译、未改写、未摘录任何第三方 SKILL.md、脚本或文档。

## Merged adaptations to this repo's conventions

1. **真实数据源优先**：把「技能清单」从代码里彻底移出，改为扫盘 + 读 manifest，
   避免清单与仓库脱节；
2. **可解释相关性**：放弃向量检索，改用可逐项复算的加权词频，
   任意一条排序结果都能人工验算，符合本仓「确定性优先」的设计公理；
3. **顺带做体检**：`stats` 额外暴露孤儿技能与悬空 pack 引用，
   把「仓库家底」与「数据一致性告警」合并到一次调用里。

## License

This skill and its reference files are distributed under Apache-2.0; the upstream specs and documents listed carry their own license terms, which do not apply to this file.
