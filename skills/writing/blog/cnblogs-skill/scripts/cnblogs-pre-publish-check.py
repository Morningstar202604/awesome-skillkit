#!/usr/bin/env python3
"""
博客园文章发布前格式检查脚本
确保文章符合排版规范，防止格式问题再次发生

使用方法：
  python3 cnblogs-pre-publish-check.py <markdown_file>
  python3 cnblogs-pre-publish-check.py <markdown_file> --title "文章标题"

检查项：
  1. 不能使用 h1（# 标题），必须用 h2（## 标题）或更低层级
  2. 标题不能包含 HTML 实体（如 &quot; &amp; 等）
  3. 代码块反引号必须成对且为三个（```），不能是两个（``）
  4. 签名区不能使用 Markdown 格式（应使用 HTML 标签）
  5. 不应过度使用 <br> 标签（应用空行分段）
  6. blockquote 引用块每篇不超过 5 个
  7. 文末签名区应使用 HTML 标签，不使用 Markdown 语法
  8. 标题层级不能跳跃（如 h2 直接到 h4）
"""

import sys
import re
import argparse
from pathlib import Path


def check_h1(content: str) -> list:
    """检查是否有 h1 标题（# 开头）"""
    issues = []
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        # 匹配行首 # 后跟空格，但不匹配 ## 或 ###
        if re.match(r'^# [^#]', line):
            issues.append(f"  行 {i}: 发现 h1 标题 -> '{line.strip()[:60]}'")
            issues.append(f"         修复方法: 将 '# ' 改为 '## '")
    return issues


def check_title_entities(title: str) -> list:
    """检查标题是否包含未解码的 HTML 实体"""
    issues = []
    entities = re.findall(r'&[#0-9a-zA-Z]+;', title)
    if entities:
        issues.append(f"  标题包含 HTML 实体: {entities}")
        issues.append(f"  修复方法: 将 HTML 实体替换为实际字符")
    return issues


def check_backticks(content: str) -> list:
    """检查代码块反引号是否正确"""
    issues = []
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        # 检查行首两个反引号后跟非反引号（应为三个）
        if re.match(r'^``[^`]', stripped) and not re.match(r'^```', stripped):
            issues.append(f"  行 {i}: 代码块标记反引号不足 -> '{stripped[:60]}'")
            issues.append(f"         修复方法: 补全为三个反引号 '```'")

    # 检查反引号是否成对
    code_blocks = re.findall(r'^```', content, re.MULTILINE)
    if len(code_blocks) % 2 != 0:
        issues.append(f"  代码块反引号不成对: 共 {len(code_blocks)} 个标记（应为偶数）")
    
    return issues


def check_br_tags(content: str) -> list:
    """检查是否过度使用 <br> 标签"""
    issues = []
    br_count = len(re.findall(r'<br\s*/?>', content, re.IGNORECASE))
    if br_count > 5:
        issues.append(f"  <br> 标签过多: {br_count} 个（建议不超过 5 个）")
        issues.append(f"  修复方法: 用空行代替 <br> 进行段落分隔")
    return issues


def check_blockquotes(content: str) -> list:
    """检查引用块数量"""
    issues = []
    lines = content.split('\n')
    bq_groups = 0
    in_bq = False
    for line in lines:
        if line.startswith('>'):
            if not in_bq:
                bq_groups += 1
                in_bq = True
        else:
            in_bq = False
    if bq_groups > 5:
        issues.append(f"  引用块过多: {bq_groups} 组（建议不超过 5 组）")
        issues.append(f"  修复方法: 精简引用，只保留最关键的内容")
    return issues


def check_signature(content: str) -> list:
    """检查文末签名区是否使用了 Markdown 而非 HTML"""
    issues = []
    lines = content.split('\n')
    sig_start = -1
    for i in range(len(lines) - 1, -1, -1):
        if '作者' in lines[i] or '签名' in lines[i] or '本文要点' in lines[i]:
            sig_start = i
            break
    
    if sig_start > 0:
        sig_content = '\n'.join(lines[sig_start:])
        if re.search(r'\*\*[^*]+\*\*', sig_content):
            issues.append(f"  文末签名区使用了 Markdown 粗体 (**text**)")
            issues.append(f"  修复方法: 改用 <strong>text</strong>")
        if re.search(r'\[([^\]]+)\]\(([^)]+)\)', sig_content):
            issues.append(f"  文末签名区使用了 Markdown 链接 [text](url)")
            issues.append(f"  修复方法: 改用 <a href=\"url\">text</a>")
    
    return issues


def check_heading_hierarchy(content: str) -> list:
    """检查标题层级是否合理"""
    issues = []
    lines = content.split('\n')
    prev_level = 0
    for i, line in enumerate(lines, 1):
        m = re.match(r'^(#{1,6}) ', line)
        if m:
            level = len(m.group(1))
            if prev_level > 0 and level > prev_level + 1:
                issues.append(f"  行 {i}: 标题层级跳跃 h{prev_level} -> h{level}")
                issues.append(f"         '{line.strip()[:60]}'")
            prev_level = level
    return issues


def run_checks(filepath: str, title: str = "") -> bool:
    """运行所有检查，返回是否通过"""
    path = Path(filepath)
    if not path.exists():
        print(f"错误: 文件不存在 - {filepath}")
        return False
    
    content = path.read_text(encoding='utf-8-sig')  # utf-8-sig 兼容带 BOM 的文件（Windows 常见）
    
    all_issues = []
    
    # 1. H1 检查
    issues = check_h1(content)
    if issues:
        all_issues.append(("H1 标题检查", issues))
    
    # 2. 标题实体检查
    if title:
        issues = check_title_entities(title)
        if issues:
            all_issues.append(("标题 HTML 实体检查", issues))
    
    # 3. 反引号检查
    issues = check_backticks(content)
    if issues:
        all_issues.append(("代码块反引号检查", issues))
    
    # 4. <br> 标签检查
    issues = check_br_tags(content)
    if issues:
        all_issues.append(("<br> 标签检查", issues))
    
    # 5. 引用块检查
    issues = check_blockquotes(content)
    if issues:
        all_issues.append(("引用块数量检查", issues))
    
    # 6. 签名区检查
    issues = check_signature(content)
    if issues:
        all_issues.append(("签名区格式检查", issues))
    
    # 7. 标题层级检查
    issues = check_heading_hierarchy(content)
    if issues:
        all_issues.append(("标题层级检查", issues))
    
    # 输出结果
    print("=" * 60)
    print("博客园文章发布前格式检查")
    print("=" * 60)
    
    if not all_issues:
        print("\n所有检查通过！文章格式符合规范。")
        return True
    else:
        print(f"\n发现 {len(all_issues)} 类问题：\n")
        for check_name, issues in all_issues:
            print(f"【{check_name}】")
            for issue in issues:
                print(issue)
            print()
        
        print("=" * 60)
        print(f"共 {len(all_issues)} 类问题，请修复后再发布。")
        return False


def main():
    parser = argparse.ArgumentParser(description='博客园文章发布前格式检查')
    parser.add_argument('filepath', help='Markdown 文件路径')
    parser.add_argument('--title', default='', help='文章标题（可选）')
    args = parser.parse_args()
    
    passed = run_checks(args.filepath, args.title)
    sys.exit(0 if passed else 1)


if __name__ == '__main__':
    main()
