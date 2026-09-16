---
name: "cross-post-orchestrator"
description: "一篇文章多平台发布编排器。读取 post.manifest.json，检查各平台前置条件（凭据/登录态/账号文件），生成执行计划；对已脚本化的平台（公众号、掘金）调度对应技能 CLI，无脚本的平台输出精确手工清单；维护发布台账。默认 plan 模式绝不联网。当用户提到 多平台发文、一键分发文章、同步发布到多个平台、发布计划、cross-post、publish to multiple platforms、one-click distribute、multi-platform publishing 时使用。 Do NOT use for platform-specific formatting fixes (delegated to sibling skills), nor for single-platform deep publishing operations."
license: Apache-2.0
compatibility: Requires network access to multiple Chinese content platforms via their web endpoints and valid session credentials in environment variables. Python 3.8+.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: "content-publishing"
  verified-date: "2026-08-26"
---

# 跨平台发布编排技能

**规划器 + 调度器**——不重复实现平台逻辑，复用各平台技能。本脚本自身零网络发送：脚本化平台由子技能 CLI 完成（其 `--execute` 控制真发），无脚本平台输出手工清单。

| 平台 | 适配方式 | 前置条件 |
|------|---------|---------|
| wechat_mp（公众号） | 调度 `wechat-mp-publisher` CLI | 环境变量 WECHAT_MP_APPID/SECRET |
| juejin（掘金） | 调度 `juejin-publisher` CLI | 环境变量 JUEJIN_COOKIE |
| cnblogs（博客园） | 输出手工清单（按其 publish-api.md 流程） | account.local.json 存在 |
| zhihu（知乎） | 输出清单（浏览器自动化走 zhihu-content-manager） | zhihu_state.json 存在 |

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| `--manifest <path>` | 是 | post.manifest.json 路径，含 title/markdown/targets 三个必填字段 |
| manifest.markdown | 是 | 相对 manifest 所在目录的 Markdown 文件路径，文件必须已存在 |
| manifest.targets[].platform | 是 | 取值：wechat_mp / juejin / cnblogs / zhihu |
| manifest.targets[].enabled | 否 | 默认 true，false 则状态 skipped |
| targets[].thumb_media_id（wechat_mp） | 条件必需 | 还需工作目录下有 article.html，二者缺一则 [SKIP] |
| targets[].category_id / tag_ids / article_id（juejin） | 条件必需 | 缺省时用脚本内置默认值，正式发布应填真实值 |
| 环境变量 WECHAT_MP_APPID / WECHAT_MP_SECRET / JUEJIN_COOKIE | 条件必需 | 对应平台 ready 的前提 |

缺输入时一次性问齐：
「请一次性提供：① 文章标题；② Markdown 文件路径；③ 目标平台列表及各自参数（公众号：thumb_media_id；掘金：category_id、tag_ids；知乎/博客园：登录态文件位置）。不逐条追问。」

## 前置自检

```bash
python3 --version                                    # 需 ≥ 3.8
test -f post.manifest.json && echo manifest-ok       # manifest 存在
python3 - <<'EOF'                                    # Markdown 文件存在（manifest.md 字段）
import json, os, sys
m = json.load(open("post.manifest.json", encoding="utf-8"))
sys.exit(0 if os.path.exists(os.path.join(os.path.dirname(os.path.abspath("post.manifest.json")), m["markdown"])) else 1)
EOF
python3 scripts/cross_post.py plan --manifest post.manifest.json   # 就绪检查（零网络）
```

任一失败 → 修复对应项（补凭据 / 补文件 / 修正 manifest 字段）→ 重跑，通过前 STOP，不进入执行步骤。

## 工作流

### 步骤 1：准备 manifest

动作：复制 `examples/post.manifest.json` 到工作目录，填入标题、markdown 路径、各平台参数。
预期：manifest 含 title / markdown / targets 字段；targets 中 platform 均在 wechat_mp/juejin/cnblogs/zhihu 内。
若失败：`ValueError: manifest 缺少必填字段: <key>` 或 `ValueError: 不支持的平台: <platform>` → 按报错补字段或改平台名。

### 步骤 2：生成计划（默认动作，零网络请求）

