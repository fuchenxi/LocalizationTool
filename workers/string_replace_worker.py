#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字符串扫描和替换工作线程
"""

import os
import re
from typing import List, Dict
from PyQt6.QtCore import QThread, pyqtSignal

from models import LocalizationParser, ProjectInfoExtractor


class ScanStringsWorker(QThread):
    """扫描硬编码字符串工作线程"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str, list, list)  # success, message, results, mismatched_keys
    
    def __init__(self, project_path: str, keys: List[str], scan_oc: bool, scan_swift: bool, case_sensitive: bool = False):
        super().__init__()
        self.project_path = project_path
        self.keys = keys
        self.scan_oc = scan_oc
        self.scan_swift = scan_swift
        self.case_sensitive = case_sensitive
    
    def run(self):
        try:
            # 1. 从多语言文件中建立 value -> key 的映射
            self.progress.emit("正在读取多语言文件...")
            value_to_key_map, mismatched_keys = self.build_value_key_map()
            
            if not value_to_key_map and not mismatched_keys:
                self.finished.emit(False, "未找到多语言文件或映射", [], [])
                return
            
            self.progress.emit(f"✓ 建立映射：{len(value_to_key_map)} 个值")
            if mismatched_keys:
                self.progress.emit(f"⚠ {len(mismatched_keys)} 个 Key 未找到对应的 Value")
            
            # 2. 扫描代码文件
            self.progress.emit("正在扫描代码文件...")
            results = []
            
            # 确定要扫描的文件类型
            extensions = []
            if self.scan_oc:
                extensions.extend(['.m', '.mm'])
            if self.scan_swift:
                extensions.append('.swift')
            
            if not extensions:
                self.finished.emit(False, "请至少选择一种文件类型", [])
                return
            
            # 扫描文件
            file_count = 0
            for root, dirs, files in os.walk(self.project_path):
                # 排除无关目录
                dirs[:] = [d for d in dirs if d not in ['Pods', 'build', 'Build', 'DerivedData', '.git', 'Carthage']]
                
                for file in files:
                    if any(file.endswith(ext) for ext in extensions):
                        file_path = os.path.join(root, file)
                        file_count += 1
                        
                        if file_count % 10 == 0:
                            self.progress.emit(f"已扫描 {file_count} 个文件...")
                        
                        # 扫描文件中的字符串
                        file_results = self.scan_file(file_path, value_to_key_map)
                        results.extend(file_results)
            
            self.progress.emit(f"✓ 共扫描 {file_count} 个文件")
            
            if results:
                self.finished.emit(True, f"发现 {len(results)} 处需要替换", results, mismatched_keys)
            else:
                self.finished.emit(True, "未发现需要替换的硬编码字符串", [], mismatched_keys)
            
        except Exception as e:
            self.finished.emit(False, f"扫描失败: {str(e)}", [], [])
    
    def build_value_key_map(self) -> tuple:
        """建立 value -> key 的映射
        
        只映射用户提供的 keys
        
        Returns:
            (value_to_key_map, mismatched_keys)
            - value_to_key_map: {value: key} 映射
            - mismatched_keys: 未找到的 keys 列表
        """
        value_to_key = {}
        found_keys = set()
        
        # 查找所有语言文件夹（使用第一个语言文件，通常是英文）
        lproj_folders = ProjectInfoExtractor.find_lproj_folders(self.project_path)
        
        for lang_code, lproj_path in lproj_folders.items():
            strings_file = os.path.join(lproj_path, 'Localizable.strings')
            if not os.path.exists(strings_file):
                continue
            
            # 解析文件
            data = LocalizationParser.parse_strings_file(strings_file)
            
            # 只添加用户提供的 keys
            for key in self.keys:
                if key in data:
                    value = data[key]
                    found_keys.add(key)
                    
                    # 根据是否区分大小写，添加映射
                    if self.case_sensitive:
                        # 区分大小写
                        if value not in value_to_key:
                            value_to_key[value] = key
                    else:
                        # 不区分大小写，使用小写作为 key
                        value_lower = value.lower()
                        if value_lower not in value_to_key:
                            value_to_key[value_lower] = key
                        # 同时保存原始大小写版本，方便精确匹配
                        if value not in value_to_key:
                            value_to_key[value] = key
            
            # 只需要读取一个语言文件即可
            break
        
        # 找出未匹配的 keys
        mismatched_keys = [k for k in self.keys if k not in found_keys]
        
        return value_to_key, mismatched_keys
    
    def scan_file(self, file_path: str, value_to_key_map: Dict[str, str]) -> List[Dict]:
        """扫描单个文件，查找多语言函数中的硬编码字符串
        
        只扫描以下函数调用中的字符串：
        - Localized(@"...")
        - D_Localized("...")
        - "...".localized
        等
        """
        results = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 相对路径
            relative_path = file_path.replace(self.project_path, "").lstrip(os.sep)
            
            # 定义要查找的多语言函数调用模式
            # OC: Localized(@"xxx"), D_Localized(@"xxx") 等
            # Swift: Localized("xxx"), "xxx".localized 等
            localized_patterns = [
                # OC 函数调用: FunctionName(@"value")
                r'(?:Localized|LocaRemoveTaglized|enLocalized|D_Localized|D_enLocalized)\s*\(\s*@"([^"]*)"\s*\)',
                # Swift 函数调用: FunctionName("value")
                r'(?:Localized|locaRemoveTaglized|D_Localized|LocalizedFormat)\s*\(\s*"([^"]*)"\s*[,\)]',
                # Swift 属性语法: "value".localized
                r'"([^"]*)"\s*\.\s*localized',
            ]
            
            for line_num, line in enumerate(lines, 1):
                # 使用所有模式匹配
                for pattern in localized_patterns:
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        string_value = match.group(1)
                        
                        # 跳过空字符串
                        if not string_value:
                            continue
                        
                        # 检查这个值是否在映射表中（说明它是 Value 而不是 Key）
                        key = None
                        if self.case_sensitive:
                            # 区分大小写：精确匹配
                            if string_value in value_to_key_map:
                                key = value_to_key_map[string_value]
                        else:
                            # 不区分大小写：先尝试精确匹配，再尝试小写匹配
                            if string_value in value_to_key_map:
                                key = value_to_key_map[string_value]
                            elif string_value.lower() in value_to_key_map:
                                key = value_to_key_map[string_value.lower()]
                        
                        if key:
                            results.append({
                                'file': relative_path,
                                'full_path': file_path,
                                'line': line_num,
                                'original': string_value,
                                'key': key,
                                'line_content': line.strip()
                            })
        
        except Exception as e:
            print(f"扫描文件失败 {file_path}: {e}")
        
        return results


