---
name: static-blog-deploy
description: >
  静态博客构建与部署自动化，封装六类部署：Hexo、Hugo（同步到 user@host:/path
  或 s3://bucket/path）、GitHub Pages（推 gh-pages 分支或 gh workflow run 触发
  Actions）、GitLab Pages（推分支或触发 CI）、Vercel（vercel --prod，需
  VERCEL_TOKEN）、Netlify（netlify deploy --prod，需 NETLIFY_AUTH_TOKEN）。
  默认 dry-run 只打印命令，加 --execute 才真正运行；SSH key 与平台 token 走
  环境变量或 CLI 登录态，不写入仓库。Use when the user asks to 部署博客 / 发布静态站点 /
  部署 Hexo / 部署 Hugo / 推到 GitHub Pages / 发布到 Vercel / 部署到 Netlify /
  deploy my static blog / deploy a Hugo site / publish to GitHub Pages.
  Do NOT use for Jekyll 等未列出的生成器、不用于带后端与数据库的动态站点部署、
  不用于域名 DNS 解析与证书申请，也不用于文章写作与内容生成。
description_zh: Hexo/Hugo/GitHub Pages/GitLab Pages/Vercel/Netlify 静态站点部署自动化
version: 1.0.0
author: skillkit authors
license: Apache-2.0
compatibility: Requires network access to static hosting providers (GitHub Pages / GitLab Pages / Vercel / Netlify) and valid session credentials in environment variables. Python 3.8+.
tags: [static-site, hexo, hugo, github-pages, gitlab-pages, vercel, netlify, deployment]
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: "content-publishing"
  verified-date: "2026-08-26"
---

# Static Blog Deploy

静态博客部署工具，支持主流静态站点生成器与托管平台。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 子命令 | 是 | `hexo-deploy` / `hugo-deploy` / `github-pages` / `gitlab-pages` / `vercel-deploy` / `netlify-deploy` |
| 项目目录 | 是 | 静态站点生成器项目根目录（全局 `--cwd` 或先 `cd` 过去） |
| 部署目标 | hugo-deploy 时必需 | `--target`：`user@host:/path` 或 `s3://bucket/path` |
| 部署方式 | github-pages/gitlab-pages 时必需 | `--method branch` / `--method actions`（GH）、`--method branch` / `--method ci`（GL） |
| 平台凭据 | 按平台 | 见"认证"节 |
| `--execute` | 否 | 不加则 dry-run，只打印将执行的命令 |

缺输入时一次性问齐（不要分多轮追问）：
"请提供：① 生成器/托管平台（Hexo/Hugo/GitHub Pages/GitLab Pages/Vercel/Netlify）；② 项目根目录路径；③ 该平台必需凭据（token/登录态）；④ Hugo 还需部署目标，GitHub/GitLab Pages 还需部署方式。"

## 前置自检

依次执行，任一失败 → 按提示修复后 STOP，不要继续部署：

```bash
# 1. Python 3 与脚本就位
python3 --version && test -f scripts/static_blog_deploy.py && echo OK
# 预期：Python 3.x + OK；失败 → 安装 Python 3.8+ / cd 到本技能目录

# 2. 项目目录是有效的站点项目（以 Hexo/Hugo 为例）
test -f /path/to/site/_config.yml || test -f /path/to/site/hugo.toml && echo OK
# 预期：OK；失败 → 目录不对，让用户确认项目根目录

# 3. 平台凭据在（按目标平台选其一核对）
test -n "$VERCEL_TOKEN" && echo Vercel OK; test -n "$NETLIFY_AUTH_TOKEN" && echo Netlify OK; gh auth status
# 预期：对应平台输出 OK / 已登录；失败 → 按下文"认证"节配置，凭据绝不写入仓库

# 4. 对应 CLI 工具已安装（按平台）
command -v hexo hugo git vercel netlify rsync | cat
# 预期：目标平台用到的 CLI 都有输出；缺哪个装哪个
```

## 支持平台

- **Hexo** — `hexo clean && hexo generate && hexo deploy`
- **Hugo** — `hugo --minify` + rsync/SSH/S3 同步
- **GitHub Pages** — 推送到 `gh-pages` 分支或触发 GitHub Actions
- **GitLab Pages** — 推送到 `pages` 分支或触发 CI
- **Vercel** — `vercel --prod` CLI 部署
- **Netlify** — `netlify deploy --prod` CLI 部署

## 安全设计

- **默认 dry-run**：所有部署命令默认只打印将执行的命令，不真正运行；加 `--execute` 才真正运行。
- **凭据隔离**：
  - SSH key / GitHub token / 云厂商密钥从环境变量读取
  - 绝不将密钥写入代码仓库

## 使用示例

```bash
# Hexo 部署
cd /path/to/hexo-blog
python static_blog_deploy.py hexo-deploy --execute

# Hugo 部署（同步到服务器）
cd /path/to/hugo-blog
python static_blog_deploy.py hugo-deploy --execute \
  --target user@host:/var/www/blog

# Hugo 部署（同步到 S3）
python static_blog_deploy.py hugo-deploy --execute \
  --target s3://my-bucket/blog

# GitHub Pages（推送到 gh-pages 分支）
cd /path/to/repo
python static_blog_deploy.py github-pages --execute \
  --method branch \
  --branch gh-pages \
  --commit-msg "chore: deploy"

# GitHub Pages（触发 GitHub Actions）
python static_blog_deploy.py github-pages --execute \
  --method actions \
  --workflow deploy.yml

# GitLab Pages
python static_blog_deploy.py gitlab-pages --execute --method branch

# Vercel 部署
export VERCEL_TOKEN="your_token"
python static_blog_deploy.py vercel-deploy --execute --scope my-team

# Netlify 部署
export NETLIFY_AUTH_TOKEN="your_token"
python static_blog_deploy.py netlify-deploy --execute --site my-site
```

