# 站点部署说明（GitHub Pages；GitCode / Gitee 仅作代码与 Release 镜像）

`site/` 是一个**零依赖、零构建**的静态站点：纯 HTML/CSS/JS + 一份 `data/site.json`。
数据由 `tools/build_site.py` 从 `manifest.json` / `skills/skill_chains.json` / 各技能 SKILL.md 生成，
任何静态托管都能直接跑。

**部署模式：只有 main 分支，没有发布分支。** 站点统一由 GitHub Pages 走 Actions 从 main
构建（不产生分支）；GitCode 与 Gitee 不部署站点，仅作代码与 Release 镜像。`site/skills/`、
`site/packs/` 这两个生成目录因此**必须提交进 main**——它们是站点的下载副本，
不在仓库里 = 下载按钮全部失效。

## 1. 它提供什么

| 能力 | 实现 | 说明 |
|---|---|---|
| 单个 SKILL.md 下载 | `site/skills/<域>/<技能>/SKILL.md` | 站点自带副本，同域直链，不依赖 raw 服务、不怕域名被墙 |
| 场景包 zip 下载（主） | `site/packs/<id>.zip` | 站内镜像，任何时候都可下载 |
| 场景包 zip 下载（副） | GitHub / GitCode / Gitee 的 Release 通道 | 见 §6 |
| 浏览与检索 | 403 技能 / 57 包 / 27 域 / 108 条链 | 实时搜索（命中高亮）、域筛选、三视图、包内技能跳转、`/` 聚焦搜索 |
| 换肤 | 玄青 / 玄紫 / 玄黄 + 明暗 | localStorage 记忆；27 域各有识别色 |

## 2. 本地预览

```bash
python3 build.py                     # 生成 dist/*.zip（首次或技能变更后）
python3 tools/build_site.py          # 生成 site/data + SKILL.md 副本 + zip 镜像
cd site && python3 -m http.server 8000
# 打开 http://localhost:8000
```

注意：必须走 HTTP 服务，直接双击 `index.html`（file://）会因浏览器 CORS 限制读不到 `data/site.json`，
页面会给出对应提示。

## 3. GitCode（代码与 Release 镜像；**Pages 不启用**）

GitCode 仓库 `badhope/awesome-skillkit` 只承担镜像职责：推 main 后代码同步，
`releases/tag/vX.Y.Z` 页面可用（Release 附件不支持 API 上传），仓库主页字段指向 GitHub Pages 站点。
**不再尝试开启 GitCode Pages**（平台未提供/不启用；如需请人工在平台侧处理，本仓库不做准备）。

## 4. GitHub Pages（Actions 自动部署 —— 唯一启用站点的平台）

工作流已就位：`.github/workflows/pages.yml`（push 到 main 即构建部署，不建任何分支）。

一次性开启：

```bash
# token 只走环境变量，绝不写进命令历史或仓库
export GH_TOKEN=ghp_xxx          # 需要 repo + workflow 权限

# 1) 建仓并推 main（仓库已存在则只 push）
gh repo create x33834/awesome-skillkit --public --source=. --remote=github --push
#   已有仓库时用：git remote add github https://github.com/x33834/awesome-skillkit.git
#                 git push github main

# 2) Pages 来源设为 GitHub Actions（一次性）
gh api -X POST repos/x33834/awesome-skillkit/pages -f "source[branch]=main" -f "source[path]=/" 2>/dev/null \
  || echo "→ 若 API 不接受，去 Settings → Pages → Source 手动选 GitHub Actions"

# 3) 传 Release 附件（57 个场景包 zip + 1 个 _all.zip），让包卡片的 GitHub 直链生效
gh release create v0.23.0 dist/*.zip --title "v0.23.0" --notes-file /tmp/relnotes.md
```

之后每次 push main 会自动：`build.py` → `tools/build_site.py` → 上传 `site/` → 部署。
站点地址：`https://x33834.github.io/awesome-skillkit/`

注意：推送历史含 `.github/workflows/pages.yml`，token 必须带 **`workflow`** scope，
否则 push 会被 `refusing to allow ... to create/update workflow` 拒绝。

## 5. Gitee（代码 + Release 镜像，附件可用 API 上传；**Pages 不启用**）

