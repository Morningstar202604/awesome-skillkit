---
name: task-scheduler
description: "Translate cron expressions into plain language, preview next fire times, generate safe crontab lines, and map the same schedule onto Linux cron, macOS launchd, and Windows Task Scheduler. Use when the user asks to 定时任务 / 定时执行 / 每天定时跑脚本 / cron 表达式怎么写 / 每个工作日早上执行 / schedule a recurring job / crontab syntax / run this every day. Do NOT use for one-off delayed commands (use `at` or `sleep`), long-running daemons, or in-process job queues like Celery."
license: Apache-2.0
compatibility: "Python 3.8+ stdlib for description and crontab parsing. croniter is optional and only improves next-fire-time precision (pip install croniter). The helper never writes to crontab itself; it prints the line for the user to install."
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: tools
  pattern: single-task
  tier: standard
  verified-date: "2026-09-17"
---

# Task Scheduler（定时任务）

解决"每隔一段时间自动跑一次"的落地问题，覆盖 Linux / macOS / Windows 三个平台。

**核心判断：定时任务失败的原因几乎从来不是 cron 本身，而是执行环境。** 交互式 shell 里能跑通的命令，
进了 crontab 就失败——因为它拿到的是一个**极简环境**（PATH 只有 `/usr/bin:/bin`、无 shell 别名、
无你 `~/.bashrc` 里的任何设置）。所以本技能的第一动作是把表达式翻译成人话让人核对，
第二动作是把命令按"绝对路径 + 输出重定向"两条规范写死，避开三大失败原因。

**本技能不替你写入 crontab。** `cron-add` 只打印可直接粘贴的行与安装步骤——
定时任务一旦写错（比如少个星号变成每秒跑一次）后果严重且无撤销栈，人工确认这道闸门不能省。

## 输入清单

| 输入 | 必填 | 说明 |
|------|:---:|------|
| 触发时间 | 是 | cron 表达式，如 `0 9 * * 1`（每周一 09:00）。不确定就让用户先说人话，再由本技能翻译 |
| 要执行的命令 | 是 | `--cmd`。必须是**绝对路径**，且建议重定向输出 |
| 任务名 | 否 | `--name`，用于注释与默认日志名，如 `backup` |
| 日志去向 | 否 | `--log <路径>`；不给则命令自身需含 `>> ... 2>&1` |
| 目标平台 | 否 | 默认 Linux cron；macOS/Windows 见下方差异表 |

缺输入时一次性问齐：「请提供：① 想让它多久跑一次（用大白话说即可）② 要跑什么命令（完整路径）③ 输出写到哪个日志文件 ④ 目标是 Linux、macOS 还是 Windows。默认：Linux cron，日志放 `~/logs/<name>.log`。」

## 前置自检

```bash
python3 --version                                    # 预期 >= 3.8
test -f scripts/schedule_helper.py && echo SCRIPT_OK # 预期打印 SCRIPT_OK
python3 -c "import croniter; print('croniter OK')" 2>/dev/null || echo "croniter 缺失：仅影响下次触发时间的精确预测"
command -v crontab || echo "无 crontab：本机不是 cron 环境（macOS 用 launchd / Windows 用 schtasks）"
crontab -l 2>&1 | head -3                            # 先看现有任务，避免覆盖
```

`croniter` 与 `crontab` 缺失都不影响"表达式翻译"这一核心能力，脚本会自动降级并说明。

## 工作流

### 步骤 1：把表达式翻译成人话，先确认理解一致

```bash
python3 scripts/schedule_helper.py cron-check "0 9 * * 1"
```

预期：打印 `含义  : 每周一 09:00`，随后列出未来 5 次触发时刻（带星期几）。

**这一步不能跳。** `0 9 * * 1` 里的 `1` 是周一不是周日，`* * * * *` 是每分钟——
绝大多数事故源于字段含义记错或字段数写错。

若失败：`字段数应为 5，实际 6 个` → 数一下空格；`取值 99 超出允许范围 0-23` → 小时字段写错了。

### 步骤 2：生成 crontab 行

```bash
python3 scripts/schedule_helper.py cron-add \
  --name backup --schedule "0 3 * * *" \
  --cmd "/usr/bin/python3 /home/me/backup.py" --log "/home/me/logs/backup.log"
```

预期：打印注释行 + crontab 行 + 备份/安装步骤。若命令有隐患，末尾附"检查中发现的问题"。

若失败：`ERROR: 表达式非法` 且退出码 2 → 回步骤 1 修正；出现"不是绝对路径"警告 → 先 `which <cmd>` 查出全路径再重跑。

### 步骤 3：核对现有任务，避免误覆盖

```bash
python3 scripts/schedule_helper.py cron-list
```

预期：表格形式列出表达式、中文含义、命令。语法错误的行会被标出 `语法错误: ...`。

若失败：`当前系统没有 crontab 命令` → 本机不是 cron 环境，改走步骤 5 的对应方案。

### 步骤 4：人工安装并验证

```bash
crontab -l > /tmp/cron.bak        # 务必先备份
crontab -l | { cat; echo '0 3 * * * /usr/bin/python3 /home/me/backup.py >> /home/me/logs/backup.log 2>&1'; } | crontab -
crontab -l                        # 确认已写入
```

预期：`crontab -l` 输出里能看到刚加的那一行。

**验证**：先临时把时间改成 2 分钟后跑一次，确认日志文件真的被写入——`crontab -e` 里的任务不会报错，
写错了它只会**静默地永远不执行**。

若失败：任务没触发 → 按下面"三大失败原因"逐条排查。

### 步骤 5：非 Linux 平台改走对应方案

