#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""诊断导出问题 - 对比原始文件和导出文件"""

import sys
import os
import re

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import LocalizationParser

def count_keyvalues_raw(file_path):
    """直接用正则统计原始文件中的 key-value 对数量"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 移除注释
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
    
    # 统计包含 = 和 ; 的行（粗略估计）
    pattern = r'"[^"]*"\s*=\s*"[^"]*"\s*;'
    simple_matches = re.findall(pattern, content)
    
    # 统计支持转义的完整模式
    pattern_full = r'"((?:[^"\\]|\\.)*)"\s*=\s*"((?:[^"\\]|\\.)*)"\s*;'
    full_matches = re.findall(pattern_full, content, re.DOTALL)
    
    return len(simple_matches), len(full_matches)

print("=" * 70)
print("诊断导出问题")
print("=" * 70)

# 1. 让用户输入原始项目路径
print("\n请输入原始项目中的某个 Localizable.strings 文件路径：")
print("(例如: /path/to/project/en.lproj/Localizable.strings)")
original_file = input().strip()

if not os.path.exists(original_file):
    print(f"❌ 文件不存在: {original_file}")
    sys.exit(1)

# 2. 分析原始文件
print(f"\n📄 分析原始文件: {os.path.basename(original_file)}")
print("-" * 70)

with open(original_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

total_lines = len(lines)
non_empty = sum(1 for line in lines if line.strip())

print(f"总行数: {total_lines}")
print(f"非空行: {non_empty}")

simple_count, full_count = count_keyvalues_raw(original_file)
print(f"简单模式匹配到: {simple_count} 个 key-value 对")
print(f"完整模式匹配到: {full_count} 个 key-value 对")

# 3. 使用解析器解析
parsed_data = LocalizationParser.parse_strings_file(original_file)
print(f"解析器解析到: {len(parsed_data)} 个 key-value 对")

# 4. 对比差异
print("\n" + "=" * 70)
if len(parsed_data) == full_count:
    print("✅ 解析正常！导出应该包含所有字段。")
elif len(parsed_data) < full_count:
    diff = full_count - len(parsed_data)
    print(f"⚠️  缺失 {diff} 个 key-value 对！")
    print("\n可能原因：")
    print("  1. 某些行格式不标准")
    print("  2. 存在特殊的转义序列")
    print("  3. 多行 value 处理有问题")
    
    # 显示一些样本
    print("\n显示前5个成功解析的 key：")
    for i, key in enumerate(list(parsed_data.keys())[:5]):
        print(f"  {i+1}. {key}")
else:
    print("⚠️  解析数量大于预期，可能有重复")

# 5. 检查导出文件
print("\n" + "=" * 70)
print("如果你已经导出，请输入导出的 .strings 文件路径")
print("(例如: ~/Desktop/LocalizationExport_xxx/Strings/en.strings)")
print("直接回车跳过: ")
exported_file = input().strip()

if exported_file and os.path.exists(exported_file):
    exported_data = LocalizationParser.parse_strings_file(exported_file)
    print(f"\n📤 导出文件包含: {len(exported_data)} 个 key-value 对")
    
    if len(exported_data) == len(parsed_data):
        print("✅ 导出数量匹配！")
    else:
        print(f"⚠️  导出数量不匹配！差异: {abs(len(exported_data) - len(parsed_data))}")

print("\n" + "=" * 70)
print("诊断完成")
print("=" * 70)

