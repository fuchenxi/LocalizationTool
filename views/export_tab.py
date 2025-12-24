#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导出多语言标签页
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QGroupBox, QCheckBox, QPushButton, QTextEdit
)
from utils.theme import get_theme_colors


class ExportTab(QWidget):
    """导出多语言标签页"""
    
    def __init__(self):
        super().__init__()
        self.colors = get_theme_colors()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # 说明文字 - 简化为一句话
        desc_label = QLabel("导出指定的多语言 key，支持导出为 .strings 或 .xml 格式")
        desc_label.setStyleSheet(
            f"color: {self.colors['text_secondary']}; font-size: 12px; padding: 4px 0;"
        )
        layout.addWidget(desc_label)
        
        # Key 列表输入 - 新增
        key_list_container = QWidget()
        key_list_container.setStyleSheet(f"""
            QWidget {{
                background: {self.colors['bg_card']};
                border-radius: 8px;
            }}
        """)
        key_list_layout = QVBoxLayout(key_list_container)
        key_list_layout.setContentsMargins(16, 12, 16, 12)
        key_list_layout.setSpacing(8)
        
        key_list_title = QLabel("Key 列表")
        key_list_title.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {self.colors['text_primary']};")
        key_list_layout.addWidget(key_list_title)
        
        key_list_hint = QLabel("输入要导出的 key（每行一个），将按照此顺序导出：")
        key_list_hint.setStyleSheet(f"color: {self.colors['text_tertiary']}; font-size: 11px;")
        key_list_layout.addWidget(key_list_hint)
        
        self.key_list_input = QTextEdit()
        self.key_list_input.setPlaceholderText(
            "例如：\n"
            "key1\n"
            "key2\n"
            "key3\n"
            "..."
        )
        self.key_list_input.setMinimumHeight(150)
        self.key_list_input.setStyleSheet(f"""
            QTextEdit {{
                font-family: 'SF Mono', 'Menlo', monospace;
                font-size: 12px;
            }}
        """)
        key_list_layout.addWidget(self.key_list_input)
        
        layout.addWidget(key_list_container)
        
        # 导出格式选择 - 卡片式设计
        format_group = QGroupBox("导出格式")
        format_layout = QVBoxLayout()
        format_layout.setSpacing(12)
        
        format_hint = QLabel("选择要导出的格式（可多选）：")
        format_hint.setStyleSheet(f"color: {self.colors['text_tertiary']}; font-size: 11px;")
        format_layout.addWidget(format_hint)
        
        # 复选框 - 横向排列，使用统一样式
        checkbox_layout = QHBoxLayout()
        checkbox_layout.setSpacing(24)
        
        self.strings_checkbox = QCheckBox("导出为 .strings")
        self.strings_checkbox.setChecked(True)
        checkbox_layout.addWidget(self.strings_checkbox)
        
        self.xml_checkbox = QCheckBox("导出为 .xml")
        self.xml_checkbox.setChecked(True)
        checkbox_layout.addWidget(self.xml_checkbox)
        
        checkbox_layout.addStretch()
        format_layout.addLayout(checkbox_layout)
        
        format_group.setLayout(format_layout)
        layout.addWidget(format_group)
        
        # 导出按钮 - 更大更突出
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.export_btn = QPushButton("📤 开始导出")
        self.export_btn.setMinimumHeight(40)
        self.export_btn.setMinimumWidth(200)
        self.export_btn.setEnabled(False)
        button_layout.addWidget(self.export_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # 导出日志
        log_group = QGroupBox("导出日志")
        log_layout = QVBoxLayout()
        log_layout.setContentsMargins(0, 0, 0, 0)
        
        self.export_log_text = QTextEdit()
        self.export_log_text.setReadOnly(True)
        self.export_log_text.setMinimumHeight(250)
        self.export_log_text.setStyleSheet("""
            QTextEdit {
                font-family: 'SF Mono', Menlo, Monaco, 'Courier New', monospace;
                font-size: 11px;
                padding: 8px;
            }
        """)
        log_layout.addWidget(self.export_log_text)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group, 1)
    
    def get_key_list(self) -> list:
        """获取用户输入的 key 列表"""
        text = self.key_list_input.toPlainText().strip()
        if not text:
            return []
        # 按行分割，去除空行和空白
        keys = [line.strip() for line in text.split('\n') if line.strip()]
        return keys

