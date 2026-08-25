---
name: "cross-post-orchestrator"
description: "一篇文章多平台发布编排器。读取 post.manifest.json，检查各平台前置条件（凭据/登录态/账号文件），生成执行计划；对已脚本化的平台（公众号、掘金）调度对应技能 CLI，无脚本的平台输出精确手工清单；维护发布台账。当用户提到多平台发文、一键分发文章、同步发布到多个平台、发布计划时使用。默认 plan 模式绝不联网。"
license: Apache-2.0
metadata:
  version: "1.0"
  category: "content-publishing"
  verified-date: "2026-08-26"
---

# 跨平台发布编排 Skill

## 定位

**规划器 + 调度器**——不重复实现平台逻辑，复用各平台技能：

| 平台 | 适配方式 | 前置条件 |
|------|---------|---------|
| wechat_mp（公众号） | 调度 `wechat-mp-publisher` CLI | 环境变量 WECHAT_MP_APPID/SECRET |
| juejin（掘金） | 调度 `juejin-publisher` CLI | 环境变量 JUEJIN_COOKIE |
| cnblogs（博客园） | 输出手工清单（按其 publish-api.md 流程） | account.local.json 存在 |
| zhihu（知乎） | 输出清单（浏览器自动化走 zhihu-content-manager） | zhihu_state.json 存在 |

## 使用流程

### 1. 准备 manifest

复制 `examples/post.manifest.json` 到工作目录，填入标题、markdown 路径、各平台参数。

### 2. 先看计划（默认不联网）

```bash
python3 scripts/cross_post.py plan --manifest post.manifest.json
```

输出每个平台状态：`ready` / `missing-credentials` / `blocked-md-missing` / `skipped`。
退出码 1 = 有阻塞项，先补前置条件。

### 3. 执行

```bash
python3 scripts/cross_post.py run --manifest post.manifest.json            # 全部
python3 scripts/cross_post.py run --manifest post.manifest.json --only juejin
```

- 脚本化平台会调用对应技能 CLI，并继承其安全约定：**对方脚本仍要求 --execute 才真发**
- 无脚本的平台打印精确操作清单，退出码 2 提示需人工介入

### 4. 台账

每次成功发布自动追加 `published.ledger.json`（时间戳/平台/标题/状态）：

```bash
python3 scripts/cross_post.py ledger --manifest post.manifest.json
```

## 安全规则

1. `plan` 是默认动作且零网络请求；`run` 也只做本地调度，真正发送由各平台技能的 `--execute` 控制
2. AI 的标准动作序列：`plan` → 向用户展示 → 用户确认 → `run --only <platform>` 逐个执行
3. 发布类操作永远逐平台确认，不要一次全发

## 扩展新平台

在 `ADAPTERS` 注册兄弟技能脚本路径 + 在 `check_readiness` 加前置条件检查 +
`cmd_run` 加调用参数拼装。三处都在 `scripts/cross_post.py`，有注释标位。