```bash
python3 scripts/cross_post.py plan --manifest post.manifest.json
```

预期：表格输出每个平台状态 `ready` / `missing-credentials` / `blocked-md-missing` / `skipped`，退出码 0。
若失败：退出码 1 = 存在阻塞项 → 按 detail 列补前置条件后重跑。

### 步骤 3：向用户展示计划并确认

动作：把步骤 2 的表格原样展示给用户，等待明确确认；发布类操作逐平台确认，不要一次全发。
预期：用户明确同意后才进入步骤 4。
若失败：用户不同意或要求修改 → 更新 manifest 回到步骤 2。

### 步骤 4：逐平台执行

```bash
python3 scripts/cross_post.py run --manifest post.manifest.json --only juejin
```

预期：脚本化平台打印 `[RUN] python <子技能脚本> --execute ...` 并继承其安全约定（真发由子技能自身控制）；成功后自动追加台账。无脚本平台打印 `[MANUAL]` 精确操作清单，整体退出码 2 提示需人工介入。
若失败：`[FAIL] <platform> 退出码 N` → 用该平台子技能脚本单独重跑定位；`[SKIP] wechat_mp 需要 article.html 与 thumb_media_id` → 在工作目录准备 article.html 并在 manifest 填 thumb_media_id。

### 步骤 5：核对台账

```bash
python3 scripts/cross_post.py ledger --manifest post.manifest.json
```

预期：JSON 输出台账条目（时间戳/平台/标题/状态），每个成功平台一条。
若失败：打印「台账为空」但用户确认已发布 → 检查 manifest 的 ledger_file 路径与工作目录是否一致。

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| `--manifest` | 文件路径 | 必填，post.manifest.json |
| 子命令 `plan` | — | 生成计划，零网络，退出码 0/1 |
| 子命令 `run` | `--only <platform>` | 逐平台执行；--only 缺省则跑全部 enabled 平台 |
| 子命令 `ledger` | — | 打印 published.ledger.json 内容 |
| manifest.ledger_file | 文件名 | 缺省 `published.ledger.json` |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|-------------|------|------|
| `FileNotFoundError: manifest 不存在` | --manifest 路径错误 | 核对路径后重跑 |
| `ValueError: manifest 缺少必填字段: <key>` | 缺 title/markdown/targets | 补字段 |
| `ValueError: 不支持的平台: <x>` | platform 拼写不在四平台内 | 改为支持的值 |
| plan 退出码 1 | 有 missing-credentials / blocked-md-missing | 按 detail 补凭据或文件 |
| run 退出码 2 | 输出了 [MANUAL] 手工清单 | 按清单人工操作，或先只跑脚本化平台 |
| `[SKIP] wechat_mp 需要 article.html 与 thumb_media_id` | 工作目录缺 article.html 或 manifest 未填 thumb_media_id | 补齐后重跑 |
| `[FAIL] <platform> 退出码 N` | 子技能脚本失败（凭据/参数/风控） | 查子技能 SKILL.md 的失败处置表，单独重跑该平台 |

## 安全规则

1. `plan` 是默认动作且零网络请求；`run` 也只做本地调度，真正发送由各平台技能的 `--execute` 控制。
2. AI 的标准动作序列：`plan` → 向用户展示 → 用户确认 → `run --only <platform>` 逐个执行。
3. 发布类操作永远逐平台确认，不要一次全发。

## 交付标准

- 成功定义：每个目标平台返回 ready 且发布成功，或输出可执行的手工清单。
- 产物：`published.ledger.json`（manifest 同目录，每次成功发布自动追加时间戳/平台/标题/状态）。
- 验证完整性：`python3 scripts/cross_post.py ledger --manifest post.manifest.json` 能列出所有已发布平台的条目。

## 扩展新平台

在 `ADAPTERS` 注册兄弟技能脚本路径 + 在 `check_readiness` 加前置条件检查 +
`cmd_run` 加调用参数拼装。三处都在 `scripts/cross_post.py`，有注释标位。

## 参考

- `examples/post.manifest.json` —— manifest 结构模板，首次使用时复制修改。
- 各平台前置条件的实际探测逻辑见 `scripts/cross_post.py` 的 `check_readiness`（零网络，只查本地文件与环境变量）。
