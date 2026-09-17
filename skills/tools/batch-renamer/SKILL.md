---
name: batch-renamer
description: "Batch-rename files with a preview-first contract: template patterns, regex substitution, prefix/suffix, case folding, and EXIF-shooting-date prefixes, plus a JSON change log for one-command rollback. Use when the user asks to 批量重命名 / 改文件名 / 文件按日期改名 / 正则替换文件名 / 去掉文件名前缀 / batch rename / rename photos by date / strip prefix from filenames. Do NOT use for moving or sorting files into folders, editing file contents, or renaming directories."
license: Apache-2.0
compatibility: "Python 3.8+; stdlib for all modes. EXIF date mode additionally uses Pillow (optional, falls back to file mtime if absent). Preview is the default; disk writes require the --yes flag."
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: tools
  pattern: single-task
  tier: standard
  verified-date: "2026-09-17"
---

# Batch Renamer（批量重命名）

解决"一堆文件要统一改名，手动改到崩溃"的问题。

**核心判断：改名是破坏性的，所以先看后做、做完留痕。** `preview` 是默认动作，
`apply` 没有 `--yes` 直接拒绝（退出码 2）；每次真实执行都往 `rename-log.txt`
追加一条 JSON 记录，`undo` 据此一键回滚。冲突一律**跳过并报告**，绝不静默覆盖。

## 输入清单

| 输入 | 必填 | 说明 |
|------|:---:|------|
| 目标目录 | 是 | 位置参数。只处理目录内普通文件，跳过符号链接与 `.git`/`node_modules` 等 |
| 改名规则 | 是 | 至少给一种：`--pattern` / `--regex` / `--prefix` / `--suffix` / `--exif-date` / `--lower` / `--upper` |
| 执行开关 | 否 | `apply` 必须加 `--yes`；`preview` 与 `undo` 预览模式不需要 |
| `--start` | 否 | `{n}` 起始序号，默认 1 |

缺输入时一次性问齐：「请提供：① 目录路径 ② 目标命名规则（给个例子即可）③ 是否需要按拍摄日期 ④ 是否先预览。其余默认：序列从 1 开始、有冲突就跳过。」

## 前置自检

```bash
python3 --version                                    # 预期 >= 3.8
test -f scripts/rename.py && echo SCRIPT_OK          # 预期打印 SCRIPT_OK
test -d "$TARGET_DIR" && echo DIR_OK                 # 预期打印 DIR_OK
python3 -c "import PIL; print('EXIF_OK', PIL.__version__)" 2>/dev/null || echo "仅在用 --exif-date 时需要 Pillow"
find "$TARGET_DIR" -maxdepth 1 -type f | wc -l       # 先看规模，>1 万先商量分批
```

Pillow 缺失不阻塞：`--exif-date` 会自动回退到文件 mtime 并在输出里标注来源。

## 工作流

### 步骤 1：预览改名结果

```bash
python3 scripts/rename.py preview "$TARGET_DIR" --pattern "IMG_{n:03d}.{ext}"
```

预期：逐行 `旧名 -> 新名`，末尾给出"将改名 N 项，跳过 M 项"。
判读要点：**通读每一行**——这是唯一能发现规则写错的时机。

若失败：`ERROR: 未知占位符 {x}` → 模板只认 `{n}` `{ext}` `{stem}` `{date}` 四个，改掉重跑。

### 步骤 2：处置冲突

预期：冲突项单独列在"冲突跳过"区块，带原因（`目标已存在` 或 `与本批次的 X 撞名`）。

| 冲突原因 | 含义 | 处置 |
|----------|------|------|
| `目标已存在 <name>` | 目录里已有同名文件 | 换规则或先处理那个文件；脚本不会覆盖它 |
| `与本批次的 <name> 撞名` | 两条计划算出同一目标名 | 模板里加 `{n}` 序号，保证唯一性 |

若失败：冲突数量接近总数 → 八成是模板漏了 `{n}`，导致所有文件都想叫同一个名字。

### 步骤 3：确认后执行

```bash
python3 scripts/rename.py apply "$TARGET_DIR" --pattern "IMG_{n:03d}.{ext}" --yes
```

预期：逐行 `[ok] 旧名 -> 新名`，结尾打印"完成：改名 N 项"与日志路径。
**执行前必须得到用户明确同意**；脚本内部走两阶段改名（先临时名再终名），因此
`a→b` 与 `b→a` 这类互换不会中途撞名。

