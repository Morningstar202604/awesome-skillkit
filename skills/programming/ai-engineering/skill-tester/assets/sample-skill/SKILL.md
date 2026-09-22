---
name: "sample-text-processor"
description: "Reference BASIC-tier skill: text analysis and transformation with word/character statistics, case transforms, batch processing, and dual JSON/human output."
---

--
name: "sample-text-processor"
description: "Reference BASIC-tier skill: text analysis and transformation with word/character statistics, case transforms, batch processing, and dual JSON/human output."
---

# Sample Text Processor

---

- **名称**：sample-text-processor
- **层级**：BASIC
- **类别**：文本处理
- **依赖**：无（仅 Python 标准库）
- **作者**：Claude Skills Engineering Team
- **版本**：1.0.0
- **更新日期**：2026-02-16

---

## 简介

Sample Text Processor 是一个简单的示范技能，用于展示 claude-skills 生态中技能应具备的基本结构与功能。它提供基础文本处理能力，包括词数统计、字符分析和基础文本变换。

本技能是 BASIC 层级要求的参考实现，可作为创建新技能的模板。它演示了符合生态最佳实践的文件结构、文档标准和实现模式。

技能处理文本文件，以人读和 JSON 两种格式输出统计与变换结果，体现 claude-skills 仓库对技能双输出格式的要求。

## 功能特性

### 核心功能

- **词数分析**：统计总词数、去重词数与词频
- **字符统计**：分析字符数、行数与特殊字符
- **文本变换**：转换为大写、小写或标题式大小写
- **文件处理**：处理单个文本文件或批量处理目录
- **双输出格式**：同时支持 JSON 与人读格式

### 技术特性

- 带完整参数解析的命令行界面
- 覆盖常见文件与处理问题的错误处理
- 批量操作的进度上报
- 可配置的输出格式与详细程度
- 仅依赖标准库，跨平台可用

## 用法

### 基础文本分析
```bash
python text_processor.py analyze assets/sample_text.txt
python text_processor.py --output results.json analyze assets/sample_text.txt
```

### 文本转换
```bash
python text_processor.py transform assets/sample_text.txt --mode upper
python text_processor.py --output transformed.txt transform assets/sample_text.txt --mode title
```

### 批量处理
```bash
python text_processor.py --output results/ batch assets/
python text_processor.py --format json --output batch_results.json batch assets/
```

## 示例

### 示例 1：基础词数统计
```bash
$ python text_processor.py analyze assets/sample_text.txt
=== TEXT ANALYSIS RESULTS ===
File: sample.txt
Total words: 150
Unique words: 85
Total characters: 750
Lines: 12
Most frequent word: "the" (8 occurrences)
```

### 示例 2：JSON 输出
```bash
$ python text_processor.py analyze assets/sample_text.txt --format json
{
  "file": "sample.txt",
  "statistics": {
    "total_words": 150,
    "unique_words": 85,
    "total_characters": 750,
    "lines": 12,
    "most_frequent": {
      "word": "the",
      "count": 8
    }
  }
}
```

### 示例 3：文本转换
```bash
$ python text_processor.py transform sample.txt --mode title
Original: "hello world from the text processor"
Transformed: "Hello World From The Text Processor"
```

## 安装

本技能只需 Python 3.7 及以上版本与标准库，无任何外部依赖。

1. 克隆或下载技能目录
2. 进入 scripts 目录
3. 用 Python 直接运行文本处理器

```bash
cd scripts/
python text_processor.py --help
```

## 配置

文本处理器通过命令行参数支持多种配置项：

- `--format`：输出格式（json、text）
- `--verbose`：开启详细输出与进度上报
- `--output`：指定输出文件或目录
- `--encoding`：指定文本文件编码（默认 utf-8）

## 架构

技能采用简单的模块化架构：

- **TextProcessor 类**：核心处理逻辑与统计计算
- **OutputFormatter 类**：负责双输出格式生成
- **FileManager 类**：管理文件 I/O 与批量处理
- **CLI 界面**：命令行参数解析与用户交互

## 错误处理

技能覆盖以下错误场景：

- 文件不存在或权限错误
- 编码无效或文本文件损坏
- 超大文件带来的内存限制
- 输出目录创建与写权限问题
- 命令行参数无效

## 性能考量

- 通过流式处理控制大文本文件的内存占用
- 用字典查找优化词数统计
- 批量处理大数据集时上报进度
- 可配置编码检测，支持国际化文本

## 参与贡献

本技能是参考实现，欢迎以演示最佳实践为目的的贡献：

1. 遵循 PEP 8 编码规范
2. 编写完整的 docstring
3. 用示例数据补充测试用例
4. 为新功能更新文档
5. 保持向后兼容

## 局限

作为 BASIC 层级技能，以下高级能力被有意省略：

- 复杂文本分析（情感分析、语言检测）
- 高级文件格式支持（PDF、Word 文档）
- 数据库集成或外部 API 调用
- 超大数据集的并行处理

本技能在保持简单、聚焦核心功能的同时，展示了 claude-skills 生态中 BASIC 层级技能所需的基本结构与质量标准。