class ReplaceStringsWorker(QThread):
    """替换字符串工作线程"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str, int)
    
    def __init__(self, results: List[Dict]):
        super().__init__()
        self.results = results
    
    def run(self):
        try:
            # 按文件分组
            files_to_update = {}
            for item in self.results:
                file_path = item['full_path']
                if file_path not in files_to_update:
                    files_to_update[file_path] = []
                files_to_update[file_path].append(item)
            
            replaced_count = 0
            
            for file_path, items in files_to_update.items():
                self.progress.emit(f"正在处理: {os.path.basename(file_path)}")
                
                # 读取文件
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # 按行号倒序处理（避免行号偏移）
                items.sort(key=lambda x: x['line'], reverse=True)
                
                for item in items:
                    line_num = item['line'] - 1  # 转为 0-based index
                    original_value = item['original']
                    key = item['key']
                    
                    # 替换字符串
                    # 只替换 Value 为 Key，保持原有的字符串格式
                    if file_path.endswith('.swift'):
                        # Swift: "原字符串" -> "key"
                        old_pattern = f'"{original_value}"'
                        new_string = f'"{key}"'
                    else:
                        # Objective-C: @"原字符串" -> @"key" 或 "原字符串" -> "key"
                        if f'@"{original_value}"' in lines[line_num]:
                            old_pattern = f'@"{original_value}"'
                            new_string = f'@"{key}"'
                        else:
                            old_pattern = f'"{original_value}"'
                            new_string = f'"{key}"'
                    
                    # 执行替换
                    lines[line_num] = lines[line_num].replace(old_pattern, new_string)
                    replaced_count += 1
                
                # 写回文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                
                self.progress.emit(f"✓ {os.path.basename(file_path)}: 替换 {len(items)} 处")
            
            self.finished.emit(True, f"成功替换 {replaced_count} 处字符串", replaced_count)
            
        except Exception as e:
            self.finished.emit(False, f"替换失败: {str(e)}", 0)

