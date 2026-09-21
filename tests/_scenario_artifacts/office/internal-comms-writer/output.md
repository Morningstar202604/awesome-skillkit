**主题：【重要】GitLab 服务器迁移通知及操作指引**

各位同事：

**结论先行**
公司内部 GitLab 服务器将于 **2026年9月26日（本周六）22:00 - 24:00** 进行迁移。届时服务将完全中断，恢复后域名将由 `git.corp.example.com` 变更为 `gitnew.corp.example.com`。

**影响范围**
迁移窗口期内（22:00-24:00）：
- 无法访问 GitLab Web 界面
- 无法执行 push / pull / merge 操作
- CI/CD 流水线暂停

**关键动作（请提前准备）**
1. **停止推送**：建议在 **9月26日 21:30 前** 完成所有代码推送与合并请求。
2. **切换远程地址**：服务恢复后，请使用新域名重新配置本地仓库：
   ```bash
   git remote set-url origin git@gitnew.corp.example.com:<组名>/<项目名>.git
   ```
3. **更新 IDE 配置**：如使用 GitKraken、SourceTree 等客户端，请同步更新远程仓库地址。

**FAQ 与支持**
- 详细迁移说明与常见问题：[https://wiki.corp.example.com/gitlab-migration](https://wiki.corp.example.com/gitlab-migration)
- IT 支持联系人：赵六（分机 8021）
- 如遇连接问题，请优先检查本地 git remote 地址是否已更新为新域名。

感谢大家的配合！

IT 基础设施部  
2026年9月