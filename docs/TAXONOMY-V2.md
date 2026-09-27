# 分类 v2：场景库信息架构 + 领域扩容「开户」方案

> 制定日期：**2026-09-27** · 状态：**全案执行完毕（P1/P2 已结项）**——导航已落地；**P0-1~P0-9 全部落地**（12 个新场景包、148 个新技能），**P1 6/6 落地**（caveman 收尾），**P2 许可核验 7 源完成**（4 源精选迁入、3 源裁决不迁，见 §3）；本次不开新版号，随下次发版（0.23.0 候选）
> 依据：2026-09-27 生态调研报告（GitHub raw LICENSE 逐仓实测 + skills.sh 装机榜 + Skillful/Agentman 生态报告）+ 本仓库资产实测（57 包 / 418 技能 / 27 域 / 112 链）
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
| 🛠 软件开发 | 从需求到上线运维 | programming | 21 / 146 | 厚：方法论（superpowers 等）+ 前端/代码质量 + 云平台 + 网络安全/语言规范已补 |
| 🤖 AI 与智能体 | 让 AI 会干活 | chat / memory / meta | 5 / 18 | 厚：caveman 省 token 工具包已落地 |
| 🎨 内容与创意 | 写作/视频/音频/设计→发布 | audio / design / music / video / writing | 13 / 75 | 厚：微信长文（baoyu）+ 视频代码化（HyperFrames）已补 |
| 📊 数据与科研 | 数据→仪表盘、论文全流程 | dataviz / paper | 2 / 14 | 中：科研计算精选（K-Dense）、HF 归软件侧 |
| 🗂 办公与效率 | 文档表格 PPT、知识库、工具集成 | communication / integrations / knowledge / office / ppt / tools | 7 / 79 | 厚：飞书官方套件 + 知识工作 + Google Workspace（27）已补 |
| 📈 商业与增长 | 营销/电商/PM/销售/财务法务 HR | marketing / product / hr / legal / finance / ops / customer / leadership | 6 / 76 | 厚：知识工作 + CMO/C-level + PM + GTM 增长 + 公司运营手册 |
| 🎓 学习与教育 | 课程/习题/作业辅导 | education | 2 / 6 | 中，上游缺少优质源，走自研 |
| 🏠 生活与个人 | 消费/就医/租房/装修决策 | life | 1 / 4 | 薄，医疗/个人财务待核实源 |
| **合计** | | **27 域** | **57 / 418** | 与 `manifest.json` 同口径 |

- 全量归属（27 域 / 52 包，每项恰好一组）见 [`taxonomy.json`](../taxonomy.json)；覆盖校验由 [`tools/taxonomy_check.py`](../tools/taxonomy_check.py) 守住（漏登记 / 重复 / 幽灵 id → FAIL；已接入 `validate_skills.py` 门禁与站点构建）。
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

### P0 —— 立刻可迁（许可清晰 + 高频/缺口）——**9/9 全部落地**

