---
name: Bug report
about: 技能不工作 / 文档断链 / 构建或安装失败
title: "[bug] "
labels: bug
assignees: ""
---

**描述 / Description**

<!-- 简明描述遇到了什么问题 -->

**哪个技能或场景包 / Which skill or pack**

<!-- 例：ai-video-pipeline / video-editor；或 dist/_all.zip 整包 -->

**复现步骤 / Steps to reproduce**

1. 下载并解压 `dist/<pack>.zip`
2. 把技能目录拖进 AI 工具的 skills 目录
3. 触发词："..."
4. 实际发生：...

**期望行为 / Expected behavior**

<!-- 你期望发生什么 -->

**环境 / Environment**

- AI 工具：<!-- 例：Claude Code / 其他支持 Agent Skills 的工具 -->
- 操作系统：
- Python 版本（如涉及脚本）：

**日志或报错 / Logs or error output**

<!-- 如有，请粘贴关键报错（注意先脱敏：不要包含 API key、token、cookie 等凭据） -->

```

```

**自查清单 / Pre-flight check**

- [ ] 我已确认凭据（API key / cookie）只放在环境变量或本地文件，未粘贴到本 issue
- [ ] 我已解压最新版本的 zip（校验过 manifest 中的 sha256）
