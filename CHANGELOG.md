# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> **版本体系说明 / Version scheme note**：本仓库在 2026-08-23（v0.1.0，
> commit `ebd7f0a` "reset version baseline"）将版本基线重置为 0.x 体系并沿用至今。
> 重置前曾短暂使用过一套 1.x 版本号（最高 v1.12.3），历史文档中的 v1.x 引用均为
> 该时期的记录；同一事件在旧体系与 0.x 体系中的编号为一一对应
> （如旧 v1.3.0 = 0.3.0，旧 v1.5.0 = 0.5.0）。2026-09-05（commit `ddfddf0`）
> 起 `manifest.json` 的 version 字段与 0.x 体系完全对齐。
> 另：0.4.0 – 0.6.1 发布于重置整理期，其内容随后被 squash 进 0.6.2 对应的提交
> （`21769cb`），独立提交已不可考，故这四个版本没有对应的 git tag。

## [Unreleased]

## [0.19.0] - 2026-09-17

### Added

- **全库逐技能逻辑链条审计（143 技能全覆盖）**——把每个技能按「输入清单 → 前置自检 →
  工作流 → 交付标准 → 失败处置表 → 参考」六要素逐项验，并用真实样例实测全部 `scripts/*.py`
  （正例 rc=0、异常样例 rc≠0），共发现并修复 **50+ 处缺陷**：

  **P0 链路必坏 / 失败被吞（8 处）**
  - `tools/file-organizer`、`tools/batch-renamer`：`plan`/`apply` 以相对路径调用时
    `dst.relative_to(root)` 抛 `ValueError` —— 而 SKILL.md 的示例命令正是相对路径写法，**照抄必崩**。
  - `tools/format-converter`：`media` 路径未知扩展直接透传 ffmpeg 返回码 **234**，
    文档承诺的 rc=3 根本没实现。
  - `integrations/cloud-drive-manager`：空目录或全被 `--exclude` 排除时返回 **rc=0**，
    把"零产出"当成功上报，流水线会带着空计划往下走。
  - `programming/math/model-solver`：LP 路径 100% 崩溃（`result.iter` 应为 `result.nit`）。
  - `programming/data/data_ml_pipeline`：`SCRIPTS["ml"]` 指向 `ml/pipeline/`（实际是 `ml/ml-pipeline/`），
    第 3 步 100% FileNotFoundError。
  - `programming/planning/code-intent-planner`：L2 不可达时 `{"error": ...}` 仍 rc=0。
  - `programming/math/result-visualizer`：数据文件缺失打印 skipped 却 rc=0。
  - `video/storyboard-designer`：交付标准里的 `beat-sheet.md`/`continuity.md` 无任何步骤产出。

  **P1（不可执行命令 / 死链 / 与文档矛盾，50+ 处）**
  - `writing/orchestrator/cross-post-orchestrator`：`ADAPTERS` 路径少一层 `..` 致
    wechat_mp 调度**从未生效**（100% 走 `[MANUAL]`）；缺 juejin 注册；
    juejin 分支重建 `cmd` 时**丢失 `--execute`** 造成"台账记 `ok` 但实际未发布"的静默失败；
    5 处示例 `--manifest` 参数顺序错误。
  - `design/layout-spec-auditor`：文档给的 `--expect` 命令实测 exit 2，不可执行。
  - `writing/humanize-rewriter`：前置自检 `--help | head; echo check=$?` 管道后 `$?` 恒为 0，
    探测完全失效。
  - `writing/blog/cnblogs-skill`：`references/image-guide.md` 4 处死链指向不存在的技能。
  - `audio/episode-publisher` 跨目录相对引用死链；`design/image-prompt-engineer` 等
    3 个生成技能前置自检用了尚未赋值的网关变量（顺序断裂）。
  - `writing/seo-optimizer` docstring 宣传不存在的 `--json '{"..."}'` 用法。
  - `integration/notion-workspace`、`dataviz/dashboard-designer` 等步骤缺「若失败」；
    全库补齐 **43 处**缺失的三件套分支。

  **结构性修复**
  - `programming/database/sql-database-assistant`：正文 518 行超硬门禁，
    外移 111 行到 `references/dialect_and_orm.md`（正文 → 421 行）。

### Fixed

- **技能发现口径统一（3 个工具此前互相矛盾）**：`skills/writing/assets/ai-cover-generator`
  是被 `ai-media-toolkit` / `content-publishing` / `image-studio` **三个包真实引用**的技能，
  却因 `assets/` 被当作垃圾目录而被 `validate_skills.py`、`skill-finder`、`skill-linter`
  静默跳过 —— 它长期逃过深度校验。现三处口径统一为「只跳过 `_common/`、`templates/`
  与 `sample-*`」，纳入后 **143 技能全绿**（此前 142）。
- **包 `id` 与产物文件名不一致**：`packs/dataviz-studio/pack.json` 的 `id` 是
  `data-viz-studio`，但 `dist/` 里的 zip 与目录名都是 `dataviz-studio`，
  导致站点生成 **失效下载链接**（`packs/data-viz-studio.zip` 不存在）。
  统一为 `dataviz-studio`，下载链接恢复可解析。
- **`epub-builder` 未登记**：补入 `office` 域并新增 `ebook_pipeline` 链。
- **3 个词库文件补目录**：`visual-detail-lexicon.md` / `music-style-lexicon.md` /
  `cinematography-lexicon.md` 超 100 行却无 TOC，`validate` 的警告清零。

## [0.18.0] - 2026-09-17

### Added

- **新场景包 ×3 — 覆盖外部集成、个人知识库、数据可视化三个主流域**：

  **`Workspace Integrations`（外部集成，4 技能）** — 此前只有 git/GitHub，本轮补齐：
  - `notion-workspace`：页面/数据库读写、blocks↔Markdown 双向转换；覆盖 API 版本头、
    分页（has_more/next_cursor）、rate limit（3 req/s）与 10 种 block 类型映射。
  - `feishu-dingtalk-bridge`：飞书 / 钉钉 / 企业微信三家协议差异对照（鉴权方式、消息格式、
    Webhook 安全设置）——飞书 content 是字符串化 JSON、钉钉是独立 markdown 对象 + 顶层 at、
    企微标题内联进 content，三家结构差异一次讲清。
  - `issue-tracker-sync`：Jira / Linear / GitHub Issues 三向字段映射（Jira 嵌套 fields、
    Linear GraphQL variables、GitHub 扁平 body）+ 跨平台状态映射表 + 周报生成。
  - `cloud-drive-manager`：上传计划、sha256 校验清单、云盘响应解析；覆盖分片阈值、秒传原理、
    百度/阿里/OneDrive 差异。**有意不提供删除命令**——删除是唯一不可逆且后果随规模放大的操作。
  - 四个技能共同红线：凭证零硬编码（只读环境变量）、写操作默认 dry-run、脚本不发真实网络请求、
    显式标注所需 scope 与"不要申请什么"。

  **`Knowledge Base`（个人知识库，2 技能）**
  - `personal-wiki`：init/index/search/lint/stats 一套；检索权重实测生效（标题 17 分 vs 正文 1 分）；
    lint 抓孤儿笔记、断链、空笔记。
  - `knowledge-graph-builder`：从 Markdown 提取实体关系（`[[wiki链接]]` 作边），导出
    Mermaid/Graphviz/DOT；分析度中心性、连通分量、孤立节点。

  **`Data Viz Studio`（数据可视化，2 技能）**
  - `dashboard-designer`：CSV 列类型推断 + 分布摘要 → 布局推荐 → 生成**零外部请求**的自包含
    单文件 HTML 仪表盘（经 Chromium 渲染验证图形真实存在）。
  - `chart-recommender`：图表选择词库（137 行）——数据类型→图型映射、每种图型的适用与反例、
    视觉编码优先级、截断 y 轴/双轴滥用/3D 饼图等经典错误清单、三类色板适用场景。

- **office-productivity 补强**：`epub-builder`（仅标准库实现，Markdown → 标准 EPUB；
  严格遵守 `mimetype` 必须为首个未压缩条目的规范，已用 zipfile 独立复核）。

- 新增链域 ×3：`integrations`（3 链）、`knowledge`、`dataviz`，全库
  **18 链域 / 57 条链**。

### Fixed

- **全仓骨架规范整治（52 → 0 FAIL）**：以 `skill-linter` 为标尺逐项修复 46 个技能：
  - 补 `## 参考` 章节 ×20（有参考文件的列真实链接，纯提示型写明确说明，禁止编造链接）
  - 失败处置表补足至 ≥4 行 ×24（补的行按平台实况撰写，如微博风控限流、小红书多图上传中断、
    LaTeX 的 TikZ 箭头压字，非套话）
  - description 补齐 `Use when` / `Do NOT` 路由与 ≥5 个中英双语触发词 ×10
  - 补 `## 工作流` 总纲章节 ×3（原有流水线内容保留，新增流程索引）
