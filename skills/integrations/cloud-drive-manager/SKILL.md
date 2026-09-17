---
name: cloud-drive-manager
description: "Plan and verify cloud-drive archives: enumerate a local directory into an upload manifest with per-file chunk strategy, generate sha256/md5 checksum lists for post-upload comparison, and render Baidu / Aliyun / OneDrive listing responses as readable tables. Use when the user asks to 归档到网盘 / 上传到百度网盘 / 备份到阿里云盘 / 同步到 OneDrive / 网盘文件清单 / 校验上传完整性 / archive to cloud drive / upload to Baidu Netdisk / backup to Aliyun Drive / sync to OneDrive. Do NOT use for Notion pages (use notion-workspace), chat notifications (use feishu-dingtalk-bridge), or local-only file organization (use file-organizer)."
license: Apache-2.0
compatibility: "Python 3.8+ stdlib only for the helper script (hashlib/json/pathlib). Live uploads need outbound HTTPS plus BAIDU_ACCESS_TOKEN / ALIYUN_REFRESH_TOKEN / ONEDRIVE_ACCESS_TOKEN in environment variables; the bundled script never contacts a network or deletes anything."
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: integrations
  pattern: single-task
  tier: standard
  verified-date: "2026-09-17"
---

# Cloud Drive Manager（云盘归档）

把一整个本地目录归档到网盘，真正难的不是"传"，而是三件事：
**传什么**（哪些该排除）、**怎么传**（简单上传还是分片）、**传完怎么证明传对了**（校验）。

**核心判断：先出计划与校验清单，再谈上传。** 上传前的清单是"将发生什么"，
上传后的校验清单是"是否真的发生"。两者缺一，归档就不可信。

**红线（本技能强制）**

1. **凭证绝不硬编码**：access_token / refresh_token / client_secret 只从环境变量读
   （`BAIDU_ACCESS_TOKEN` / `ALIYUN_REFRESH_TOKEN` / `ONEDRIVE_ACCESS_TOKEN`）。
   脚本**完全不接触**这些值——它只读本地目录。禁止把令牌写进脚本、配置或 repo。
2. **默认 dry-run**：`plan-upload` 输出的是计划，**不上传任何文件**。
   真实上传需要用户确认清单后另起一步执行。
3. **删除双重确认**：本脚本**不提供任何删除命令**。若用户要删云盘文件，
   必须先列出清单，然后**分两次确认**——① 目标路径正确；② 受影响文件数与
   预期一致。任一项存疑就改用移动/归档目录，不要删。
4. **最小权限**：网盘开放平台只申请文件读写（如百度的 `netdisk`），
   **不要**申请用户信息、通讯录等无关 scope；授权只给单个目录时不要申请全盘。

## 输入清单

| 输入 | 必填 | 说明 |
|---|---|---|
| 源目录 | 是 | 本地要归档的目录；符号链接会被跳过 |
| 远端根路径 | 是 | 如 `/archive/2026-Q3`；上传前确认该目录归属与配额 |
| 云盘平台 | 是 | `baidu` / `aliyun` / `onedrive`，决定分片阈值与哈希算法 |
| 排除规则 | 否 | 逗号分隔 glob，如 `*.tmp,.DS_Store,node_modules/*` |
| 子路径前缀 | 否 | `--prefix`，在相对路径前追加一层，如 `backup` |
| access_token | 真实上传必填 | 只在环境变量；计划与校验阶段不需要 |
| 列表响应 JSON | 解析必填 | 从云盘 API 拉回的列表响应体 |

**缺输入时一次性问齐**：

> 请一次提供：① 本地源目录；② 云盘平台与远端目标路径；③ 需要排除的文件类型
> （如临时文件、依赖目录）；④ access_token 是否已在环境变量里（不要贴给我，
> 我只检查存在性）。我默认先出上传计划与校验清单，不上传。

## 前置自检

```bash
python3 --version                                        # 预期 >= 3.8
test -f scripts/drive_ops.py && echo SCRIPT_OK            # 预期打印 SCRIPT_OK
# 凭证检查：只判断存在性，绝不回显
for v in BAIDU_ACCESS_TOKEN ALIYUN_REFRESH_TOKEN ONEDRIVE_ACCESS_TOKEN; do
  printf '%s: ' "$v"; test -n "$(printenv $v)" && echo present || echo missing
done
test -d "$SRC_DIR" && echo DIR_OK                         # 源目录存在
du -sh "$SRC_DIR" 2>/dev/null                             # 先看体积与配额对比
df -h "$SRC_DIR" | tail -1                                # 顺带确认本地可读
```

| 结果 | 判读 |
|---|---|
| 令牌 `missing` | 只影响真实上传；计划与校验照常，先出计划 |
| `DIR_OK` 缺失 | 源目录不存在，`plan-upload` 会直接报错退出 |
| 目录体积 > 云盘剩余配额 | **停下来先问用户**如何取舍，不要自动分批 |

