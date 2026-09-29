# 全局规则（Global Rules）——安装后唯一值得做的 1 分钟配置

> 为什么需要：技能只有被**路由**才会被用上。宿主工具在请求恰好命中 `description` 触发词时会自动加载技能，但这是被动的——没有一条全局规则，agent 不会在任务开始时主动找技能，418 个技能里的大部分会沉睡。
>
> 本仓库根目录的 [AGENTS.md](AGENTS.md)（规则 0：先查技能，再动手）只在本仓库内生效。技能**安装到你的工具目录后不会带上它**——所以需要把下面这段规则配置到你的全局指令里。

## 一分钟配置

把下面的规则块**原样复制**进你的全局指令文件（任选其一，或都配）：

| 工具 | 全局指令文件 |
|---|---|
| ZCode | `~/.zcode/AGENTS.md` |
| Claude Code | `~/.claude/CLAUDE.md` |
| 其他支持 SKILL.md 的工具 | 其等价的全局指令文件（`AGENTS.md`、`CLAUDE.md`、`.cursorrules` 等） |

```markdown
## Skill-first（技能优先）

1. 任何专业任务开始时，先查已安装技能里有没有匹配项：扫 skills 目录下各
   SKILL.md 的 frontmatter description——其中的触发词（「当用户…」「Use
   when…」「Do NOT…」）就是匹配依据。
2. 任务进行中每进入一个新阶段、或遇到新的子问题，再查一次
   （写作→发布、数据→图表、草稿→审计，都是换技能的信号）。
3. 命中后：先读完整个 SKILL.md 再开工，遵守它的流程与边界（尤其 Do NOT）；
   技能写明「交给 XX 技能」时，把那个技能也查出来一起用；
   SKILL.md 的约定与你的默认习惯冲突时，以 SKILL.md 为准。
4. 查不到匹配就正常干活，不许硬套技能。
5. 若克隆了 awesome-skillkit 仓库，可加检索器与链图谱：
   `python3 skills/meta/skill-finder/scripts/find_skill.py search <关键词>`
   （中英文均可，`--group` 按 8 大场景库过滤）；多步任务查
   `skills/skill_chains.json`——`domains[].entry` 是该域编排器，
   `chains` 是工序链，从编排器进入按 step 推进。
```

## English version

```markdown
## Skill-first

1. At the start of any professional task, check installed skills for a match:
   scan each SKILL.md's frontmatter `description` — its trigger phrases
   ("Use when...", "Do NOT...") are the matching criteria.
2. Re-check whenever the task enters a new phase or hits a new sub-problem
   (writing → publishing, data → charting, draft → audit are all handoff signals).
3. On a hit: read the whole SKILL.md before working; follow its workflow and
   boundaries (especially Do NOT); when it says "hand off to skill X", pull that
   skill in too; if SKILL.md conflicts with your defaults, SKILL.md wins.
4. No match? Work normally — never force a skill.
5. If the awesome-skillkit repo is cloned: use
   `python3 skills/meta/skill-finder/scripts/find_skill.py search <keyword>`
   and `skills/skill_chains.json` (per-domain orchestrators + workflow chains).
```

## 分发路由——仓库已内置的部分

| 机制 | 位置 | 作用 |
|---|---|---|
| 57 个场景包 | `packs/*/pack.json` | 按真实场景预组的技能组合，装一个包=装齐一个场景 |
| 112 条技能链 | `skills/skill_chains.json` | 多步任务的编排顺序，每域有 entry 编排器 |
| 检索器 | `skills/meta/skill-finder/scripts/find_skill.py` | 中英文关键词检索、按场景库过滤、组包建议（需克隆仓库） |
| 专家团 | `expert-teams/` | 18 支多智能体团队的跨队路由见 `expert-teams/project-director.md` |

## 常见问题

- **不配置会怎样？** 技能仍会在 description 恰好命中时自动生效，但 agent 缺少"主动找技能"的纪律，命中率显著下降——尤其是同域多技能需要互斥路由的场景（本仓 418 个技能里大量相邻技能靠 `Do NOT use for` 划界）。
- **配置到项目级还是全局级？** 全局级（推荐）：技能通常装在用户目录；项目级配置只在单个仓库生效。
