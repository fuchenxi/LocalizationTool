#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
长度对比工作线程
对比不同语言的 value 长度，找出变长的字段
"""

import os
from typing import Dict, List, Optional
from PyQt6.QtCore import pyqtSignal

from models import LocalizationParser
from workers.base_worker import BaseWorker


class LengthCompareWorker(BaseWorker):
    """长度对比工作线程"""
    finished = pyqtSignal(bool, str, dict)  # success, message, results
    
    def __init__(
        self, 
        project_path: str, 
        target_languages: List[str],
        compare_mode: str = "average",  # "average", "max", "base_lang"
        base_lang: Optional[str] = None,
        min_diff_percent: float = 0.0  # 最小差异百分比阈值
    ):
        super().__init__(project_path)
        self.target_languages = target_languages
        self.compare_mode = compare_mode
        self.base_lang = base_lang
        self.min_diff_percent = min_diff_percent
    
    def validate_inputs(self) -> bool:
        """验证输入参数"""
        if not super().validate_project_path():
            self.finished.emit(False, "项目路径无效", {})
            return False
        
        if not self.target_languages:
            self.finished.emit(False, "请至少选择一个目标语言", {})
            return False
        
        if self.compare_mode == "base_lang" and not self.base_lang:
            self.finished.emit(False, "选择基准语言模式时，必须指定基准语言", {})
            return False
        
        return True
    
    def calculate_base_length(
        self, 
        key: str, 
        all_values: Dict[str, Dict[str, any]], 
        exclude_langs: List[str]
    ) -> float:
        """计算基准长度
        
        Args:
            key: key 名称
            all_values: {lang: {"value": str, "length": int}}
            exclude_langs: 要排除的语言列表（目标语言）
        
        Returns:
            基准长度（平均/最大/指定语言）
        """
        # 获取所有非目标语言的 value 长度
        other_lengths = []
        for lang, data in all_values.items():
            if lang not in exclude_langs and data.get("value") is not None:
                other_lengths.append(data["length"])
        
        if not other_lengths:
            return 0.0
        
        if self.compare_mode == "average":
            return sum(other_lengths) / len(other_lengths)
        elif self.compare_mode == "max":
            return max(other_lengths)
        elif self.compare_mode == "base_lang":
            if self.base_lang in all_values and all_values[self.base_lang].get("value") is not None:
                return float(all_values[self.base_lang]["length"])
            else:
                # 如果基准语言没有该 key，使用平均值
                return sum(other_lengths) / len(other_lengths) if other_lengths else 0.0
        
        return 0.0
    
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
            
            # 验证目标语言是否存在
            missing_langs = [lang for lang in self.target_languages if lang not in lproj_folders]
            if missing_langs:
                self.finished.emit(False, f"目标语言不存在: {', '.join(missing_langs)}", {})
                return
            
            # 验证基准语言（如果使用 base_lang 模式）
            if self.compare_mode == "base_lang" and self.base_lang not in lproj_folders:
                self.finished.emit(False, f"基准语言 {self.base_lang} 不存在", {})
                return
            
            # 2. 读取所有语言的 strings 文件
            self.progress.emit("正在读取所有语言文件...")
            all_lang_data = {}  # {lang_code: {key: value}}
            
            for lang_code, lproj_path in lproj_folders.items():
                if self.check_stopped():
                    self.finished.emit(False, "操作已取消", {})
                    return
                
                strings_file = os.path.join(lproj_path, 'Localizable.strings')
                if os.path.exists(strings_file):
                    lang_data = LocalizationParser.parse_strings_file(strings_file)
                    all_lang_data[lang_code] = lang_data
                    self.progress.emit(f"✓ 已读取 {lang_code}: {len(lang_data)} 个 key")
            
            if not all_lang_data:
                self.finished.emit(False, "未找到任何语言文件", {})
                return
            
            # 3. 收集所有 key
            all_keys = set()
            for lang_data in all_lang_data.values():
                all_keys.update(lang_data.keys())
            
            if not all_keys:
                self.finished.emit(False, "未找到任何 key", {})
                return
            
            self.progress.emit(f"✓ 共找到 {len(all_keys)} 个 key")
            
            # 4. 对每个 key 进行长度对比
            self.progress.emit("正在对比长度...")
            results = {}  # {key: {target_lang, target_value, target_length, base_length, diff, diff_percent, all_values}}
            
            for key in all_keys:
                if self.check_stopped():
                    self.finished.emit(False, "操作已取消", {})
                    return
                
                # 收集所有语言的 value 和长度
                all_values = {}
                for lang_code, lang_data in all_lang_data.items():
                    value = lang_data.get(key)
                    if value is not None:
                        length = len(value)
                        all_values[lang_code] = {
                            "value": value,
                            "length": length
                        }
                
                # 对每个目标语言进行对比
                for target_lang in self.target_languages:
                    if target_lang not in all_values:
                        continue  # 该目标语言没有这个 key，跳过
                    
                    target_data = all_values[target_lang]
                    target_length = target_data["length"]
                    
                    # 计算基准长度（排除目标语言本身）
                    base_length = self.calculate_base_length(
                        key, 
                        all_values, 
                        [target_lang]
                    )
                    
                    if base_length == 0:
                        continue  # 没有基准数据，跳过
                    
                    # 计算差异
                    diff = target_length - base_length
                    diff_percent = (diff / base_length * 100) if base_length > 0 else 0.0
                    
                    # 只保留变长的字段（diff > 0 且超过阈值）
                    if diff > 0 and diff_percent >= self.min_diff_percent:
                        result_key = f"{key}__{target_lang}"  # 使用组合 key 支持多目标语言
                        results[result_key] = {
                            "key": key,
                            "target_lang": target_lang,
                            "target_value": target_data["value"],
                            "target_length": target_length,
                            "base_length": base_length,
                            "diff": diff,
                            "diff_percent": diff_percent,
                            "all_values": all_values.copy()  # 保存所有语言的值用于参考
                        }
            
            # 5. 返回结果
            if results:
                total_count = len(results)
                message = f"对比完成，发现 {total_count} 个变长的字段"
            else:
                message = "对比完成，未发现变长的字段"
            
            self.finished.emit(True, message, results)
            
        except Exception as e:
            error_msg = self.emit_error("长度对比", e)
            self.finished.emit(False, error_msg, {})

