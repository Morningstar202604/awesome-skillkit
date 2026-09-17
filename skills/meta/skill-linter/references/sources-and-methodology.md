# 来源与方法论说明 / Sources & Methodology

- 技能：`skill-linter`（awesome-skillkit 原创编写，Apache-2.0）。
- 定位：本仓库元技能之一，与 `skill-author`（生成）、`skill-finder`（检索）共同组成场景包 `Skill Forge`。

## 方法论借鉴（仅结构层面，未复制任何文本或代码）

| 来源 | 许可证 | 借鉴的方法论要点 |
|---|---|---|
| agentskills.io 开放规范 | 见站点 | frontmatter 字段集与 name 的 kebab-case 约束，作为 `FM-FIELDS` / `NAME-SYNC` 的判定依据 |
| Anthropic《Skill Authoring Best Practices》公开文档 | 见原文 | 「description 决定技能是否被加载」，因此把路由信息独立成 `DESC-ROUTE` 而非并入字段检查 |
| 社区 lint 类工具（SkillCheck 等）的公开定位说明 | 见各自仓库 | 「报告 + 修法建议 + 退出码」三件套的输出形态；本仓库未参考其规则实现或代码 |
| 本仓库的仓库级校验器（仓库根 `tools/` 目录下的 `validate_skills.py`） | Apache-2.0（同仓） | 复用了「最小 YAML 子集解析 + 围栏代码块跳过」的解析策略，属同仓内复用；本脚本为独立实现，未复制代码 |

## 原创性声明

`scripts/lint_skill.py` 的八项检查、判定阈值（220 行 / 0.15 CJK 占比 / 触发词 >=5 /
失败处置表 >=4 行）、`Finding` 数据结构、`FIX:` 输出格式均为本仓库从零设计与实现。
`references/check-rules.md` 中的边界用例表来自对本脚本的实际执行观察，非引自任何外部清单。
未翻译、未改写、未摘录任何第三方 SKILL.md、校验脚本或其文档。

## 与本仓库规范的合并改造

1. **双轨门禁**：本技能定位为技能级自律线（更严的行数线、更细的修法提示），
   与仓库级校验器（仓库根 `tools/` 目录下的 `validate_skills.py`）并存，冲突时以后者为合并判据；
2. **可执行化**：把「规范符合性」这种主观判断降级为八条确定性谓词 + 一个退出码，
   便于挂进 CI 与 pre-commit；
3. **中文优先**：新增 `LANG-CJK` 检查，对应本仓「正文全中文、frontmatter 机器层英文」的写作要求；
   该检查对纯代码技能存在已知误报，已在 `check-rules.md` 中显式记录。

## 许可

本技能及其参考文件以 Apache-2.0 分发；所列上游规范与文档各自的许可条款与本文互不适用。
