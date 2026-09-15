# 站点部署说明（GitHub Pages + GitCode Pages）

`site/` 是一个**零依赖、零构建**的静态站点：纯 HTML/CSS/JS + 一份 `data/site.json`。
数据由 `tools/build_site.py` 从 `manifest.json` / `skills/skill_chains.json` / 各技能 SKILL.md 生成，
任何静态托管都能直接跑。

## 1. 它提供什么

| 能力 | 实现 | 说明 |
|---|---|---|
| 单个 SKILL.md 下载 | `site/skills/<域>/<技能>/SKILL.md` | 站点自带副本，同域直链，不依赖 raw 服务、不怕域名被墙 |
| 场景包 zip 下载（主） | `site/packs/<id>.zip` | 站内镜像，任何时候都可下载 |
| 场景包 zip 下载（副） | GitHub / GitCode Releases 附件 | 版本化附件链接，`/releases/download/v0.14.0/<id>.zip` |
| 浏览与检索 | 112 技能 / 27 包 / 12 域 / 39 条链 | 实时搜索、域筛选、三视图切换、包内技能跳转 |
| 换肤 | 玄青 / 玄紫 / 玄黄 + 明暗 | localStorage 记忆 |

**为什么 zip 给两条链接**：`dist/` 按仓库既定策略不进主仓库（走 Releases 发布），
所以 Release 附件可能尚未上传；站内镜像保证下载按钮永不 404，Release 就绪后可切为主入口。

## 2. 本地预览

```bash
python3 build.py                     # 生成 dist/*.zip（首次或技能变更后）
python3 tools/build_site.py          # 生成 site/data + SKILL.md 副本 + zip 镜像
cd site && python3 -m http.server 8000
# 打开 http://localhost:8000
```

注意：必须走 HTTP 服务，直接双击 `index.html`（file://）会因浏览器 CORS 限制读不到 `data/site.json`，
页面会给出对应提示。

## 3. GitCode Pages（已推送分支，需一次性开启）

分支 `gh-pages` 已由 `tools/publish_site.py` 推送，只需在平台点一次：

1. 打开 `https://gitcode.com/badhope/awesome-skillkit` → **项目设置 → Pages**（或项目菜单 Pages）
2. 模板选 **html**；部署分支选 **gh-pages**；路径填 **/**
3. 保存，等 1–2 分钟，平台会分配地址（形如 `https://gitcode.host/badhope/awesome-skillkit`）

后续更新站点只需重跑：

```bash
python3 tools/publish_site.py        # 重新生成并强推 gh-pages
```

## 4. GitHub Pages（Actions 自动部署）

工作流已就位：`.github/workflows/pages.yml`（push 到 main 即构建部署）。

一次性开启：

```bash
# token 只走环境变量，绝不写进命令历史或仓库
export GH_TOKEN=ghp_xxx          # 需要 repo + workflow 权限

# 1) 建仓并推 main（仓库已存在则只 push）
gh repo create MS33834/awesome-skillkit --public --source=. --remote=github --push
#   已有仓库时用：git remote add github https://github.com/MS33834/awesome-skillkit.git
#                 git push github main

# 2) Pages 来源设为 GitHub Actions（一次性）
gh api -X POST repos/MS33834/awesome-skillkit/pages -f "source[branch]=main" -f "source[path]=/" 2>/dev/null \
  || echo "→ 若 API 不接受，去 Settings → Pages → Source 手动选 GitHub Actions"

# 3) 传 Release 附件（28 个 zip），让包卡片的 GitHub 直链生效
gh release create v0.14.0 dist/*.zip --title "v0.14.0" --notes-file /tmp/relnotes.md
```

之后每次 push main 会自动：`build.py` → `tools/build_site.py` → 上传 `site/` → 部署。
站点地址：`https://ms33834.github.io/awesome-skillkit/`

若不想用 Actions，也可复用同一套发布脚本：

```bash
git remote add github https://<token>@github.com/MS33834/awesome-skillkit.git
python3 tools/publish_site.py --remote github      # 推 gh-pages 分支
# 然后 Settings → Pages → Deploy from a branch → gh-pages / (root)
```

## 5. Release 附件（zip 的第二下载通道）

站内镜像（`packs/<id>.zip`）随站点一起发布，**永远可用**，是主下载按钮。
Release 附件只是第二通道，缺失不影响下载：

| 平台 | 附件直链 | 说明 |
|---|---|---|
| GitHub | `…/releases/download/vX.Y.Z/<id>.zip` | API 支持上传，发版时把 `dist/*.zip`（28 个）挂到 Release 资产 |
| GitCode | 无直链，站点指向 Release 页面 | `attach_files` 接口返回 405/404，API 不支持上传附件；如需附件，在 Release 页面手动拖入 |

站点上 GitCode 的副链接因此指向 `…/releases/tag/vX.Y.Z`（Release 存在即有效），
不会给访客 404 死链。

## 6. 更新流程（技能有增删时）

```bash
python3 build.py                      # 1. 重新打包 dist/*.zip（同步 manifest）
python3 tools/build_site.py           # 2. 刷新站点数据与副本
python3 tools/publish_site.py         # 3. 推 GitCode gh-pages
git add -A && git commit -m "..." && git push origin main   # 4. main（GitHub Actions 自动部署）
```

## 7. 文件清单

| 文件 | 作用 |
|---|---|
| `site/index.html` | 页面骨架 |
| `site/assets/app.css` | 样式与换肤（CSS 变量） |
| `site/assets/app.js` | 数据加载、搜索、筛选、视图切换、下载 |
| `site/data/site.json` | 生成的数据（提交进仓库，文本 diff 友好） |
| `site/skills/`、`site/packs/` | 生成的可下载副本（gitignore，随发布分支走） |
| `tools/build_site.py` | 站点数据生成器（`--github-repo` 可改 Release 基址） |
| `tools/publish_site.py` | 发布到 Pages 分支（`--remote` / `--branch` / `--dry-run`） |
| `.github/workflows/pages.yml` | GitHub Actions 自动部署 |