- **`sql-database-assistant` 正文瘦身**：518 行超门禁硬线（<500），将「多数据库支持」与
  「ORM 模式」两段共 111 行参考型知识外移到 `references/dialect_and_orm.md`，正文留导航，
  压至 421 行——修正了该技能与自身 references 内容重复的问题。

### Changed

- 三语言 README 数据刷新：**143 技能 / 37 包 / 18 链域 57 链**（新增 5 个主题分组）。

### Verified

- `validate_skills.py`：142 技能 / **0 error** / PASSED
- `skill-linter` 全仓：**0 FAIL**（整治前 52）
- `pytest`：271 passed
- `build.py`：37 个压缩包

### Added

- **新场景包 `Workspace Integrations`（外部集成，4 技能，全部自研）** —— 补齐长期空白的
  「外部集成」域（此前只有 git/GitHub 有覆盖）。四技能共享同一套操作契约：
  **写操作默认 dry-run 先出负载、凭证只从环境变量读取、脚本只做「请求构造 + 响应解析」
  的纯函数**——四个脚本仅用标准库（json/argparse/hashlib/pathlib），**不发任何 HTTP 请求**，
  因此在无凭证、无网络的环境下可完整实测；真实执行时由 AI/用户用 curl/SDK 注入凭证。
  - `notion-workspace`：`build-page`（构造创建页面请求体，区分 page/database 两种 `parent` 结构）、
    `build-database-query`（filter/sorts/游标分页，`page_size` 上限 100 本地拦截）、
    `parse-page`（10+ 种属性类型压平成 Markdown 表格）、`blocks-to-markdown`（9 种块类型映射，
    未映射类型渲染成 HTML 注释留痕）。SKILL.md 覆盖 `Notion-Version` 版本头、`has_more`/`next_cursor`
    游标分页、约 3 req/s 限速与退避、以及「未授权页面返回 404 而非 403」这一高频误判点。
  - `feishu-dingtalk-bridge`：`build-message` 按三家**各自**的协议构造负载（不做"通用负载再翻译"
    的伪抽象），`parse-webhook` 解析回调/响应并给出错误码定向解释（`310000`、`300001`、`19002`、
    `93000`、`45009`）。SKILL.md 含 13 行协议差异对照表（鉴权/加签/令牌周期/Markdown 支持/
    内容容器类型/@ 人实现/文本上限/成功判定/回调形态/频率限制）。钉钉加签算法以参考函数形式提供，
    脚本本身不持有密钥。
  - `issue-tracker-sync`：`build` 构造三家建单请求（Jira 嵌套 `fields` / Linear GraphQL mutation /
    GitHub 扁平 REST），`field-map` 打印优先级-状态-字段三张映射表（支持 `--json` 供程序消费），
    `weekly-report` 从 issue 列表离线渲染周报（按状态分组 + **阻塞项引用块置顶高亮**，
    兼容三家不同的响应包装层级）。SKILL.md 给出跨平台**状态语义映射表**——强调
    "语义对齐而非字符串对拷"，并记录 Jira `customfield_NNNNN` 与 Linear `labelIds` 需 UUID 等陷阱。
  - `cloud-drive-manager`：`plan-upload` 生成上传计划（文件清单 + 体积 + 目标路径 + 分片策略，
    可落 manifest JSON）、`checksum-plan` 生成**可被 `sha256sum -c` 直接消费**的校验清单、
    `parse-list` 归一化百度/阿里云盘/OneDrive 三家列表响应。SKILL.md 含三家 API 差异对照表、
    分片阈值依据（4MB / 100MB / 250MB，OneDrive 分片须为 320KiB 倍数）、**秒传原理说明**
    （哈希算法因平台而异，用错则永不命中），以及**删除操作的双重确认要求**——
    本技能**有意不提供删除命令**，只提供"看清将删什么"的能力。
- 新增链域 `integrations`（3 条链：weekly_status_broadcast / meeting_notes_distribution /
  deliverable_archive），全库 **16 链域 / 55 条链**。

## [0.17.0] - 2026-09-17

### Added

- **新场景包 ×2 — 补齐「工具与自动化」与「元技能」两个空白域**（对标 6 个主流 skill 生态来源的分布调研，
  见 [docs/SKILL-GAP-PLAN.md](docs/SKILL-GAP-PLAN.md)）：

  **`Toolsmith`（工具与自动化，4 技能，全部含实测脚本）**
  - `file-organizer`：目录体检（扩展名分布 + 1KB 快速判重）、整理计划（type/date）、执行（默认 dry-run）、
    重复文件处置建议；路径越界（`../`、绝对路径、符号链接外逃）全部拦截。
  - `batch-renamer`：模板序号 / 正则 / 前后缀 / EXIF 拍摄日期（无则回退 mtime）；两阶段改名支持互换；
    变更日志 + 一键 `--undo` 回滚。
  - `format-converter`：文档（pandoc）/ 图片（Pillow，含缩放质量）/ 音视频（ffmpeg）统一入口，
    依赖缺失给安装指引；拒绝跨管线转换（如 mp4→jpg）并给出正确做法。
  - `task-scheduler`：cron 表达式 → 中文描述（含 `@reboot`、闰年 2 月 29 日边界）、crontab 解析、
    三平台落地差异表（cron / launchd / 任务计划程序）；只生成不写入，避免不可撤销的误操作。

  **`Skill Forge`（技能锻造厂，3 技能）**
  - `skill-author`：一次性问齐 5 问 → 生成合规 SKILL.md；内联十诫；附可填空模板。
  - `skill-linter`：8 项静态检查（frontmatter / 命名 / 描述与触发词 / 骨架章节 / 行数 / 中文占比 /
    参考文件存在性 / 失败处置表行数），返回可做 CI 门禁的退出码。**首跑即抓出全仓 52 个技能的真实规范缺口。**
  - `skill-finder`：基于真实数据检索（名称加权 > 描述 > 正文）、按技能组合反查所属包、仓库统计。

- 新增链域 ×2：`tools`（messy_folder_cleanup / recurring_automation）、`meta`（new_skill_pipeline /
  discover_and_compose），全库 **15 链域 / 52 条链**。

### Changed

- 三语言 README 徽章与计数刷新：**140 技能 / 33 包 / 15 链域 52 链**。

### Known issues

- `skill-linter` 全仓扫描报 52 个 FAIL，集中在内容发布类技能（16 个平台技能普遍缺 `## 参考` 章节、
  失败处置表仅 3 行）。这是历史技能与现行骨架标准的差异，已记入下一批修复计划，不影响仓库门禁
  （`validate_skills.py` 仍为 0 error）。

### Added

- **新场景包 `Toolsmith`（工具与自动化，4 技能，全部自研）** —— 补齐长期空白的「工具与自动化」域。
  四技能共享同一套操作契约：**只读优先、dry-run 默认、不可逆动作需显式确认、留痕可回滚**。
  - `file-organizer`：目录体检（扩展名分布/体积分档/重复文件）、整理计划、执行、去重建议四子命令。
    判重用「文件大小 + 前 1KB 哈希」做预筛，避免全量读取大文件；`plan` 打印"将把 X 移到 Y"完整清单；
    `apply` 默认 dry-run，仅 `--yes` 落盘。`_resolve_within` 用 canonicalize-then-check 挡住
    `../` 与逃逸符号链接；冲突自动加 `_1` 序号；**永不删除文件**。
  - `batch-renamer`：`--pattern`（`{n}/{ext}/{stem}/{date}`）/`--regex`/`--prefix`/`--suffix`/
    `--exif-date`/`--lower`/`--upper` 多规则组合；**两阶段改名**（先临时名再终名）消除
    a↔b 互换的中途撞名；冲突一律跳过并报告；执行写 `rename-log.txt`（JSONL），`--undo` 逆序回滚。
  - `format-converter`：文档（pandoc）/图片（Pillow，含等比缩放与质量）/音视频（ffmpeg）/批量
    四子命令统一入口。每个子命令先探测外部依赖，缺失时按当前操作系统打印确切安装命令（退出码 4）；
    拒绝输入输出同路径；批量模式拦截跨管线转换（如 `.mp4`→`.jpg` 需抽帧，属另一类任务）。
  - `task-scheduler`：`cron-add` 生成 crontab 行+安装步骤（**不自动写入**，定时任务无撤销栈）、
    `cron-list` 解析 `crontab -l` 为可读表格、`cron-check` 把表达式翻成中文（如 `0 9 * * 1`
    → 每周一 09:00）并预测下次触发。SKILL.md 含 cron/launchd/schtasks 三平台差异表与
    「定时任务失败三大原因」（环境变量缺失、路径非绝对、权限不足）。croniter 可选，缺失时降级为
    内置解析器描述。

## [0.16.1] - 2026-09-16

### Added