Gitee 仓库 `badhope/awesome-skillkit` 承担镜像职责：推 main 同步代码，Release 用
`attach_files` API 上传附件（GitCode 不行），仓库主页字段指向 GitHub Pages 站点。

```bash
# token 只走环境变量
export GITEE_TOKEN=xxx           # Gitee 私人令牌（需 projects + releases 权限）

# 1) 建仓（已存在则跳过；返回 400 = 已存在）
curl -s -X POST "https://gitee.com/api/v5/repos" \
  -H "Content-Type: application/json" \
  -d "{\"access_token\":\"$GITEE_TOKEN\",\"name\":\"awesome-skillkit\",\"private\":false,\"auto_init\":false}"

# 2) 推 main + tag（一次命令推两个 ref，一条连接）
git remote add gitee https://badhope:$GITEE_TOKEN@gitee.com/badhope/awesome-skillkit.git
git push gitee main v0.23.0

# 3) 建 Release（tag 已随上一步推上去）
curl -s -X POST "https://gitee.com/api/v5/repos/badhope/awesome-skillkit/releases" \
  -H "Content-Type: application/json" \
  -d "{\"access_token\":\"$GITEE_TOKEN\",\"tag_name\":\"v0.23.0\",\"name\":\"v0.23.0\",\"body\":\"57 scene packs\"}"

# 4) 传 58 个 zip 附件（57 场景包 + 1 个 _all.zip；逐个、间隔 1-2 秒，避免触发限流）
RID=$(curl -s "https://gitee.com/api/v5/repos/badhope/awesome-skillkit/releases/tags/v0.23.0?access_token=$GITEE_TOKEN" | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")
for z in dist/*.zip; do
  curl -s -X POST "https://gitee.com/api/v5/repos/badhope/awesome-skillkit/releases/$RID/attach_files" \
    -F "access_token=$GITEE_TOKEN" -F "file=@$z" && echo " → $z" && sleep 1.5
done
```

**Gitee Pages 不启用**：站点统一由 GitHub Pages 提供；Gitee 侧不再准备 Pages（如需请人工在平台侧处理）。

## 6. Release 附件（zip 的第二下载通道）

站内镜像（`packs/<id>.zip`）随站点一起发布，**永远可用**，是主下载按钮。
Release 附件只是第二通道，缺失不影响下载：

| 平台 | 附件直链 | 说明 |
|---|---|---|
| GitHub | `…/releases/download/vX.Y.Z/<id>.zip` | API 支持上传，发版时把 `dist/*.zip`（58 个：57 场景包 + _all）挂到 Release 资产 |
| Gitee | `…/releases/download/vX.Y.Z/<id>.zip`（与 GitHub 同构） | API 支持 `attach_files` 上传（§5 第 4 步），附件直链实测可达 |
| GitCode | 无直链，站点指向 Release 页面 | `attach_files` 接口返回 405/404，API 不支持上传附件；如需附件，在 Release 页面手动拖入 |

站点上 GitCode 的副链接因此指向 `…/releases/tag/vX.Y.Z`（Release 存在即有效），
不会给访客 404 死链。

## 7. 更新流程（技能有增删时）

```bash
python3 build.py                      # 1. 重新打包 dist/*.zip（同步 manifest）
python3 tools/build_site.py           # 2. 刷新站点数据与副本（site/skills、site/packs 进 main）
git add -A && git commit -m "..." && git push origin main
# 3. 推完即部署：GitHub Actions 自动构建并发布站点；GitCode / Gitee 同步代码与 Release 镜像（不部署站点）
```

## 8. 文件清单

| 文件 | 作用 |
|---|---|
| `site/index.html` | 页面骨架（含骨架屏、OG meta、SVG favicon） |
| `site/assets/app.css` | 样式与换肤（CSS 变量；`.bg-grid` 背景网格与 `.grid` 卡片容器严格分离） |
| `site/assets/app.js` | 数据加载、搜索高亮、筛选、三视图、域色板、count-up、快捷键 |
| `site/data/site.json` | 生成的数据（提交进仓库，文本 diff 友好） |
| `site/skills/`、`site/packs/` | 生成的可下载副本（**进 main**，Pages 直接伺服） |
| `tools/build_site.py` | 站点数据生成器（`--github-repo` / `--gitee-repo` 可改 Release 基址） |
| `.github/workflows/pages.yml` | GitHub Actions 自动部署 |
