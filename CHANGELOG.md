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
[Unreleased]: https://gitcode.com/badhope/awesome-skillkit/compare/v0.13.0...HEAD
