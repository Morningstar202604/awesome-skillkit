# AGENTS.md — 使用本仓库的全局规则（AI Agent 必读）

本文件是 awesome-skillkit 面向 AI agent 的全局指令。opencode / Codex 等宿主会自动加载本文件；Claude Code 用户可将本文件内容复制为 `CLAUDE.md`。人类贡献者请看 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 规则 0：先查技能，再动手（skill-first）

**每个任务开始时**，先确认本仓库是否已有能完成该任务的技能；**任务进行中每进入一个新阶段、或遇到新的子问题，再查一次**。查到匹配的就必须用上；查不到就正常干活，不许硬套。

三个查法（任一命中即可）：

1. **扫描述**：浏览 `skills/<域>/<子类>/<技能名>/SKILL.md` 的 frontmatter `description`——其中的触发词（「当用户…」「Use when…」「Do NOT…」）就是匹配依据。`skills/` 顶级目录即域（20 个，与 [`skills/skill_chains.json`](skills/skill_chains.json) 的域一一对应）。
2. **关键词检索**（在仓库根目录运行）：
   ```bash
   python3 skills/meta/skill-finder/scripts/find_skill.py search <关键词>
   ```
   数据实时读自 `manifest.json` 与真实 `SKILL.md`，可加 `--json`、`--top N`、`--category`。
3. **多步任务查链**：`skills/skill_chains.json` 里 `domains[].entry` 是该域的编排器（入口技能），`chains` 是既有工序链。从编排器进入，按链的 step 顺序推进。

命中后的执行纪律：

- 先读完整个 `SKILL.md` 再开工，遵守它的流程与边界（尤其是 Do NOT）；
- 技能写明「交给 XX 技能」（chain / sibling 引用）时，把那个技能也查出来一起用；
- `SKILL.md` 的约定与你的默认习惯冲突时，以 `SKILL.md` 为准。

中途需要回到规则 0 再查一次的信号：产出要进入下一阶段（写作→发布、数据→图表、草稿→审计）、当前技能明确点名了下游技能、或你正准备手搓一个技能描述里已经写好的流程。

## 修改本仓库时

- 写 / 改技能前先读 `docs/SKILL_WRITING_GUIDE.md` 与 `docs/SKILL-STANDARD-v2.md`；
- 提交前两道门禁必须全绿：
  ```bash
  python3 tools/validate_skills.py   # 期望 0 errors / 0 warnings
  python3 -m pytest skills -q        # 期望全绿
  ```
- 结构约束由门禁自动校验（域必须有可解析的 entry、manifest 摘要必须与 `site/packs/*.zip` 一致、链与磁盘双向一致）。门禁报错 = 数据有错，按报错修数据，不许改门禁放水。
