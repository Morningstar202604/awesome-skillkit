# Sources & Methodology

- 技能：`chart-recommender`（awesome-skillkit 原创编写，Apache-2.0）。
- 定位：场景包 `dataviz` 的选择侧技能，纯提示型、无脚本。
  与 `dashboard-designer`（生成侧）的分工是：本技能回答「画什么」，后者负责「画出来」。

## Methodology borrowed (ideas and taxonomy only; no text or code copied)

| Source | License | Methodology points borrowed |
|---|---|---|
| Jacques Bertin《Semiology of Graphics》的视觉变量理论（公开转述） | 见原书 | 「位置/长度/角度/面积/明度/色相」作为编码通道，及其可读精度差异 |
| William Cleveland & Robert McGill 关于图形感知精度的公开研究 | 见论文 | 「人对位置与长度的判断精度高于角度与面积」这一实证结论，是饼图与气泡图警告的依据 |
| Leland Wilkinson《The Grammar of Graphics》公开概念 | 见原书 | 图形 = 数据 + 映射 + 标度 + 几何对象；「先定维度与度量，再选几何」的次序 |
| 数据可视化社区广泛引用的图表选择指南与反模式清单 | 见各自原文 | 「避免 3D、避免彩虹配色、双 Y 轴慎用、柱状图基线必须为 0」等通行共识 |
| 顺序/发散色板设计公开规范（如 ColorBrewer 的分类体系） | Apache-2.0 | 定性 / 顺序 / 发散三类色板的划分与各自适用场景 |

上述来源全部作为**方法论骨架**被再表述。`references/chart-selection.md` 中的全部表格、
图型适用条件与反例、12 条错误清单、七项输出规格，以及本 SKILL.md 的工作流，
均为本仓库原创撰写与整理，未翻译、未改写、未摘录任何上游文档的段落或示例。
色值取自公开的定性色板惯例并单独验证过对比度。

## Key design decisions (why this way)

1. **强制先问意图**：数据形态相同的两份数据，因意图不同应选不同图。
   不追问意图就给图型，是把「我觉得好看」冒充「适合你的场景」。
2. **每个方案必须写「代价」**：图表选择的本质是权衡而非找唯一正确答案。
   只列优点的方案对比没有决策价值。
3. **词库独立成文件且带目录**：超过 100 行必须给目录（本仓规范），
   且 SKILL.md 正文保持精简，只在步骤里指明「何时读它」。
4. **反例与禁忌和推荐同等重要**：多数选图错误不是选不出好图，
   而是选了明显不该用的图；因此映射表里「禁忌」列与「推荐」列并置。
5. **视觉编码优先级放在错误清单之前**：先建立「精度有高低」的判断框架，
   后面那些反模式（3D 饼图、面积编码）才有统一的解释，而不是一串需要背诵的规则。
6. **纯提示型不配脚本**：本技能产出的是判断与规格，不是文件。
   加脚本反而会把「权衡」伪装成「计算结果」。

## Limitations and boundaries

- **不给最终裁决**：给方案与代价，由用户结合业务语境决定。
- **不画图、不校验真实数据**：输入是用户描述的形态，若描述有误则建议随之失效；
  需要基于真实数据画像时，先跑 `dashboard-designer inspect`。
- **不覆盖极冷门图型**（如和弦图、地平线图）：可用视觉编码优先级自行推理，
  但不在词库范围内。
- **配色仅给通用建议**：正式交付需按品牌规范与无障碍要求复核对比度。

## License

This skill and its reference files are distributed under Apache-2.0; the upstream documents listed carry their own license terms, which do not apply to this file.
