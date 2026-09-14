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
tags: [static-site, hexo, hugo, github-pages, gitlab-pages, vercel, netlify, deployment]
metadata:
  version: "1.0"
  category: "content-publishing"
  verified-date: "2026-08-26"
---

# Static Blog Deploy

静态博客部署工具，支持主流静态站点生成器与托管平台。

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

## 依赖

- Python 3.8+
- 标准库
- 对应 CLI 工具（hexo、hugo、git、vercel、netlify、aws、gh、rsync 等）
- `publish_common`

## 相关技能

- `cross-post-orchestrator` — 多平台编排
- `ai-cover-generator` — AI 封面图生成（用于博客封面）