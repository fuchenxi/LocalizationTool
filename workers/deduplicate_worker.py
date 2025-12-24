#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
删除重复项工作线程
"""

import os
from typing import List
from PyQt6.QtCore import QThread, pyqtSignal

from models import ProjectInfoExtractor, LocalizationParser


class DeduplicateWorker(QThread):
    """删除重复项工作线程"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str, int)
    
    def __init__(self, project_path: str, ignore_folders: List[str] = None):
        super().__init__()
        self.project_path = project_path
        self.ignore_folders = ignore_folders
    
    def run(self):
        try:
            # 查找所有 .lproj 文件夹
            self.progress.emit("正在查找语言文件夹...")
            lproj_folders = ProjectInfoExtractor.find_lproj_folders(self.project_path, self.ignore_folders)
            
            if not lproj_folders:
                self.finished.emit(False, "项目中未找到 .lproj 文件夹", 0)
                return
            
            total_removed = 0
            processed_count = 0
            
            for lang_code, lproj_path in lproj_folders.items():
                self.progress.emit(f"正在处理 {lang_code} 语言...")
                
                # 查找 Localizable.strings 文件
                strings_file = os.path.join(lproj_path, 'Localizable.strings')
                
                if not os.path.exists(strings_file):
                    self.progress.emit(f"跳过: {strings_file} 不存在")
                    continue
                
                # 删除重复项
                removed = LocalizationParser.remove_duplicates(strings_file)
                total_removed += removed
                processed_count += 1
                
                self.progress.emit(f"✓ {lang_code}: 删除了 {removed} 个重复项")
            
            self.finished.emit(True, f"成功处理 {processed_count} 个语言文件", total_removed)
            
        except Exception as e:
            self.finished.emit(False, f"删除失败: {str(e)}", 0)

