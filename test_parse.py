#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试解析 .strings 文件"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import LocalizationParser

# 请用户提供实际的 .strings 文件路径
print("请输入要测试的 .strings 文件路径：")
file_path = input().strip()

if not os.path.exists(file_path):
    print(f"文件不存在: {file_path}")
    sys.exit(1)

print(f"\n开始解析: {file_path}")
print("=" * 60)

# 统计原始文件的信息
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

total_lines = len(lines)
non_empty_lines = sum(1 for line in lines if line.strip())
comment_lines = sum(1 for line in lines if line.strip().startswith('//') or line.strip().startswith('/*'))

print(f"原始文件统计：")
print(f"  总行数: {total_lines}")
print(f"  非空行数: {non_empty_lines}")
print(f"  注释行数: {comment_lines}")

# 手动统计包含 = 的行
equals_lines = sum(1 for line in lines if '=' in line and not line.strip().startswith('//'))
print(f"  包含 '=' 的行数: {equals_lines}")

# 使用解析器解析
result = LocalizationParser.parse_strings_file(file_path)
print(f"\n解析结果：")
print(f"  解析到的 key-value 对数: {len(result)}")

# 如果数量不一致，显示一些未解析的行
if len(result) < equals_lines:
    print(f"\n⚠️ 警告: 有 {equals_lines - len(result)} 行包含 '=' 但未被解析")
    print("\n前10个未被解析的行：")
    
    parsed_count = 0
    shown_count = 0
    for i, line in enumerate(lines, 1):
        if '=' not in line or line.strip().startswith('//'):
            continue
        
        # 检查这行是否被解析
        parts = line.split('=', 1)
        if len(parts) == 2:
            key_part = parts[0].strip()
            if key_part.startswith('"') and key_part.endswith('"'):
                key = key_part[1:-1]
                # 解码转义字符
                key = key.replace('\\\\', '\x00').replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t').replace('\x00', '\\')
                
                if key in result:
                    parsed_count += 1
                    continue
        
        # 未被解析
        if shown_count < 10:
            print(f"  Line {i}: {line.strip()[:100]}")
            shown_count += 1

print("\n" + "=" * 60)
print(f"✓ 测试完成")

