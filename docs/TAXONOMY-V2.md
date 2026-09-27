# 分类 v2：场景库信息架构 + 领域扩容「开户」方案

> 制定日期：**2026-09-27** · 状态：**导航部分已落地**（随下次发版，0.23.0 候选）；扩容清单按 §6 顺序执行
> 依据：2026-09-27 生态调研报告（GitHub raw LICENSE 逐仓实测 + skills.sh 装机榜 + Skillful/Agentman 生态报告）+ 本仓库资产实测（39 包 / 163 技能 / 20 域 / 73 链）
> 配套数据文件：[`taxonomy.json`](../taxonomy.json)（站点一级导航的单一事实源）

---

## 0. 一句话

把「39 个包平铺 + 20 个能力域单层筛选」升级为**两级引导**：

```
一级：场景库（我在做什么） → 二级：能力域（用什么能力） → 技能卡 / 场景包 zip
```

同时：**扩容不局限于现有领域**——按高频领域"开户"（新场景包 + 新来源仓库），补上商业/办公/云/前端等空白。

---

## 1. 高频领域证据（决定先开哪些包）

| 信号（2026-09-27 实测） | 数据 | 指向 |
|---|---|---|
| skills.sh 全站装机榜 | find-skills **250 万+**（发现/元技能第一）、frontend-design 66 万、react-best-practices 55 万、grill-me / agent-browser 54 万、web-design-guidelines 46 万 | 元技能与"发现"、前端规范、研究方法论 |
| skills.sh 官方仓装机 | open.feishu.cn **880 万+**（lark-approval 单技能 39.9 万）、larksuite/cli **310 万+**；microsoft/azure-skills **620 万+**（微软占前 30 榜 10+ 席） | **办公套件（飞书）与云平台是最高频两类** |
| 工程方法论 | mattpocock/skills：tdd 43 万、grill-me 54 万、to-prd / triage / handoff 35 万级；remotion 42 万、caveman 34.7 万 | 工程全生命周期方法论、视频代码化、token 经济 |
| 分类供给量（Skillful 2026-09-15 / Agentman 2026-06） | 开发 28.9 万 · PM **8.7 万** · 营销 **7.5 万** · 数据 6.9 万 · 运营 **5.1 万** · 销售 **4.3 万** · 设计 2.6 万 · 法务 **1.8 万** | 供给集中处 = 需求集中处；**PM/营销/销售/运营/法务是我们近乎空白的域** |
| 质量基准（SkillsBench） | 47,150 技能均分 **6.2/12**；精选技能平均 **+16.2pp** | 继续"宁精勿多"，靠门禁精选，不追量 |

**结论**：先开的包集中在——①飞书/知识工作（国内办公最高频）②云平台与工程方法论（全球最高频）③微信长文/视频代码化（中文内容链路）④PM/营销（需求大、上游有 MIT 现货）。

---

## 2. 信息架构 v2：8 个场景库（已落地）

| 场景库 | 一句话 | 能力域 | 包/技能（现装） | 现状 |
|---|---|---|---|---|
| 🛠 软件开发 | 从需求到上线运维 | programming | 14 / 49 | 厚，缺方法论与前端规范/云平台 |
| 🤖 AI 与智能体 | 让 AI 会干活 | chat / memory / meta | 4 / 11 | 够，按需补 |
| 🎨 内容与创意 | 写作/视频/音频/设计→发布 | writing / video / audio / music / design | 10 / 52 | 厚，缺微信长文与视频代码化 |
| 📊 数据与科研 | 数据→仪表盘、论文全流程 | dataviz / paper | 2 / 14 | 中，缺 HF/科研上游 |
| 🗂 办公与效率 | 文档表格 PPT、知识库、工具集成 | office / ppt / tools / knowledge / integrations / communication | 5 / 24 | **缺飞书官方套件与知识工作大包** |
| 📈 商业与增长 | 营销/电商/PM/销售/财务法务 HR | marketing | 1 / 3 | **最薄，本轮扩容重点** |
| 🎓 学习与教育 | 课程/习题/作业辅导 | education | 2 / 6 | 中，上游缺少优质源，走自研 |
| 🏠 生活与个人 | 消费/就医/租房/装修决策 | life | 1 / 4 | 薄，医疗/个人财务待核实源 |

- 全量归属（20 域 / 39 包，每项恰好一组）见 [`taxonomy.json`](../taxonomy.json)；覆盖校验由 [`tools/taxonomy_check.py`](../tools/taxonomy_check.py) 守住（漏登记 / 重复 / 幽灵 id → FAIL；已接入 `validate_skills.py` 门禁与站点构建）。
- 站点展示口径：**技能按能力域归组、场景包按使用场景归组**（两者允许不同：找包看场景，找技能看能力）。

