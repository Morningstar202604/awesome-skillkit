# 版本管理与发布制度

> 生效日期：2026-08-25（v1.6.3 起）。本文件是版本管理的唯一准绳；与 README/口头约定冲突时以本文为准。

## 1. 版本号语义（SemVer）

格式 `MAJOR.MINOR.PATCH`，对"技能消费者"承诺兼容性：

| 位 | 触发条件 | 示例 |
|---|---|---|
| **MAJOR**（大版本） | 破坏性变更：删除技能或整个包；SKILL.md 结构要求不兼容升级；分发/安装方式变更导致老用户必须迁移 | 删除 basics 包；frontmatter 必填字段新增导致旧技能不合规 |
| **MINOR**（小版本） | 向后兼容的新增：新技能、新场景包；既有技能获得实质性新能力；新门禁/新工具 | 新增品类 B 媒体生成包；validator 上线新检查 |
| **PATCH**（修订版） | 缺陷修复与维护：断链修复、元数据修正、文档勘误、构建/安装器修复。**不得改变任何技能的对外行为契约** | 修复 install.ps1；补 sha256 |

规则：
- 版本号唯一权威来源：`manifest.json` 的 `version` 字段；README/文档中的版本一律引用它，禁止另写。
- 每个发布版本必须有：CHANGELOG 小节 + annotated git tag（`vx.y.z`）。
- 不确定归哪级时取更高级别（保守原则）。

## 2. 发布流程（每次发版逐步执行）

```bash
python tools/validate_skills.py     # 门禁：0 ERROR 才能继续
python -m pytest skills -q          # 全部单测通过
python build.py                     # 重建 dist，回填 size_kb/sha256 到 manifest
python tools/release.py X.Y.Z --commit   # 校验 CHANGELOG 小节存在→bump→commit→打 tag
git push origin main --follow-tags && powershell -File sync-mirrors.ps1   # 双镜像同步
```

- CHANGELOG 遵循 Keep a Changelog：开发中的改动先记在 `## [Unreleased]`，发版时改为正式小节。
- tag 一律 annotated；禁止移动已有 tag。

## 3. 历史处置（一次性决定，不再翻案）

政策生效前的状态：版本号只存在于 manifest 与 CHANGELOG，15 个提交仅 2 个 tag（v0.1.0、v1.6.2），中间 6 个版本无法可靠映射到具体 commit。

处置决定：
1. **不回溯伪造历史 tag**——映射不可靠的 tag 比没有 tag 更糟；
2. v0.1.0、v1.6.2 两个现存 tag 保留不动；
3. CHANGELOG 是政策前版本的唯一权威记录；
4. **自 v1.6.3 起 tag 全覆盖**，此后任何版本不得缺 tag。

## 4. 技能生命周期

| 状态 | 标记 | 说明 |
|---|---|---|
| active | — | 正常维护 |
| deprecated | `metadata.deprecated: "true"` + `metadata.replacement: "<skill-name>"` | 仍可用但不再修 bug；README 标注 |
| removed | 仅 MAJOR 可删 | 删除前必须经历 deprecated 至少 2 个 MINOR 周期 |

平台 API 失效导致的技能：优先修复端点常量（PATCH）；无法修复时转 deprecated 并在 description 开头加 `[DEPRECATED]`。

## 5. 分发产物完整性

- `dist/*.zip` 为构建产物不入库；其指纹（size_kb + sha256）由 `build.py` 构建后自动写回 `manifest.json` 对应 pack 条目。
- 用户侧校验：下载 zip 后比对 Release 页公布 的 sha256。
- 禁止手工编辑 manifest 中由构建生成的 `size_kb`/`sha256` 字段。
