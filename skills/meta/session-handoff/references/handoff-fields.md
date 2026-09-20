# Handoff JSON 字段

`--input handoff.json` 可含以下键（缺省用模板占位）：

| 键 | 类型 | 说明 |
|---|---|---|
| title | str | 会话标题 |
| author | str | 作者 agent 名 |
| goal | str | 原始意图 |
| done | list[str] | 已完成（按序） |
| next | list[str] | 下一步（按序） |
| gotchas | list[str] | 已知坑 |
| files | list[str] | 关键文件路径 |
| repo | str | 仓库/项目 |
| verify | str | 运行/验证方式 |
| blocker | str | 当前卡点 |

命令行同名参数会被 JSON 覆盖（JSON 优先）。
