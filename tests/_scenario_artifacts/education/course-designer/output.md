# 学习契约

| 字段 | 内容 |
|------|------|
| **Scope** | Python `asyncio` + `await` / 并发原语 / 错误处理 / 与现有生态（HTTP、数据库）整合 |
| **Level** | Intermediate（假定已掌握基础 Python 语法与函数/类，了解回调地狱痛点） |
| **Target** | 能独立写出结构清晰、有错误处理的 async/await 程序；能在面试/工作中用 asyncio 重构同步阻塞代码 |
| **Constraints** | 8 课时（每课时约 60-90 分钟）；不讲授 asyncio 源码实现细节 |

---

# Checkpoint 分解（依赖排序）

```
CP1 词法语义与事件循环 ────────────────────────────────────── 能说出 async/await 是什么，能在简单场景运行
  ↓
CP2 协程编排 ─────────────────────────────────────────────── 能用 gather/sleep 串/并行调度多个协程
  ↓
CP3 资源与异常 ───────────────────────────────────────────── 能写 try/finally + cancel 语义
  ↓
CP4 工具类封装 ───────────────────────────────────────────── 能把业务逻辑包成可复用的 async 函数/类
  ↓
CP5 生态整合 ─────────────────────────────────────────────── 能对接 aiohttp / asyncpg 等
  ↓
CP6 综合项目 ─────────────────────────────────────────────── 能完成一个真实异步任务（如并发爬虫 / 多协程模拟服务）
```

---

# 每课学习路径

## 课 1 — `async` / `await` 与事件循环
**目标（CP1）**：能用自己的话解释 "什么是协程"，能运行最简单的 `async def` 函数。

**前置**：Python 基础语法、函数定义、`pip` 使用。

**学习路径**：
1. 对比同步 `def` 与 `async def` 的代码形态差异（5 min）
2. `await` 的语义：暂停当前协程，交出控制权给事件循环（10 min）
3. 用 `asyncio.run()` 启动事件循环的最小模板（10 min）
4. 可视化：时间轴演示两个协程如何"交替执行"（10 min）
5. **练习**：写一个打印 "start → await 3s → end" 的程序，观察事件循环调度（15 min）
6. 常见错误：忘记 `await`、在同步函数里调用 `await`（10 min）

**Check-in（5 min）**：
- 口头/书面回答："`async def` 函数被调用时发生了什么？什么时候真正开始执行？"
- 代码验收：能否把一段包含 `time.sleep(3)` 的同步函数改写成异步版本并跑通？

---

## 课 2 — 协程编排：`gather` / `sleep` / `as_completed`
**目标（CP2）**：能串行和并行调度多个协程，理解 `gather` 的返回值顺序。

**前置**：完成 CP1，能运行基本 async 程序。

**学习路径**：
1. 串行 vs 并行：为什么并行不等于快（要算总等待时间）（10 min）
2. `asyncio.gather(*coros)` 的语义与返回值（15 min）
3. `asyncio.wait_for()` 与超时控制（10 min）
4. `asyncio.as_completed()` 适用场景：需要按完成顺序处理结果（10 min）
5. **练习**：写一个"下载模拟"，3 个协程各自 sleep 不同秒数，用 `gather` 收集，再用 `as_completed` 重做（20 min）
6. 坑点：`gather` 中某个协程抛异常会取消其他协程（10 min）

**Check-in（5 min）**：
- 代码：实现一个 `delayed_add(a, b, delay)` 并发求和，验证总耗时 < 单个耗时之和。
- 概念：`gather` 和 `as_completed` 的区别是什么？

---

## 课 3 — 资源管理与异常处理
**目标（CP3）**：能正确处理 `try/finally`、`async with`、`CancelledError`，写出可恢复的异步代码。

**前置**：完成 CP2，理解协程取消机制。

**学习路径**：
1. `async with` vs 普通 `with`：异步上下文管理器（10 min）
2. `try/except/finally` 在协程中的行为（10 min）
3. `CancelledError`：如何区分"正常取消"和"真实异常"（15 min）
4. `asyncio.Task` 的 `cancel()` 语义与传播链（10 min）
5. **练习**：写一个模拟数据库连接的类（`async def connect/close`），用 `async with` 包裹，并在 `finally` 中确保连接关闭（20 min）
6. 扩展：演示忘记关闭资源的后果（内存/连接泄漏）（10 min）

**Check-in（5 min）**：
- 代码：捕获 `CancelledError` 并在内部决定是否重新 raise。
- 概念：为什么在 `asyncio.Task` 中被取消的协程会引发 `CancelledError`？

---

## 课 4 — 异步工具类封装
**目标（CP4）**：能把业务逻辑封装为可复用、可测试的 async 函数/类。

**前置**：完成 CP3，理解异步上下文管理器。

**学习路径**：
1. 异步迭代器 `async for` 与 `async iterator` 协议（15 min）
2. `asyncio.Queue` 生产者-消费者模型（15 min）
3. 设计原则：单一职责、可单测（不用事件循环也能测）（10 min）
4. **练习**：实现一个 `AsyncPipeline`，支持链式 `map/filter`，内部用 `Queue` 调度（25 min）
5. 测试技巧：用 `pytest-asyncio` 或手动 `asyncio.run()` 测试异步函数（10 min）

**Check-in（5 min）**：
- 代码：提交 `AsyncPipeline` 实现，要求支持 `await p.map(f).filter(g).collect()` 风格调用。
- 概念：为什么异步迭代器比回调更优雅？

---

## 课 5 — 生态整合：HTTP 与数据库
**目标（CP5）**：能用 `aiohttp` / `asyncpg` / `httpx` 等库进行异步 IO。

**前置**：完成 CP4，理解异步工具类。

**学习路径**：
1. 为什么普通 `requests` / `psycopg2` 不能直接用在 async 环境（阻塞线程）（10 min）
2. `aiohttp.ClientSession` 的使用模式（连接池、复用）（20 min）
3. `asyncpg` 或 `databases` 异步数据库访问（20 min）
4.