# 方法论出处与致谢 / Sources & Methodology

> 本技能的分镜方法论不是凭空发明的。以下开源项目提供了经过实战验证的结构与纪律，
> 我们提炼其**方法论骨架**（节拍表先行、连续性约束表、逐场景 prompt 成对产出、
> 输出契约化），并结合本仓 SKILL-STANDARD-v2 的「机器优先十诫」重写为中文工作流。
> 未复制任何原文内容；如需原版，请访问下列仓库。

## 主要来源

| 来源 | 许可证 | 借鉴的方法论要点 |
|------|--------|------------------|
| [agentara/skills — video-storyboard](https://github.com/agentara/skills) | 见其仓库 | 逐场景双产物（图像板 + 视频 prompt 脚本）成对产出；连续性约束表（角色/服装/道具/场景/画幅）；两位数场景编号与输出路径契约；**分镜图必须由图像模型生成、禁止代码/SVG 凑数**的硬规则 |
| [nexu-io/open-design — create-video-storyboard](https://github.com/nexu-io/open-design) | Apache-2.0 | 五步工作流（澄清 → 节拍表 → prompt 包 → 镜头清单 → 节奏审查）；先出 beat sheet 再出分镜的次序纪律 |
| [smixs/visual-skills](https://github.com/smixs/visual-skills) | CC BY 4.0 | 「分镜是设计与生成的合同」定位；关键帧先行、运动后置的两段式思路 |

## CC BY 4.0 署名声明

smixs/visual-skills 的方法论在其许可下要求署名。本技能对其仅为方法论结构层面的
借鉴与再表述（未复制文本），仍在此明确致谢：

> Methodology inspired by Serge Shima — github.com/smixs/visual-skills (CC BY 4.0)

## 与本仓标准的合并

上述方法论进入本仓时做了三类改造：

1. **十诫化**：每个步骤补齐「预期结果 + 失败分支」（SKILL-STANDARD-v2 §3 诫 2）；
2. **确定性化**：场景文件给出固定 9 字段结构公式，而非自由格式；
3. **可验证化**：新增 `scene_lint.py` 机器校验（命名连续性 + 必需字段），
   把「人工审查」降级为「脚本把门 + 人工只看创意」。
