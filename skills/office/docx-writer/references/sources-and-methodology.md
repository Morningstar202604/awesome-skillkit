# Sources & Methodology（docx-writer）

## 方法论来源

本技能的设计思想蒸馏自 Anthropic 官方公开技能仓库中 docx 与 pdf 两个技能的
**公开描述与结构思路**（按任务选路径、生成后必须读回验证、把易错点写成清单），
未复制其任何文本段落、脚本代码或文档内容；本目录下所有文字与代码均为原创。
上游内容为专有许可，禁止再分发。

- Anthropic skills 仓库（仅作思想参考）：
  https://github.com/anthropics/skills/tree/main/skills/docx
  https://github.com/anthropics/skills/tree/main/skills/pdf

## 技术依据

- python-docx 官方文档（Document/Paragraph/Table API）：
  https://python-docx.readthedocs.io/
- OOXML / ECMA-376 标准中 `w:rFonts/@w:eastAsia` 属性：中文字形由 eastAsia
  字体渲染，仅设 latin 字体会导致中文回退默认字体——这是"中文乱码/方块"
  问题的标准层原因，`scripts/docx_ops.py` 的 styles 子命令据此实现。
