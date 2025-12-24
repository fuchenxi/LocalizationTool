#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提取 Key Worker
从指定语言的 Localizable.strings 文件中提取所有 key
"""

import os
from PyQt6.QtCore import QThread, pyqtSignal
from models.localization_parser import LocalizationParser
from models.project_info import ProjectInfoExtractor


class ExtractKeysWorker(QThread):
    """提取 Key 的后台线程"""
    
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str, list)  # success, message, keys
    
    def __init__(self, project_path: str, language: str):
        super().__init__()
        self.project_path = project_path
        self.language = language
    
    def run(self):
        """执行提取"""
        try:
            # 查找指定语言的 .lproj 文件夹
            lproj_folders = ProjectInfoExtractor.find_lproj_folders(self.project_path)
            
            if self.language not in lproj_folders:
                self.finished.emit(False, f"未找到语言 '{self.language}' 的文件夹", [])
                return
            
            lproj_path = lproj_folders[self.language]
            self.progress.emit(f"找到语言文件夹: {lproj_path}")
            
            # 查找 Localizable.strings 文件
            strings_file = os.path.join(lproj_path, "Localizable.strings")
            
            if not os.path.exists(strings_file):
                # 尝试在 Supporting Files 目录下查找
                supporting_files_path = os.path.join(lproj_path, "..", "Supporting Files", self.language + ".lproj", "Localizable.strings")
                if os.path.exists(supporting_files_path):
                    strings_file = supporting_files_path
                else:
                    self.finished.emit(False, f"未找到 {self.language} 语言的 Localizable.strings 文件", [])
                    return
            
            self.progress.emit(f"找到文件: {strings_file}")
            
            # 解析文件，提取所有 key
            parsed_data = LocalizationParser.parse_strings_file(strings_file)
            
            if not parsed_data:
                self.finished.emit(False, f"文件为空或无法解析", [])
                return
            
            # 提取所有 key
            keys = list(parsed_data.keys())
            
            self.progress.emit(f"✓ 成功提取 {len(keys)} 个 key")
            self.finished.emit(True, f"成功提取 {len(keys)} 个 key", keys)
            
        except Exception as e:
            self.finished.emit(False, f"提取失败: {str(e)}", [])