## 三家云盘 API 差异对照表

| 维度 | 百度网盘 | 阿里云盘 | OneDrive |
|---|---|---|---|
| 鉴权 | OAuth2 `access_token`（有效期 30 天，需 refresh） | `refresh_token` 换 `access_token`（2 小时） | OAuth2 `access_token`（1 小时，用 refresh 续） |
| 单请求上传上限 | **4MB**（超出强制分片） | 100MB | **250MB** |
| 分片大小 | 固定 **4MB** | 建议 8MB | 必须是 **320KiB 的整数倍** |
| 秒传/去重键 | 整文件 **MD5** + 分片 MD5 | **SHA1** + 分段 SHA1 | **quickXorHash** 或 sha256 |
| 列表响应条目字段 | `list[]`，`isdir` 为 1/0，`fs_id`、`server_filename` | `items[]`，`type` 为 `folder`/`file`，`file_id` | `value[]`，用 `folder`/`file` **子对象**判类型 |
| 目录判定 | `isdir == 1`（整数） | `type == "folder"`（字符串） | 存在 `folder` 键 |
| 删除接口 | 进回收站（可恢复，有保留期） | 进回收站 | 进回收站 / 永久删除（需显式 `permanent` 参数） |
| 频率限制 | 较严格，分片上传需间隔 | 中等 | 较宽松，有 429 退避要求 |
| 特别注意 | 授权令牌 30 天必须刷新，否则整批中断 | 直接暴露的第三方 SDK 较少，建议直连 REST | 分片大小必须是 320KiB 倍数，否则 400 |

## 秒传原理（为什么上传前要算哈希）

"秒传"（instant upload）不是传输优化，而是**去重**：客户端先算文件内容哈希，
把哈希提交给服务端；服务端在自己的存储里查有没有相同哈希的**整文件**记录，
有则直接建立一条指向已有内容的引用，一个字节都不传。

推论有三条，直接决定归档策略：

1. **算哈希是上传的前置成本，不是可选项**。不算哈希的客户端永远享受不到秒传。
2. **服务端只认自己的哈希算法**。百度认 MD5、阿里云盘认 SHA1、OneDrive 认
   quickXorHash——用错算法会让秒传永远不命中，白白重传。
3. **秒传命中的文件同样需要校验**。命中只说明"服务端有相同哈希的内容"，
   不说明你这次的引用建对了。上传后仍要对引用逐条核对。

因此本技能把 `checksum-plan` 放在上传**之前**跑一次（拿到基准），
上传**之后**再从云盘拉清单比对，形成闭环。

## 工作流

### 步骤 1：规划上传（dry-run）

```bash
python3 scripts/drive_ops.py plan-upload \
  --dir "$SRC_DIR" --remote /archive/2026-Q3 \
  --provider baidu --prefix backup \
  --exclude "*.tmp,.DS_Store,node_modules/*" \
  --manifest upload_plan.json
```

预期：打印文件清单（相对路径 / 大小 / 上传策略）、将创建的远端目录列表、
以及该平台的分片依据。`--manifest` 把同一份计划落成 JSON 供后续步骤消费。

**排版含义**：`simple` 表示单请求可传；`slice xN (4MB/片)` 表示需要分片上传 N 次。

若失败：`不是目录` → 核对路径；`目录内没有可上传的文件` → **脚本以退出码 2 报错**
（空清单不是成功），检查 `--dir` 是否指错、或 `--exclude` 是否把内容全排除了。

### 步骤 2：生成校验基准

```bash
python3 scripts/drive_ops.py checksum-plan --dir "$SRC_DIR" \
  --output sha256_before.txt --algo sha256 --exclude "*.tmp"
```

预期：标准 `<hash>  <相对路径>` 格式，**可直接用系统工具验证**：

```bash
cd "$SRC_DIR" && sha256sum -c sha256_before.txt
```

若失败：`不支持的算法` → 只能选 `sha256` / `md5` / `sha1`；
`目录内没有可计算的文件` → **脚本以退出码 2 报错**（0 行清单不是有效基准，会让
`sha256sum -c` 空过而掩盖问题），先核对 `--dir` 与 `--exclude`；
大目录很慢 → 属正常，`hashlib` 流式计算不占内存但受磁盘读速限制。

### 步骤 3：上传（凭证由代理层注入）

上传本身由 AI/用户用 SDK 或 REST 完成，脚本不参与。关键约束：

- 按 `mode` 走对应路径：`simple` 走单请求接口，`slice` 先 `create` 拿 uploadid
  再逐片 `upload`，最后 `create` 收尾；
- 分片必须**按序**提交（百度/阿里都要求顺序，乱序会失败）；
- 每片之间留间隔，避免触发频率限制；
- 秒传接口先试一次——命中的文件跳过字节传输。