若失败：`拒绝执行：apply 必须显式加 --yes`（退出码 2）→ 补 `--yes`；
`[skip] ... 改名失败: Permission denied` → 检查目录写权限。

### 步骤 4：需要时回滚

```bash
python3 scripts/rename.py undo "$TARGET_DIR"          # 先预览回滚清单
python3 scripts/rename.py undo "$TARGET_DIR" --yes    # 确认回滚
```

预期：逆序打印 `新名 -> 原名`，执行后文件恢复原名，日志中已回滚的记录被移除。
未成功回滚的记录会留在日志里，便于后续排查。

若失败：`[skip] 原名已被占用，无法回滚` → 该原名后来被别的文件占了，手动处理后再跑。

## 规则组合速查表

| 参数 | 示例 | 说明 |
|------|------|------|
| `--pattern` | `"IMG_{n:03d}.{ext}"` | 占位符：`{n}` 序号、`{ext}` 扩展名、`{stem}` 原名、`{date}` 日期 |
| `--pattern` 日期规格 | `"{date:%Y-%m}_{stem}.{ext}"` | `{date:%...}` 后接 strftime 模板 |
| `--regex OLD NEW` | `--regex "^(.)" "doc_\1"` | Python `re.sub`，作用于名干，支持反向引用 |
| `--prefix` / `--suffix` | `--prefix "2026_"` | 加在名干两侧，扩展名之前 |
| `--exif-date` | — | 加 `YYYYMMDD_` 前缀；JPEG/TIFF 读 EXIF，其余回退 mtime |
| `--lower` / `--upper` | — | 名干大小写（二者互斥） |
| `--start N` | `--start 100` | `{n}` 起始值 |

**规则应用顺序固定为**：`--regex` → `--prefix`/`--suffix` → `--lower`/`--upper`；
`--pattern` 一旦给出就取代上述文本变换的结果（`{stem}` 里已含变换后的名干）。

## 失败处置表

| 现象 | 原因 | 处置 |
|------|------|------|
| 退出码 2，`拒绝执行` | `apply` 缺少 `--yes` | 补 `--yes`；先跑 `preview` 复核 |
| `ERROR: 未知占位符 {x}` | 模板里写了未支持的占位符 | 只用 `{n}` `{ext}` `{stem}` `{date}` |
| `ERROR: 正则语法错误` | `--regex` 的 OLD 不是合法正则 | 先 `python3 -c "import re;re.compile(r'...')"` 验证 |
| 大量 `撞名` 冲突 | 模板缺 `{n}`，目标名不唯一 | 在模板里加 `{n:03d}` |
| EXIF 日期全部显示 `[mtime (Pillow 未安装)]` | 未装 Pillow | `pip3 install pillow`；或接受 mtime 结果 |
| EXIF 显示 `[mtime]` 但图确实有日期 | 相机未写 `DateTimeOriginal`，或格式非常规 | 属正常回退；可 `exiftool <file>` 确认元数据 |
| `undo` 说日志为空 | 该目录从未成功执行过 `apply` | 无内容可回滚；检查是否找错了目录 |
| 目录里出现 `.rename_tmp_*` | 执行中途被强杀 | 手工改回原名，或删掉这些残留临时文件 |

## 交付标准

**成功定义**：`apply --yes` 后结尾打印"完成：改名 N 项"，且目录中不再有 `.rename_tmp_*` 残留。

**产物**：改名后的文件 + 目录内的 `rename-log.txt`（每行一条 JSON：`ts`/`from`/`to`）。

**保存位置**：文件仍在原目录内（本工具不移动文件，只改名）；日志写在目标目录根。

**完整性验证**：

```bash
find "$TARGET_DIR" -maxdepth 1 -type f | wc -l    # 数量必须与改名前后一致
ls "$TARGET_DIR"/.rename_tmp_* 2>/dev/null && echo "有残留，需处理" || echo "无残留"
python3 scripts/rename.py undo "$TARGET_DIR"      # 预览回滚清单是否与预期一一对应
```

## 参考

- `scripts/rename.py` —— 运行它执行 preview / apply / undo；`_detect_conflicts` 是冲突闸门
- `references/sources-and-methodology.md` —— 两阶段改名、EXIF 回退与日志格式的设计依据