见下方三平台差异表，把同一语义翻译过去。

## 三平台差异表

| 维度 | Linux cron | macOS launchd | Windows 任务计划程序 |
|------|-----------|---------------|---------------------|
| 配置位置 | `crontab -e` | `~/Library/LaunchAgents/*.plist` | `taskschd.msc` 图形界面 |
| 时间语法 | `0 9 * * 1` | `StartCalendarInterval` 字典 | XML `Triggers` 或 `schtasks /sc` |
| 命令行创建 | 见步骤 4 | `launchctl load <plist>` | `schtasks /create /tn X /tr CMD /sc daily /st 09:00` |
| 环境变量 | **几乎为空**，需显式 `PATH=` | 同样极简，写在 plist 的 `EnvironmentVariables` | 以服务账户运行，环境≠登录用户 |
| 输出去向 | 默认发邮件（易撑满 `/var/mail`） | `StandardOutPath`/`StandardErrorPath` | 任务历史记录或重定向 |
| 是否需登录 | 否 | **用户级 Agent 需已登录**；系统级 Daemon 不需要 | 可配"是否用户登录时运行" |
| 查看方式 | `crontab -l` | `launchctl list \| grep <label>` | `schtasks /query /tn X /v /fo list` |
| 手动触发 | 无内建；临时改时间 | `launchctl kickstart -k gui/$(id -u)/<label>` | `schtasks /run /tn X` |
| 典型坑 | PATH 缺失、无重定向 | Agent 未 load、plist 语法错但静默忽略 | 账户权限、"仅在登录时运行" |

一句话选型：**Linux 服务器用 cron；macOS 桌面优先 launchd（cron 仍可用但已被 Apple 标记为遗留）；Windows 用 schtasks 或任务计划程序 GUI。**

## 定时任务失败的三大原因

### 原因一：环境变量缺失

cron 拿到的环境几乎是空的——`PATH` 通常只有 `/usr/bin:/bin`，你在 `~/.zshrc` 里 `export` 的东西一个都没有。

**判据**：命令在终端手敲能跑，进了 crontab 就报 `command not found` 或读不到某个变量。

**处置**：在 crontab 顶部显式声明（每行一个赋值，不要用 `export`）：

```bash
PATH=/usr/local/bin:/usr/bin:/bin
MY_API_KEY=xxx
```

或者让脚本自己加载环境：`/usr/bin/env bash -lc '/usr/bin/python3 /path/job.py'`。

### 原因二：路径不是绝对路径

cron 的**工作目录是当前用户的家目录**（不是你的项目目录），PATH 又极简，
所以 `python3 job.py` 这类不带全路径的写法必然失败。

**判据**：报错含 `no such file or directory`，或日志里找不到相对路径引用的文件。

**处置**：命令、参数里的文件、脚本内部引用的资源**全部改成绝对路径**；
脚本开头加 `cd /absolute/project/dir || exit 1`。

### 原因三：权限不足

cron 以你的用户身份运行，但**不继承你的 sudo 权限**，也不能访问需要交互授权的资源
（如 macOS 的 TCC 保护目录、需要解锁的密钥链）。

**判据**：报错含 `Permission denied`、`Operation not permitted`；或任务表面成功但什么都没做。

**处置**：检查文件与目录权限（`ls -l`）、确认不依赖交互输入；
需要提权的任务用 `sudo crontab -e`（系统级）而非在用户任务里写 `sudo`——cron 里没有终端，`sudo` 一定卡住等密码。

## 失败处置表

| 现象 | 原因 | 处置 |
|------|------|------|
| 任务完全不执行，也无报错 | 表达式写错，cron 静默忽略 | `cron-check` 复核；检查字段数、小时是否写了 `99` |
| `command not found` | PATH 缺该命令 | crontab 顶部加 `PATH=`，或改绝对路径 |
| `No such file or directory` | 相对路径 / 工作目录不对 | 全部改绝对路径，脚本内先 `cd /abs/path` |
| `Permission denied` | 权限不足或需交互授权 | `ls -l` 查权限；不要在 cron 里用 `sudo` |
| `/var/mail` 爆满 | 未重定向输出，cron 当邮件发 | 命令追加 `>> /path/job.log 2>&1` 或加 `--log` |
| macOS 上 plist 无反应 | Agent 未 load，或用户未登录 | `launchctl load` 后 `list` 确认；改系统级 Daemon |
| Windows 任务未运行 | 账户权限 / "仅登录时运行"未取消 | 查任务历史；改为"不管是否登录都运行"并配账户 |
| `croniter 拒绝该表达式` | 表达式超出 croniter 支持范围 | 用 `cron-check` 内置解析器看中文描述，语法仍可判定 |

## 交付标准

**成功定义**：`cron-check` 输出的中文含义与用户的口头意图一致，且 `crontab -l` 里能看到该行。

**产物**：一条可直接粘贴的 crontab 行（含注释），或对应平台的 plist / schtasks 命令。

**保存位置**：Linux 在用户 crontab（`crontab -l` 可见）；安装前务必 `crontab -l > /tmp/cron.bak` 备份。

**完整性验证**：

```bash
crontab -l | grep -F "<刚加入的命令片段>"      # 确认已写入
ls -l "<--log 指定的日志路径>"                 # 触发一次后应出现并持续增长
grep CRON /var/log/syslog | tail -5            # Debian/Ubuntu 上看 cron 是否真的调用了它
```

## 参考

- `scripts/schedule_helper.py` —— 运行它执行 cron-add / cron-list / cron-check；`describe` 是翻译核心
- `references/sources-and-methodology.md` —— 字段翻译规则、降级策略与三平台语义映射的依据
