# 站点部署说明（GitHub Pages + GitCode Pages）

`site/` 是一个**零依赖、零构建**的静态站点：纯 HTML/CSS/JS + 一份 `data/site.json`。
数据由 `tools/build_site.py` 从 `manifest.json` / `skills/skill_chains.json` / 各技能 SKILL.md 生成，
任何静态托管都能直接跑。

**部署模式：只有 main 分支，没有发布分支。** GitCode Pages 直接指向 `main` 的 `/site`
目录；GitHub Pages 走 Actions（从 main 构建，同样不产生分支）。`site/skills/`、
`site/packs/` 这两个生成目录因此**必须提交进 main**——它们是站点的下载副本，
不在仓库里 = 下载按钮全部失效。

## 1. 它提供什么

| 能力 | 实现 | 说明 |
|---|---|---|
| 单个 SKILL.md 下载 | `site/skills/<域>/<技能>/SKILL.md` | 站点自带副本，同域直链，不依赖 raw 服务、不怕域名被墙 |
| 场景包 zip 下载（主） | `site/packs/<id>.zip` | 站内镜像，任何时候都可下载 |
| 场景包 zip 下载（副） | GitHub Release 附件直链 / GitCode Release 页面 | 见 §5 |
| 浏览与检索 | 112 技能 / 27 包 / 12 域 / 39 条链 | 实时搜索（命中高亮）、域筛选、三视图、包内技能跳转、`/` 聚焦搜索 |
| 换肤 | 玄青 / 玄紫 / 玄黄 + 明暗 | localStorage 记忆；12 域各有识别色 |

## 2. 本地预览

```bash
python3 build.py                     # 生成 dist/*.zip（首次或技能变更后）
python3 tools/build_site.py          # 生成 site/data + SKILL.md 副本 + zip 镜像
cd site && python3 -m http.server 8000
# 打开 http://localhost:8000
```

注意：必须走 HTTP 服务，直接双击 `index.html`（file://）会因浏览器 CORS 限制读不到 `data/site.json`，
页面会给出对应提示。

## 3. GitCode Pages（main + /site，一次性开启）

1. 打开 `https://gitcode.com/badhope/awesome-skillkit` → **项目设置 → Pages**（或项目菜单 Pages）
2. 模板选 **html**；部署分支选 **main**；路径填 **/site**
3. 保存，等 1–2 分钟，平台会分配地址

后续更新站点 = 正常推 main（见 §6），Pages 自动跟着走，无额外发布动作。

## 4. GitHub Pages（Actions 自动部署）

工作流已就位：`.github/workflows/pages.yml`（push 到 main 即构建部署，不建任何分支）。

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
python3 tools/build_site.py           # 2. 刷新站点数据与副本（site/skills、site/packs 进 main）
git add -A && git commit -m "..." && git push origin main
# 3. 推完即部署：GitCode Pages 读 main/site；GitHub Actions 自动构建发布
```

## 7. 文件清单

| 文件 | 作用 |
|---|---|
| `site/index.html` | 页面骨架（含骨架屏、OG meta、SVG favicon） |
| `site/assets/app.css` | 样式与换肤（CSS 变量；`.bg-grid` 背景网格与 `.grid` 卡片容器严格分离） |
| `site/assets/app.js` | 数据加载、搜索高亮、筛选、三视图、域色板、count-up、快捷键 |
| `site/data/site.json` | 生成的数据（提交进仓库，文本 diff 友好） |
| `site/skills/`、`site/packs/` | 生成的可下载副本（**进 main**，Pages 直接伺服） |
| `tools/build_site.py` | 站点数据生成器（`--github-repo` 可改 Release 基址） |
| `.github/workflows/pages.yml` | GitHub Actions 自动部署 |
