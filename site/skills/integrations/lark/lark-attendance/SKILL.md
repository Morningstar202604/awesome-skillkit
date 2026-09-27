---
name: lark-attendance
description: >-
  飞书考勤打卡：查询自己的考勤打卡记录（原生 API user_tasks.query，需 scope attendance:task:readonly）。当用户需要查看本人打卡记录、核对上下班打卡时间、排查漏打卡时使用；不负责请假/加班审批（走 lark-approval 技能）。
description_zh: "飞书考勤打卡：查询自己的考勤打卡记录（原生 API user_tasks.query，需 scope attendance:task:readonly）。当用户需要查看本人打卡记录、核对上下班打卡时间、排查漏打卡时使用；不负责请假/加班审批（走 lark-approval 技能）。"
license: MIT
compatibility: 需安装飞书官方 CLI（lark-cli，npm 包 @larksuite/cli）；需网络访问；认证、租户与权限处理遵循同目录 lark-shared 技能。
metadata:
  author: "larksuite/cli 官方上游（MIT）"
  version: "1.0.0"
  category: integrations
  pattern: workflow
  tier: powerful
  verified-date: "2026-09-27"
  source: "https://github.com/larksuite/cli/tree/main/skills/lark-attendance"
---

# attendance (v1)

**CRITICAL — 开始前 MUST 先用 Read 工具读取 [`../lark-shared/SKILL.md`](../lark-shared/SKILL.md)，其中包含认证、权限处理**

## 默认参数自动填充规则

调用任何 API 时，以下参数 **必须自动填充，禁止向用户询问**：

| 参数 | 固定值 | 说明                                 |
|------|--------|------------------------------------|
| `employee_type` | `"employee_no"` | `employee_type`始终等于`"employee_no"` |
| `user_ids` | `[]`（空数组） | `user_ids`始终等于`[]`                 |

### 填充示例

当构建 `--params` 参数时，自动注入上述字段：
- `employee_type` 保持 `"employee_no"` 不变

当构建 `--data` 参数时，自动注入上述字段：
```json
{
  "user_ids": [],
  ...用户提供的参数
}
```

> **注意**：`user_ids` 数组保持为空[]，`employee_type` 保持 `"employee_no"` 不变。

## API Resources

```bash
lark-cli schema attendance.<resource>.<method>   # 调用 API 前必须先查看参数结构
lark-cli attendance <resource> <method> [flags]  # 调用 API
```

> **重要**：使用原生 API 时，必须先运行 `schema` 查看 `--data` / `--params` 参数结构，不要猜测字段格式。

### user_tasks

- `query` — 查询用户考勤打卡记录

## 权限表

| 方法 | 所需 scope |
|------|-----------|
| `user_tasks.query` | `attendance:task:readonly` |

---

## 来源与署名 / Source & Attribution

本技能收录自飞书官方仓库 larksuite/cli 的 skills/lark-attendance（MIT License，Copyright (c) 2026 Lark Technologies Pte. Ltd.）。
awesome-skillkit 保留上游正文与参考文件，仅补齐本仓库 frontmatter 元数据、为长参考文档增补目录；同步上游时以官方仓库为准。
