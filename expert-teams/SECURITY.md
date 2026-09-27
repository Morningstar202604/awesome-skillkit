# 安全策略

## 报告漏洞

如果发现安全漏洞，请**不要**在公开 Issue 中披露细节，以免被恶意利用。请通过以下方式私下联系维护者：

- 在 [awesome-skillkit 仓库](https://github.com/X33834/awesome-skillkit)（GitHub / [GitCode](https://gitcode.com/badhope/awesome-skillkit) / [Gitee](https://gitee.com/badhope/awesome-skillkit) 任一平台）提交 Issue 声明"发现安全问题，请求私下沟通渠道"
- 或通过 [仓库所有者主页](https://gitcode.com/badhope) 获取联系方式

我们会尽快响应、确认并修复，修复后再公开披露细节。

## 支持的版本

仅最新发布版本（`main` 分支最新提交）接受安全修复。

## 已知的安全边界

- 本子目录为纯 Markdown 资产 + Python 校验/导出脚本，**无后端、无 `.env`**
- 请勿将任何 API Key、token、Cookie、凭据提交进仓库（`.gitignore` 已排除 `dist/`、`.aqg/` 等本地产物）
- `dist/` 导出包由脚本从仓库实装生成，**不含任何密钥**；若发现密钥泄露，立即在 Issue 报告并轮换凭据