- **细节词库 ×3（v0.16.0 词库计划的第二梯队，举一反三扫描全仓 13 域后按"零词库裸奔"优先补齐）**：
  - `music-generation/references/music-style-lexicon.md`：五槽位 Style 公式（曲风两级/情绪/人声三层/乐器点名/
    制作+BPM）、曲风族谱 9 族种子、情绪×BPM 对照（禁配警告）、结构/人声/乐器 tag 全集、8 种制作美学词、
    负面清单与 5 条现成种子——调研 Suno 官方与五家社区指南蒸馏，references 署名。
  - `ppt-builder/references/layout-and-chart-rules.md`：字号层级表（6 元素最小/推荐值）、信息密度三档、
    图表选择决策树（比较/趋势/占比/相关/流程→图型映射 + 图表纪律）、对齐网格、WCAG 对比度基准、负面清单。
  - `product-copywriter/references/copywriting-formulas.md`：10 型标题公式（带例）、PAS/FAB/AIDA 结构模板、
    CTA 按场景词库、四平台调性差异表（同一卖点四种写法）、负面清单。
- 交叉挂链 3 处：video-script-writer 与 storyboard-designer 挂 cinematography-lexicon（脚本镜头指示词
  统一从词库选），product-copywriter 挂 copywriting-formulas。

## [0.16.0] - 2026-09-16

### Added

- **细节词库 ×3（高密度模板，词条格式：术语 EN/CN + 效果 + 何时用 + prompt 示例）**：
  - `video-prompt-engineer/references/cinematography-lexicon.md`：17 种转场（smash cut/match cut/J-cut/
    invisible cut/seamless FPV fly-through…）、动作动词空间语义表（approaches vs comes）、微表情表演细节、
    速度节奏词、Runway 官方运动类型词、可灵物理属性描述法、Veo 3/Runway/Sora/可灵/即梦五模型方言速查、
    迭代修复对照表与负面清单——调研 Runway Gen-3 官方关键词体系与各家官方指南后蒸馏。
  - `image-prompt-engineer/references/visual-detail-lexicon.md`：三层光照（自然/戏剧/棚拍 30+ 词条）、
    构图 11 词条、焦段透视性格 10 词条、材质微细节与"材质×年代×色板×环境"堆叠公式、色彩方案、
    静态图动势词、负面词节制、五大场景模板。
  - `tts-voice-director/references/emotion-delivery-lexicon.md`：情绪→文案手法对照、标点停顿层级、
    重音位置规则、双人对话节奏、参数档位、"情绪平"修复路径。
- **新技能 ×5（方法论蒸馏自 Anthropic 公开技能文档思想，全部原创实现零复制，references 署名合规）**：
  - `docx-writer`（office-productivity 包）：Word 文档生成/读取/中文字体统一（eastAsia 处理），
    scripts/docx_ops.py 实测 create/inspect/styles 全通过。
  - `pdf-pipeline`（office-productivity 包）：merge/split/extract/meta/rotate + 表单字段探测 +
    扫描件 OCR 转线，scripts/pdf_ops.py 实测 6 子命令全通过。
  - `internal-comms-writer`（office-productivity 包）：内部通讯四文体（团队更新/全员公告/FAQ 回答/
    跨团队协调），四 W 一次问齐 + 原创自查清单，templates.md 全中文语境模板。
  - `webapp-flow-tester`（tdd 包）：Playwright 网页应用流程测试，scripts/with_server.py 实测
    起服务→就绪探测→测试→清理全生命周期（含 404 超时与退出码透传用例）。
  - `frontend-design-director`（visual-design-studio 包）：设计总监式两遍工作流 + 原创五类 16 条
    AI 味设计自查清单（ai-design-tells.md）。
- 新链 3 条：document_pipeline 重排（内宣→docx→excel→纪要→pdf）、frontend_design、web_flow_test；
  office 域 +pdf_pipeline 链。全量 126 技能文件 / 31 包 / 13 域。

## [0.15.0] - 2026-09-16

### Added

- **新场景包 ×4 / 新技能 ×10（第 13 个域：memory）**：
  - `memory-systems` 长期记忆系统：memory-architect（分层架构设计）/ memory-extractor（对话→记忆条目）/
    memory-manager（生命周期与冲突消解）/ memory-retriever（混合检索与预算注入）——方法论蒸馏自
    mem0、letta (MemGPT)、Claude memory tool，references 署名。
  - `de-ai-writing` 去 AI 味写作：ai-trace-auditor（痕迹体检，附实测脚本 trace_scanner.py：句长方差 +
    中英 AI 高频词表）/ humanize-rewriter（burstiness + 具体性 + 情绪注入）/ personal-voice-profile（个人风格画像）。
  - `homework-autopilot` 作业自动驾驶：assignment-intake（九题型审题拆解）/ solution-drafter（分题型作答）/
    own-voice-rewrite（学生口吻重写，红线：不虚构经历、保留可复述难度、不担保过检测）。
  - `image-studio` 画图工作台：组包 image-prompt-engineer / image-generation / visual-style-anchor / ai-cover-generator。
- 新链 6 条：full_memory_stack、retrofit_memory、populate_and_serve、homework_autopilot、
  humanized_homework、de_ai_pipeline。全量 122 技能 / 31 包 / 13 域 / 45 链，validate 0/0，pytest 257 passed。

## [0.14.1] - 2026-09-16

### Changed

- **全仓 SKILL.md 语言统一（113 篇）**：正文叙述一律中文，代码/命令/参数/专有名词保留英文，
  消灭同篇文档中英混排——44 篇以英文为主的技能全文翻译（含 infrastructure/security/containers
  15 个大文件与 scenarios/paper/ppt 全部），38 篇中文骨架中的残留英文块（标题/段落/表格句子）
  局部翻译；骨架章节名统一词汇表（输入清单/前置自检/工作流/参数速查表/失败处置表/交付标准）；
  frontmatter 机器匹配层（英文 description + 中英双语触发词）按规范保持不变。
- **排版修复**：拆分 resume-tailor / ai-baby-podcast / video-thumbnail / sample-skill 的稠密叙述块；
  全部块间保证空行分隔。门禁保持全绿（validate 0/0、pytest 257 passed、正文 <500 行）。

### Added

- **技能目录 / 下载站点（site/）**：零依赖静态站（纯 HTML/CSS/JS + 一份 data JSON），
  覆盖 113 个技能（112 个入包 + 1 个模板）/ 27 场景包 / 12 域 / 39 条技能链。支持**单个 SKILL.md 直接下载**
  （站点自带副本，不依赖 raw 服务）与**场景包 zip 双通道下载**（站内镜像 + GitHub/GitCode
  Release 链接，附件未上传时镜像保证按钮不失效）；实时搜索（命中词高亮）、域筛选、
  技能/场景包/技能链三视图、包内技能跳转、玄青/玄紫/玄黄 + 明暗换肤（localStorage 记忆）、
  12 域识别色 / 数字滚动 / 卡片入场动画 / 骨架屏 / `/` 聚焦搜索 / 回到顶部。
  新增 `tools/build_site.py`（数据生成）、`.github/workflows/pages.yml`
  （GitHub Actions 自动部署）、`docs/DEPLOY-SITE.md`。

### Changed

- **全仓 113 个 SKILL.md 逐篇内容质量重构（机器优先规范）**：统一骨架
  输入清单 / 前置自检 / 工作流（动作+预期+若失败三件套）/ 参数速查表 /
  失败处置表 / 交付标准 / 参考（何时读）。审计中实测脚本逐个核实，修复一批
  真实缺陷：编造的 CLI 参数（tex-cleaner `--check`、schema_explorer
  `--dialect` 等 4 处）、不存在的脚本引用（`spec_validator.py`）、缺
  `scripts/` 前缀的脚本路径（5 处）、编造的输出结构（2 处）、失真的
  compatibility 声明；盘上存在但从未被引用的 references 全部挂入参考章节。
  同轮完成机械规范化：全文单 H1、彩色 emoji 归零（保留 →≤≥✓① 等有用符号）、
  裸代码块补语言、标题粘连清零、行尾空白清理。门禁：pytest 257 passed /
  validate 0 error 0 warning / 正文全部 <500 行。

- **站点部署只走 main 分支，废弃发布分支**：删除 `tools/publish_site.py` 与远程
  `gh-pages` 分支。GitCode Pages 直接指向 `main` 的 `/site` 目录，GitHub Pages 走
  Actions（同样不产生分支）；`site/skills/`、`site/packs/` 生成副本相应改为**提交进
  main**（它们是站点下载本体，不进仓库 = 下载按钮全废）。

### Fixed

- **站点布局两处结构性 bug**（视觉上表现为：技能卡片飘在 hero 上、页脚顶到首屏、
  滚动后内容区一片空白、切换视图时新旧内容叠加）：
  1. 背景网格与卡片容器共用类名 `.grid`，两条规则合并后卡片容器继承
     `position: absolute; inset: 0` 脱离文档流 → 背景网格改名 `.bg-grid`；
  2. `.grid { display: grid }` / `.chain-view { display: block }` 覆盖了 UA 的
     `[hidden] { display: none }`，切 tab 后旧视图并未真正隐藏 → 显式
     `[hidden] { display: none !important }` 兜底。
- 站点卡片描述渲染用截断版 `short`、搜索匹配用完整 `desc`，命中词被截掉导致
  高亮落空 → 统一渲染完整 desc（CSS line-clamp 负责截断展示），删除 `short`
  字段与 `shorten()`。

