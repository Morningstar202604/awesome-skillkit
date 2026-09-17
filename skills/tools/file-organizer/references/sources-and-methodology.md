# 方法论来源与设计取舍

> 何时读：当你想改判重策略、调整冲突命名规则，或质疑"为什么不直接删重复文件"时读本文件。
> 本文件不含 API 细节，只讲设计依据。

## 思想来源（公开方法论蒸馏，非代码搬运）

| 本脚本的做法 | 蒸馏自的思想 |
|--------------|--------------|
| 只读优先 / dry-run 默认 | Unix 工具链"先 `--dry-run` 后落盘"的惯例；`rsync -n`、`git clean -n`、Terraform `plan/apply` 两阶段模型 |
| `resolve()` 后做前缀断言 | OWASP 路径穿越防护的 canonicalize-then-check 模式 |
| 大小 + 头部哈希判重 | `fdupes` / `jdupes` 的 size-then-partial-hash 预筛思路；完整内容比对只在同大小候选间进行 |
| 保留"最旧 / 路径最短" | 归档工具链（如备份去重）默认"保留最早出现的原件"以减少断链 |
| 冲突加 `_1` 序号 | Windows 资源管理器 / macOS Finder 的 "copy 2" 命名惯例改良版（序号单调递增，便于脚本幂等重跑） |

## 关键取舍

**为什么判重只读前 1KB？** 全量哈希一个 4GB 视频要数十秒，而绝大多数重复文件
连大小都相同，读 1KB 就足以区分。代价是理论上存在"大小相同 + 头部 1KB 相同 + 尾部不同"
的漏判——因此 `dedupe` 是**建议工具而非清理工具**，删除动作始终留在人手里。

**为什么 apply 不支持 `--by size`？** 体积是文件的物理属性，不是语义分类。
按体积归档后，"发票.pdf" 会跑到 `small(<1MB)/` 里，用户再也找不到它。
`plan --by size` 保留是为了让用户观察体积分布，而不是鼓励这么归档。

**为什么符号链接一律跳过？** 跟随符号链接遍历会让"整理 A 目录"意外改动 B 目录，
并使边界断言失去意义。跳过是唯一能同时保证安全与可预测的选择。

**为什么移动而非复制再删除？** `shutil.move` 在同一文件系统内是 `rename`，
原子且瞬时；跨文件系统时自动退化为复制 + 删除。复制删除式实现会在中途失败时留下半份文件。

## 官方文档

- Python `pathlib`（`Path.resolve` 的符号链接语义）：<https://docs.python.org/3/library/pathlib.html>
- Python `os.walk`（原地裁剪 `dirnames` 控制下潜）：<https://docs.python.org/3/library/os.html#os.walk>
- Python `shutil.move`：<https://docs.python.org/3/library/shutil.html#shutil.move>
- Python `hashlib`：<https://docs.python.org/3/library/hashlib.html>
- `fdupes`（size + partial hash 判重的参照实现）：<https://github.com/adrianlopezroche/fdupes>
