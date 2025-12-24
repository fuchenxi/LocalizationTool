#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导入多语言工作线程
"""

import os
import zipfile
import shutil
from PyQt6.QtCore import QThread, pyqtSignal

from models import ProjectInfoExtractor, LocalizationParser


class ImportWorker(QThread):
    """导入工作线程"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, zip_path: str, project_path: str, version: str):
        super().__init__()
        self.zip_path = zip_path
        self.project_path = project_path
        self.version = version
    
    def run(self):
        try:
            # 1. 解压 zip 文件
            self.progress.emit("正在解压 zip 文件...")
            extract_dir = os.path.join(os.path.dirname(self.zip_path), 
                                      os.path.splitext(os.path.basename(self.zip_path))[0])
            
            # 清理之前的解压目录
            if os.path.exists(extract_dir):
                shutil.rmtree(extract_dir)
            
            os.makedirs(extract_dir, exist_ok=True)
            
            with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # 2. 查找 .strings 文件
            self.progress.emit("正在查找语言文件...")
            strings_files = {}
            
            # 检查是否直接在解压目录下有 .strings 文件
            for file in os.listdir(extract_dir):
                if file.endswith('.strings'):
                    lang_code = os.path.splitext(file)[0]
                    strings_files[lang_code] = os.path.join(extract_dir, file)
            
            # 如果没有，递归查找
            if not strings_files:
                for root, dirs, files in os.walk(extract_dir):
                    for file in files:
                        if file.endswith('.strings'):
                            lang_code = os.path.splitext(file)[0]
                            strings_files[lang_code] = os.path.join(root, file)
            
            if not strings_files:
                self.finished.emit(False, "未找到 .strings 文件")
                return
            
            # 3. 查找项目中的 .lproj 文件夹
            self.progress.emit("正在查找项目语言文件夹...")
            lproj_folders = ProjectInfoExtractor.find_lproj_folders(self.project_path)
            
            if not lproj_folders:
                self.finished.emit(False, "项目中未找到 .lproj 文件夹")
                return
            
            # 4. 导入语言文件
            imported_count = 0
            for lang_code, strings_file in strings_files.items():
                self.progress.emit(f"正在导入 {lang_code} 语言...")
                
                # 查找对应的 .lproj 文件夹
                if lang_code not in lproj_folders:
                    self.progress.emit(f"警告: 项目中未找到 {lang_code}.lproj 文件夹，跳过")
                    continue
                
                # 查找 Localizable.strings 文件
                target_file = os.path.join(lproj_folders[lang_code], 'Localizable.strings')
                
                if not os.path.exists(target_file):
                    self.progress.emit(f"警告: {target_file} 不存在，跳过")
                    continue
                
                # 直接追加原始文件内容（不解析，保持原始格式）
                LocalizationParser.append_strings_with_version(target_file, strings_file, self.version)
                
                # 只用于统计显示
                new_data = LocalizationParser.parse_strings_file(strings_file)
                imported_count += 1
                self.progress.emit(f"✓ {lang_code} 导入成功 ({len(new_data)} 条)")
            
            # 5. 清理解压目录
            shutil.rmtree(extract_dir)
            
            self.finished.emit(True, f"成功导入 {imported_count} 个语言文件")
            
        except Exception as e:
            self.finished.emit(False, f"导入失败: {str(e)}")

