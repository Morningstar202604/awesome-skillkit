# Sources & Methodology（pdf-pipeline）

## 方法论来源

本技能的设计思想蒸馏自 Anthropic 官方公开技能仓库中 pdf 技能的**公开
描述所体现的任务划分思路**（合并/拆分/提取/元数据/旋转的子任务切分、
"扫描件走 OCR"的路线判断），未复制其任何文本段落、脚本代码或文档内容；
本目录下所有文字与代码均为原创。上游内容为专有许可，禁止再分发。

- Anthropic skills 仓库（仅作思想参考）：
  https://github.com/anthropics/skills/tree/main/skills/pdf
  https://github.com/anthropics/skills/tree/main/skills/docx

## 技术依据

- pypdf 官方文档（PdfReader / PdfWriter / append / add_metadata /
  get_fields / rotate）：
  https://pypdf.readthedocs.io/
- PDF 规范（ISO 32000）中的 AcroForm 字段字典与 /Rotate 页属性：
  表单字段探测（/FT 类型）与旋转标志读回均直接对应标准结构。
- 无文本层判定：extract_text() 对图像页返回空字符串，据此提示 OCR
  路线（ocrmypdf / tesseract 为常见外部工具，本技能不捆绑）。
