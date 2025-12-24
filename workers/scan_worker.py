#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
扫描重复项工作线程
"""

import os
from typing import List
from PyQt6.QtCore import pyqtSignal

from models import LocalizationParser
from workers.base_worker import BaseWorker
from PyQt6.QtCore import pyqtSignal


class ScanDuplicatesWorker(BaseWorker):
    """扫描重复项工作线程（不删除）"""
    finished = pyqtSignal(bool, str, dict)  # success, message, duplicates_info
    
    def run(self):
        try:
            if not self.validate_project_path():
                self.finished.emit(False, "项目路径无效", {})
                return
            
            # 查找所有 .lproj 文件夹
            self.progress.emit("正在查找语言文件夹...")
            lproj_folders = self.find_lproj_folders()
            if lproj_folders is None:
                self.finished.emit(False, "项目中未找到 .lproj 文件夹", {})
                return
            
            duplicates_info = {}
            total_duplicates = 0
            
            for lang_code, lproj_path in lproj_folders.items():
                if self.check_stopped():
                    self.finished.emit(False, "操作已取消", {})
                    return
                
                self.progress.emit(f"正在扫描 {lang_code} 语言...")
                
                # 查找 Localizable.strings 文件
                strings_file = os.path.join(lproj_path, 'Localizable.strings')
                
                if not os.path.exists(strings_file):
                    self.progress.emit(f"跳过: {strings_file} 不存在")
                    continue
                
                # 查找重复项详情
                duplicate_details = LocalizationParser.find_duplicates(strings_file)
                if duplicate_details:
                    duplicate_count = sum(len(items) - 1 for items in duplicate_details.values())
                    duplicates_info[lang_code] = {
                        'file': strings_file,
                        'count': duplicate_count,
                        'details': duplicate_details  # {key: [(value1, line1), (value2, line2), ...]}
                    }
                    total_duplicates += duplicate_count
                    self.progress.emit(f"⚠ {lang_code}: 发现 {duplicate_count} 个重复项")
                else:
                    self.progress.emit(f"✓ {lang_code}: 无重复项")
            
            if total_duplicates > 0:
                self.finished.emit(True, f"扫描完成，共发现 {total_duplicates} 个重复项", duplicates_info)
            else:
                self.finished.emit(True, "扫描完成，未发现重复项", {})
            
        except Exception as e:
            error_msg = self.emit_error("扫描", e)
            self.finished.emit(False, error_msg, {})

