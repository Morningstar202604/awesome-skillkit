---
name: "sample-text-processor"
description: "Reference BASIC-tier skill: text analysis and transformation with word/character statistics, case transforms, batch processing, and dual JSON/human output."
---

# Sample Text Processor

---

- **Name**: sample-text-processor
- **Tier**: BASIC
- **Category**: text processing
- **Dependencies**: none (Python standard library only)
- **Author**: Claude Skills Engineering Team
- **Version**: 1.0.0
- **Updated**: 2026-02-16

---

## Introduction

Sample Text Processor is a simple demonstration skill that shows the basic structure and functionality a skill should have in the claude-skills ecosystem. It provides basic text-processing capabilities, including word-count statistics, character analysis, and basic text transforms.

This skill is a reference implementation of the BASIC-tier requirements and can be used as a template for creating new skills. It demonstrates the file structure, documentation standards, and implementation patterns that follow ecosystem best practices.

The skill processes text files and outputs statistics and transform results in both human-readable and JSON formats, reflecting the claude-skills repo's requirement that skills support dual output formats.

## Features

### Core functionality

- **Word-count analysis**: total words, unique words, and word frequency
- **Character statistics**: character count, line count, and special characters
- **Text transforms**: convert to uppercase, lowercase, or title case
- **File processing**: process a single text file or batch-process a directory
- **Dual output formats**: supports both JSON and human-readable output

### Technical features

- A command-line interface with full argument parsing
- Error handling covering common file and processing problems
- Progress reporting for batch operations
- Configurable output format and verbosity
- Standard-library only, cross-platform

## Usage

### Basic text analysis
```bash
python text_processor.py analyze assets/sample_text.txt
python text_processor.py --output results.json analyze assets/sample_text.txt
```

### Text transforms
```bash
python text_processor.py transform assets/sample_text.txt --mode upper
python text_processor.py --output transformed.txt transform assets/sample_text.txt --mode title
```

### Batch processing
```bash
python text_processor.py --output results/ batch assets/
python text_processor.py --format json --output batch_results.json batch assets/
```

## Examples

### Example 1: basic word count
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

### Example 2: JSON output
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

### Example 3: text transform
```bash
$ python text_processor.py transform sample.txt --mode title
Original: "hello world from the text processor"
Transformed: "Hello World From The Text Processor"
```

## Installation

This skill requires only Python 3.7+ and the standard library, with no external dependencies.

1. Clone or download the skill directory
2. Enter the scripts directory
3. Run the text processor directly with Python

```bash
cd scripts/
python text_processor.py --help
```

## Configuration

The text processor supports several configuration options via command-line arguments:

- `--format`: output format (json, text)
- `--verbose`: enable verbose output and progress reporting
- `--output`: specify an output file or directory
- `--encoding`: specify the text-file encoding (default utf-8)

## Architecture

The skill uses a simple modular architecture:

- **TextProcessor class**: core processing logic and statistical computation
- **OutputFormatter class**: responsible for generating the dual output formats
- **FileManager class**: manages file I/O and batch processing
- **CLI interface**: command-line argument parsing and user interaction

## Error Handling

The skill covers the following error scenarios:

- File not found or permission errors
- Invalid encoding or corrupted text files
- Memory limits from very large files
- Output-directory creation and write-permission issues
- Invalid command-line arguments

## Performance Considerations

- Controls memory usage for large text files through streaming
- Uses dictionary lookups to optimize word-count statistics
- Reports progress when batch-processing large datasets
- Configurable encoding detection supports international text

## Contributing

This skill is a reference implementation; contributions aimed at demonstrating best practices are welcome:

1. Follow PEP 8 style
2. Write complete docstrings
3. Add test cases with sample data
4. Update documentation for new features
5. Keep backward compatibility

## Limitations

As a BASIC-tier skill, the following advanced capabilities are intentionally omitted:

- Complex text analysis (sentiment analysis, language detection)
- Advanced file-format support (PDF, Word documents)
- Database integration or external API calls
- Parallel processing of very large datasets

While keeping things simple and focused on core functionality, this skill demonstrates the basic structure and quality standards required for a BASIC-tier skill in the claude-skills ecosystem.
