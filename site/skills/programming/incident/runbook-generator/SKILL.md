---
name: runbook-generator
description: "Generate operational runbooks from a service name — deployment, incident response, maintenance, and rollback workflows. Templated structure customizable per environment. Use when documenting on-call procedures for a new service, standardizing incident response across teams, or producing runbooks before launching to production. 当用户要求 写运维手册 / runbook / 应急处置步骤 时使用。 Do NOT use for executing the runbook steps (generation only)."
license: Apache-2.0
compatibility: Pure prompt-based; may read project structure via Bash.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: incident
  pattern: code-generator
  tier: powerful
  verified-date: "2026-09-09"
---

# Runbook Generator

从服务名生成可运维的 runbook 骨架：部署、事故响应、维护、回滚工作流，按环境定制的模板化结构。只生成，不执行其中步骤。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 服务名 | 必需 | 位置参数，如 `payments-api` |
| `--owner` | 可选 | 负责团队，写入 runbook 头部 |
| `--output` | 可选 | 写出路径；不传则打印到 stdout |
| 服务特定命令/URL | 可选 | 生成后由人工填入 |

缺失输入时一次性问齐：「请提供：①服务名 ②负责团队（owner，可选）③输出路径（可选，默认 stdout）。其余按默认骨架生成。」

## 前置自检

```bash
python3 scripts/runbook_generator.py --help >/dev/null 2>&1   # 预期退出码 0；失败：脚本/ python3 缺失 → STOP
```

## 工作流

### 步骤 1：生成骨架

```bash
# 打印到 stdout
python3 scripts/runbook_generator.py payments-api
# 写出文件
python3 scripts/runbook_generator.py payments-api --owner platform --output docs/runbooks/payments-api.md
```

预期：输出含 start/stop/health/rollback 标准段的 runbook 骨架；`--output` 时写入目标路径。
若失败：`--output` 父目录不存在 → 先 `mkdir -p` 目标目录再写；服务名缺失 → 提示补全位置参数。

### 步骤 2：填充服务特定内容

- 用真实命令与 URL 替换占位符（每步需可复制粘贴）。
- 为每个关键步骤加健康检查；定义回滚触发条件与回滚命令。

### 步骤 3：在 staging 演练并入库

- dry-run 在 staging 验证每步预期输出。
- 存入服务代码附近的版本库，交由 on-call 团队 review。

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| 位置参数 | 服务名 | 如 `payments-api` |
| `--owner` | 团队名 | runbook 头部责任人 |
| `--output` | 文件路径 | 写出位置；不传=stdout |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------------|------|------|
| `--output` 写失败 | 父目录不存在 | `mkdir -p` 目标目录后重跑 |
| 服务名缺失 | 未传位置参数 | 补全服务名 |

## 交付标准

成功定义：每命令可复制粘贴、每关键步有预期输出、回滚步骤在 staging 验证过、owner/升级联系人当前、健康检查齐全、存入版本库并经 on-call review。
产物命名：`<service>.md`（或 `--output` 指定）。
保存位置：服务代码附近（如 `docs/runbooks/`），进入版本库。
验证完整性：逐条核对 runbook 质量清单——命令可粘贴、有预期输出、回滚已测、owner 当前、含事故通报模板、含事后更新流程。

## 安全红线

- **只生成不执行**：本技能不运行 runbook 内的任何命令（部署/回滚/重启）。实际执行由 on-call 在演练/事故中操作，并经用户确认。
- 回滚触发与命令必须在 staging 验证后再写入生产 runbook。

## 参考

- `references/runbook-templates.md` —— 部署与事故 playbook 参考模板
