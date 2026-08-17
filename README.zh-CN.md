---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 98adaa6f98486df4666888a6691e7607_1c7ffc529a2411f1a98a525400f8a581
    ReservedCode1: c4Rcdsi8C/sVj6fiVq4Ms4viKQX6q4HD1vDadl70xfx5rJy2EmbQEOQ+p5zksHxfy/Coo9Ty/ZYTVdtB+lUOC58bDmBroB3c0KeHPHaGLU2OtOAyuBoohhqEJkz/I15vnYjSCc/8Rl5BSj3TgOStUmyPjqXvQUEaME3595ryAZRWcCD0Ry0lIH7/OI0=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 98adaa6f98486df4666888a6691e7607_1c7ffc529a2411f1a98a525400f8a581
    ReservedCode2: c4Rcdsi8C/sVj6fiVq4Ms4viKQX6q4HD1vDadl70xfx5rJy2EmbQEOQ+p5zksHxfy/Coo9Ty/ZYTVdtB+lUOC58bDmBroB3c0KeHPHaGLU2OtOAyuBoohhqEJkz/I15vnYjSCc/8Rl5BSj3TgOStUmyPjqXvQUEaME3595ryAZRWcCD0Ry0lIH7/OI0=
---



# awesome-skillkit

[English](README.md) | **中文**

常用技能包合集。**下载 zip → 解压 → 拖进 AI 工具的 skills 目录 → 立即生效**，不用再纠结一堆技能该用哪个。

## 定位

**场景即答案，落地到平台+工具。**

- 每个技能包对应一个**具体使用场景**（"我要发博客"、"我要发知乎"），而不是"营销""工程"这类大领域。
- 细节落到**平台 + 工具**：如"博客园发文"（cnblogs.com + API/浏览器）、"知乎发文"（zhihu.com + Playwright）。
- 包内只放精选的 3-5 个技能，下载即用，不堆数量。

## 快速选择

| 技能 | 场景 | 平台 + 工具 | 什么时候用 |
|------|------|-----------|-----------|
| [agent-builder-skill](skills/agent-builder-skill/) | 开发 | 通用 + 代码生成 | 想"做个 XX 应用/Agent"，但不想多轮沟通 |
| [chinese-parents-skill](skills/chinese-parents-skill/) | 生活 | 通用 + 模拟/诊断 | 想理解家长、分析家长类型、不知道怎么开口 |
| [cnblogs-skill](skills/cnblogs-skill/) | 写作 | 博客园 cnblogs.com + API/浏览器 | 要发博文、管理博客、社区互动 |
| [zhihu-skill](skills/zhihu-skill/) | 写作 | 知乎 zhihu.com + Playwright | 要发/改/删知乎文章、清草稿、修乱码 |

## 怎么用（30 秒上手）

1. 从 **Releases** 下载对应技能的 zip（或直接使用 `skills/` 下的源码目录）
2. 解压，得到一个以技能名命名的文件夹（内含 `SKILL.md`）
3. 把整个文件夹**拖进** AI 工具的 skills 目录：
   - Claude Code：`~/.claude/skills/`（全局）或项目下 `.claude/skills/`（仅该项目）
   - 其他支持 skills 的工具：放入其对应 skills 目录
4. 新开会话即可触发，无需任何配置

> 也可以一键安装全部技能（见下方"一键安装"）。

## 一键安装

把全部技能解压到 `~/.claude/skills/`：

```bash
# 1. 先生成压缩包（若 dist/ 为空）
bash build.sh

# 2. Linux / macOS
bash install.sh

# Windows (PowerShell)
.\install.ps1
```

指定安装目录：

```bash
bash install.sh /path/to/skills-dir
```

## 打包发布

源码在 `skills/`，压缩包通过 GitHub Releases 发布（不进仓库，`dist/` 已被 .gitignore 忽略）。

```bash
# 生成 dist/*.zip
bash build.sh

# 发布流程
git tag v1.0.0
git push origin v1.0.0
# 在 GitHub Releases 页面创建 release，上传 dist/*.zip
```

## 技能清单

完整元数据见 [manifest.json](manifest.json)（名称 / 类别 / 触发词 / 大小）。

| 技能 | 大小 | 来源 |
|------|------|------|
| agent-builder-skill | 735 KB | [weed33834/agent-builder-skill](https://github.com/weed33834/agent-builder-skill) |
| chinese-parents-skill | 255 KB | [weed33834/chinese-parents-skill](https://github.com/weed33834/chinese-parents-skill) |
| cnblogs-skill | 29 KB | [weed33834/cnblogs-skill](https://github.com/weed33834/cnblogs-skill) |
| zhihu-skill | 8 KB | [weed33834/zhihu-skill](https://github.com/weed33834/zhihu-skill) |

## 说明

- 仅收录本人自建仓库的 skill（不含 fork）。
- 打包时已剔除 `.github`、`.gitignore`、`docker-compose.yml` 等非技能核心文件，保留 `SKILL.md`、`references/`、`scripts/`、`templates/` 等运行所需内容。
- 各技能依赖（如 playwright、登录态）以各自 `SKILL.md` 内说明为准。
*（内容由AI生成，仅供参考）*

## 许可证

[Apache License 2.0](LICENSE) © 2026 weed33834
