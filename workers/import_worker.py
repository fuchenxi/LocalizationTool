#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导入多语言工作线程
"""

import os
import zipfile
import shutil
from PyQt6.QtCore import pyqtSignal

from models import LocalizationParser
from workers.base_worker import BaseWorker
from PyQt6.QtCore import pyqtSignal


class ImportWorker(BaseWorker):
    """导入工作线程"""
    finished = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, zip_path: str, project_path: str, version: str, 
                 language_mappings: dict = None, ignore_folders: list = None):
        super().__init__(project_path, ignore_folders)
        self.zip_path = zip_path
        self.version = version
        self.language_mappings = language_mappings or {}  # {zip_lang: project_lang}
        self.extract_dir = None
    
    def validate_inputs(self) -> bool:
        """验证输入参数"""
        if not super().validate_project_path():
            self.finished.emit(False, "项目路径无效")
            return False
        
        if not self.zip_path or not os.path.exists(self.zip_path):
            self.finished.emit(False, f"ZIP 文件不存在: {self.zip_path}")
            return False
        
        if not self.version or not self.version.strip():
            self.finished.emit(False, "版本号不能为空")
            return False
        
        return True
    
    def run(self):
        try:
            if not self.validate_inputs():
                return
            
            # 1. 解压 zip 文件
            self.progress.emit("正在解压 zip 文件...")
            self.extract_dir = os.path.join(os.path.dirname(self.zip_path), 
                                      os.path.splitext(os.path.basename(self.zip_path))[0])
            
            # 清理之前的解压目录
            if os.path.exists(self.extract_dir):
                shutil.rmtree(self.extract_dir)
            
            os.makedirs(self.extract_dir, exist_ok=True)
            
            with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.extract_dir)
            
            # 2. 查找 .strings 文件
            self.progress.emit("正在查找语言文件...")
            strings_files = {}
            
            # 检查是否直接在解压目录下有 .strings 文件
            for file in os.listdir(self.extract_dir):
                if file.endswith('.strings'):
                    lang_code = os.path.splitext(file)[0]
                    strings_files[lang_code] = os.path.join(self.extract_dir, file)
            
            # 如果没有，递归查找
            if not strings_files:
                for root, dirs, files in os.walk(self.extract_dir):
                    for file in files:
                        if file.endswith('.strings'):
                            lang_code = os.path.splitext(file)[0]
                            strings_files[lang_code] = os.path.join(root, file)
            
            if not strings_files:
                self.finished.emit(False, "未找到 .strings 文件")
                return
            
            # 3. 查找项目中的 .lproj 文件夹
            self.progress.emit("正在查找项目语言文件夹...")
            lproj_folders = self.find_lproj_folders()
            if lproj_folders is None:
                self.finished.emit(False, "项目中未找到 .lproj 文件夹")
                return
            
            # 4. 导入语言文件
            imported_count = 0
            for zip_lang, strings_file in strings_files.items():
                if self.check_stopped():
                    self.finished.emit(False, "操作已取消")
                    return
                
                # 使用语言映射（如果有的话）
                if self.language_mappings:
                    if zip_lang not in self.language_mappings:
                        self.progress.emit(f"跳过: {zip_lang} (未配置映射)")
                        continue
                    project_lang = self.language_mappings[zip_lang]
                    self.progress.emit(f"正在导入 {zip_lang} → {project_lang}...")
                else:
                    # 没有映射时，直接使用 zip 中的语言代码
                    project_lang = zip_lang
                    self.progress.emit(f"正在导入 {zip_lang} 语言...")
                
                # 查找对应的 .lproj 文件夹
                if project_lang not in lproj_folders:
                    self.progress.emit(f"警告: 项目中未找到 {project_lang}.lproj 文件夹，跳过")
                    continue
                
                # 查找 Localizable.strings 文件
                target_file = os.path.join(lproj_folders[project_lang], 'Localizable.strings')
                
                if not os.path.exists(target_file):
                    self.progress.emit(f"警告: {target_file} 不存在，跳过")
                    continue
                
                # 直接追加原始文件内容（不解析，保持原始格式）
                LocalizationParser.append_strings_with_version(target_file, strings_file, self.version)
                
                # 只用于统计显示
                new_data = LocalizationParser.parse_strings_file(strings_file)
                imported_count += 1
                if self.language_mappings and zip_lang != project_lang:
                    self.progress.emit(f"✓ {zip_lang} → {project_lang} 导入成功 ({len(new_data)} 条)")
                else:
                    self.progress.emit(f"✓ {project_lang} 导入成功 ({len(new_data)} 条)")
            
            # 5. 清理解压目录
            if self.extract_dir and os.path.exists(self.extract_dir):
                try:
                    shutil.rmtree(self.extract_dir)
                except Exception as e:
                    print(f"清理解压目录失败: {e}")
            
            self.finished.emit(True, f"成功导入 {imported_count} 个语言文件")
            
        except Exception as e:
            error_msg = self.emit_error("导入", e)
            self.finished.emit(False, error_msg)
            # 确保清理解压目录
            if self.extract_dir and os.path.exists(self.extract_dir):
                try:
                    shutil.rmtree(self.extract_dir)
                except:
                    pass