- 三个语言 README 顶部的计数徽章停留在 87 技能 / 22 包 → 修正为 **113 / 27**
  （113 = 磁盘 `SKILL.md` 总数，其中 112 个打包进场景包，1 个 `sample-skill`
  为编写模板不入包）。
- `build.py` 的 `sync_manifest` 只对**新增**包写入 `skills`，已存在条目从不更新 →
  `manifest.json` 的 `ai-research-writing` 长期缺 12 个 paper 域技能，索引只有
  100 个技能，与 README 徽章和 `packs/*/pack.json` 都不一致。现改为**始终以
  pack.json 的 `skills` 为准**做 upsert，索引恢复 112 个入包技能。
- lit-review 的 `compatibility` 仍宣称 `--arxiv` 是"离线 mock、无网络调用" → 更正为
  真实 arXiv API（20s 超时 + 429 退避）并在失败时回退 mock、以 `data_source` 标注。

### Added

- **P3 清零轮**：tdd-guide 统一 CLI 入口 `tdd_cli.py`（7 子命令覆盖 8 库模块，
  rc 0/2/1 语义）；pipeline_orchestrator 补 5 步 runner（code_review /
  dependency_audit / ci_cd_setup / ship_gate / runbook_generation），
  full_project 4 步 → 9 步与链定义对齐，失败步骤向进程退出码传播；
  编排器 research 模式新增 `--offline` 熔断；lit-review `--arxiv` 真调
  arXiv API（HTTPS + 429 退避重试，失败自动回退 mock 并以 `data_source` /
  `warning` 诚实标注）；experiment-runner 输出带 `mode: "simulated"` 显式标注。

### Fixed

- **P3 清零轮**：dep_scanner 12 个解析器由吞异常改为严格 raise，
  非法清单计入 `parse_errors`（含 summary 计数 / 文本报告行 / recommendations
  WARNING），不再静默按 0 依赖；database-designer 与 sql-database-assistant 的
  migration_generator.py 经比对确认非重复实现（schema 对比迁移 vs 自然语言模板），
  双方 SKILL.md 与 docstring 划清边界互指；tdd-guide SKILL.md 纠正
  `tdd_workflow.py --phase` 失效引用。

## [0.14.0] - 2026-09-15

### Added

- **大规模全量测试轮（三层测试，详见 docs/FULL-TEST-REPORT.md）**：chains 静态一致性 +
  9 编排器 ×19 真实情景 dry-run + 139 个本地脚本 ×约 90 用例正例/异常双向深测。
- **链条大扩展：9 域 21 链 → 12 域 39 链，游离技能 53 → 1**。新增 chat 域
  （prompt_audit）、office 域（document_pipeline）、paper 域（full_paper / quick_draft /
  polish_only / submit_ready 四链）；programming 补登 32 技能 + 9 条专家链（security_fix /
  debug_hotfix / data_ml / math_modeling / api_design / infra_delivery / db_change /
  sre_readiness / release_audit）；video 补 pre_production 上游规划链；writing 登记
  全部 11 个发布平台技能并补齐 news_flash；design 补 thumbnail / banner 两链。全部经
  静态一致性校验。
- **补齐 12 个 paper 脚本技能的 SKILL.md**（lit-review / experiment-runner / figure-maker /
  arch-diagram / neural-net-draw / latex-formatter / self-reviewer / journal-adapt /
  anti-defensive / ai-humanizer / tex-cleaner / pub-plotter）并收编进 ai-research-writing
  包（7→19 技能）——此前它们无 SKILL.md、不在任何场景包，zip 下载拿不到。
- 26 个游离/上游技能 SKILL.md 补"继续调用 X——链条自动展开"衔接话术。

### Fixed

- **P0（4 项）**：paper 13 脚本 `main()` 返回码被 `__main__` 丢弃 → 进程恒 rc=0，
  编排器把失败当成功、门禁在编排层被静默绕过（13 处改 `sys.exit(main())`）；video 链
  真实模式文件交接断裂（tts 写 CWD 而非 audio-dir、lipsync 输出 `lipsync_scene_*.mp4`
  与 editor 期望 `scene_*.mp4` 契约不符，被 mock 掩盖——batch 加 `--audio-dir`、输出
  对齐命名，SKILLKIT_MOCK=1 真跑 6/6 闭环）；math `model_solver` LP 路径 `result.iter`
  必崩（scipy 无此属性 → `result.nit`）；`data_ml_pipeline` ml 脚本路径错致链条第 3 步
  必断（`ml/pipeline/` → `ml/ml-pipeline/`）。
- **P1（8 项）**：video 编排器无视 `--type` 硬编码 talking_character 步骤（现按链分流
  meme/tutorial，素材生成步如实标 manual）；writing content-editor 产物未落盘、seo 读
  编辑前稿（`--output edited.json` 接线，真跑验证）；ppt 编排器调用 5 个不存在的脚本而
  从不调 make_pptx.py（重构为 spec 骨架生成 → LLM 填充提示 → 真调 make_pptx 渲染，
  真跑产出 31 KB pptx）；code-intent-planner L2 失败 rc=0、visualizer 数据缺失 rc=0、
  math 四件套返回码不传播、code-generator/diagnoser 返回码、programming 编排器硬编码
  `python`（→ sys.executable）与 tdd 路径少一层。
- **P2（15 项）**：dep_scanner CVE 重复计数、ship_gate 未知 `--category` 静默通过、
  exercise_lint 空输入崩溃、figure_maker heatmap 假成功、latex/self/tex 缺文件 rc=0、
  topic_selector 非法 JSON 抛栈、outliner `--json-input` 强制 `--topic`、drafter 缺文件
  回溯、math/data_ml 编排器 dry-run 状态与失败 rc、programming 编排器 CWD 落盘垃圾等。
- 修复后回归：pytest 257 passed / 1 skipped；validate_skills 111 skills 0 err 0 warn；
  28 个 zip 重建（_all bundle 112 skills）。

### Added

- **新增场景包 `growth-marketing`（3 技能，自研）+ `marketing` 域链条**：
  `product-copywriter`（按受众决策阶段选转化框架 FAB/PAS/AIDA + 异议处理
  独立成段 + 广告法事实卫生）、`campaign-designer`（营销日历 + 渠道角色
  矩阵 + 单变量 A/B 变体对纪律）、`channel-adapter`（内置 5 渠道约束表——
  小红书字数/抖音口播节奏/朋友圈行数/邮件主题截断线/搜索广告关键词——
  channel_fit_check.py 机器校验，6 个 pytest 用例）。marketing_pipeline.py
  编排 + 注册 product_launch/single_post 两链。
- **新增场景包 `edu-craft`（3 技能，自研）+ `education` 域链条**：
  `course-designer`（学习契约 ≤3 问 + checkpoint 依赖排序 + 深度控制表）、
  `exercise-generator`（开放题严格题库，**禁选择题防蒙**，评分标准与题同出，
  exercise_lint.py 守门 + 5 个 pytest 用例）、`feynman-explainer`（费曼六拍
  循环 + "不太聪明的学生"反向教学 + 换角度重测闭环）。education_pipeline.py
  编排 + 注册 full_course/topic_mastery/remedial_only 三链。方法论借鉴
  AI-Learning-Agent / Feynman Learning Coach / 授悟 FeynMind 与掌握式学习，
  已署名。
- **仓库达成 100 技能 / 9 域全链条**：programming / video / writing / ppt /
  music / design / audio / marketing / education，每域具备"入口技能 →
  编排器 → 链条收口"的完整使用路径。

### Added

- **新增场景包 `visual-design-studio`（3 技能，自研）+ `design` 域完整链条**：
  `design-brief-interpreter`（模糊需求 → 7 字段可机检设计规格单，风格锚纪律
  借鉴 Anthropic canvas-design 与 designskills 的 design-context 先行模式）、
  `image-prompt-engineer`（五段式文生图 prompt + 文字渲染铁律"图上要可读文字
  选 GPT Image 系" + 摄影词汇 + 模型方言笔记）、`layout-spec-auditor`（内置
  8 平台规格表，审计比例/分辨率/文件限额/文字预算，附 spec_audit.py +
  8 个 pytest 用例）。`design_pipeline.py` 编排 + skill_chains.json 注册
  cover/poster/infographic 三条链。
- **新增场景包 `audio-studio`（3 技能，自研）+ `audio` 域完整链条**：
  `podcast-producer`（钩子→三段→CTA 大纲，纯口播词铁律"TTS 会读出一切标记"，
  附 script_lint.py 机器守门 + 5 个 pytest 用例）、`tts-voice-director`
  （跨引擎声音目录：Kokoro/DIA/Qwen3-TTS 气质→ID 映射 + ffmpeg 拼接计划）、
  `episode-publisher`（shownotes + podcasting 2.0 时间戳章节 + 平台元数据 +
  AI 内容披露行）。`audio_pipeline.py` 编排 + 注册 podcast_episode/
  document_to_podcast/audiobook_chapter 三条链。方法论提炼自 Podify、
  inference.sh skills 与开源 TTS 生态，已署名。
