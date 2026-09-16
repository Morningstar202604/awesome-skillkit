# 来源与方法论说明

- 技能：webapp-flow-tester（awesome-skillkit 原创编写，Apache-2.0）。
- 方法论 distilled from Anthropic public skills docs (no content copied)：仅借鉴"测试本地 Web 应用时先侦察页面再写选择器、由包装脚本统一管理服务进程生命周期"这一公开的方法论思想，本目录下的 SKILL.md、dump 脚本、测试模板与 with_server.py 均为从零原创，未复制、翻译或改写任何上游文档的段落、示例或代码。
- "启动 → 轮询就绪 → 执行 → 必清理"的包装器模式为本仓库独立实现（socket 轮询 + 进程组信号清理）。
- 许可：本技能及参考文件以 Apache-2.0 分发，与上游文档的许可条款互不适用。