## 工作流

一次部署按以下 3 步执行；所有平台子命令都遵守 dry-run 默认。

### 步骤 1：dry-run 预演

- **动作**：不带 `--execute` 运行目标子命令，如 `python static_blog_deploy.py hexo-deploy`。
- **预期**：stdout 打印将执行的完整命令序列，退出码 0；命令内容与"支持平台"节描述一致。
- **若失败**：退出码 1 + 参数错误 → 对照"参数速查表"修正；提示找不到生成器配置 → 项目目录不对，回前置自检第 2 项。

### 步骤 2：执行部署

- **动作**：确认预演命令无误后加 `--execute` 重跑同一命令；Vercel/Netlify 确保 token 在环境变量或用 `--token`/`--auth` 传入。
- **预期**：退出码 0；部署命令真实运行完成（hexo/hugo 构建并同步，或 CLI 返回部署成功）。
- **若失败**：构建失败 → 用生成器 CLI 手动跑一次构建定位报错（如 `hugo --minify`）；认证失败 → 回前置自检第 3 项更新凭据；SSH 同步失败 → 检查 key 免密登录。

### 步骤 3：验证线上结果

- **动作**：打开站点线上地址（或 `curl -sI <站点URL>`），确认本次发布内容可见。
- **预期**：HTTP 200，且能看到本次更新的页面/资源。
- **若失败**：站点内容未更新 → GitHub Actions/CI 触发型部署查 workflow 运行日志；CDN 缓存 → 等待或按平台文档清缓存后复验。

## 认证

- **SSH/rsync**：需配置 SSH key 免密登录
- **GitHub Actions**：需 `gh` CLI 已认证（`gh auth login`）
- **GitLab CI**：需 GitLab Runner 已配置
- **Vercel**：需 `VERCEL_TOKEN` 环境变量或 `--token`
- **Netlify**：需 `NETLIFY_AUTH_TOKEN` 环境变量或 `--auth`

```bash
export VERCEL_TOKEN="xxx"
export NETLIFY_AUTH_TOKEN="xxx"
```

## 退出码

- `0` 成功
- `1` 参数错误或部署失败

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| 子命令 | `hexo-deploy` / `hugo-deploy` / `github-pages` / `gitlab-pages` / `vercel-deploy` / `netlify-deploy` | 六类部署，见"支持平台"节 |
| `--cwd` | 项目根目录路径 | 全局参数，指定站点项目目录 |
| `--execute` | 开关 | 缺省 dry-run 只打印命令 |
| `--target` | `user@host:/path` 或 `s3://bucket/path` | hugo-deploy 必需 |
| `--method` | `branch`/`actions`（GH）；`branch`/`ci`（GL） | Pages 部署方式 |
| `--branch` / `--commit-msg` | 分支名 / 提交信息 | Pages branch 方式使用 |
| `--workflow` | workflow 文件名 | GitHub Pages actions 方式使用 |
| `--ci-branch` | 分支名 | GitLab Pages ci 方式使用 |
| `--token` | Vercel token | vercel-deploy，缺省读 `VERCEL_TOKEN` |
| `--scope` | 团队/个人 scope | vercel-deploy |
| `--auth` | Netlify token | netlify-deploy，缺省读 `NETLIFY_AUTH_TOKEN` |
| `--site` / `--dir` | 站点名 / 目录 | netlify-deploy |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|-------------|------|------|
| 退出码 1 + 参数错误 | 参数拼写/缺漏 | 对照"参数速查表"修正，先 dry-run 预演 |
| hexo/hugo 构建失败 | 生成器报错或项目配置问题 | 手动运行 `hexo generate` / `hugo --minify` 定位报错 |
| rsync/SSH 失败 | key 未配置免密登录 | 按"认证"节配置 SSH key；确认 `user@host` 可达 |
| GitHub Actions 未触发 | `gh` 未登录或 workflow 文件名错 | `gh auth login` 后重试；核对 `--workflow` 文件名 |
| GitLab Pages 未触发 | Runner 未配置或分支不对 | 检查 CI 配置与 `--ci-branch` |
| Vercel/Netlify 认证失败 | token 缺失或过期 | 更新 `VERCEL_TOKEN` / `NETLIFY_AUTH_TOKEN` 环境变量 |
| 部署成功但站点未更新 | CDN 缓存或 CI 排队 | 查平台构建日志；必要时清缓存后复验 |

## 交付标准

- **成功定义**：`--execute` 下部署退出码 0，且步骤 3 验证线上内容已更新。
- **产物命名**：构建产物在项目生成器默认输出目录（Hexo `public/`、Hugo `public/`），不在本技能内重命名。
- **保存位置**：站点产物留在项目目录；token 永远只在环境变量或 CLI 登录态，绝不写入仓库。
- **完整性验证**：线上 URL 返回 HTTP 200 且含本次更新内容；dry-run 与实际执行的命令序列一致。

## 依赖

- Python 3.8+
- 标准库
- 对应 CLI 工具（hexo、hugo、git、vercel、netlify、aws、gh、rsync 等）
- `publish_common`

## 相关技能

- `cross-post-orchestrator` — 多平台编排
- `ai-cover-generator` — AI 封面图生成（用于博客封面）