预期：每个文件返回一个远端 file_id，记录到台账。
若失败：`access_token 过期` → 百度 30 天、阿里 2 小时、OneDrive 1 小时，
刷新后**从断点续传**而不是重头开始（已完成的片不必重传）。

### 步骤 4：拉清单并核对

```bash
# 先取云盘列表存成 JSON，再解析
python3 scripts/drive_ops.py parse-list --json cloud_list.json --provider baidu
```

预期：条目数、文件合计体积与步骤 1 的计划一致；目录/文件分类正确。

**逐文件比对**：用步骤 2 的基准清单比对远端哈希（若 API 返回哈希字段），
或至少比对**文件名 + 体积**两组；体积不同的必须重传。

若失败：条目数少 → 上传中断未续传；体积为 0 → 上传创建了占位但未写入内容。

### 步骤 5：删除（若确有必要）——双重确认

本脚本**不提供删除命令**，这是有意的。若要删，必须：

1. **第一次确认**：把 `parse-list` 的输出给用户，让其确认**目标路径**完全正确；
2. **第二次确认**：明确报出**受影响文件数与合计体积**，让用户确认与预期一致；
3. 优先考虑**移到归档目录**而不是删除——回收站有保留期，过期即不可恢复。

预期：用户两次确认后才执行，且优先走"移动"。
若失败：任一次确认存疑 → 停止，改为移动或让用户自己在网页端操作。

## 交付标准

- **成功定义**：云盘侧文件数与合计体积与上传计划一致，且抽样文件哈希与
  本地基准一致。
- **产物**：`upload_plan.json`（计划）、`sha256_before.txt`（本地基准）、
  云盘列表 JSON + 解析输出（远端口径）、上传台账（file_id 映射）。
- **完整性验证**：
  - `sha256sum -c sha256_before.txt` 全 OK（确认本地基准自身可靠）；
  - 云盘条目数 == 计划文件数，合计体积相等；
  - 台账中每个本地文件都有对应 file_id，无遗漏；
  - 所有产物中不得出现令牌明文：`grep -lE 'access_token|refresh_token' *.json` 应无命中。

## 失败处置表

| 现象 | 原因 | 处置 |
|---|---|---|
| 百度分片上传报 `file size error` | 超过 4MB 仍走简单上传，或片大小不是 4MB | 用 `plan-upload` 的 `mode` 字段决定路径；百度的片大小固定 4MB，不可自选 |
| OneDrive `400 invalidRequest` | 分片大小不是 320KiB 的整数倍 | 用 10MB（320KiB×32）之类；`plan-upload` 给出的默认值已满足 |
| 上传中途 `access_token` 失效 | 百度 30 天、阿里 2 小时、OneDrive 1 小时的短周期 | 刷新令牌后**断点续传**：已完成的分片用 uploadid 继续，不要重头 |
| 秒传始终不命中 | 用了平台不认的哈希算法（如给阿里云盘传 MD5） | 百度用 MD5、阿里用 SHA1、OneDrive 用 quickXorHash；错误算法永远不命中 |
| 列表比计划少文件 | 上传中断，或上传时目录被并发修改 | 用 `plan-upload --manifest` 的快照比对差异，只补传缺失项 |
| `计划为空` / `目录内没有可上传的文件`（退出码 2） | `--dir` 指错，或 `--exclude` 通配符过宽把内容全排掉 | 核对 `--dir` 指向的绝对路径；把 `--exclude` 收窄后重跑 `plan-upload` 看清单。空清单不是成功，脚本有意返回非 0 阻断流水线 |
| 列表体积为 0 但文件存在 | 创建了文件记录但内容未写入（分片没收尾） | 重传该文件；分片上传必须调收尾接口（百度 `create`、阿里 `complete`） |
| 上传触发频率限制 | 请求过密（百度尤其严格） | 串行上传 + 片间间隔；遇 429 指数退避，不要并发重试 |
| 跳过了本该上传的文件 | 误用 `--exclude` 通配符（如 `*.log` 排掉了要留的日志） | 先跑 `plan-upload` 看清单，确认无误再上传——这正是 dry-run 的意义 |
| 符号链接内容未被上传 | 脚本有意跳过符号链接 | 这是保护：跟随链接会意外上传链接指向的外部目录。需要就传真实文件 |
| 删除后无法恢复 | 回收站保留期已过，或用了永久删除参数 | 删除前双重确认；优先"移动到归档目录"而非删除 |

## 参考

- `scripts/drive_ops.py` —— `plan-upload`（清单 + 分片策略 + manifest）/
  `checksum-plan`（可被 `sha256sum -c` 直接消费）/ `parse-list`（三家列表归一）
- `references/sources-and-methodology.md` —— 秒传原理、分片阈值依据、
  为什么脚本不提供删除命令