- 至此仓库 7 个域全部具备"入口技能 → 编排器 → 链条收口"的完整使用链条
  （programming / video / writing / ppt / music / design / audio）。

## [0.13.1] - 2026-09-14

### Added

- **新增场景包 `chat-prompt-craft`（1 技能，自研）**：面向豆包 / ChatGPT / Kimi /
  DeepSeek 等对话式助手的提示词工程——`chat-prompt-engineer` 双模式（task /
  agent）：task 模式按五要素公式（角色+背景+任务+要求+格式）写一次性任务提示词；
  agent 模式按五段骨架（人设/能力与流程/约束/输出格式/边界处理）写智能体
  system prompt；含反向约束纪律（禁用词表/字数硬限）、三轮迭代法（骨架→血肉
  →抛光）、`prompt_audit.py` 启发式结构审计（6 个 pytest 用例）。方法论提炼自
  豆包官方教程五要素公式、Coze 官方四段式与 CO-STAR 框架，已署名
  （见技能 sources-and-methodology.md）。
- **新增场景包 `video-design-studio`（4 技能，全部自研）**：把"生成前设计"从
  临时发挥变成可复用工作流——`storyboard-designer`（节拍表 → 逐场景 prompt 对
  → 连续性约束表，输出 `scene-NN.md` 9 字段结构，附场景 lint 脚本）、
  `shot-recipe-designer`（12 张镜头配方卡：establishing-wide / hook-pop-in /
  match-cut / beat-sync-cut 等）、`video-prompt-engineer`（六槽位结构 +
  write/audit 双模式 + 启发式审计脚本 + 相机词汇表 + 模型方言笔记）、
  `visual-style-anchor`（风格锚公式 + 角色一致性卡：身份行纪律/三视图/
  漂移审计/变体机制）。
- `docs/VIDEO-LANDSCAPE.md`：主流 AI 视频方案全景调研（闭源旗舰 / 中国系 /
  开源自托管三张矩阵表 + 六条跨模型硬纪律 + ComfyUI 关键帧管线工作流 +
  对本仓的 6 项 gap 分析），全部条目标注来源分级与快照日期。
- `video-prompt-engineer` 方言笔记扩充至 6 家模型（Sora 2 档位与对话块 /
  Veo 3.1 五段公式与名词式负向 / Runway Gen-4.5 运动优先 / Seedance 2.5 /
  Kling 3.0 / Wan 相机词前置与 I2V 纪律），新增音频扩展槽位说明。

### Fixed

- **G1 合规补齐**：60 个技能 description 追加排除句（"Do NOT use for X"），
  17 个平台绑定技能补 `compatibility` 字段，60 个技能补 `metadata.author`
  ——此前 `validate_skills.py` 不查这两项，属标准盲区。
- **G7 冒烟测试**：为 19 个自建技能补 `test_smoke_<skill>.py`（模块名唯一化
  避免 pytest 收集冲突），全量 227 passed / 1 skipped。
- **构建产物污染（重要）**：删除 `build.sh`——其 zip 排除规则 glob 对嵌套
  路径失效，产物混入 240 个 `__pycache__` 文件且哈希与 `build.py` 不一致；
  `build.py` 确立为唯一构建入口，README 同步更新。
- **CI 假绿（重要）**：CI 测试步骤由 subprocess 直跑改为 `python3 -m pytest`
  ——前者不会真正执行断言，测试绿但没测。
- 新增 `requirements.txt`（按用途分组，注明优雅降级）与 `pytest.ini`
  （过滤 `PytestCollectionWarning`，警告 3 → 0）。

## [0.13.0] - 2026-09-14

### Added

- **新增 4 个场景包，23 个技能从孤儿状态归位**（此前这些技能已在盘上但未纳入任何包，
  用户下载任何 zip 都拿不到）：
  - `ai-video-pipeline`（6 技能）：脚本 → 配音 → 口型 → 剪辑 → 字幕 → 封面，短视频全链路；
  - `ai-research-writing`（7 技能）：多轮检索 → 选题 → 大纲 → 初稿 → 润色 → SEO，
    含 `paper-topic-selector`（学术选题空白识别）；
  - `code-planning`（3 技能）：意图识别 → 结构化计划 → 两档代码生成 → 故障诊断；
  - `data-ml-science`（7 技能）：ETL → 特征 → 建模 → 求解 → 仿真 → 可视化 → ML 流水线。
- **补全 36 篇缺失的 references 文档**（约 5,000 行），修复 35 处 broken reference——
  这些引用此前指向不存在的文件，技能激活后必然执行失败。覆盖 video（8 篇）、
  writing/paper（9 篇）、programming 数据/调试/数学/ML（11 篇）、
  code-generator 模板（4 个 Jinja2 + 1 篇说明）。
- `code-generator` 补齐 Jinja2 模板并实渲染验证（Python 产物过 `py_compile`，
  TS 过 `tsc --strict`），模板渲染已固化为单测。
- `sql-database-assistant` 补齐 `schema_explorer.py`（支持 SQLite 实内省、
  JSON/CSV 输入、Markdown/JSON 输出），`skill-tester` 补齐 `audit_skills.py`
  （批量审计：校验 + 打分 + 安全三合一，支持 `--fail-under` 供 CI 使用）。

### Fixed

- **门禁假绿（重要）**：`tools/validate_skills.py` 的 `check_pack_consistency`
  把 orphan 警告写进了一个调用方丢弃的临时列表，导致 23 条警告既不打印也不计入
  `warn_total`——门禁显示 `warnings: 0` 实际是假象。现改为按技能名归桶统计。
- **manifest 漏包（重要）**：`build.py` 的 `sync_manifest` 只更新 manifest 中
  已存在的包，新增包（dist 里有 zip 但 manifest 无条目）被静默跳过。
  现改为以 `packs/*/pack.json` 为准做 upsert，并同步 `updated` 日期。
- **硬编码 mock 死代码**：`video-editor` / `video-lip-sync` / `video-thumbnail` /
  `video-voice-synth` 四个脚本存在 `MOCK_MODE = True` 常量，真实执行分支永远不可达。
  现改为 `--mock` 参数 + `SKILLKIT_MOCK` 环境变量，**默认真实模式**；缺依赖时
  输出安装指引并以非 0 退出，不再静默返回假结果。
- `code-generator` 生成的 `service.py` 缺 `from datetime import datetime`，
  任一 create/update 调用都会 `NameError` 崩溃——已修，并纳入单测。
- 11 个技能目录名与 frontmatter `name` 不一致（如 `video/editor` 声明
  `video-editor`），按规范 §1.1 统一为 `name` 全称，并修正 `paper_pipeline.py`
  中的路径引用。
- **12 个发布技能的 description 过短**（40–100 字符），模型无从判断是否加载，
  等于技能不存在。按规范 §1.2 四段式重写为 400–570 字符，补齐中英文触发短语
  与排除项，覆盖 CSDN / 简书 / 博客园静态部署 / 豆瓣 / 开源中国 / SegmentFault /
  V2EX / 百家号 / 头条 / 微博 / 小红书 / B站。
- 68 篇超过 100 行的 references 缺目录（违反门禁 G5），补齐带锚点链接的 TOC。
- **54 个技能 description 缺中文触发词**（规范 §3.4 要求触发短语双语，中文用户是主力）。
  按各技能真实能力逐个定制中文触发短语，现全仓 82 个技能 description 均含
  中英文触发短语 + 排除项。
- 三处 `./scripts/convert.sh` 被当作本地脚本引用，实为上游 claude-skills 仓库的
  转换工具（不随技能分发）——改为显式外部引用并标注来源仓库路径。
- **`code-intent-planner` 污染用户工作目录**：`pipeline.py` 把会话缓存写成
  当前目录下的 `_session_*.json`（与 `session_manager.py` 的
  `~/.code_intent_planner/sessions` 两套实现不一致），用户每次调用都在项目根
  留下一堆垃圾文件。现统一到规范路径，并支持 `SKILLKIT_SESSION_DIR` 覆盖；
  `_session_*.json` 同时加入 `.gitignore`。
- **`skill_chains.json` 引用幽灵技能**：ppt 域引用 6 个从未创建的技能
  （ppt-outline-architect 等），video 域引用 6 个改名前的旧目录名
  （script-writer → video-script-writer 等）。按实际存在的技能清理，
  可选依赖的 `?` 后缀语义保留。
- **编排器路径失配**：`video_pipeline.py`、`math_pipeline.py` 共 8 处引用
  改名前的旧目录名（`editor` → `video-editor` 等），任一编排调用都会
  `FileNotFoundError`——已全部修正。

### Removed

- 清理仓库根目录 12 个历史遗留的 `_session_*.json` 会话缓存（由上述
  写入缺陷产生，此前被误提交进版本历史）。
