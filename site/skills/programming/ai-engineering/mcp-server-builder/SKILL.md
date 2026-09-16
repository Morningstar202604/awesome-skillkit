---
name: mcp-server-builder
description: "Design and ship production-ready MCP (Model Context Protocol) servers from OpenAPI contracts instead of hand-written tool wrappers. Python and TypeScript support, schema validation, safe evolution. Use when exposing an existing API as an MCP server, building tool integrations for Claude or Codex or Cursor, or scaffolding an MCP project from scratch. 当用户要求 搭 MCP 服务 / 把 API 变成 MCP / 写 MCP server / 用 OpenAPI 生成 MCP / 给 LLM 暴露 API 时使用。 Do NOT use for implementing the business logic of an existing MCP server."
license: Apache-2.0
compatibility: Pure prompt-based; may read project structure via Bash. Requires Python 3.8+ (stdlib only) to run bundled scripts.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: ai-engineering
  verified-date: "2026-09-09"
---

# MCP Server Builder

从 API 契约出发设计和交付生产可用的 MCP server，替代手写的一次性 tool 包装。聚焦快速脚手架、schema 质量、校验与安全演进。工作流支持 Python 与 TypeScript 两种 MCP 实现，把 OpenAPI 当作唯一事实来源。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| OpenAPI 规格 | 是 | `--input openapi.json`（或经 stdin 传入）；须为合法 OpenAPI 文档 |
| 服务名 | 是 | `--server-name`，如 `billing-mcp`；决定生成目录与工具前缀 |
| 语言 | 否 | `--language python\|typescript`，默认 python |
| 输出目录 | 否 | `--output-dir`，默认 `./out` |
| 运行时配置 | 否 | 供 mcp_validator 校验的可选运行时配置路径 |

缺失时一次性问齐：
「请提供：①OpenAPI 规格路径（或贴入内容经 stdin）②服务名 `--server-name` ③语言 python/typescript ④输出目录（默认 `./out`）。其余我用默认值；确认后开始。」

## 前置自检

- Python 3.8+ 可用：`python3 --version` → 输出版本号 ≥3.8。否则提示安装后 **STOP**。
- 两个脚本在盘：`test -f scripts/openapi_to_mcp.py && test -f scripts/mcp_validator.py` → 均存在；任一缺失 → **STOP** 报告文件名。
- OpenAPI 规格可读：`test -r <input>` 或 stdin 有内容。否则报错并提示用户提供。

## 工作流

### 步骤 1：从 OpenAPI 生成 MCP 脚手架

```bash
python3 scripts/openapi_to_mcp.py \
  --input openapi.json \
  --server-name billing-mcp \
  --language python \
  --output-dir ./out \
  --format text
```

也支持 stdin：

```bash
cat openapi.json | python3 scripts/openapi_to_mcp.py --server-name billing-mcp --language typescript
```

动作：读取 OpenAPI，将 paths/operations 转为 MCP tool 定义，生成 manifest + 起始服务端代码。
预期：在 `--output-dir` 下生成服务端脚手架与 `tool_manifest.json`；退出码 `0`；`--format text` 打印报告。
若失败：OpenAPI 非法 → 脚本报 schema 错误，先修规格；`--server-name` 冲突 → 换名或删旧目录。

### 步骤 2：校验 MCP 工具定义

```bash
python3 scripts/mcp_validator.py --input out/tool_manifest.json --strict --format text
```

动作：在集成测试前校验 manifest，检查重复名、非法 schema 形状、缺失描述、空 required 字段、命名卫生。
预期：打印校验报告；无错误时退出码 `0`。
若失败：`--strict` 下存在错误 → 退出码非 0；按报告修复 manifest 后重跑。

### 步骤 3：选择运行时

- **Python**：快速迭代、数据密集型后端首选。
- **TypeScript**：统一 JS 技术栈、前后端契约复用更紧。
- 即使 transport/runtime 变化，也要保持 tool contract 稳定。

### 步骤 4：生产加固

发布前关键项：
- 密钥走环境变量，不要写进 tool schema
- 优先出站 host 白名单，而非开放代理
- 仅做增量式改动；绝不在原地重命名 tool 名

完整加固指引见 references/production-hardening-guide.md。

## 脚本接口

- `python3 scripts/openapi_to_mcp.py --help`
  - 从 stdin 或 `--input` 读取 OpenAPI
  - 产出 manifest + 服务端脚手架
  - 输出 JSON 摘要或 text 报告
- `python3 scripts/mcp_validator.py --help`
  - 校验 manifest 与可选运行时配置
  - strict 模式存在错误时返回非 0 退出码

## 参数速查表

| 脚本 | 参数 | 取值 | 说明 |
|------|------|------|------|
| openapi_to_mcp.py | `--input` | 路径 | OpenAPI 规格文件 |
| | `--server-name` | 字符串 | 服务名，决定目录/前缀 |
| | `--language` | `python\|typescript` | 目标语言 |
| | `--output-dir` | 路径 | 输出目录，默认 `./out` |
| | `--format` | `text\|json` | 输出格式 |
| mcp_validator.py | `--input` | 路径 | `tool_manifest.json` 路径 |
| | `--strict` | 标志 | 严格模式，错误即非 0 退出 |
| | `--format` | `text\|json` | 输出格式 |

## 失败处置表

| 现象/错误 | 原因 | 处置 |
|-----------|------|------|
| `python3: command not found` | Python 未装 | 安装 3.8+ 后重跑 |
| 脚本 `FileNotFoundError` | 脚本缺失 | STOP 报告缺失文件名 |
| OpenAPI schema 错误 | 规格非法 | 修复 OpenAPI 后再生成 |
| mcp_validator 非 0 退出 | manifest 有错 | 按报告修重名/缺描述/空 required |
| 重复 tool 名 | 多路径同名 | 在规格中消歧或重命名 |

## 交付标准

成功定义：由 OpenAPI 生成可运行的脚手架，`mcp_validator.py --strict` 退出码 `0`，tool 名唯一、描述完整、无空 required。
产物命名/位置：`--output-dir` 下的服务端代码与 `tool_manifest.json`。
完整性验证：重跑 `mcp_validator.py --input out/tool_manifest.json --strict` 退出码为 `0`。

## 参考

- references/production-hardening-guide.md — 加固/发布前读：auth & 安全设计、版本策略、常见坑、测试与部署
- references/openapi-extraction-guide.md — 从源码抽取 OpenAPI 时读
- references/python-server-template.md — 选 Python 时读的起始模板
- references/typescript-server-template.md — 选 TypeScript 时读的起始模板
- references/validation-checklist.md — 发布前逐项核对清单
- README.md — 本技能总览与安装说明
