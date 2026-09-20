# 占位符填写规则

## 命名约定
- 占位符：`{{KEY}}`，KEY 为 `[a-zA-Z0-9_]+`，建议全大写下划线（`EMP_NAME`、`AMOUNT`）。
- JSON key **精确匹配**（区分大小写）；缺失 key → 原样保留 `{{KEY}}` 并列入 `[NOTICE]`。

## 降级与边界
- 未装 `python-docx`：脚本只打印"数据 keys 本可填入"，rc=3，不写文件。
- 批注：本技能用"文末【批注·作者】斜体段"近似；真 Word comment（w:comment part）需改
  document.xml + comments.xml + 关系表，超出脚本范围，按需手工 OXML。
- 表格：`doc.tables[].rows[].cells[].paragraphs` 全部覆盖；合并单元格的文字只改首格。

## 校验
- 填前后对源模板 `md5sum` 应一致（源从不写）。
- 输出可被 Word/WPS 打开；段落样式保留（脚本清空 runs 写回首 run，不重建段落样式）。