- 删除 `code-intent-planner/scripts/l2_flash.py`：硬编码 `MOCK_MODE = True`
  且括号未闭合（语法错误）、全仓无任何引用的孤儿死模块。

### Changed

- **CI 重写为三 job 流水线（重要）**：原 CI 只有 manifest JSON 校验 + build + zip
  产出三步，从未运行门禁——46 个 broken reference 因此直接进了 main。现拆为：
  `gate`（validate_skills.py 强制 0 错误 0 警告）、`build`（构建 + manifest
  覆盖断言 + 可复现性双构建哈希比对）、`tests`（全仓 py_compile + 26 个
  自验证测试脚本）。
- `install.sh` 跳过 `_all.zip` 的重复解压（此前解压合集包会把 83 个技能
  再覆盖安装一遍）。
- **项目完整性补齐**：新增 `.github/ISSUE_TEMPLATE`（bug report / feature request
  + config）与 `.github/PULL_REQUEST_TEMPLATE.md`；CHANGELOG 归档尾部遗留的
  第二个 `[Unreleased]` 节为 `[0.1.0]`（对应 tag `v0.1.0`，2026-08-23 版本基线
  重置提交）；补打 v0.2.0 / v0.3.0 历史 annotated tag（内容精确对应提交
  `03f4eb9` / `1e089a9`）；顶部增加版本体系说明，澄清 1.x → 0.x 重置史。
- 三语 README 深度对齐：英文版 Pack Details 18 处大小数字与 manifest 一致、
  发布流程示例统一为 `tools/release.py`、移除指向已删除文档的链接。
- 文档状态同步：`SOURCES.md` 重写为 83 技能 / 21 包双轨现状（上游 33 + 自建 50），
  `docs/VERSIONING.md` 发布流程移除已删除的 sync-mirrors.ps1 引用，
  `docs/DIRECTION-V2.md` 品类地图对齐实际交付。
- 门禁基线：**82 技能 / 21 包 / 0 错误 / 0 警告**（此前为 46 错误 / 83 警告）。
- 构建产物 21 个包 + `_all` 合集，21 个 sha256 全覆盖，连续两次构建哈希一致。

## [0.12.3] - 2026-08-26

### Fixed

- **构建不可复现修复**：zip 条目此前嵌入源文件时间戳，导致每次重建产生不同
  sha256（manifest 校验和随构建漂移、失去可信度）。现统一固定条目时间戳，
  相同输入产出字节级相同的 zip——已实测连续两次构建哈希完全一致。
- 平台仓库描述补齐：GitCode 与 Gitee 均已通过各自 API 写入英文简介
  （GitHub 此前已完成 description + 15 topics）。

## [0.12.2] - 2026-08-26

### Changed

- **可发现性优化（对标同类头部仓库后择优采纳）**：
  - 三语 README 增加徽章行（License/Skills/Packs/Gitee/GitCode）与底部三平台 Star 引导——awesome-claude-skills(13k★) 与 anthropics/skills 均有徽章，属同行标准做法；
  - **不添加自定义 Logo**：头部同类仓库均无 Logo 图标，遵循"同行没做就不做"原则。
- **平台元数据**：GitHub 仓库 description 与 15 个 topics 已通过 API 生效；Gitee/GitCode 的 API 拒绝 git 凭据直调（需网页端设置或专用私人令牌）。

### Fixed

- **sync-mirrors.ps1 假报错修复**：PowerShell 5.1 在 EAP=Stop 下把 git 的 stderr 进度（如 "Everything up-to-date"）渲染为红色异常并可能中断脚本；现改为经 cmd /c 进程级合并流、仅以退出码判定成败。实测三平台一次跑通、退出码 0。

## [0.12.1] - 2026-08-26

### Changed

- 三语 README 同步至当前状态：17 包 / 59 技能总览表、三个新包详情段（ai-media-toolkit / office-productivity / viral-entertainment）、项目文档链接区、发布示例命令更新。
- sync-mirrors.ps1 升级为三平台同步（GitCode + Gitee + GitHub）：支持环境变量令牌与命名 remote 凭据双通道，自动推送 tags；新增 gitee/github 命名 remote。
- 许可确认：全仓统一 Apache-2.0（LICENSE、frontmatter、CONTRIBUTING 已一致）。

## [0.12.0] - 2026-08-26

### Changed

- **`meme-mascot-shorts` 重写为 `nailong-laugh-shorts`**（按需求改为"大笑奶龙"直出版）：
  - 删除路线门与梗源复盘，改为纯生产手册：形象描述库（官方风基础体/大笑变异体/比例失调"奶蛙感"三套可复制 prompt）、双管线（A 表情包成精图生视频 / B 真人动作套壳还原原梗扭曲感）、自制笑声变声器配方、概率 bait 文案模板表、皮肤矩阵系列化；
  - 风险提示压缩为一行事实陈述（非盈利常见后果=限流下架、商用必追责），决策权交还用户。

### Fixed

- **发布流程缺陷（重要）**：release.py 此前只提交 manifest+CHANGELOG，导致
  v1.7.0–v1.11.0 的标签树缺失当时未暂存的新增技能文件。现 release.py 增加
  脏工作区硬门禁：有任何未提交变更即拒绝发版；本版为首个全量完整树。
- 补交 v1.7.0 以来全部场景技能与三个新包文件。

## [0.11.0] - 2026-08-26

### Added

- **品类 G 第二个技能 `meme-mascot-shorts`**（"大笑奶龙"式魔性萌物短视频，基于 2026-01 梗源调研）：
  - 梗源拆解：真人动作 AI 套壳（军体拳→奶龙="奶蛙"）× 变声器魔性笑声 × 概率 bait 文案的四方缝合公式；
  - **三条合规路线硬性前置**（A 正版素材 / B 原创同类萌物【推荐】 / C 直接用 IP=高侵权风险）：奶龙 IP 方有活跃维权判例（玩具销售赔偿、商标异议胜诉、上海知产法院首例 AI LoRA 侵权案判赔 5 万），Route C 需用户书面确认已知风险；
  - Route B 原创度自检底线（剪影/五官/配色两项以上明显不同）、"听觉锤先行"设计法、hook-and-body 皮肤矩阵系列化；
  - references/meme-case-study.md：梗起源与官方应对失效的传播学复盘（脱敏公式）。
- `viral-entertainment` 包扩至 2 技能。
- 门禁基线：59 技能 / 17 包 / 0 错误 / 76 警告；18 个分发包 sha256 全覆盖。

## [0.10.0] - 2026-08-26

### Added

- **品类 C 落地：新包 `office-productivity` 四件套**
  - `ppt-builder`：大纲公式→逐页 spec JSON→捆绑脚本渲染真 .pptx（python-pptx 缺席时优雅降级 markdown），含 spec 校验器与 7 个单测；
  - `excel-assistant`：先勘察后动手、一步一改带前后证据、编码三连降序尝试、交付 `_cleaned` + findings.md；
  - `resume-tailor`：JD 提取→差距矩阵→STAR 量化重写→ATS 卫生检查，双产物（定制稿+逐条可追溯 edit_log），硬禁造假红线；
  - `meeting-notes`：议题分段→决议/讨论/行动三分类（原话作证据）→行动项表格（无主必标 `<待指派>`），固定骨架输出。
- **品类 G 上线：新包 `viral-entertainment` 首个技能 `ai-baby-podcast`**（AI 宝宝播客/会说话角色短视频全流水线，基于 2026-08 成熟打法调研）：
  - 形象图 prompt 公式 → 反差脚本公式（成人观点×婴儿脸+固定口癖）→ 成人声 TTS 干声 → 口型驱动（短句先行）→ 剪映收尾五步；
  - 角色一致性纪律：角色卡七件套、锁定 seed/音色、每 10 条漂移审计、永不从文字重生角色（references/character-consistency.md）；
  - 合规红线四条硬禁令：《人工智能生成合成内容标识办法》显式声明要求（2025-09-01 施行）、纯虚构形象、不克隆名人声纹肖像、避开平台点名整治题材。
- DIRECTION-V2 品类表新增 G 行与电影级/宣传片系列愿景备注。
- 门禁基线：58 技能 / 17 包 / 0 错误 / 76 警告；测试 180 通过 +1 条件跳过；18 个分发包含 sha256。

## [0.9.0] - 2026-08-26

### Added

- **品类 B 第三个技能 `music-generation`**（brief → 配乐/歌曲）：三槽位风格公式（流派+乐器+情绪用途）、纯音乐/歌词双模式、端点 404 快速失败（VERIFY BEFORE USE，禁止本地合成兜底）、六症状失败处置表、量化交付标准。
- **`ai-cover-generator` 跨包挂入 `ai-media-toolkit`**（封面图生成复用既有资产，不造重复轮子），包扩至 4 技能。
- 门禁基线：53 技能 / 0 错误 / 76 警告；16 个分发包 sha256 全覆盖。

## [0.8.0] - 2026-08-26

### Added

