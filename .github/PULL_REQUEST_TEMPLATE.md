<!-- 标题格式：<type>(<scope>): <subject>，如 feat(video): add timeline view to video-editor -->

## What & why / 改了什么，为什么改

<!-- 一句话说清动机。修 bug 请附触发条件与现象；新技能请说明归属包与触发词 -->

## Changes / 变更清单

-
-

## Checks / 自查（全部通过才可合并）

- [ ] `python tools/validate_skills.py` → **0 错误 / 0 警告**（门禁硬要求）
- [ ] `python -m pytest skills -q` → 全部通过
- [ ] `python build.py` → 构建成功，连续两次构建 sha256 一致
- [ ] 新增/修改的 SKILL.md：`name` 与目录名一致，description ≥ 400 字符且含中英文触发短语
- [ ] 未引入硬编码凭据（API key / token / cookie 仅走环境变量或 gitignored 本地文件）
- [ ] 版本号相关改动已同步 `manifest.json` + `CHANGELOG.md`（若影响对外行为）

## Screenshots / 截图（如涉及 UI 或文档渲染）
