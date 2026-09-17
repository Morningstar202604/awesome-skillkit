---
name: performance-profiler
description: "对 Node.js、Python、Go 应用做系统性性能剖析：定位 CPU/内存/I/O 瓶颈、生成火焰图、分析包体积、优化数据库查询、用 k6 与 Artillery 跑压测。始终先测后改。何时使用：排查慢接口、规划性能预算或定位内存泄漏时。触发场景（中/英）：性能分析 / 找瓶颈 / 优化慢代码 / profile performance / find bottleneck / optimize slow code。排除项：不改业务代码修复热点（仅做剖析）。 何时使用：接口变慢、内存持续增长或需要定性能预算时。触发场景（中/英）：性能分析 / 找瓶颈 / 优化慢代码 / 内存泄漏排查 / profile performance / find bottleneck / optimize slow code.排除项：不直接改业务代码修复热点（仅做剖析与建议）。Use when the user asks 性能分析 / 找瓶颈 / 优化慢代码 / 内存泄漏排查 / profile performance / find bottleneck / optimize slow code. Do NOT use when the ask is to patch business logic or refactor the hot path directly (this skill only diagnoses)."
license: Apache-2.0
compatibility: Pure prompt-based; may read project structure via Bash.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: performance
  pattern: single-task
  tier: powerful
  verified-date: "2026-09-09"
---

# Performance Profiler

系统性性能剖析：定位瓶颈、量化前后差异、给出优化方向。

## 核心能力

- **CPU 剖析** — Node.js 火焰图、Python py-spy、Go pprof
- **内存剖析** — 堆快照、泄漏检测、GC 压力
- **包体积分析** — webpack-bundle-analyzer、Next.js bundle analyzer
- **数据库优化** — EXPLAIN ANALYZE、慢查询日志、N+1 检测
- **压测** — k6 脚本、Artillery 场景、阶梯加压
- **前后对比** — 先建基线，再剖析、优化、复测验证

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| project_path | 是 | 待剖析项目根目录路径 |
| format | 否 | `text` / `json`（用 `--json`） | text |
| large_file_threshold_kb | 否 | 大文件告警阈值（KB） | 脚本默认 |

缺失时一次性问齐：「请提供：① project_path（项目根目录）。输出格式与阈值我按默认处理。」

## 前置自检

```bash
python3 --version
test -f scripts/performance_profiler.py && echo "OK script present"
```

- 预期：版本号输出；脚本存在打印 `OK script present`。
- 若失败：脚本缺失 → STOP 回报；非 Python 项目剖析时还需对应运行时（node/py-spy/go）与 k6/artillery 按需安装。

## 工作流

### 步骤 1：扫描风险指标（基线）

```bash
python3 scripts/performance_profiler.py /path/to/project
python3 scripts/performance_profiler.py /path/to/project --json
python3 scripts/performance_profiler.py /path/to/project --large-file-threshold-kb 256
```

- 动作：扫描项目，输出性能风险指标（大文件、可疑模式等）。
- 预期：终端打印风险清单；`--json` 时输出结构化 JSON；`--large-file-threshold-kb` 覆盖阈值。
- 若失败：`No such file or directory` → project_path 错；非预期退出 → 去掉 `--json` 看文本报错。

### 步骤 2：建立前后测量基线

- 动作：在任意优化前记录 P50/P95/P99 延迟、RPS、错误率、内存占用。
- 预期：得到可对比的数字基线。
- 若失败：无监控数据 → 先用步骤 1 扫描 + 运行时 profiler 取数，禁止凭感觉优化。

### 步骤 3：按语言剖析并优化

- 动作：对照 references/profiling-recipes.md 取对应命令生成火焰图/堆快照；按 references/optimization-playbook.md 的清单做优化。
- 预期：定位到具体热点（函数/查询/依赖）。
- 若失败：无热点 → 回到基线确认瓶颈假设是否成立。

### 步骤 4：复测验证

- 动作：优化后重复步骤 1–2，对比基线确认改善。
- 预期：关键指标较基线下降（延迟）或资源占用减少。
- 若失败：无改善甚至回退 → 回滚变更，重读 recipes 选其他路径。

## 快速优化清单

- 数据库：为高频查询列加索引；连接池（pgBouncer/HikariCP）；结果缓存（Redis）；把 N+1 合并为批量查询。
- 应用：同步 I/O 改异步；大结果集分页；大文件流式处理；缓存昂贵计算（LRU/Redis）。
- 前端：大包 code-split（动态 import）；首屏外图片懒加载；gzip/brotli 压缩；静态资源走 CDN。

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------------|------|------|
| `No such file or directory` | project_path 错误 | 核对路径后重跑 |
| 非预期非零退出 | 项目含不支持结构 | 去掉 `--json` 看文本错误 |
| 优化后指标无改善 | 热点判断错 | 回滚，重读 profiling-recipes.md |
| 缺运行时工具 | node/py-spy/go 未装 | 安装对应剖析工具后重测 |

## 交付标准

- 成功定义：产出基线数字 + 热点定位 + 优化后复测对比（至少延迟或资源一项有改善）。
- 产物命名：`profile-<date>.json`（--json 时）或终端报告文本。
- 保存位置：项目根目录或用户指定目录。
- 验证完整性：前后两次 `--json` 输出可解析，关键指标字段存在且可对比。

## 参考

- references/profiling-recipes.md — Node/Python/Go 剖析命令、火焰图、堆快照时读
- references/optimization-playbook.md — 前后测量模板、DB/Node/包/API 优化清单、常见陷阱时读
