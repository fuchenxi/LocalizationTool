#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多语言文件解析器
负责 .strings 文件的解析、写入和去重
"""

import os
import re
from collections import OrderedDict
from typing import Optional


class LocalizationParser:
    """处理 .strings 文件的解析和写入"""
    
    @staticmethod
    def parse_strings_file(file_path: str) -> OrderedDict:
        """解析 .strings 文件，返回有序字典保持原始顺序
        
        支持：
        - 单行格式: "key" = "value";
        - 多行格式: "key" = "line1\nline2\nline3";
        - 转义字符: \", \\, \n, \t
        - 注释: // 和 /* */
        """
        result = OrderedDict()
        
        if not os.path.exists(file_path):
            return result
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 移除多行注释 /* ... */
            content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
            
            # 移除单行注释 //
            lines = content.split('\n')
            cleaned_lines = []
            for line in lines:
                # 移除 // 注释（但保留字符串内的 //）
                if '//' in line:
                    # 简单处理：如果 // 在字符串外，则移除
                    in_string = False
                    escape_next = False
                    for i, char in enumerate(line):
                        if escape_next:
                            escape_next = False
                            continue
                        if char == '\\':
                            escape_next = True
                            continue
                        if char == '"':
                            in_string = not in_string
                        if not in_string and i < len(line) - 1 and line[i:i+2] == '//':
                            line = line[:i]
                            break
                cleaned_lines.append(line)
            
            content = '\n'.join(cleaned_lines)
            
            # 使用正则匹配所有 "key" = "value"; 对
            # (?:[^"\\]|\\.)* 匹配：非引号非反斜杠的字符，或反斜杠后跟任意字符（转义）
            # re.DOTALL 让 . 匹配换行符
            pattern = r'"((?:[^"\\]|\\.)*)"\s*=\s*"((?:[^"\\]|\\.)*)"\s*;'
            matches = re.findall(pattern, content, re.DOTALL)
            
            for key, value in matches:
                # 解码转义字符（注意顺序）
                key = key.replace('\\\\', '\x00').replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t').replace('\x00', '\\')
                value = value.replace('\\\\', '\x00').replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t').replace('\x00', '\\')
                result[key] = value
                
        except Exception as e:
            print(f"解析文件出错 {file_path}: {e}")
        
        return result
    
    @staticmethod
    def write_strings_file(file_path: str, data: OrderedDict, version: Optional[str] = None):
        """写入 .strings 文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                for key, value in data.items():
                    # 转义特殊字符
                    escaped_key = key.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\t', '\\t')
                    escaped_value = value.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\t', '\\t')
                    f.write(f'"{escaped_key}" = "{escaped_value}";\n')
        except Exception as e:
            print(f"写入文件出错 {file_path}: {e}")
    
    @staticmethod
    def write_xml_file(file_path: str, data: OrderedDict):
        """写入 Android strings.xml 格式的文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write('<resources>\n')
                for key, value in data.items():
                    # 转义 XML 特殊字符
                    escaped_value = (value
                        .replace('&', '&amp;')
                        .replace('<', '&lt;')
                        .replace('>', '&gt;')
                        .replace('"', '&quot;')
                        .replace("'", '&apos;'))
                    f.write(f'    <string name="{key}">{escaped_value}</string>\n')
                f.write('</resources>\n')
        except Exception as e:
            print(f"写入 XML 文件出错 {file_path}: {e}")
    
    @staticmethod
    def append_strings_with_version(file_path: str, strings_file_path: str, version: str):
        """直接追加原始文件内容，用版本号注释包裹，保持原始格式和转义"""
        try:
            # 读取原始文件内容
            with open(strings_file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # 追加到目标文件
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(f'\n\n//<!-- ========== {version} 新增 ========== -->\n')
                f.write(content)
                f.write(f'\n//<!-- ========== {version} 新增 ========== -->\n')
        except Exception as e:
            print(f"追加文件出错 {file_path}: {e}")
    
    @staticmethod
    def remove_duplicates(file_path: str) -> int:
        """删除重复的 key，只保留最后一个，返回删除的数量
        
        保留：
        - 所有注释（// 和 /* */）
        - 所有空行
        - 文件原有结构
        
        删除：
        - 只删除重复出现的 key-value 行
        """
        if not os.path.exists(file_path):
            return 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 第一遍：找出所有 key 的所有出现位置
            pattern = r'"([^"]*)"\s*=\s*"([^"]*)"\s*;'
            key_positions = {}  # {key: [line_index1, line_index2, ...]}
            
            for i, line in enumerate(lines):
                match = re.match(pattern, line.strip())
                if match:
                    key = match.group(1)
                    if key not in key_positions:
                        key_positions[key] = []
                    key_positions[key].append(i)
            
            # 第二遍：标记要删除的行（保留每个 key 的最后一次出现）
            lines_to_remove = set()
            duplicates_count = 0
            
            for key, positions in key_positions.items():
                if len(positions) > 1:
                    # 有重复，删除前面的，保留最后一个
                    for pos in positions[:-1]:
                        lines_to_remove.add(pos)
                        duplicates_count += 1
            
            # 第三遍：写入文件，跳过要删除的行
            with open(file_path, 'w', encoding='utf-8') as f:
                for i, line in enumerate(lines):
                    if i not in lines_to_remove:
                        f.write(line)
            
            return duplicates_count
            
        except Exception as e:
            print(f"删除重复项出错 {file_path}: {e}")
            return 0
    
    @staticmethod
    def count_duplicates(file_path: str) -> int:
        """计算文件中重复项的数量（不删除）"""
        duplicates_info = LocalizationParser.find_duplicates(file_path)
        return sum(len(items) - 1 for items in duplicates_info.values())
    
    @staticmethod
    def find_duplicates(file_path: str) -> dict:
        """查找文件中的重复项，返回 {key: [(value1, line1), (value2, line2), ...]}"""
        if not os.path.exists(file_path):
            return {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            pattern = r'"([^"]*)"\s*=\s*"([^"]*)"\s*;'
            
            # 记录每个 key 的所有出现
            key_occurrences = {}
            for line_num, line in enumerate(lines, 1):
                match = re.match(pattern, line.strip())
                if match:
                    key, value = match.groups()
                    if key not in key_occurrences:
                        key_occurrences[key] = []
                    key_occurrences[key].append((value, line_num))
            
            # 只返回出现多次的 key
            duplicates = {k: v for k, v in key_occurrences.items() if len(v) > 1}
            return duplicates
            
        except Exception as e:
            print(f"查找重复项出错 {file_path}: {e}")
            return {}

