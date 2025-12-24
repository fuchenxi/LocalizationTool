#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提取 Key 标签页
从指定语言的 Localizable.strings 文件中提取所有 key
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QPushButton, QTextEdit, QSplitter
)
from PyQt6.QtCore import Qt
from utils.theme import get_theme_colors


class ExtractKeysTab(QWidget):
    """提取 Key 标签页"""
    
    def __init__(self):
        super().__init__()
        self.colors = get_theme_colors()
        self.all_key_values = {}  # 存储所有 key-value 对 {key: value}
        self.selected_language = ""  # 当前选中的语言
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # ============ 顶部工具栏 ============
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(12)
        
        # 语言选择标签
        lang_label = QLabel("语言:")
        lang_label.setStyleSheet(f"color: {self.colors['text_secondary']}; font-size: 13px;")
        toolbar_layout.addWidget(lang_label)
        
        # 语言下拉框
        self.lang_combo = QComboBox()
        self.lang_combo.setMinimumHeight(32)
        self.lang_combo.setMinimumWidth(120)
        self.lang_combo.setStyleSheet(f"""
            QComboBox {{
                padding: 6px 12px;
                border: 1px solid {self.colors['border']};
                border-radius: 6px;
                background: {self.colors['bg_card']};
                color: {self.colors['text_primary']};
                font-size: 13px;
            }}
            QComboBox:hover {{
                border: 1px solid {self.colors['border_focus']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            QComboBox QAbstractItemView {{
                border: 1px solid {self.colors['border']};
                border-radius: 6px;
                background: {self.colors['bg_card']};
                selection-background-color: {self.colors['button_bg']};
                selection-color: white;
            }}
        """)
        toolbar_layout.addWidget(self.lang_combo)
        
        toolbar_layout.addStretch()
        
        # 提取按钮
        self.extract_btn = QPushButton("🔑 提取 Key")
        self.extract_btn.setMinimumHeight(32)
        self.extract_btn.setMinimumWidth(120)
        self.extract_btn.setEnabled(False)
        self.extract_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 6px 16px;
                border-radius: 6px;
                background: {self.colors['button_bg']};
                color: white;
                font-size: 13px;
                font-weight: 500;
                border: none;
            }}
            QPushButton:hover {{
                background: {self.colors['button_bg_hover']};
            }}
            QPushButton:pressed {{
                background: {self.colors['button_bg_pressed']};
            }}
            QPushButton:disabled {{
                background: {self.colors['bg_secondary']};
                color: {self.colors['text_tertiary']};
            }}
        """)
        toolbar_layout.addWidget(self.extract_btn)
        
        layout.addLayout(toolbar_layout)
        
        # ============ 左右分栏 ============
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧：过滤输入框
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)
        
        # 左侧标题
        left_title = QLabel("过滤 Key")
        left_title.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {self.colors['text_primary']};")
        left_layout.addWidget(left_title)
        
        # 过滤输入框
        self.filter_input = QTextEdit()
        self.filter_input.setAcceptRichText(False)  # 禁用富文本，只接受纯文本
        self.filter_input.setPlaceholderText(
            "输入要过滤的 key，支持两种格式：\n"
            "1. 纯 key 列表（每行一个）\n"
            "2. .strings 文件格式（自动提取 key）\n\n"
            "例如：\n"
            "key1\n"
            "action_\n\n"
            "或粘贴 .strings 文件内容：\n"
            '"journey_through_nature"="Journey Through Nature";'
        )
        self.filter_input.textChanged.connect(self.on_filter_changed)
        self.filter_input.setStyleSheet(f"""
            QTextEdit {{
                font-family: 'SF Mono', Menlo, Monaco, 'Courier New', monospace;
                font-size: 12px;
                padding: 12px;
                border: none;
                border-radius: 8px;
                background: {self.colors['bg_card']};
                color: {self.colors['text_primary']};
            }}
            QTextEdit:focus {{
                border: 2px solid {self.colors['border_focus']};
                background: {self.colors['bg_main']};
            }}
        """)
        left_layout.addWidget(self.filter_input, 1)
        
        splitter.addWidget(left_widget)
        
        # 右侧：结果输出框
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)
        
        # 右侧标题和统计
        right_header = QHBoxLayout()
        right_header.setSpacing(8)
        
        right_title = QLabel("提取结果")
        right_title.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {self.colors['text_primary']};")
        right_header.addWidget(right_title)
        
        self.result_count_label = QLabel("")
        self.result_count_label.setStyleSheet(f"font-size: 12px; color: {self.colors['text_secondary']};")
        right_header.addWidget(self.result_count_label)
        
        right_header.addStretch()
        right_layout.addLayout(right_header)
        
        # 结果输出框
        self.keys_text = QTextEdit()
        self.keys_text.setReadOnly(True)
        self.keys_text.setPlaceholderText("提取的 key 将显示在这里...")
        self.keys_text.setStyleSheet(f"""
            QTextEdit {{
                font-family: 'SF Mono', Menlo, Monaco, 'Courier New', monospace;
                font-size: 12px;
                padding: 12px;
                border: none;
                border-radius: 8px;
                background: {self.colors['bg_card']};
                color: {self.colors['text_primary']};
            }}
        """)
        right_layout.addWidget(self.keys_text, 1)
        
        splitter.addWidget(right_widget)
        
        # 设置分割比例 (30% : 70%)
        splitter.setSizes([300, 700])
        
        layout.addWidget(splitter, 1)
        
        # ============ 底部按钮 ============
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.setSpacing(12)
        
        # 复制按钮（主要按钮）
        self.copy_btn = QPushButton("📋 复制")
        self.copy_btn.setMinimumHeight(36)
        self.copy_btn.setMinimumWidth(100)
        self.copy_btn.setEnabled(False)
        self.copy_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 8px 20px;
                border-radius: 8px;
                background: {self.colors['button_bg']};
                color: white;
                font-size: 13px;
                font-weight: 500;
                border: none;
            }}
            QPushButton:hover {{
                background: {self.colors['button_bg_hover']};
            }}
            QPushButton:pressed {{
                background: {self.colors['button_bg_pressed']};
            }}
            QPushButton:disabled {{
                background: {self.colors['bg_secondary']};
                color: {self.colors['text_tertiary']};
            }}
        """)
        button_layout.addWidget(self.copy_btn)
        
        # 保存按钮（次要按钮）
        self.save_btn = QPushButton("💾 保存")
        self.save_btn.setMinimumHeight(36)
        self.save_btn.setMinimumWidth(100)
        self.save_btn.setEnabled(False)
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 8px 20px;
                border-radius: 8px;
                background: {self.colors['bg_card']};
                color: {self.colors['text_primary']};
                font-size: 13px;
                font-weight: 500;
                border: 1px solid {self.colors['border']};
            }}
            QPushButton:hover {{
                background: {self.colors['bg_hover']};
                border: 1px solid {self.colors['border_focus']};
            }}
            QPushButton:pressed {{
                background: {self.colors['bg_secondary']};
            }}
            QPushButton:disabled {{
                background: {self.colors['bg_secondary']};
                color: {self.colors['text_tertiary']};
                border: 1px solid {self.colors['border']};
            }}
        """)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
    
    def update_languages(self, languages: list):
        """更新语言列表"""
        self.lang_combo.clear()
        if languages:
            self.lang_combo.addItems(sorted(languages))
            self.extract_btn.setEnabled(True)
        else:
            self.extract_btn.setEnabled(False)
    
    def get_selected_language(self) -> str:
        """获取选中的语言"""
        return self.lang_combo.currentText()
    
    def get_filter_keys(self) -> list:
        """获取过滤的 key 列表
        支持两种格式：
        1. 纯 key 列表（每行一个 key）
        2. .strings 文件格式（自动提取 key）
        """
        import re
        
        text = self.filter_input.toPlainText().strip()
        if not text:
            return []
        
        filter_keys = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # 跳过空行
            if not line:
                continue
            
            # 跳过注释行（以 // 开头）
            if line.startswith('//'):
                continue
            
            # 尝试匹配 .strings 文件格式："key"="value";
            # 匹配格式：引号内的 key
            match = re.match(r'^"([^"]+)"\s*=', line)
            if match:
                # 从 .strings 格式中提取 key
                key = match.group(1)
                filter_keys.append(key)
            else:
                # 如果不是 .strings 格式，当作纯 key 处理
                # 移除可能的引号
                key = line.strip('"\'')
                if key:
                    filter_keys.append(key)
        
        return filter_keys
    
    def on_filter_changed(self):
        """过滤输入改变时，更新显示结果（排除过滤的 key）"""
        if not self.all_key_values:
            return
        
        filter_keys = self.get_filter_keys()
        
        if not filter_keys:
            # 没有过滤条件，显示所有 key
            filtered_keys = list(self.all_key_values.keys())
        else:
            # 排除过滤的 key
            filtered_keys = []
            
            for key in self.all_key_values.keys():
                # 检查 key 是否在过滤列表中（完全匹配或包含匹配）
                should_exclude = False
                
                for filter_str in filter_keys:
                    # 完全匹配
                    if key == filter_str:
                        should_exclude = True
                        break
                    # 包含匹配（不区分大小写）
                    if filter_str.lower() in key.lower():
                        should_exclude = True
                        break
                
                # 如果不在过滤列表中，则保留
                if not should_exclude:
                    filtered_keys.append(key)
        
        # 只显示 key，每行一个
        self.keys_text.setPlainText('\n'.join(filtered_keys))
        self.update_result_count(len(filtered_keys))
    
    def update_result_count(self, count: int):
        """更新结果统计"""
        total_count = len(self.all_key_values) if self.all_key_values else 0
        filter_text = self.filter_input.toPlainText().strip()
        
        if count > 0:
            if filter_text:
                self.result_count_label.setText(f"(显示 {count}/{total_count} 个)")
            else:
                self.result_count_label.setText(f"(共 {count} 个)")
            self.copy_btn.setEnabled(True)
            self.save_btn.setEnabled(True)
        else:
            if filter_text:
                self.result_count_label.setText(f"(过滤后无结果，共 {total_count} 个)")
            else:
                self.result_count_label.setText("")
            self.copy_btn.setEnabled(False)
            self.save_btn.setEnabled(False)
    
    def update_results(self, keys: list, key_values: dict = None):
        """更新结果显示
        
        Args:
            keys: key 列表（兼容旧接口）
            key_values: key-value 字典（新接口）
        """
        if key_values:
            # 使用新接口：直接传入 key-value 字典
            self.all_key_values = key_values
        elif keys:
            # 兼容旧接口：只有 keys，需要重新获取 values
            # 这里需要从 Worker 获取完整数据，暂时先保存 keys
            # 实际应该在 Worker 中返回完整数据
            self.all_key_values = {key: "" for key in keys}
        
        if self.all_key_values:
            # 应用过滤
            self.on_filter_changed()
        else:
            self.keys_text.clear()
            self.result_count_label.setText("")
            self.copy_btn.setEnabled(False)
            self.save_btn.setEnabled(False)
    
    def clear_results(self):
        """清空结果"""
        self.all_key_values = {}
        self.keys_text.clear()
        self.result_count_label.setText("")
        self.copy_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.filter_input.clear()