### 位置调整：本轮怎么"调"

1. **不搬物理目录**（`skills/<域>/`、`packs/` 保持原位）——门禁、链图谱、zip 摘要全部按路径绑定；搬目录 = 全链路重算。分类只加在**导航层**（taxonomy.json），零破坏、随改随生效。
2. 经研判的 3 个边界归属（理由）：
   - `ai-research-writing`（18 技能）→ 归**内容与创意**：用户目标是"成稿发布"这条产线；其中 12 个论文技能按能力域自然落在「数据与科研」。
   - `web-ops`（网页结构化提取）→ 归**软件开发**（其能力域是 programming）。
   - `communication-essentials`（职场沟通话术）→ 归**办公与效率**；若日后生活向沟通技能变多，再评估拆组。
3. 物理目录的调整**暂缓**：等 P0 新包批量落地后一次性评估（避免二次搬迁）。

---

## 3. 开户清单（新场景包 × 来源 × 许可实测）

> 许可纪律：一律以仓库内 LICENSE **文件级**实测为准，README 口述不采信；无许可不迁（沿用先例：5 个无许可上游技能不入仓）。

### P0 —— 立刻可迁（许可清晰 + 高频/缺口）

| # | 场景库 | 新包（建议 id） | 内容来源 | 许可（09-27 实测） | 规模建议 |
|---|---|---|---|---|---|
| 1 | 🗂 办公与效率 | `feishu-suite` | [larksuite/cli](https://github.com/larksuite/cli) 官方 26 技能（消息/文档/Base/表格/日历/邮箱/任务/会议/Markdown） | **MIT** | 26（整包） |
| 2 | 🗂 办公与效率 | `knowledge-work` | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins)（数据可视化/任务管理/内容创作/竞争情报） | **Apache-2.0**（根 LICENSE 实测；入库前逐技能复核） | 挑 15~30 |
| 3 | 🛠 软件开发 | `engineering-lifecycle` | [obra/superpowers](https://github.com/obra/superpowers)（TDD / 系统化调试 / 计划执行 / 子代理并行 / worktree） | **MIT** | 16（整包） |
| 4 | 🛠 软件开发 | `frontend-standards` | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)（QA/spec/PRD）+ [mattpocock/skills](https://github.com/mattpocock/skills)（tdd / triage / to-prd / handoff / grill-me） | **MIT + MIT**（raw LICENSE 双实测） | 8~12 |
| 5 | 🛠 软件开发 | `cloud-platforms` | [microsoft/azure-skills](https://github.com/microsoft/azure-skills)（装机 620 万+）+ cloudflare/skills + supabase/agent-skills + firebase/agent-skills + [googleworkspace/cli](https://github.com/googleworkspace/cli) | **MIT / Apache 全部** | 10~15 |
| 6 | 📈 商业与增长 | `cmo-suite` | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) 增量：营销 43 / C-level 28 / business growth 4（现有 33 技能的上游，仍是大金矿） | **MIT** | 挑 20~30 |
| 7 | 📈 商业与增长 | `product-management` | [phuryn/pm-skills](https://github.com/phuryn/pm-skills)（100+）+ mattpocock to-prd / triage | **MIT** | 挑 10~15 |
| 8 | 🎨 内容与创意 | `wechat-longform` | [JimLiu/baoyu-skills](https://github.com/JimLiu/baoyu-skills)（公众号发布 / 封面 / 插图 / Markdown 格式化） | **MIT** | 挑 8~12 |
| 9 | 🎨 内容与创意 | `video-code` | [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes)（HTML 视频合成，装机 47~50 万） | **Apache-2.0** | 挑 3~5 |

### P1 —— 需筛选（逐个过 validator，宁精勿多）

- 🗂 `google-workspace` ← googleworkspace/cli（Apache-2.0）
- 📊 `hf-ml-hub` ← [huggingface/skills](https://github.com/huggingface/skills)（Apache-2.0）；`scientific` 精选 ← K-Dense-AI（MIT，166 技能挑 10~20）
- 🎨 单技能补强：`humanizer`（MIT）、`diagram-design`（MIT）、`archify`（MIT）、`video-shotcraft`（Apache）
- 🤖 AI 与智能体：caveman（token 经济，**许可待核实**）；「find-skills 式发现」走自研增强 `skill-finder`
- 🛠 wshobson/agents（MIT，183 技能挑 20~40）；alibaba/open-code-review（Apache）

### P2 —— 先核许可再谈（多为垂直大包）

Lawvable Legal 272 · OpenClaw Medical 863 · Cybersecurity 818 · headcount 172 · goose-skills 257 · Mindrally 265 —— 一律先找到 LICENSE 文件；医疗/法律类额外做内容合规与人审。来源线索见调研报告 §5。

### 不迁（本轮实测新增的裁决）

- [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) —— **raw main 无 LICENSE 文件**（README 口述 MIT 不采信；调研报告中的"待复核"到此结案为暂缓，除非上游补 LICENSE）。
- [remotion-dev/skills](https://github.com/remotion-dev/skills)（无 LICENSE）、[llllllllama/RigorPilot-Skills](https://github.com/llllllllama/RigorPilot-Skills)（无 LICENSE）。
- anthropics/skills 的 docx / pdf / pptx / xlsx（source-available）；ComposioHQ / travisvn / anbeime 等无许可清单仓。

---

## 4. 本次已落地（导航、门禁与三个修复）

**新增**

- `taxonomy.json`：8 场景库 + 20 能力域中文名（域/包归属各唯一）。
- 站点首页导航升级为两级 chips：「场景」（8+全部）→「能力域」（随场景联动收缩）+ 用法提示行；场景包卡片带场景库标签；技能链视图按中文域名分组。
- `tools/taxonomy_check.py`：覆盖校验的单一事实源，`validate_skills.py`（CI 门禁）与 `tools/build_site.py`（构建，构建前 fail-closed）共用。
- 首页产品线 A 卡片新增「8 大场景库」计数锚点（与 site.json meta 同源，防漂移）。

**顺手修掉的四个历史问题**（浏览器实测通过）

1. **83 个技能卡片描述显示为 ">"**：`build_site.py` 的 frontmatter 解析不支持 YAML 块标量（`>` / `>-` / `|`），导致 83 个技能 description 取值为 `>` 或 `>-`（中文关键词也因此搜不到）。已支持块标量，实装后异常描述 0 个。
2. **导航计数口径不一致**（场景 chip 49 / 能力域 chip 48 / 卡片 49）：能力域 chip 原用"链域声明口径"（含跨目录声明、含 2 个不入包夹具）。新增 `n_packed`（实装口径）用于导航计数；现 8 场景 / 20 域 / 163 卡片三者自洽（49+11+52+14+24+3+6+4 = 163）。
3. **≤640px 窄屏整页横向溢出**：`.level` 竖排时改 `align-items: stretch` + `.chips` 加 `min-width: 0`，chips 行内横向滚动恢复；480px 实测 `body.scrollWidth == clientWidth`。
4. **下载产物刷新（3 个包内容过期）**：重跑构建后 `communication-essentials` / `skill-forge` / `visual-design-studio` 的更新才真正进入已提交 zip（此前一直停在旧版内容），其余 36 包仅条目顺序规范化（逐文件比对内容一致）；`build_site.py` 增加 dist↔manifest 摘要防呆（不一致 fail-closed）。

---

## 5. 待办（不阻塞本轮）

1. **三语 README 的 39 包目录**按场景库重排（等本分类定稿后再动，避免二次改版）。
2. **中文检索**：技能 frontmatter 目前只有英文 description（全仓约定），中文词只能命中"场景包"tab（包有 `desc_zh`）。方案二选一：为 163 技能补 frontmatter `description_zh`；或站点生成时从正文摘要中文首段。建议随下一轮内容批次做。
3. `find_skill.py`（仓库内检索）与 taxonomy 场景库联动（可选：`search --group software`）。
4. P0 各包的迁移与署名登记（`manifest.json` / `pack.json` 的 source 字段 + `SOURCES.md`）。

---

## 6. 执行顺序（建议）

```
本轮：分类 + 导航 + 门禁 ✅
 ↓
P0-1 飞书套件（国内最高频）→ P0-2 知识工作 → P0-3 工程方法论 → P0-4 前端规范
→ P0-5 云平台 → P0-6 营销/C-level → P0-7 PM → P0-8 微信长文 → P0-9 视频代码化
 ↓（每包一提交：许可核验 → 与 163+100 去重 → 重组为包 → 登记 source → 过门禁 → CHANGELOG）
 ↓
站点/三语 README/安装包随发版更新；P1、P2 按序。
```

**每包验收沿用既有纪律**：`python3 tools/validate_skills.py`（0/0）→ `python3 -m pytest skills -q` → `python3 build.py` → `python3 tools/build_site.py`；taxonomy 覆盖校验自动生效（新包必须在 `taxonomy.json` 里落位，否则门禁 FAIL）。