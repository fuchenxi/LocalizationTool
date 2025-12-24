#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对比多语言工作线程
对比不同语言的 key-value，找出缺失的翻译
"""

import os
from typing import Dict, List
from PyQt6.QtCore import pyqtSignal

from models import LocalizationParser
from workers.base_worker import BaseWorker
from PyQt6.QtCore import pyqtSignal


class CompareWorker(BaseWorker):
    """对比工作线程"""
    finished = pyqtSignal(bool, str, dict)  # success, message, missing_keys
    
    def __init__(self, project_path: str, base_lang: str, ignore_folders: List[str] = None):
        super().__init__(project_path, ignore_folders)
        self.base_lang = base_lang
    
    def validate_inputs(self) -> bool:
        """验证输入参数"""
        if not super().validate_project_path():
            self.finished.emit(False, "项目路径无效", {})
            return False
        
        if not self.base_lang or not self.base_lang.strip():
            self.finished.emit(False, "基准语言不能为空", {})
            return False
        
        return True
    
    def run(self):
        try:
            if not self.validate_inputs():
                return
            
            # 1. 查找所有 .lproj 文件夹
            self.progress.emit("正在查找语言文件夹...")
            lproj_folders = self.find_lproj_folders()
            if lproj_folders is None:
                self.finished.emit(False, "项目中未找到 .lproj 文件夹", {})
                return
            
            # 检查基准语言是否存在
            if self.base_lang not in lproj_folders:
                self.finished.emit(False, f"基准语言 {self.base_lang} 不存在", {})
                return
            
            # 2. 读取基准语言的所有 key
            self.progress.emit(f"正在读取基准语言 {self.base_lang}...")
            base_lproj_path = lproj_folders[self.base_lang]
            base_strings_file = os.path.join(base_lproj_path, 'Localizable.strings')
            
            if not os.path.exists(base_strings_file):
                self.finished.emit(False, f"基准语言文件 {base_strings_file} 不存在", {})
                return
            
            base_keys = set(LocalizationParser.parse_strings_file(base_strings_file).keys())
            
            if not base_keys:
                self.finished.emit(False, f"基准语言 {self.base_lang} 没有 key", {})
                return
            
            self.progress.emit(f"✓ 基准语言 {self.base_lang} 共有 {len(base_keys)} 个 key")
            
            # 3. 对比其他语言
            missing_keys = {}  # {lang_code: [key1, key2, ...]}
            
            for lang_code, lproj_path in lproj_folders.items():
                if self.check_stopped():
                    self.finished.emit(False, "操作已取消", {})
                    return
                
                # 跳过基准语言本身（不区分大小写）
                if lang_code.lower() == self.base_lang.lower():
                    continue
                
                # 跳过 base 语言（无论基准语言是什么）
                if lang_code.lower() == 'base':
                    continue
                
                self.progress.emit(f"正在对比 {lang_code}...")
                
                # 读取该语言的所有 key
                strings_file = os.path.join(lproj_path, 'Localizable.strings')
                
                if not os.path.exists(strings_file):
                    # 如果文件不存在，所有 key 都缺失
                    missing_keys[lang_code] = list(base_keys)
                    self.progress.emit(f"⚠ {lang_code}: 文件不存在，缺失 {len(base_keys)} 个 key")
                    continue
                
                lang_keys = set(LocalizationParser.parse_strings_file(strings_file).keys())
                
                # 找出缺失的 key
                missing = base_keys - lang_keys
                
                if missing:
                    missing_keys[lang_code] = sorted(list(missing))
                    self.progress.emit(f"⚠ {lang_code}: 缺失 {len(missing)} 个 key")
                else:
                    self.progress.emit(f"✓ {lang_code}: 完整")
            
            # 4. 返回结果
            if missing_keys:
                total_missing = sum(len(keys) for keys in missing_keys.values())
                message = f"对比完成，发现 {len(missing_keys)} 个语言文件共缺失 {total_missing} 个 key"
            else:
                message = f"对比完成，所有语言都完整！"
            
            self.finished.emit(True, message, missing_keys)
            
        except Exception as e:
            error_msg = self.emit_error("对比", e)
            self.finished.emit(False, error_msg, {})

