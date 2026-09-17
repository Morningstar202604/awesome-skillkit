# 方法论来源与设计取舍

> 何时读：想改改名规则的应用顺序、调整冲突策略，或质疑"为什么日志用 JSONL 而不是纯文本"时读。
> 本文件不含 CLI 参数表（那在 SKILL.md），只讲设计依据。

## 思想来源（公开方法论蒸馏，非代码搬运）

| 本脚本的做法 | 蒸馏自的思想 |
|--------------|--------------|
| `preview` 默认 / `apply` 需显式确认 | 批量运维工具的双阶段模型（Terraform `plan`→`apply`、`git clean -n`） |
| 两阶段改名（先临时名再终名） | 经典批量改名算法：先全体脱离原命名空间，再统一落位，从根本上消除环状依赖 |
| 冲突跳过而非自动加后缀 | 改名场景与归档场景不同：改名后文件名是给人看的，自动加 `_1` 会污染命名意图，不如让人决策 |
| JSONL 变更日志 + 逆序回滚 | 预写日志（WAL）思路：先记变更意图、再执行，回滚即反向重放 |
| EXIF 失败回退 mtime | 渐进降级：元数据可能缺失，但"按拍摄时间排序"这个用户意图必须始终被满足 |

## 关键取舍

**为什么 `{n}` 只在模板真的用到时才自增？** 若无条件自增，被跳过的文件（已合规、或有冲突）
会白白吃掉一个号，产出 `IMG_001, IMG_003, IMG_007` 这样的空洞编号。用户看到的应该是连续序列。

**为什么互换（a→b, b→a）不在 `_detect_conflicts` 里放行？**
冲突检测基于"目标当前是否存在"，无法区分"被别人占着"和"即将被同批次另一个文件腾出来"。
若放行，一旦阶段二中途失败就会丢文件。当前实现选择保守：直接互换会被报为冲突，
驱动用户改用不构成环的规则。脚本内部的两阶段机制仍然保留了应对中断的健壮性。

**为什么日志格式是 JSONL 而不是 `old -> new` 文本？**
文件名可以包含空格、引号、换行、`->` 本身。用分隔符文本解析必然在某天崩掉；
JSONL 每行独立可解析，坏行可单独跳过（`--undo` 遇到坏行只警告不中断）。

**为什么 `undo` 成功后要从日志里删掉已回滚的记录？**
否则重复执行 `undo` 会尝试再次回滚同一批记录，把用户后来新建的同名文件误改。
保留无法回滚的记录则是为了让遗留问题可见。

## 官方文档

- Python `re`（`sub` 与反向引用语法）：<https://docs.python.org/3/library/re.html>
- Python `str.format` 的 Format Specification Mini-Language（`{n:03d}` 的依据）：<https://docs.python.org/3/library/string.html#format-specification-mini-language>
- Python `datetime.strftime`（`{date:%Y-%m}` 的依据）：<https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes>
- Pillow `Image.Exif`（EXIF 读取，tag 36867 = DateTimeOriginal）：<https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Exif>
- CIPA DC-008 EXIF 规范（`DateTimeOriginal` 字段定义）：<https://www.cipa.jp/std/documents/e/DC-008-2012_E.pdf>
- Python `pathlib.Path.rename`（同文件系统内的原子改名）：<https://docs.python.org/3/library/pathlib.html#pathlib.Path.rename>
