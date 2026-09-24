# Methodology sources and acknowledgements

## Main sources

| Source | License | Methodology points borrowed |
|------|--------|------------------|
| [smixs/visual-skills](https://github.com/smixs/visual-skills) | CC BY 4.0 | 跨模型 prompt 工程（write / audit 双模式：「Write a Seedance prompt」「Audit this prompt: what's broken, how to fix?」）；关键帧→运动两段式；转场词汇表；参考角色纪律与优先级声明；戏剧方法论蒸馏（Walter Murch 等） |
| 各模型官方文档 | 各自条款 | 六槽位结构的通用性来自官方 prompt guide 的公共部分（主体/动作/镜头/风格/时长在多数官方示例中均出现） |

## CC BY 4.0 署名声明

本技能对 smixs/visual-skills 为方法论结构层面的借鉴与再表述（未复制其文本）。
按其许可证要求明确署名：

> Methodology inspired by Serge Shima — github.com/smixs/visual-skills (CC BY 4.0)

## Merged to this repo's standards

1. **槽位化**：把「写好 prompt 的经验」固化为六槽位填空 + 词典查表（诫 2/诫 3）；
2. **可验证化**：`prompt_audit.py` 把「审计」从口험变成机器可重复的结构检查；
3. **反时效化**：模型方言单独成文件并强制 VERIFY BEFORE USE 核实步骤
   （诫 7/诫 8），通用六槽位与方言解耦——方言过期不影响核心方法论。
