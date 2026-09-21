#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
scenario_overrides.py — 第三代场景台架的逐技能定制输入（SCRIPT_OVERRIDES）。

为什么需要：121 个脚本技能的 CLI 形态各异（子命令 / 必填文件 / 专用 JSON 契约 / 双输入），
纯自动推导只能覆盖「参数名语义清晰」的大多数；这里为其余技能给**场景真实输入**——
不是占位符，而是能被技能当真用掉的内容（合法题库、真实 JD、可解析的 spec…）。

files 契约：
  - 值为字符串 → 按文本写入（相对 work 目录，可带子目录，自动建父目录）
  - 值以 "@" 开头 → 二进制夹具构建器：@png / @wav / @docx:<正文> / @pdf
seed_args 令牌：
  - {work} → 本技能 work 目录；{repo} → 仓库根；{<文件名>} → files 里建好的文件路径
  - {scene_dir} → 预置的样例文件目录（report_v1.md / report_v2_final.md / img.png）
cwd: "work" → 子进程以 work 目录为 cwd（避免技能把产物写进仓库根）
"""
REPO_MARKER = "scenario_overrides"

PROMPT_TEXT = ("拍一支 30 秒的赛博朋克城市夜景短片：雨夜霓虹街道，镜头低角度缓慢推进，"
               "霓虹灯牌在积水中倒影，一个穿雨衣的身影撑伞走过，光斑闪烁，"
               "35mm 胶片颗粒感，时长 30 秒。")

EXERCISE_BANK = '''# 题库

### Q1 [recall]
题干：用自己的话定义"过拟合"，不抄教材。
参考答案：训练误差持续下降但泛化误差上升的状态；要素：训练/泛化分离、记忆噪声。
评分标准：5 分制——要素各 1 分 + 表述完整 1 分。
常见陷阱：把"训练误差高"当过拟合。
关联：CP2

### Q2 [transfer]
题干：推荐系统把用户看过的都推给用户，这属于什么问题？写出机制层面的理由。
参考答案：过拟合用户历史；要素：泛化失败、多样性坍缩。
评分标准：5 分制——机制判定 3 分 + 理由 2 分。
常见陷阱：只说"不好"不给机制。
关联：CP3
'''

AGENT_EVAL_CASE = jsonl = (
    '{"prompt": "总结这段日志", "response": "## 结论\\n服务在 14:02 出现连接超时。\\n'
    '| 指标 | 值 |\\n|---|---|\\n| 超时率 | 12% |\\n来源：内部监控 2026-09 摘要。", '
    '"expects": {"min_length": 30, "must_include": ["超时"], '
    '"evidence": ["14:02", "连接超时"], "forbidden": ["rm -rf /"]}}\n')

MODEL_SPEC = ("{\"model_type\": \"LP\", \"name\": \"预算分配\", "
              "\"objective_coeffs\": [3.0, 2.0], \"A_ub\": [[1.0, 2.0], [2.0, 1.0]], "
              "\"b_ub\": [40.0, 30.0], \"bounds\": [[0, null], [0, null]]}")

OPENAPI_SAMPLE = ("{\"openapi\": \"3.0.0\", \"info\": {\"title\": \"Orders\", \"version\": \"1.0\"}, "
                  "\"paths\": {\"/orders\": {\"get\": {\"summary\": \"list orders\", "
                  "\"responses\": {\"200\": {\"description\": \"ok\"}}}}}}")

SCHEMA_BEFORE = ("{\"tables\": {\"users\": {\"columns\": {"
                 "\"id\": {\"type\": \"int\"}, \"email\": {\"type\": \"varchar\"}}}}}")
SCHEMA_AFTER = ("{\"tables\": {\"users\": {\"columns\": {"
                "\"id\": {\"type\": \"int\"}, \"email\": {\"type\": \"varchar\"}, "
                "\"email_verified\": {\"type\": \"boolean\"}}}}}")

QUERIES_JSON = ("{\"queries\": ["
                "{\"id\": \"q1\", \"table\": \"users\", \"type\": \"SELECT\", "
                "\"where_conditions\": [{\"column\": \"email\", \"operator\": \"=\"}], "
                "\"frequency\": 1000}, "
                "{\"id\": \"q2\", \"table\": \"users\", \"type\": \"SELECT\", "
                "\"where_conditions\": [{\"column\": \"id\", \"operator\": \"=\"}], "
                "\"frequency\": 5000}]}")

INCIDENT_JSON = ("{\"description\": \"Database connection timeouts spiking since 14:02\", "
                 "\"service\": \"user-service\", \"affected_users\": \"80%\", "
                 "\"business_impact\": \"high\"}")

CRD_YAML = ("apiVersion: apiextensions.k8s.io/v1\nkind: CustomResourceDefinition\n"
            "metadata:\n  name: widgets.example.com\nspec:\n  group: example.com\n"
            "  names:\n    kind: Widget\n    plural: widgets\n"
            "  scope: Namespaced\n  versions:\n    - name: v1\n      served: true\n"
            "      storage: true\n      schema:\n        openAPIV3Schema:\n"
            "          type: object\n          properties:\n            spec:\n"
            "              type: object\n            status:\n              type: object\n"
            "      subresources:\n        status: {}\n")

ALERTS_JSON = ("{\"alerts\": [{\"name\": \"HighLatency\", \"expr\": \"latency_p99 > 1s\", "
               "\"for\": \"5m\", \"severity\": \"warning\"}, "
               "{\"name\": \"Down\", \"expr\": \"up == 0\", \"for\": \"1m\", "
               "\"severity\": \"critical\"}]}")

AGENT_LOGS = ("{\"execution_logs\": ["
              "{\"task_id\": \"t1\", \"agent_id\": \"planner\", "
              "\"start_time\": \"2026-09-01T10:00:00\", \"end_time\": \"2026-09-01T10:02:00\", "
              "\"status\": \"success\", \"tokens\": 1200, \"tool_calls\": 2, \"retries\": 0}, "
              "{\"task_id\": \"t2\", \"agent_id\": \"executor\", "
              "\"start_time\": \"2026-09-01T10:02:00\", \"end_time\": \"2026-09-01T10:05:00\", "
              "\"status\": \"failure\", \"tokens\": 3400, \"tool_calls\": 5, \"retries\": 1}]}")

COMMIT_SUBJECTS = ("feat: add retry client\nfix: handle zero division in divide\n"
                   "chore: bump deps\nbad message without prefix\n")

MCP_MANIFEST = ("{\"tools\": [{\"name\": \"get_weather\", \"description\": \"query weather\", "
                "\"inputSchema\": {\"type\": \"object\", \"properties\": {\"city\": "
                "{\"type\": \"string\"}}, \"required\": [\"city\"]}}]}")

VIDEO_SCRIPT_JSON = ("{\"scenes\": [{\"id\": 1, \"text\": \"开场：城市夜景\", \"duration\": 3}, "
                     "{\"id\": 2, \"text\": \"主角走过积水街道\", \"duration\": 4}]}")

CROSS_MANIFEST = ("{\"title\": \"为什么你的单元测试测不到真正的 bug\", "
                  "\"markdown\": \"article.md\", "
                  "\"targets\": [{\"platform\": \"zhihu\", \"enabled\": true}, "
                  "{\"platform\": \"juejin\", \"enabled\": false}]}")

JD_TEXT = ("岗位职责：负责后端服务开发（Python），要求 3 年以上经验，熟悉异步编程（asyncio）、"
           "单元测试与 CI；有高并发服务经验优先。\n任职要求：本科及以上，能独立交付。")

RESUME_TEXT = ("张三 · 后端工程师\n- 3 年 Python：爬虫与数据管道\n- 维护 CI 流水线（GitHub Actions）\n"
               "- 给开源库 aiohttp 提过 2 个 PR（异步超时处理）\n- 写过 300+ 单元测试\n")

DEBT_JSON = ("{\"debt_items\": [{\"file_path\": \"a.py\", \"type\": \"long_function\", "
             "\"severity\": \"medium\", \"effort_hours\": 3, \"description\": \"函数 120 行\"}, "
             "{\"file_path\": \"b.py\", \"type\": \"duplication\", \"severity\": \"low\", "
             "\"effort_hours\": 1, \"description\": \"重复工具函数\"}], "
             "\"scan_metadata\": {\"scan_date\": \"2026-09-01\"}}")

ETL_RAW = "name,age,city\n张三,28,北京\n,35,上海\n李四,,深圳\n王五,41,\n"

WIKI_NOTE = "# 笔记：测试金字塔\n单元测试快而多，E2E 慢而少。\n关联：[[测试左移]]\n标签: testing\n"

SCENE_01 = (
    "# Scene 01\n\n"
    "画幅: 16:9\n景别: 全景\n画面: 雨夜霓虹街道，积水倒影\n"
    "运镜: 低角度缓慢推进\n光影: 霓虹主光，冷暖对比\n声音: 雨声 + 低频氛围乐\n"
    "视频 prompt: rainy neon street, low angle slow push, 35mm film grain\n"
    "转场: 硬切\n时长: 3s\n")

SCENE_02 = (
    "# Scene 02\n\n"
    "画幅: 16:9\n景别: 特写\n画面: 穿雨衣的身影撑伞走过\n"
    "运镜: 手持跟随\n光影: 轮廓光勾勒背影\n声音: 脚步声渐强\n"
    "视频 prompt: figure in raincoat walking, handheld follow, neon rim light\n"
    "转场: 叠化\n时长: 4s\n")

ARTICLE_MD = ("## 为什么要批量发布\n\n一次写作、多平台分发是内容团队的标准动作。"
              "手工复制粘贴既容易漏平台，又容易格式走样。\n\n"
              "## 编排器怎么解决\n\n以 post.manifest.json 为唯一事实源，"
              "先 plan 预览各平台的落库计划，再 run 逐平台执行并记录台账。\n\n"
              "## 小结\n\n台账可审计、失败可重试，是编排器区别于脚手架脚本的关键。\n")

SCRIPT_OVERRIDES = {
    # ---------- audio / chat ----------
    "audio/podcast-producer": {"seed_args": [
        "--text", "HOST: 欢迎来到本期节目。\nGUEST: 谢谢，今天聊聊本地大模型为什么跑不动。\n"
                  "HOST: 先从内存带宽说起。\nGUEST: 7840HS 的 780M 共享约 12GB 内存，带宽是瓶颈。"]},
    "chat/chat-prompt-engineer": {"seed_args": [
        "--prompt", "你是资深 Python 后端工程师（角色）。背景：团队要聚合公开新闻做内部检索。"
                    "请帮我写一个新闻爬虫程序。要求：① 只爬公开站点并遵守 robots.txt ② 限速 1 请求/秒 "
                    "③ 失败指数退避重试 3 次 ④ 结果输出 JSON。输出格式：给出完整代码与运行说明。"]},
    # ---------- design ----------
    "design/frontend-component-lab": {"seed_args": [
        "--name", "PricingCard", "--props", "title,price", "--out", "{work}/comp"]},
    "design/layout-spec-auditor": {"seed_args": [
        "--width", "1080", "--height", "1920", "--platform", "douyin-vertical"]},
    # ---------- education ----------
    "education/exercise-generator": {"seed_args": ["--text", EXERCISE_BANK]},
    # ---------- integrations ----------
    "integrations/cloud-drive-manager": {"seed_args": [
        "plan-upload", "--dir", "{scene_dir}", "--remote", "backup/notes"]},
    "integrations/issue-tracker-sync": {"seed_args": [
        "build", "--title", "修复分页在第二页报 500", "--tracker", "github",
        "--body", "复现步骤：翻到第二页即 500。期望：正常返回。",
        "--repo", "acme/pay-service", "--priority", "P1"]},
    "integrations/notion-workspace": {"seed_args": [
        "build-page", "--title", "九月复盘", "--parent", "1f2e3d4c5b6a",
        "--properties", "{\"tags\": {\"multi_select\": [\"月度\"]}}"]},
    # ---------- knowledge ----------
    "knowledge/knowledge-graph-builder": {"seed_args": [
        "extract", "{scene_dir}"], "cwd": "work"},
    "knowledge/personal-wiki": {"seed_args": [
        "init", "{work}/wikinew"], "cwd": "work",
        "post": [["index", "{work}/wikinew"], ["stats", "{work}/wikinew"]]},
    # ---------- marketing ----------
    "marketing/channel-adapter": {"seed_args": [
        "--channel", "moments", "--text",
        "用了三年终于把备份流程自动化了：一条命令，本地加密，增量上传。"
        "省下的时间陪家人。评论区聊聊你的备份方案，抽 2 人送同款 NAS。"]},
    # ---------- meta ----------
    "meta/agent-eval-harness": {"files": {"cases.jsonl": AGENT_EVAL_CASE},
                                "seed_args": ["--input", "{cases.jsonl}", "--index", "0"]},
    "meta/skill-finder": {"seed_args": ["stats"]},
    "meta/skill-linter": {"seed_args": ["--json", "{repo}/skills/tools/batch-renamer"]},
    # ---------- office ----------
    "office/career-ops-lite": {"files": {"jd.txt": JD_TEXT, "resume.txt": RESUME_TEXT},
                               "seed_args": ["--jd", "{jd.txt}", "--resume", "{resume.txt}",
                                             "--write", "-o", "{work}/score.json"]},
    "office/docx-template-fill": {"files": {"tpl.docx": "@docx:尊敬的{{name}}，您的订单 {{order_id}} 已发货。",
                                            "data.json": "{\"name\": \"张三\", \"order_id\": \"A1024\"}"},
                                  "seed_args": ["--template", "{tpl.docx}", "--data", "{data.json}",
                                                "--list-only"]},
    "office/docx-writer": {"files": {"doc_src.md": "# 标题\n正文第一段。\n\n## 小节\n列表项一。\n"},
                           "seed_args": ["create", "--input", "{doc_src.md}",
                                         "--output", "{work}/out.docx", "--title", "季度汇报"]},
    "office/epub-builder": {"files": {"book.md": "# 我的书\n\n## 第一章\n开篇。\n\n## 第二章\n发展。\n"},
                            "seed_args": ["build", "{book.md}", "--out", "{work}/book.epub",
                                          "--title", "我的书", "--author", "张三"]},
    "office/pdf-pipeline": {"files": {"sample.pdf": "@pdf"},
                            "seed_args": ["meta", "{sample.pdf}"]},
    # ---------- paper ----------
    "paper/neural-net-draw": {"seed_args": [
        "--layers", "4:input,8:conv,4:pool,2:output", "--label", "TinyNet",
        "--style", "typed-blocks"]},
    "paper/paper-topic-selector": {
        "files": {"cands.json": ("{\"candidates\": [{\"topic\": \"多智能体预算约束协调\", "
                                 "\"keywords\": [\"multi-agent\"], \"workload_weeks\": 6}, "
                                 "{\"topic\": \"RAG 幻觉评测基准\", \"keywords\": [\"hallucination\"], "
                                 "\"workload_weeks\": 3}]}"),
                  "cons.json": "{\"time\": {\"deadline_weeks\": 8}, \"gpu\": \"1x4090\", "
                               "\"venue\": \"neurips\"}"},
        "seed_args": ["--candidates", "{cands.json}",
                      "--constraints", "{\"time\": \"3mo\", \"gpu\": \"1x4090\"}",
                      "--top-n", "2"]},
    # ---------- ppt ----------
    "ppt/ppt-builder": {"files": {"spec.json": (
        "{\"deck_title\": \"季度技术分享\", \"slides\": ["
        "{\"title\": \"背景\", \"bullets\": [\"流量翻倍\", \"故障率持平\"], \"notes\": \"开场\"}, "
        "{\"title\": \"方案\", \"bullets\": [\"缓存前置\", \"读写分离\"], \"notes\": \"重点\"}]}")},
        "seed_args": ["{spec.json}", "{work}/deck.pptx"]},
    # ---------- programming ----------
    "programming/ai-engineering/mcp-server-builder": {
        "files": {"manifest.json": MCP_MANIFEST},
        "seed_args": ["--input", "{manifest.json}", "--format", "json"]},
    "programming/ai-engineering/skill-tester": {
        "seed_args": ["--json", "{repo}/skills/tools/batch-renamer"]},
    "programming/api/api-design-reviewer": {"seed_args": ["--sample", "--format", "json"]},
    "programming/architecture/migration-architect": {
        "files": {"before.json": SCHEMA_BEFORE, "after.json": SCHEMA_AFTER},
        "seed_args": ["--before", "{before.json}", "--after", "{after.json}",
                      "--type", "database", "--format", "json"]},
    "programming/architecture/monorepo-navigator": {
        "seed_args": ["--json", "{repo}/tools"]},
    "programming/architecture/senior-architect": {
        "seed_args": ["{repo}/tools", "--format", "ascii", "--type", "component"]},
    "programming/cicd/ci-cd-pipeline-builder": {
        "seed_args": ["--repo", "{repo}", "--platform", "github", "--format", "json"]},
    "programming/cicd/ship-gate": {"seed_args": [
        "{work}", "--json", "--no-interactive", "--category", "SEC"],
        "accept_rc": [1], "require_json_key": "summary.verdict"},
    "programming/code-quality/dependency-auditor": {
        "seed_args": ["{repo}/tools", "--format", "json", "--quick-scan"]},
    "programming/code-quality/tech-debt-tracker": {
        "files": {"debt.json": DEBT_JSON},
        "seed_args": ["--format", "json", "{work}/debt.json"]},
    "programming/code-quality/tdd-guide": {
        "files": {"coverage.lcov": "TN:\nSF:src/pay.py\nDA:1,1\nDA:2,0\nDA:3,1\nend_of_record\n"},
        "seed_args": ["{coverage.lcov}", "--threshold", "80"]},
    "programming/data/etl-builder": {
        "files": {"raw.csv": ETL_RAW},
        "seed_args": ["--source", "{raw.csv}", "--target", "{work}/out.json",
                      "--transform", "drop_null,trim"]},
    "programming/database/database-designer": {
        "files": {"schema.json": SCHEMA_BEFORE, "queries.json": QUERIES_JSON},
        "seed_args": ["--schema", "{schema.json}", "--queries", "{queries.json}",
                      "--format", "json"]},
    "programming/database/sql-database-assistant": {"seed_args": [
        "--change", "add email_verified boolean to users", "--dialect", "postgres",
        "--format", "sql", "--json"]},
    "programming/github/changelog-generator": {
        "files": {"subjects.txt": COMMIT_SUBJECTS},
        "seed_args": ["--input", "{subjects.txt}", "--format", "json"]},
    "programming/incident/incident-commander": {
        "files": {"incident.json": INCIDENT_JSON},
        "seed_args": ["--input", "{incident.json}", "--format", "json"]},
    "programming/incident/slo-architect": {"seed_args": ["--sample", "--format", "json"]},
    "programming/infrastructure/kubernetes-operator": {
        "files": {"crd.yaml": CRD_YAML},
        "seed_args": ["--crd", "{crd.yaml}", "--format", "json"]},
    "programming/infrastructure/observability-designer": {
        "files": {"alerts.json": ALERTS_JSON},
        "seed_args": ["--input", "{alerts.json}", "--analyze-only",
                      "--report", "{work}/report.json", "--format", "json"]},
    "programming/math/model-solver": {"files": {"spec.json": MODEL_SPEC},
                                      "seed_args": ["--spec", "{spec.json}"]},
    "programming/ml/ml-pipeline": {"files": {"data.csv": (
        "age,income,tenure,churn\n25,3000,1,0\n41,8000,6,0\n33,5200,3,1\n"
        "47,9100,9,0\n29,4100,2,1\n52,12000,12,0\n35,6000,4,0\n28,3800,1,1\n")},
        "seed_args": ["--data", "{data.csv}", "--target", "churn", "--cv", "3"]},
    "programming/performance/performance-profiler": {
        "seed_args": ["{repo}/tools", "--json"]},
    "programming/planning/web-search": {"seed_args": [
        "Python asyncio 教程", "--engine", "ddg", "-m", "3", "-f", "json", "--no-cache"]},
    "programming/security/env-secrets-manager": {"seed_args": ["{repo}/tools", "--json"]},
    "programming/security/pii-redactor": {"seed_args": [
        "{repo}/tools", "--dry-run", "--strategy", "mask"]},
    "programming/security/secrets-vault-manager": {"seed_args": ["--sample", "--json"]},
    "programming/testing/webapp-flow-tester": {"seed_args": [
        "--cmd", "python -m http.server 8123", "--port", "8123", "--timeout", "30",
        "--", "python", "-c", "print('flow-ok')"]},
    "programming/workflow/agent-designer": {
        "files": {"logs.json": AGENT_LOGS},
        "seed_args": ["{work}/logs.json", "-o", "{work}/eval", "--format", "json"]},
    # ---------- tools ----------
    "tools/bank-statement-reconcile": {
        "files": {"stmt.csv": "date,item,amount\n2026-09-01,高铁票,553.00\n2026-09-03,午餐,32.50\n",
                  "bill.csv": "date,item,amount\n2026-09-01,高铁票,553.00\n2026-09-03,午餐,35.00\n"},
        "seed_args": ["--statement", "{stmt.csv}", "--billing", "{bill.csv}"]},
    "tools/batch-renamer": {"seed_args": [
        "preview", "{scene_dir}", "--pattern", "report_{n:02d}.md"]},
    "tools/file-organizer": {"seed_args": ["scan", "{scene_dir}"]},
    "tools/format-converter": {"files": {"pic.png": "@png"},
                               "seed_args": ["image", "{pic.png}", "{work}/pic_small.png"]},
    "tools/invoice-organizer": {"files": {
        "invoices/发票-餐饮-32.5.pdf": "@pdf", "invoices/发票-交通-553.pdf": "@pdf",
        "invoices/收据-住宿-420.pdf": "@pdf"},
        "seed_args": ["--src", "{work}/invoices", "--dst", "{work}/organized"]},
    # ---------- video ----------
    "video/storyboard-designer": {"files": {
        "scenes/scene-01.md": SCENE_01, "scenes/scene-02.md": SCENE_02},
        "seed_args": ["{work}/scenes"]},
    "video/video-editor": {"files": {"script.json": VIDEO_SCRIPT_JSON},
                           "seed_args": ["--script", "{script.json}", "--mock",
                                         "--output", "{work}/out.mp4"]},
    "video/video-lip-sync": {"files": {"face.png": "@png", "line.wav": "@wav"},
                             "seed_args": ["--face", "{face.png}", "--audio", "{line.wav}",
                                           "--mock", "--output", "{work}/lipsync.mp4"]},
    "video/video-prompt-engineer": {"seed_args": ["--prompt", PROMPT_TEXT, "--mode", "audit"]},
    "video/video-subtitles": {"seed_args": [
        "--text", "大家好，欢迎来到本期节目。", "--start", "0", "--end", "5",
        "--output", "{work}/subs.srt"]},
    "video/video-thumbnail": {"seed_args": [
        "--title", "为什么你的单元测试测不到真正的 bug", "--style", "funny",
        "--platform", "bilibili", "--mock"]},
    "video/video-voice-synth": {"seed_args": [
        "--text", "大家好，欢迎来到本期节目。", "--voice", "narrator_01", "--mock"]},
    # ---------- writing ----------
    "writing/ai-trace-auditor": {"files": {"draft.md": (
        "# 深入探讨：在当今快速发展的时代\n"
        "首先，我们需要理解基础概念；其次，动手实践不可或缺；最后，持续学习至关重要。"
        "总而言之，这值得我们深入思考。值得注意的是，技术在不断发展。\n")},
        "seed_args": ["{draft.md}"]},
    "writing/article-drafter": {"seed_args": [
        "--topic", "为什么你的单元测试总是测不到真正的 bug", "--audience", "初级到中级工程师"]},
    "writing/article-outliner": {"seed_args": [
        "--topic", "为什么你的单元测试总是测不到真正的 bug", "--type", "technical",
        "--length", "medium"]},
    "writing/blog/cnblogs-skill": {"files": {"post.md": (
        "发布前自检一篇：正文含代码块与列表。\n\n## 小节\n\n```python\nprint('ok')\n```\n")},
        "seed_args": ["--title", "发布前检查", "{post.md}"]},
    "writing/content-editor": {"seed_args": [
        "--text", "在当今快速发展的技术时代，首先我们要理解概念，其次要动手实践，"
                  "最后要持续学习。", "--style", "technical"]},
    "writing/orchestrator/cross-post-orchestrator": {
        "files": {"post.manifest.json": CROSS_MANIFEST,
                  "article.md": "# 为什么你的单元测试测不到真正的 bug\n\n正文。\n" * 4,
                  "zhihu_state.json": "{}"},
        "seed_args": ["--manifest", "{post.manifest.json}", "plan"],
        "cwd": "work"},

    # ---------- writing / 发布类（计划模式：不发网络请求，只打印落库计划） ----------
    "writing/blog/csdn-publisher": {
        "files": {"post.md": ARTICLE_MD},
        "seed_args": ["draft-save", "--title", "一次写作多平台分发：编排器设计",
                      "--markdown", "{post.md}", "--brief", "以 manifest 为唯一事实源的多平台发布编排",
                      "--category-id", "2", "--tags", "python,自动化"]},
    "writing/blog/jianshu-publisher": {
        "files": {"post.md": ARTICLE_MD},
        "seed_args": ["draft-save", "--title", "一次写作多平台分发：编排器设计",
                      "--markdown", "{post.md}", "--brief", "manifest 驱动的发布编排器"]},
    "writing/blog/static-blog-deploy": {
        "seed_args": ["github-pages"]},
    "writing/community/douban-publisher": {
        "seed_args": ["note-create", "--title", "一次写作多平台分发：编排器设计",
                      "--content", "以 post.manifest.json 为唯一事实源，先 plan 后 run，台账可审计。"]},
    "writing/community/oschina-publisher": {
        "seed_args": ["blog-publish", "--title", "一次写作多平台分发：编排器设计",
                      "--content", "以 manifest 为唯一事实源，先 plan 后 run。",
                      "--catalog", "1"],
        "env": {"OSCHINA_ACCESS_TOKEN": "st-dry-run-token"}},
    "writing/community/segmentfault-publisher": {
        "seed_args": ["article-save", "--title", "一次写作多平台分发：编排器设计",
                      "--content", "以 manifest 为唯一事实源，先 plan 后 run，台账可审计。"]},
    "writing/community/v2ex-publisher": {
        "seed_args": ["topic-create", "--title", "一次写作多平台分发：编排器设计",
                      "--content", "以 manifest 为唯一事实源，先 plan 后 run。",
                      "--node-id", "1"]},
    "writing/juejin/juejin-publisher": {
        "files": {"post.md": ARTICLE_MD},
        "seed_args": ["draft-save", "--title", "一次写作多平台分发：编排器设计",
                      "--markdown", "{post.md}", "--brief", "manifest 驱动，台账可审计",
                      "--category-id", "2"]},
    "writing/news/baijiahao-publisher": {
        "seed_args": ["draft-save", "--title", "一次写作多平台分发：编排器设计",
                      "--content", "以 manifest 为唯一事实源，先 plan 后 run。",
                      "--category-id", "2"],
        "env": {"BAIJIAHAO_ACCESS_TOKEN": "st-dry-run-token"}},
    "writing/news/toutiao-publisher": {
        "seed_args": ["article-publish", "--title", "一次写作多平台分发：编排器设计",
                      "--content", "以 manifest 为唯一事实源，先 plan 后 run。"],
        "env": {"TOUTIAO_ACCESS_TOKEN": "st-dry-run-token"}},
    "writing/social/weibo-publisher": {
        "seed_args": ["post-web", "--text",
                      "本地大模型跑不动？先看内存带宽：7840HS 的 780M 共享 12GB，实测瓶颈清晰。"],
        "env": {"WEIBO_COOKIE": "SUB=_st_dry_run_; SSOLoginState=1789000000"}},
    "writing/social/xiaohongshu-publisher": {
        "seed_args": ["draft-save", "--title", "本地大模型跑不动？先看内存带宽",
                      "--content", "7840HS 的 780M 共享 12GB 内存，带宽才是瓶颈。实测数据见正文。"]},
    "writing/video/bilibili-publisher": {
        "files": {"post.md": ARTICLE_MD},
        "seed_args": ["article-save", "--title", "一次写作多平台分发：编排器设计",
                      "--content", "{post.md}", "--summary", "manifest 驱动的发布编排"],
        "env": {"BILI_COOKIE": "SESSDATA=st_dry_run_"}},
    "writing/wechat/wechat-mp-publisher": {
        "files": {"content.html": "<p>以 manifest 为唯一事实源，先 plan 后 run。</p>"},
        "seed_args": ["add-draft", "--title", "一次写作多平台分发：编排器设计",
                      "--content-html", "{content.html}",
                      "--thumb-media-id", "thumb_media_123", "--author", "工程团队"],
        "env": {"WECHAT_MP_APPID": "st-dry-run-appid", "WECHAT_MP_SECRET": "st-dry-run-secret"}},
}
