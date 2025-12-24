#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导出多语言工作线程
"""

import os
import zipfile
import tempfile
import shutil
from datetime import datetime
from typing import List
from PyQt6.QtCore import pyqtSignal
from collections import OrderedDict

from models import LocalizationParser
from workers.base_worker import BaseWorker
from utils.config import ConfigManager
from PyQt6.QtCore import pyqtSignal


class ExportWorker(BaseWorker):
    """导出工作线程"""
    finished = pyqtSignal(bool, str, str)  # success, message, zip_path
    
    def __init__(self, project_path: str, export_strings: bool, export_xml: bool, 
                 key_list: list = None, ignore_folders: List[str] = None):
        super().__init__(project_path, ignore_folders)
        self.export_strings = export_strings
        self.export_xml = export_xml
        self.key_list = key_list or []  # 如果提供 key_list，只导出指定的 key
        self.temp_dir = None
    
    def run(self):
        try:
            if not self.validate_project_path():
                self.finished.emit(False, "项目路径无效", "")
                return
            
            # 1. 查找项目中的 .lproj 文件夹
            self.progress.emit("正在查找项目语言文件...")
            lproj_folders = self.find_lproj_folders()
            if lproj_folders is None:
                self.finished.emit(False, "项目中未找到 .lproj 文件夹", "")
                return
            
            self.progress.emit(f"✓ 找到 {len(lproj_folders)} 个语言文件夹")
            
            # 2. 创建临时目录
            self.temp_dir = tempfile.mkdtemp()
            try:
                # 3. 读取每个语言的多语言数据
                language_data = {}  # {lang_code: OrderedDict}
                
                for lang_code, lproj_path in lproj_folders.items():
                    if self.check_stopped():
                        self.finished.emit(False, "操作已取消", "")
                        return
                    
                    self.progress.emit(f"正在读取 {lang_code} 语言...")
                    
                    # 查找 Localizable.strings 文件
                    strings_file = os.path.join(lproj_path, 'Localizable.strings')
                    
                    if not os.path.exists(strings_file):
                        self.progress.emit(f"⚠ {lang_code}.lproj/Localizable.strings 不存在，跳过")
                        continue
                    
                    # 解析语言文件
                    all_data = LocalizationParser.parse_strings_file(strings_file)
                    if not all_data:
                        self.progress.emit(f"⚠ {lang_code}: 文件为空")
                        continue
                    
                    # 如果指定了 key_list，只导出指定的 key，并按照指定顺序
                    if self.key_list:
                        filtered_data = OrderedDict()
                        missing_keys = []
                        for key in self.key_list:
                            if key in all_data:
                                filtered_data[key] = all_data[key]
                            else:
                                missing_keys.append(key)
                        
                        if missing_keys:
                            self.progress.emit(f"⚠ {lang_code}: 缺少以下 key: {', '.join(missing_keys)}")
                        
                        if filtered_data:
                            language_data[lang_code] = filtered_data
                            self.progress.emit(f"✓ {lang_code}: {len(filtered_data)}/{len(self.key_list)} 条")
                    else:
                        # 如果没有指定 key_list，导出全部
                        language_data[lang_code] = all_data
                        self.progress.emit(f"✓ {lang_code}: {len(all_data)} 条")
                
                if not language_data:
                    self.finished.emit(False, "没有可导出的多语言数据", "")
                    return
                
                # 4. 根据选项导出文件
                # 先导出 .strings 格式（如果选择了 XML，也需要先导出 .strings）
                strings_dir = None
                if self.export_strings or self.export_xml:
                    self.progress.emit("\n正在导出 .strings 格式...")
                    strings_dir = os.path.join(self.temp_dir, "Strings")
                    os.makedirs(strings_dir, exist_ok=True)
                    
                    for lang_code, data in language_data.items():
                        if self.check_stopped():
                            self.finished.emit(False, "操作已取消", "")
                            return
                        
                        output_file = os.path.join(strings_dir, f"{lang_code}.strings")
                        LocalizationParser.write_strings_file(output_file, data)
                        self.progress.emit(f"✓ 已导出: {lang_code}.strings")
                
                # 如果选择了 XML，根据导出的 .strings 文件导出 XML
                if self.export_xml:
                    self.progress.emit("\n正在根据 .strings 文件导出 .xml 格式...")
                    xml_dir = os.path.join(self.temp_dir, "XML")
                    os.makedirs(xml_dir, exist_ok=True)
                    
                    # 从导出的 .strings 文件读取数据，然后导出为 XML
                    for lang_code in language_data.keys():
                        if self.check_stopped():
                            self.finished.emit(False, "操作已取消", "")
                            return
                        
                        strings_file = os.path.join(strings_dir, f"{lang_code}.strings")
                        if os.path.exists(strings_file):
                            # 从 .strings 文件读取数据
                            xml_data = LocalizationParser.parse_strings_file(strings_file)
                            if xml_data:
                                output_file = os.path.join(xml_dir, f"{lang_code}.xml")
                                LocalizationParser.write_xml_file(output_file, xml_data)
                                self.progress.emit(f"✓ 已导出: {lang_code}.xml")
                
                # 5. 打包成 zip 文件
                self.progress.emit("\n正在打包...")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                zip_filename = f"LocalizationExport_{timestamp}.zip"
                
                # 使用配置的导出路径
                export_path = ConfigManager.get_export_path()
                zip_path = os.path.join(export_path, zip_filename)
                
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(self.temp_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, self.temp_dir)
                            zipf.write(file_path, arcname)
                
                self.progress.emit(f"✓ 导出完成: {zip_filename}")
                self.progress.emit(f"✓ 保存位置: {zip_path}")
                
                # 统计信息
                formats = []
                if self.export_strings:
                    formats.append(".strings")
                if self.export_xml:
                    formats.append(".xml")
                
                summary = f"成功导出 {len(language_data)} 个语言，格式: {', '.join(formats)}"
                self.finished.emit(True, summary, zip_path)
                
            finally:
                # 清理临时目录
                if self.temp_dir and os.path.exists(self.temp_dir):
                    try:
                        shutil.rmtree(self.temp_dir)
                    except Exception as e:
                        print(f"清理临时目录失败: {e}")
                
        except Exception as e:
            error_msg = self.emit_error("导出", e)
            self.finished.emit(False, error_msg, "")
            # 确保清理临时目录
            if self.temp_dir and os.path.exists(self.temp_dir):
                try:
                    shutil.rmtree(self.temp_dir)
                except:
                    pass

