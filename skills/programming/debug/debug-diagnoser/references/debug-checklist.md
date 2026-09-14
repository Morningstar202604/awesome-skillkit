# Debug Checklist（系统化调试流程清单）

> 配套 debug-diagnoser。`diagnoser.py` 只做**日志文本的模式匹配**，给出候选成因与严重度；接下来的定位与验证由本清单驱动。原则：**假设驱动，不随机试错**——每次改动前必须能说出"我预期看到什么变化"，否则那不是调试，是碰运气。

## 目录
- §0 时间盒与止损
- §1 复现（不可复现的问题无法调试）
- §2 最小化
- §3 假设驱动（写下来再验证）
- §4 二分法定位
- §5 日志与断点
- §6 git bisect（回归类问题）
- §7 何时停止猜测、去读源码
- §8 修复后的收尾
- §9 一页速查清单

## §0 时间盒与止损

- 给自己一个时间盒（例如 30 分钟）仍无线索 → **换方法**：换二分法、换读源码、或向他人复述（橡皮鸭）。
- 禁止行为：连续 3 次以上"改一点、跑一下、看会不会好"而说不出因果假设。

## §1 复现

- [ ] 拿到**完整**报错原文（含 traceback 全部行），不是截图里的一行
- [ ] 固定输入：同样的命令、同一份数据、同一环境
```bash
python3 -X dev your_script.py 2>&1 | tee err.log    # 保留完整输出供 diagnoser 读取
python3 diagnoser.py --file err.log                 # 先拿机器初判（可选）
```
预期：能稳定复现（≥3 次结果一致）。
若**时好时坏** → 优先怀疑：随机 seed 未固定、字典/集合遍历顺序、并发竞态、依赖缓存。验证：`for i in 1 2 3 4 5; do python3 your_script.py; done` 比较输出是否一致。
若只在 CI 复现 → 对比 `python3 -m pip freeze` 与本地差异，以及环境变量。

## §2 最小化

目标：把问题压到**十几行**且无需外部依赖。
- [ ] 删掉与报错无关的输入数据（把 CSV 裁到 5 行）
- [ ] 删掉无关代码路径（注释掉或 `return` 早退）
- [ ] 把外部依赖（API/DB）换成硬编码常量
- [ ] 输出最小复现脚本 `minrepro.py`，它必须**独立可运行**

判据：`python3 minrepro.py` 仍报同样的错。若压到最小后错误消失 → 消失的那部分就是线索（回头用 §4 二分）。

## §3 假设驱动

- [ ] 写出假设："我认为 `X` 在 `f()` 处是 `None`，因为 `g()` 无返回值"
- [ ] 写出**预期观测**："若成立，`print(type(X))` 应输出 `<class 'NoneType'>`"
- [ ] 只做一个改动去验证它，观测结果与预期不符 → 假设错，改假设而不是继续改代码

反例（禁止）：同时改三处、换库版本、加 try/except 后"不报错了"就当修好。

## §4 二分法定位

三种粒度，从粗到细：

1. **代码二分**：在流程中点插入检查点，确认"到这里之前是对的"，则根因在后半段；再取后半段中点，直到定位到具体行。
2. **数据二分**：数据类报错（解析失败、维度不匹配）时，一半一半喂数据：
```python
df.iloc[:len(df)//2]      # 若这半不报错，坏数据在另一半
```
3. **提交二分**：昨天还好、今天坏了 → 用 `git bisect`（§6）。

## §5 日志与断点

- [ ] 用 `logging` 而非 `print`，带级别便于关掉噪音：
```python
import logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(name)s %(message)s")
log = logging.getLogger(__name__)
log.debug("x=%r type=%s", x, type(x))     # 用 %r 打印，能看见空格与 None
```
- [ ] 断点进入报错帧：
```bash
python3 -m pdb your_script.py
```
常用命令：`l`（看代码）、`n`（下一行）、`s`（进入函数）、`c`（继续）、`p expr`（打印）、`w`（看调用栈）、`q`（退出）。
- [ ] 崩溃后进入事后调试（保留现场变量）：
```bash
python3 -m pdb -c continue your_script.py    # 异常后停在报错帧
```
- [ ] 卡死/挂起类问题：用 `faulthandler` 打印卡在哪个栈：
```bash
python3 -X faulthandler your_script.py       # 再按 Ctrl+\ 触发栈转储
```

## §6 git bisect（回归类问题）

适用：明确知道"某版本之前是好的"。
```bash
git bisect start
git bisect bad                 # 当前提交有问题
git bisect good <good-commit>  # 已知正常的提交或 tag
git bisect run python3 -m pytest -x    # 自动二分：测试非 0 退出视为 bad
git bisect log                 # 查看/复盘二分过程
git bisect reset               # 结束并回到原分支（必做）
```
预期：最终输出 "X is the first bad commit"。
前提：`git bisect run` 依赖测试能**稳定**反映好坏；测试本身不稳定的话（flaky），先修测试再二分。
注意：若工作区有未提交改动，先 `git stash`；结束后 `git stash pop` 确认恢复。

## §7 何时停止猜测、去读源码

出现以下任一信号，停止试错，直接读实现：
- 参数名对了但行为与文档不符（版本差异最常见）
- 报错来自库内部，且你的调用看起来完全合法
- 同一个调用在不同数据上"有时对有时错"（多半有隐式 dtype/就地修改约定）

```bash
python3 -c "import mod; print(mod.__file__)"          # 定位实际加载的源文件
python3 -c "import inspect, mod; print(inspect.getsource(mod.func))"   # 直接看函数源码
python3 -m pip show -f package                        # 确认版本与安装位置
```
在 IPython/Jupyter 里可用 `mod.func??` 看源码。读源码时优先看：函数的**默认参数**、文档字符串里的 "Notes"（常写着边界条件）、以及是否有就地修改（in-place）语义。

## §8 修复后的收尾

- [ ] 补一个**能复现原 bug 的测试**并确认它在修复前失败（`git stash` 修复后再跑一次验证）
- [ ] 确认没有引入 `except Exception: pass`（那会把下一个 bug 藏起来）
- [ ] 用 `python3 -m pytest -x` 跑全量，而非只跑刚改的用例
- [ ] 记录到提交信息：现象 / 根因 / 修复 / 验证方式

## §9 一页速查清单

1. 拿到完整 traceback → `python3 diagnoser.py --file err.log`（机器初判）
2. 稳定复现？否 → 查 seed / 顺序 / 并发 / 环境
3. 压成 `minrepro.py`（十几行、独立可跑）
4. 写假设 + 预期观测 → 一次只改一处
5. 不定位点 → 二分（代码 / 数据 / `git bisect`）
6. 日志 `logging` + 断点 `python3 -m pdb`，必要时 `python3 -X faulthandler`
7. 库行为可疑 → 读源码（`inspect.getsource`）而不是继续猜
8. 修完补测试 → 全量 `python3 -m pytest -x` → 提交信息写清根因
