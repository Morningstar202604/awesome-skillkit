# 贡献指南

感谢你对 **expert-teams**（平台中立的通用专家团队资产；原 `ai-expert-teams` 仓库，2026-09-27 迁入 `awesome-skillkit`）的关注！欢迎以任何形式参与贡献：提 Issue、修 Bug、写文档、加功能都可以。

## 快速开始

1. Fork [awesome-skillkit](https://github.com/X33834/awesome-skillkit) 仓库到你的账号
2. 从 `main` 创建功能分支：`git checkout -b feat/your-feature`
3. 本地开发与运行方式见 [README](README.md)；仓库整体贡献规范见上级目录的 [CONTRIBUTING.md](../CONTRIBUTING.md)
4. 提交改动并发起 Pull Request，描述清楚改了什么、为什么改

## 提交规范

- 提交信息建议遵循 Conventional Commits：`feat: 新增xx`、`fix: 修复xx`、`docs: 文档`、`chore: 杂务`
- 每个提交聚焦单一改动，便于回溯与回滚
- 不要把密钥、个人数据提交进仓库

## 问题反馈

- 提 Issue 前请先搜索是否已有同类问题
- Bug 请附上复现步骤、预期/实际行为、环境信息
- 功能建议请说明使用场景

## 行为准则

参与贡献即表示同意遵守 [贡献者行为准则](CODE_OF_CONDUCT.md)。

## 发布流程（维护者）

本子目录资产随 **awesome-skillkit** 仓库统一发布（版本、tag、Release 与站点部署均按仓库根目录 [CONTRIBUTING.md](../CONTRIBUTING.md) / [docs/VERSIONING.md](../docs/VERSIONING.md) 执行）。发版时除 pack zip 外，请一并把 `site/downloads/expert-teams-*.zip`（或重新生成的 `expert-teams/dist/zips/*.zip`）上传到 GitHub / Gitee Release 附件，供非 git 用户直接下载。

改动本子目录后，本地门禁须全绿：

```bash
python3 expert-teams/verify.py                          # 内容质量总校验（需 pyyaml）
python3 -m unittest discover -s expert-teams/tests      # 子目录单测
python3 expert-teams/build-site.py --check              # 官网数据防漂移
python3 expert-teams/export-platforms.py                # 重生成四平台安装包
python3 tools/build_site.py --no-zip                    # 同步站点子页与 site/downloads/
```