- **品类 B 第二个技能 `image-generation`**（文生图 + 图生图，同骨架同纪律）：
  - 尺寸约束表（16 倍数、宽高比 1:3–3:1、总像素上下限，标 VERIFY BEFORE USE）与常用尺寸清单；
  - 参数错误自动修正重试路径；轮询 3–5 秒/次、120 次上限；
  - 六症状失败处置表；量化交付标准（非空 png + 时间戳命名 + 绝对路径回报）;
  - 提示词四段式公式：主体细节 / 风格媒介 / 构图视角 / 文字排版（含"精确引述文字内容"规则）。
- **`ai-media-toolkit` 包扩至 2 技能**（对齐 SkillsBench"每包 2–3 个聚焦技能"最优区间），双语描述同步更新。
- 门禁基线：52 技能 / 0 错误 / 76 警告；16 个分发包 sha256 全覆盖。

## [0.7.0] - 2026-08-26

### Added

- **品类 B（AI 媒体生成）首个示范技能 `video-generation`**，按 SKILL-STANDARD-v2 §4 骨架编写：
  - 输入清单 + 一次性询问模板；前置自检（网关探活，失败即停、禁止回退本地渲染）；
  - 工作流五步全部"命令+预期输出+失败分支"三件套；60 次轮询上限；
  - 失败处置表六种症状对应处置；交付标准量化（非空 mp4 + 时间戳命名 + 绝对路径回报）；
  - `references/prompt-recipes.md`：四槽位提示词公式与强弱示例对照。
  - 网关地址走 `VIDEO_GATEWAY_BASE` 环境变量（默认 `http://127.0.0.1:30080`）。
- **新场景包 `ai-media-toolkit`**（15 号包），manifest 同步注册。
- 门禁基线更新：51 技能 / 0 错误 / 76 警告；16 个分发包全部带 sha256。

## [0.6.3] - 2026-08-26

### Fixed

- **install.ps1 平铺解压修复**：原先按 zip 名嵌套子目录解压，导致 Windows 用户安装后技能无法被 AI 工具发现；现与 install.sh 同语义平铺，并在安装后自检 SKILL.md 可发现数量。
- **build.py 两处修复**：
  - `_common` 公共库此前因全局累积状态被误打进所有后序场景包，现仅打包真正依赖它的包；
  - 构建完成后自动把每个包的实际 `size_kb` 与 `sha256` 回填 `manifest.json`，分发产物首次可校验。
- **导航断链清零**（由新增 validator 驱动）：
  - `ship-gate` 补齐被三处引用的 `references/checks.md` 检查目录（与 scanner 内 CHECKS/MANUAL_CHECKS 注册表逐条对齐）；
  - `slo-architect` 移除指向不存在文件的引用、修正跨技能路径表述；
  - `cnblogs-skill/image-guide` 移除指向不存在旧版文档的指针；
  - `bilibili/weibo/jianshu/csdn` 四个 publisher 中 `_common` 相对路径更正为打包布局真实形态。
- manifest.json 中文描述中重复的"豆瓣"去除。

### Added

- **治理制度文档**：`docs/VERSIONING.md`（SemVer 语义、发布流程、历史处置决定：不回溯伪造 tag、自本版起 tag 全覆盖）、`docs/DIRECTION-V2.md`（通用场景工作流库战略）、`docs/SKILL-STANDARD-v2.md`（机器优先编写规范与门禁清单）。
- **tools/validate_skills.py** 质量门禁：frontmatter 合规、引用完整性（区分"导航断链=ERROR"与"宣传性缺失脚本=WARN"）、渐进披露行数、绝对路径检测、pack↔磁盘一致性。当前基线：**50 技能 0 错误 / 76 警告（存量债务已登记）**。
- **tools/release.py** 发布助手：SemVer 校验、CHANGELOG 小节强制、manifest 版本同步、annotated tag。
- **tools/migrate_metadata_v2.py** 一次性迁移（已完成）：全部 50 个技能补齐 `license` 与 `metadata.version/category/verified-date`。
- CONTRIBUTING.md 接入门禁：PR 必须通过 validator + pytest + build 三关。

### Changed

- `terraform-patterns` 正文 740→417 行（规范 G5），CI/CD、多云、OpenTofu、Terragrunt 等章节移入 `references/cicd-and-advanced-patterns.md`。

### Security

- `.git/config` 中内嵌的明文访问令牌已从 remote URL 移除（该令牌应视为已泄露，需在 GitCode 后台吊销轮换）。

## [0.6.2] - 2026-08-25

### Added

- **content-publishing 场景包扩展至 18 个技能**（第二批量产完成，覆盖主流中文平台）：
  - `csdn-publisher`：CSDN 博客发布/管理，Web 内部 API，7 子命令，7 测试。
  - `jianshu-publisher`：简书发布/管理，Web 内部 API，4 子命令，4 测试。
  - `bilibili-publisher`：B 站视频/专栏/动态发布，官方 API + Web API 混合，5 子命令，4 测试。
  - `toutiao-publisher`：今日头条/抖音文章/微头条发布，官方 API + Web API，2 子命令，4 测试。
  - `baijiahao-publisher`：百家号文章/视频/草稿发布，官方 API，3 子命令，3 测试。
  - `xiaohongshu-publisher`：小红书笔记草稿/发布/编辑/删除，Web 内部 API，4 子命令，4 测试。
  - `weibo-publisher`：微博发布/转发/评论/删除/图片上传，官方 API + Web API，3 子命令，4 测试。
  - `douban-publisher`：豆瓣日记/广播/小组话题发布，Web 内部 API，3 子命令，3 测试。
  - `v2ex-publisher`：V2EX 发帖/回复/节点列表，Web 内部 API，3 子命令，3 测试。
  - `segmentfault-publisher`：SegmentFault 文章/提问发布，Web 内部 API，3 子命令，3 测试。
  - `oschina-publisher`：开源中国博客/问答/动态，官方 API + Web API，3 子命令，3 测试。
  - `static-blog-deploy`：Hexo/Hugo/GitHub Pages/GitLab Pages/Vercel/Netlify 静态站点部署，6 子命令，3 测试。
- 全新增 12 个技能，content-publishing 包从 6 扩展至 18 技能（覆盖 CSDN、简书、B站、头条、百家号、小红书、微博、豆瓣、V2EX、SegmentFault、开源中国、静态博客部署）。
- 所有新技能均遵循统一安全设计：默认 dry-run、凭据环境变量隔离、端点常量标注 VERIFY BEFORE USE、带单元测试。

## [0.6.1] - 2026-08-25

### Refactored

- 提取发布公共工具 `skills/writing/_common/publish_common.py`，集中以下重复逻辑：
  - `http_json`：统一 GET/POST、cookie 支持 str|dict、网络异常包装为 `PublishError`
  - `dry_run_guard`：统一 dry-run 提示
  - `load_credential`：统一从环境变量/文件加载凭据
  - `dump_json(data)`：统一 `json.dumps(data, ensure_ascii=False, indent=2)` 输出（消除 12+ 处重复）
  - `load_json(path)`：统一 BOM-safe JSON 读取（消除 4 处 `open + json.load` 重复）
- 简化 3 个脚本的 import 前导（10 行→3 行，删除死代码路径）
- wechat / juejin / ai-cover-generator / cross-post-orchestrator 四个脚本改为复用该模块，
  删除各自重复的 HTTP、UA、`_guarded_execute`、`load_cookie`、`json.dumps` 实现
- `build.py` 现在会把 `_common` 一并打包进引用它的场景包（如 content-publishing），
  保证用户解压后即可运行；本地经 junction 调用时 `os.path.realpath` 也能正确解析

## [0.6.0] - 2026-08-25

### Added

- **content-publishing 场景包扩至 6 个技能**（第一批产线完成）：
  - `wechat-mp-publisher`：公众号官方草稿箱/发布 API 客户端（token/uploadimg/add_material/draft_add/freepublish），multipart 手工构造、默认 dry-run，7 个单元测试。
  - `juejin-publisher`：掘金 Web 内部接口客户端；端点常量显式标注 VERIFY BEFORE USE 并附 DevTools 核对步骤（不虚构 API），6 个单元测试。
  - `cross-post-orchestrator`：manifest 驱动的多平台编排器——plan 模式零联网检查各平台前置条件，run 模式调度兄弟技能 CLI，无脚本平台输出精确手工清单并返回退出码 2；发布台账持久化，8 个单元测试。
  - `ai-cover-generator`：对接本地图片服务（127.0.0.1:30080）——尺寸约束校验（16 倍数/宽高比/总像素）、task_id 容错解析、轮询下载、PIL 压缩 <1MB；服务不可达明确报错，7 个单元测试。
- `cnblogs-skill` 补充单元测试（5 个，含 BOM 回归用例）。

### Verified

- 全部 33 个单元测试通过（6 技能 × unittest discover）。
- agentseed MCP 门禁：4 个新脚本 verify_code suspects=[] 且 scan_hallucination clean/blocking=false。

## [0.5.0] - 2026-08-25

### Added

