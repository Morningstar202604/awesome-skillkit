# Sources & Methodology

- 技能：`skill-author`（awesome-skillkit 原创编写，Apache-2.0）。
- 定位：本技能是本仓库的**元技能**之一，与 `skill-linter`（校验）、`skill-finder`（检索）共同组成场景包 `Skill Forge`。

## 方法论借鉴（仅结构层面，未复制任何文本）

| Source | License | Methodology points borrowed |
|---|---|---|
| Anthropic《Skill Authoring Best Practices》公开文档 | 见原文 | 「元数据常驻 → 正文激活 → 资源按需」的渐进披露三层；description 决定技能是否被加载这一核心结论 |
| agentskills.io 开放规范 | 见站点 | frontmatter 字段集（name / description / license / compatibility / metadata）与 name 的 kebab-case 约束 |
| SkillsBench 公开实证结论 | 见论文 | 「单体大杂烩」技能显著掉分，一场景一技能；技能粒度应与触发语一一对应 |
| OpenAI skill-creator 公开说明 | 见仓库 | 「先澄清需求再落笔」的次序纪律：需求不清时不得直接产出文件 |

上述来源全部作为**方法论骨架**被再表述：本技能的五问澄清模板、十诫检查表、四种骨架变体表、
`references/skill-template.md` 全部为从零撰写，未翻译、未改写、未摘录任何上游段落或示例。

## Merged adaptations to this repo's conventions

1. **十诫内联**：本仓技能编写规范（仓库根 `docs/` 目录下的 SKILL-STANDARD-v2）§3 的十条写作诫律以表格形式内联进正文，
   每条附「怎么算违反」的判据，避免作者再跳转外部文档；
2. **机器层英文 / 人类层中文分离**：frontmatter 与代码保持英文，正文中文，
   对齐本仓「中文用户是主力」的触发词工程要求；
3. **可验证化**：自检步骤改为可执行命令（`lint_skill.py` + `wc -l` + `grep -c`），
   把「写得好不好」降级为「检查是否通过」。

## License

This skill and its reference files are distributed under Apache-2.0; the upstream documents listed carry their own license terms, which do not apply to this file.