| # | 场景库 | 新包（建议 id） | 内容来源 | 许可（09-27 实测） | 实际规模 |
|---|---|---|---|---|---|
| 1 | 🗂 办公与效率 | `feishu-suite` ✅ **已落地** | [larksuite/cli](https://github.com/larksuite/cli) 官方 26→实际 28 技能（消息/文档/Base/表格/日历/邮箱/任务/会议/Markdown/画板 + 底座与配方） | **MIT** | 28（整包） |
| 2 | 🗂 办公与效率 | `knowledge-work` ✅ **已落地** | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins)（HR/法务/财务/运营/客服/设计研究） | **Apache-2.0**（根 LICENSE 实测；逐技能复核） | 21 |
| 3 | 🛠 软件开发 | `engineering-playbook` ✅ **已落地**（原 engineering-lifecycle 并入） | [obra/superpowers](https://github.com/obra/superpowers)（TDD / 系统化调试 / 计划执行 / 子代理并行 / worktree） | **MIT** | 12 |
| 4 | 🛠 软件开发 | 并入 `engineering-playbook` / `code-quality-pro` ✅ **已落地** | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)（spec/planning/review/debug/ship/incremental）+ [mattpocock/skills](https://github.com/mattpocock/skills)（tdd / handoff / grill-me）+ [wshobson/agents](https://github.com/wshobson/agents) | **MIT ×3**（raw LICENSE 实测） | 6+3+12 |
| 5 | 🛠 软件开发 | `cloud-platforms` ✅ **已落地** | [microsoft/azure-skills](https://github.com/microsoft/azure-skills)（装机 620 万+）+ cloudflare/skills + supabase/agent-skills + firebase/agent-skills | **MIT / Apache 全部** | 12 |
| 6 | 📈 商业与增长 | `cmo-suite` ✅ **已落地**（LinkedIn 6 + C-level 6） | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) 增量：营销/C-level/business growth（仍是大金矿，后续可续挑） | **MIT** | 12 |
| 7 | 📈 商业与增长 | `product-management` ✅ **已落地** | [phuryn/pm-skills](https://github.com/phuryn/pm-skills)（100+ 挑 12）+ mattpocock `to-spec` / `triage` | **MIT ×2** | 14 |
| 8 | 🎨 内容与创意 | `wechat-longform` ✅ **已落地** | [JimLiu/baoyu-skills](https://github.com/JimLiu/baoyu-skills)（公众号发布 / 封面 / 插图 / Markdown 格式化） | **MIT** | 10 |
| 9 | 🎨 内容与创意 | `video-code` ✅ **已落地** | [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes)（HTML 视频合成，装机 47~50 万） | **Apache-2.0** | 5 |

### P1 —— 需筛选（逐个过 validator，宁精勿多）——**6/6 全部落地**

- 🗂 `google-workspace` ✅ ← googleworkspace/cli（Apache-2.0，12 技能）
- 📊 `hf-ml-hub` ✅ ← [huggingface/skills](https://github.com/huggingface/skills)（Apache-2.0，11 技能）；`scientific-agent-skills` ✅ ← K-Dense-AI（MIT，166 挑 12）
- 🎨 单技能补强 ✅：`humanizer`（MIT）、`diagram-design`（MIT）、`archify` + `archify-review`（MIT）、`video-shotcraft`（Apache）→ 成包 `creator-boosters`（5）
- 🛠 wshobson/agents ✅（MIT，183 挑 12）+ alibaba/open-code-review ✅（Apache，1）→ 成包 `code-quality-pro`（13）
- 🪨 `caveman` ✅ ← [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman)（技能面 **MIT**、引擎目录 BSL-1.1 不取）→ 成包 `caveman-toolkit`（7）；「find-skills 式发现」自行增强 `skill-finder` ✅（`--group` 联动 + 中文检索，见 §5）

### P2 —— 许可核验完成（2026-09-27 raw LICENSE 实测）——**4 迁 3 不迁**

| 来源 | LICENSE 实测 | 裁决 |
|---|---|---|
| Cybersecurity 818（mukul975/Anthropic-Cybersecurity-Skills，社区项目） | **Apache-2.0** | ✅ 精选 14 → `cybersecurity-pro` |
| goose-skills 257（gooseworks-ai/goose-skills） | **MIT** | ✅ 精选 16 → `gtm-growth` |
| Mindrally 265（mindrally/skills，Cursor Rules 转换） | **Apache-2.0** | ✅ 精选 14 → `language-standards` |
| headcount 172（cbrock84/headcount） | **MIT** | ✅ 精选 13 → `company-playbooks` |
| Lawvable Legal 272（lawvable/awesome-legal-skills） | **CC BY-NC-ND 4.0**（禁商用 + 禁衍生物；个别条目另有 AGPL-3.0 标注） | ⛔ 不迁（ND 禁止改写再分发） |
| OpenClaw Medical 863（FreedomIntelligence/OpenClaw-Medical-Skills） | **无 LICENSE 文件**（README 口述不采信） | ⛔ 不迁（医疗内容另需合规审查 + 人审） |
| buildwithclaude 373（davepoon/buildwithclaude） | MIT（但本体是发现/市场平台，条目授权链路混杂） | ⛔ 不迁（聚合平台非作者本体） |

### 不迁（本轮实测新增的裁决）

- [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) —— **raw main 无 LICENSE 文件**（README 口述 MIT 不采信；调研报告中的"待复核"到此结案为暂缓，除非上游补 LICENSE）。
- [remotion-dev/skills](https://github.com/remotion-dev/skills)（无 LICENSE）、[llllllllama/RigorPilot-Skills](https://github.com/llllllllama/RigorPilot-Skills)（无 LICENSE）。
- [lawvable/awesome-legal-skills](https://github.com/lawvable/awesome-legal-skills)（**CC BY-NC-ND 4.0**：禁商用 + 禁衍生物）、[FreedomIntelligence/OpenClaw-Medical-Skills](https://github.com/FreedomIntelligence/OpenClaw-Medical-Skills)（**无 LICENSE 文件**）、[davepoon/buildwithclaude](https://github.com/davepoon/buildwithclaude)（MIT 本体为聚合平台，条目授权链路混杂）。
- anthropics/skills 的 docx / pdf / pptx / xlsx（source-available）；ComposioHQ / travisvn / anbeime 等无许可清单仓。

---

## 4. 本次已落地（导航、门禁、全部 P0 与 5 项 P1）

**结构层**

- `taxonomy.json`：8 场景库 + 27 能力域中文名（域/包归属各唯一）。
- 站点首页导航升级为两级 chips：「场景」（8+全部）→「能力域」（随场景联动收缩）+ 用法提示行；场景包卡片带场景库标签；技能链视图按中文域名分组。
- `tools/taxonomy_check.py`：覆盖校验的单一事实源，`validate_skills.py`（CI 门禁）与 `tools/build_site.py`（构建，构建前 fail-closed）共用。
- 首页产品线 A 卡片新增「8 大场景库」计数锚点（与 site.json meta 同源，防漂移）。
- 三语 README（EN/简中/日）场景包目录按 8 大场景库重排为分组表格（新增 12 包行 + 日语包名），计数同步 52 包 / 339 技能 / 27 域 / 88 链。

**资产层 II（P1 收尾 + P2 四源精选：5 包 / 64 技能，2026-09-27 追加）**

- `caveman-toolkit`（caveman 技能面 7，MIT）、`cybersecurity-pro`（818 挑 14，Apache-2.0）、`gtm-growth`（281 挑 16，MIT）、
  `language-standards`（14，Apache-2.0）、`company-playbooks`（13，MIT；落 ops/leadership/finance/product 四域）。
- 注册：`packs/*` 新增 5 包 + `manifest.json`（57 包 / 418 技能，含 2026-09-27 查漏补缺的 15 个 gws 兄弟技能）；`skill_chains.json` 88→112 链（27 域不变）；`taxonomy.json` 三组落位；
  `SOURCES.md` 新增「本批新收录 II」一节（5 包 × 5 仓库许可与更新指引 + 三项不迁裁决）。
- 迁移规范化：同 §4 既有口径（frontmatter 归一、署名段、长参考补目录、绝对路径占位化、补 `description_zh`）；cyber 的 5 个长参考文档补 TOC。

**资产层 I（本轮批量迁入 12 包 / 148 技能，21 个上游仓库）**

- `P0-1` feishu-suite（28，larksuite/cli，MIT）：frontmatter 规范化、140 个长参考文档补目录、约 230 处相对链接归一化、每技能附来源署名；上游自带 232 项测试纳入 CI。
- `P0-2~P0-9` + P1 五个：knowledge-work（21）、engineering-playbook（21）、cloud-platforms（12）、cmo-suite（12）、product-management（14）、wechat-longform（10）、video-code（5）、google-workspace（12）、hf-ml-hub（11）、scientific-agent-skills（12）、code-quality-pro（13）、creator-boosters（5）。
- 统一迁移规范化：frontmatter 归一（含 `metadata.source`）、来源署名段、长文档补 TOC、超长正文拆 references、盘符/绝对路径占位化、嵌套 SKILL.md 与杂散目录清理、过短 description 补写、名称与目录名对齐。
- 注册：`packs/*` 12 个新包 + `manifest.json`（52 包 / 339 技能）；`skill_chains.json` 20→27 域（新增 product/hr/legal/finance/ops/customer/leadership）、75→88 链；`taxonomy.json` 全部落位；`SOURCES.md` 新增「本批新收录」一节（12 包 × 21 仓库许可与更新指引）。

**检索层**

- **中文检索**：为 302 个原仅英文的技能补 frontmatter `description_zh`（全仓 339 技能均可中文路由）；站点卡片优先展示中文描述、搜索词命中 `desc_zh`；`find_skill.py` 搜索加 `description_zh` 权重 + CJK 字符集匹配（「合同审查」可命中「审查合同」）。
- `find_skill.py search --group <场景库>`：按 taxonomy 场景库（id / 中文名 / 英文名）过滤，与 `taxonomy.json` 单一事实源联动。

**顺手修掉的四个历史问题**（浏览器实测通过）

1. **83 个技能卡片描述显示为 ">"**：`build_site.py` 的 frontmatter 解析不支持 YAML 块标量（`>` / `>-` / `|`），导致 83 个技能 description 取值为 `>` 或 `>-`（中文关键词也因此搜不到）。已支持块标量，实装后异常描述 0 个。
2. **导航计数口径不一致**（场景 chip 49 / 能力域 chip 48 / 卡片 49）：能力域 chip 原用"链域声明口径"（含跨目录声明、含 2 个不入包夹具）。新增 `n_packed`（实装口径）用于导航计数；现 8 场景 / 27 域 / 339 卡片三者自洽。
3. **≤640px 窄屏整页横向溢出**：`.level` 竖排时改 `align-items: stretch` + `.chips` 加 `min-width: 0`，chips 行内横向滚动恢复；480px 实测 `body.scrollWidth == clientWidth`。
4. **下载产物刷新（3 个包内容过期）**：重跑构建后 `communication-essentials` / `skill-forge` / `visual-design-studio` 的更新才真正进入已提交 zip（此前一直停在旧版内容），其余 36 包仅条目顺序规范化（逐文件比对内容一致）；`build_site.py` 增加 dist↔manifest 摘要防呆（不一致 fail-closed）。

---

## 5. 完成情况

1. ✅ **三语 README 的场景包目录**已按 8 大场景库重排（分组表格 + 新增 12 包行 + 日语包名 + 计数同步）。
2. ✅ **中文检索**：取「补 frontmatter `description_zh`」方案——302 个技能补齐（另 37 个原本已有中文 description）；站点展示与搜索引擎同步。
3. ✅ `find_skill.py` 与 taxonomy 场景库联动（`search --group software`，支持 id / 中文名 / 英文名）。
4. ✅ 全部 P0 包的迁移与署名登记（`pack.json` 的 `skills[].source` + `manifest.json` + `SOURCES.md`「本批新收录」）。
5. ✅ **P1 收尾与 P2 许可核验**：caveman 落地为 `caveman-toolkit`；P2 七源逐仓实测 LICENSE——四源精选迁入（cybersecurity-pro / gtm-growth / language-standards / company-playbooks）、三源裁决不迁（Lawvable / OpenClaw Medical / buildwithclaude，见 §3）。
6. ✅ **可选依赖脚本测试**：上游为可选依赖的脚本统一走 skip 守卫（`video-shotcraft/jianying-export/smoke_test.py` 已实现；本轮复核全仓测试脚本无同类阻断项）。

**结论：路线图全部执行完毕（2026-09-27 结项），无遗留项。**

---

## 6. 执行顺序（建议）——**已全部执行**

```
本轮：分类 + 导航 + 门禁 ✅
 ↓
P0-1 飞书套件 ✅ → P0-2 知识工作 ✅ → P0-3 工程方法论 ✅ → P0-4 前端规范 ✅（并入 engineering-playbook/code-quality-pro）
→ P0-5 云平台 ✅ → P0-6 营销/C-level ✅ → P0-7 PM ✅ → P0-8 微信长文 ✅ → P0-9 视频代码化 ✅
 ↓（每包一提交：许可核验 → 去重 → 重组为包 → 登记 source → 过门禁 → CHANGELOG）
 ↓ P1：google-workspace ✅ / hf-ml-hub ✅ / scientific ✅ / creator-boosters ✅ / code-quality-pro ✅ / caveman ✅
 ↓ P2：许可核验 7 源——cybersecurity ✅ / goose-skills ✅ / mindrally ✅ / headcount ✅ 精选迁入；Lawvable ⛔ / OpenClaw Medical ⛔ / buildwithclaude ⛔（见 §3）
 ↓
站点/三语 README/安装包已随本轮更新；**全部结项**。
```

**每包验收沿用既有纪律**：`python3 tools/validate_skills.py`（0/0）→ `python3 -m pytest skills -q` → `python3 build.py` → `python3 tools/build_site.py`；taxonomy 覆盖校验自动生效（新包必须在 `taxonomy.json` 里落位，否则门禁 FAIL）。