- **Scenario-skill track**: the repo now maintains self-authored China-platform automation skills alongside upstream curation, under `skills/writing/`.
- Restored `zhihu-content-manager` and reworked it:
  - removed sandbox-hardcoded paths (`/app/chromium-...`, `/tmp/.pip-global/...`); browser path now resolves via env var or Playwright's bundled Chromium.
  - decoupled from private image-generation tooling; any text-to-image tool works.
  - moved personal style/content-ops guidance to `references/content-ops.md` (customizable baseline).
  - added `scripts/zhihu_html_lint.py` — offline pre-publish gate (bare `<img>`, `<table>`, empty paragraphs, unescaped code brackets, Latin-1 mojibake) with 10 unit tests.
- Restored `cnblogs-skill` and reworked it:
  - fixed BOM bug in `cnblogs-pre-publish-check.py` (`utf-8-sig`); h1 detection now works on Windows-authored files.
  - removed private tool dependencies (`dumate-browser-use`, `baidu-image-gen`); generalized to any Playwright session / image tool.
- New pack `content-publishing` bundling both skills.

### Removed

- Deceptive engagement playbook: fake-persona reply script for "are you AI?" questions and daily quota farming table. Replaced with honest, quality-first interaction guidelines.

## [0.4.0] - 2026-08-25

### Removed

- **Dropped all self-authored skills** — the repository is now a pure curated collection of the upstream project:
  - `agent-builder-skill` (was in pack `ai-agent-development`)
  - `chinese-parents-skill` (was in pack `family-communication`)
  - `cnblogs-skill` (was in pack `blog-writing`)
  - `zhihu-content-manager` (was in pack `zhihu-writing`)
  - Removed now-empty packs: `blog-writing`, `family-communication`, `zhihu-writing`. Packs: 16 → 13; skills: 37 → 33.

### Changed

- `manifest.json`: removed self-authored entries; source notes now point to the single upstream.
- Added [SOURCES.md](SOURCES.md) — upstream address and step-by-step update guide for all skills.

## [0.3.0] - 2026-08-23

### Fixed

- **skill-tester**: the entire `scripts/` suite advertised by SKILL.md was missing. Implemented all four tools for real: `skill_validator.py` (structure/tier compliance), `script_tester.py` (syntax/imports/runtime with timeout), `quality_scorer.py` (4×25% scoring, `--include-security` rebalances to 5×20%, `--minimum-score` CI gate), `security_scorer.py` (four-component security posture, 53 unit tests pass). Also restored the two reference docs (`skill-structure-specification.md`, `tier-requirements-matrix.md`) and gave the bundled sample skill proper YAML frontmatter; regenerated its golden validation report.
- **env-secrets-manager**: `scripts/env_auditor.py` (referenced 4× as the core tool) did not exist. Implemented a real auditor: provider-key detection (OpenAI/GitHub/AWS/PEM/Slack/JWT), sensitive-assignment detection, `.gitignore` coverage check, `.env ↔ .env.example` drift, rotation-date awareness; output values always redacted. Added README, sample fixture + golden audit report, and 12 unit tests (65 total across both fixed skills).
- **quality_scorer**: security dimension now correctly maps the 0–25 component scale to a percentage (was reporting ~20 instead of ~80).

### Added

- `build.py` — cross-platform packaging (same semantics as `build.sh`) so Windows users can build without bash/zip.
- `_all.zip` convenience bundle — every skill from every pack in a single download (37 skills).

### Changed

- **Merged near-duplicate skills** to stop shipping reinvented wheels:
  - `database-schema-designer` merged into `database-designer` (>70% overlap). Unique material preserved in `references/schema-design-playbook.md` (multi-tenancy, RLS policies, seed data) and `references/full-schema-examples.md`.
  - `agent-workflow-designer` merged into `agent-designer`. Pattern templates and handoff contract preserved in `references/workflow_patterns.md`; `workflow_scaffolder.py` moved over.
  - Total curated skills: 35 → 33.
- **observability-designer**: dropped its duplicate `slo_designer.py`; SLO work now routes cleanly to `slo-architect` (docs updated).
- **code-reviewer / pr-review-expert**: disambiguated trigger phrases — code-reviewer is the static-analysis engine, pr-review-expert owns the end-to-end PR review workflow.
- **env-secrets-manager**: trimmed sections duplicating `secrets-vault-manager` (cloud store comparison, rotation execution, audit logging) into cross-references; this skill keeps env hygiene and detection.

### Security

- Removed stray working file from agent-builder-skill; zhihu-content-manager SKILL.md now carries proper YAML frontmatter so tools can load it.
- **Removed personal account data from the public skills**: `cnblogs-skill` and `zhihu-content-manager` no longer hardcode username/blogId/column IDs/article ledgers in SKILL.md. Account data moved to gitignored `references/account.local.json` (shipped template: `account.example.json`); `*.local.json` is excluded from git and from all scene-pack zips (verified).
- Added `.github/workflows/skill-quality.yml`: runs bundled unit tests, builds all packs, and gates changed skills on YAML frontmatter presence + dangling script references.
- Added `sync-mirrors.ps1` for pushing to the GitCode + Gitee mirrors (tokens via env vars, never stored). GitHub is dropped as a distribution platform for now; upstream attribution links are unaffected.

## [0.2.0] - 2026-08-18

### Changed

- Restructured from per-skill zips into scene packs: one pack = one real-world scenario containing multiple skills.
- 16 scene packs covering coding, ops, writing and life scenarios.
- 35 developer skills curated from `alirezarezvani/claude-skills` (MIT), combined with 4 self-authored skills.
- `build.sh` now packages by scene pack (`packs/*/pack.json` → `dist/*.zip`).
- `manifest.json` now lists packs with per-skill source attribution.

### Added

- 16 curated scene packs under `packs/`.
- Source attribution for every skill (`alirezarezvani/claude-skills (MIT)` / `Morningstar202604 (self-authored)`).

## [0.1.0] - 2026-08-23

版本基线重置为 0.x 体系的首个版本（tag `v0.1.0` 指向 commit `ebd7f0a`
"unify Apache-2.0 license, reset version baseline"）。此前该仓库短暂使用过
一套 1.x 版本号，相关记录见顶部「版本体系说明」。

### Added

- Initial SkillKit hub: curated skill packs for AI tools.
- Positioning: "the scenario is the answer — grounded in platform + tool".
- 4 self-authored skill packs:
  - `agent-builder-skill` — one-line requirement to a production-grade AI agent.
  - `chinese-parents-skill` — Chinese-parent behavior simulation / diagnosis / coping.
  - `cnblogs-skill` — automated blog publishing & management on cnblogs.com.
  - `zhihu-skill` — Zhihu article publishing & management.
- `build.sh` — one-command packaging of `skills/*` into `dist/*.zip`.
- `install.sh` / `install.ps1` — one-click install of all packs.
- Bilingual docs: English primary (`README.md`) + Chinese (`README.zh-CN.md`).
- License: Apache License 2.0.

<!-- version compare links (Keep a Changelog). 0.4.0-0.6.1 have no tags;
     see the version-scheme note at the top of this file. -->
[0.1.0]: https://gitcode.com/badhope/awesome-skillkit/releases/tag/v0.1.0
[0.2.0]: https://gitcode.com/badhope/awesome-skillkit/compare/v0.1.0...v0.2.0
[0.3.0]: https://gitcode.com/badhope/awesome-skillkit/compare/v0.2.0...v0.3.0
[0.6.2]: https://gitcode.com/badhope/awesome-skillkit/compare/v0.3.0...v0.6.2
[0.6.3]: https://gitcode.com/badhope/awesome-skillkit/compare/v0.6.2...v0.6.3
[0.7.0]: https://gitcode.com/badhope/awesome-skillkit/compare/v0.6.3...v0.7.0
[0.8.0]: https://gitcode.com/badhope/awesome-skillkit/compare/v0.7.0...v0.8.0
[0.9.0]: https://gitcode.com/badhope/awesome-skillkit/compare/v0.8.0...v0.9.0
[0.10.0]: https://gitcode.com/badhope/awesome-skillkit/compare/v0.9.0...v0.10.0
[0.11.0]: https://gitcode.com/badhope/awesome-skillkit/compare/v0.10.0...v0.11.0
[0.12.0]: https://gitcode.com/badhope/awesome-skillkit/compare/v0.11.0...v0.12.0
[0.12.1]: https://gitcode.com/badhope/awesome-skillkit/compare/v0.12.0...v0.12.1
[0.12.2]: https://gitcode.com/badhope/awesome-skillkit/compare/v0.12.1...v0.12.2
[0.12.3]: https://gitcode.com/badhope/awesome-skillkit/compare/v0.12.2...v0.12.3
[0.13.0]: https://gitcode.com/badhope/awesome-skillkit/compare/v0.12.3...v0.13.0
[Unreleased]: https://gitcode.com/badhope/awesome-skillkit/compare/v0.14.0...HEAD
[0.14.0]: https://gitcode.com/badhope/awesome-skillkit/compare/v0.13.1...v0.14.0
[0.13.1]: https://gitcode.com/badhope/awesome-skillkit/compare/v0.13.0...v0.13.1
