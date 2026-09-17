---
name: file-organizer
description: "Audit and reorganize a messy directory with a dry-run-first planner: extension/date/size statistics, fast duplicate detection (size + first-1KB hash), and a reviewable move plan before anything touches disk. Use when the user asks to 整理文件夹 / 整理目录 / 文件分类归档 / 找出重复文件 / 清理下载文件夹 / organize my files / file cleanup / find duplicate files / sort downloads folder. Do NOT use for deleting files, renaming in place, syncing between machines, or touching system/VCS directories."
license: Apache-2.0
compatibility: "Python 3.8+ stdlib only (no third-party packages). Reads and moves files inside the directory you pass; apply is dry-run unless --yes is given."
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: tools
  pattern: single-task
  tier: standard
  verified-date: "2026-09-17"
---

# File Organizer（文件整理）

解决"下载文件夹/桌面/项目目录乱成一团"的问题：先体检、再出方案、最后才动手。

**核心判断：整理是不可逆操作，所以顺序永远不能颠倒。** `scan` 和 `plan` 只读，
`apply` 默认 dry-run——用户看到"将把 X 移到 Y"的完整清单并确认后，才用 `--yes` 落盘。
本脚本**永不删除文件**：重复文件只给保留建议，删不删由人决定。

## 输入清单

| 输入 | 必填 | 说明 |
|------|:---:|------|
| 目标目录 | 是 | 位置参数，如 `~/Downloads`。脚本只在此目录内部操作，符号链接与 `../` 均被拦截 |
| 整理维度 `--by` | 否 | `type`（默认，按扩展名）/ `date`（按 mtime 的 `YYYY-MM`）/ `size`（仅 `plan` 可用） |
| 执行开关 | 否 | `--yes` 才真正移动；`--dry-run` 是默认行为，可显式写出以自文档化 |

缺输入时一次性问齐：「请提供：① 要整理的目录路径 ② 按类型还是按日期归档 ③ 是否已有备份。其余我将采用默认值：`--by type`、dry-run 预览。」

## 前置自检

```bash
python3 --version                                   # 预期 >= 3.8
test -f scripts/organize.py && echo SCRIPT_OK       # 预期打印 SCRIPT_OK
test -d "$TARGET_DIR" && echo DIR_OK                # 预期打印 DIR_OK
python3 -c "import os;print(len(os.listdir('$TARGET_DIR')))"   # 先看规模，超大目录先沟通
```

三项任一失败即 STOP 并报明缺什么；目录为空时 `scan` 会直接说明"没有可整理的文件"，不必继续。

## 工作流

### 步骤 1：体检现状

```bash
python3 scripts/organize.py scan "$TARGET_DIR"
```

预期：打印扩展名分布表（数量 + 体积）、体积分档计数、重复文件组。
判读要点：重复组数 × 冗余体积决定是否值得先做 `dedupe` 再整理；文件数 > 5000 时先与用户确认是否分批。

若失败：`ERROR: 不是目录` → 路径拼错或指向了文件，用 `ls -ld` 核对。

### 步骤 2：审查重复文件

```bash
python3 scripts/organize.py dedupe "$TARGET_DIR"
```

预期：每个重复组列出"保留"与"可清理"两栏，保留项按**最旧 mtime → 最短路径**排序。

若失败：未发现重复 → 说明文件内容各异，跳过本步直接整理。
注意：判重指纹是"大小 + 前 1KB 哈希"，对**头部相同但后缀不同**的大文件存在极低概率误判，
因此脚本只出建议不代删；清理前请 `cmp` 确认。

### 步骤 3：生成整理计划

```bash
python3 scripts/organize.py plan "$TARGET_DIR" --by type
```

预期：逐行 `将把 <相对路径> 移到 <相对路径>`，末尾给出下一步命令。
把清单交给用户逐条过目——这是整条流程里唯一的人工闸门。

若失败：计划为空 → 文件已在目标位置；`--by size` 报错 → 体积是属性不是语义，归档会让文件难检索，请换 `type` 或 `date`。

### 步骤 4：dry-run 复核

```bash
python3 scripts/organize.py apply "$TARGET_DIR" --by type --dry-run
```

预期：每行前缀 `[dry-run]`，结尾打印"磁盘未发生任何变化"。
用 `find "$TARGET_DIR" -type f | wc -l` 前后对比数量应完全一致。

若失败：出现 `[skip] 目标已存在` → 说明计划期间磁盘状态变了，重跑步骤 3 重新生成计划（脚本会自动加 `_1`、`_2` 序号后缀避让）。

### 步骤 5：确认后执行

```bash
python3 scripts/organize.py apply "$TARGET_DIR" --by type --yes
```

预期：每行前缀 `[ok]`，结尾打印"完成：移动 N 项，跳过 M 项"。
**执行前必须已得到用户明确同意**；建议先 `cp -r` 或 `rsync` 做一份备份。

若失败：`[skip] ... 移动失败: Permission denied` → 目标目录不可写，检查权限后重试；跳过项会在结尾计数里体现，逐条排查。

## 目标目录结构示例

```
$TARGET_DIR/
├── pdf/          # .pdf
├── jpg/          # .jpg
├── txt/          # .txt
├── csv/          # .csv
└── (no-ext)/     # 无扩展名文件
```

按 `--by date` 时目录名为 `2026-09` 形式的 `YYYY-MM`，取自文件 mtime。

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| `scan <dir>` | 路径 | 只读体检 |
| `plan <dir> --by` | `type`/`date`/`size` | 只打印方案 |
| `apply <dir> --by` | `type`/`date` | 执行；默认 dry-run |
| `apply --yes` | 标志 | 唯一能改动磁盘的开关 |
| `dedupe <dir>` | 路径 | 只读重复报告 |

## 失败处置表

| 现象 | 原因 | 处置 |
|------|------|------|
| `ERROR: 不是目录` | 路径指向文件或不存在 | `ls -ld` 核对后重跑 |
| `逃出了目录边界` | 目标解析后落在目录外 | 正常保护；检查是否有符号链接指向外部，本脚本拒绝跨界写入 |
| `[skip] 目标已存在，跳过` | 计划与执行之间磁盘变了 | 重跑 `plan` 重新生成（冲突时脚本也会自动加序号后缀） |
| 重复组明显误报 | 大文件头部相同（如同一模板导出的 PDF） | 用 `cmp -s a b` 二次确认，`dedupe` 只给建议不代删 |
| 文件数太多输出刷屏 | 目录规模过大 | 分批：先处理子目录，或把输出重定向到文件再分段阅读 |
| `apply` 后找不到文件 | 已按扩展名归档 | 按 `plan` 输出的映射表回查，或用 `find "$TARGET_DIR" -name "<原文件名>"` |

## 交付标准

**成功定义**：`apply --yes` 后结尾打印"完成：移动 N 项"，且 `scan` 复查时各扩展名桶内文件数与计划一致。

**产物**：整理后的目录树，子目录名 = 扩展名小写（或 `YYYY-MM`）；无扩展名文件归入 `(no-ext)/`。

**保存位置**：全部在原目录内部，不产生任何外部副本。

**完整性验证**：

```bash
find "$TARGET_DIR" -type f | wc -l    # 移动前后数量必须相等
find "$TARGET_DIR" -type f -exec du -cb {} + | tail -1   # 总体积必须相等
```

## 参考

- `scripts/organize.py` —— 运行它执行四个子命令；`_resolve_within` 是边界闸门
- `references/sources-and-methodology.md` —— 判重策略、冲突命名与不可逆操作的设计取舍
