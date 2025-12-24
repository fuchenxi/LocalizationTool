#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字符串替换标签页
将代码中硬编码的字符串替换为多语言 Key
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTextEdit, QPushButton, QGroupBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QCheckBox, QSplitter
)
from PyQt6.QtCore import Qt
from utils.theme import get_theme_colors


class ReplaceTab(QWidget):
    """字符串替换标签页"""
    
    def __init__(self):
        super().__init__()
        self.colors = get_theme_colors()
        self.init_ui()
    
    def init_ui(self):
        # 主布局 - 垂直
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)
        
        # 说明文字 - 简化
        desc_label = QLabel(
            "粘贴多语言 Key 列表，工具会在 Localized() 等函数调用中查找使用了 Value 的地方，并替换为 Key。"
            "例如: Localized(@\"取消\") → Localized(@\"action_cancel\")"
        )
        desc_label.setStyleSheet(
            f"color: {self.colors['text_secondary']}; font-size: 12px; padding: 8px 0;"
        )
        desc_label.setWordWrap(True)
        main_layout.addWidget(desc_label)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧：输入和配置
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(12)
        
        # Key 列表输入
        input_group = QGroupBox("Key 列表")
        input_layout = QVBoxLayout()
        input_layout.setSpacing(8)
        
        input_hint = QLabel("粘贴需要处理的 Key（每行一个）：")
        input_hint.setStyleSheet(f"color: {self.colors['text_tertiary']}; font-size: 11px;")
        input_layout.addWidget(input_hint)
        
        self.key_input = QTextEdit()
        self.key_input.setPlaceholderText(
            "例如：\n"
            "action_cancel\n"
            "action_ok\n"
            "welcome_text\n"
            "..."
        )
        self.key_input.setMinimumHeight(150)
        self.key_input.setStyleSheet("font-family: 'SF Mono', 'Menlo', monospace; font-size: 12px;")
        input_layout.addWidget(self.key_input)
        
        input_group.setLayout(input_layout)
        left_layout.addWidget(input_group)
        
        # 配置选项
        config_group = QGroupBox("扫描配置")
        config_layout = QVBoxLayout()
        config_layout.setSpacing(10)
        
        self.scan_oc_checkbox = QCheckBox("扫描 Objective-C 文件 (.m, .mm)")
        self.scan_oc_checkbox.setChecked(True)
        self.scan_oc_checkbox.setStyleSheet("font-size: 12px;")
        config_layout.addWidget(self.scan_oc_checkbox)
        
        self.scan_swift_checkbox = QCheckBox("扫描 Swift 文件 (.swift)")
        self.scan_swift_checkbox.setChecked(True)
        self.scan_swift_checkbox.setStyleSheet("font-size: 12px;")
        config_layout.addWidget(self.scan_swift_checkbox)
        
        self.case_sensitive_checkbox = QCheckBox("区分大小写")
        self.case_sensitive_checkbox.setChecked(False)  # 默认不区分
        self.case_sensitive_checkbox.setStyleSheet(f"font-size: 12px; color: {self.colors['warning']};")
        config_layout.addWidget(self.case_sensitive_checkbox)
        
        config_group.setLayout(config_layout)
        left_layout.addWidget(config_group)
        
        # 大小写不匹配的 Key
        mismatch_group = QGroupBox("大小写不匹配的 Key")
        mismatch_layout = QVBoxLayout()
        mismatch_layout.setSpacing(8)
        
        mismatch_hint = QLabel("以下 Key 在多语言文件中找不到（可能是大小写问题）：")
        mismatch_hint.setStyleSheet(f"color: {self.colors['text_tertiary']}; font-size: 11px;")
        mismatch_layout.addWidget(mismatch_hint)
        
        self.mismatch_text = QTextEdit()
        self.mismatch_text.setReadOnly(True)
        self.mismatch_text.setMaximumHeight(100)
        self.mismatch_text.setPlaceholderText("扫描后显示...")
        self.mismatch_text.setStyleSheet("font-family: 'SF Mono', 'Menlo', monospace; font-size: 11px;")
        mismatch_layout.addWidget(self.mismatch_text)
        
        mismatch_group.setLayout(mismatch_layout)
        left_layout.addWidget(mismatch_group)
        
        # 操作按钮
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(10)
        
        self.scan_btn = QPushButton("🔍 开始扫描")
        self.scan_btn.setMinimumHeight(40)
        self.scan_btn.setEnabled(False)
        buttons_layout.addWidget(self.scan_btn)
        
        self.replace_btn = QPushButton("🔄 确认替换")
        self.replace_btn.setMinimumHeight(40)
        self.replace_btn.setStyleSheet("""
            QPushButton {
                font-size: 13px;
                font-weight: 500;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #FF9500, stop:1 #E68000);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #E68000, stop:1 #CC7000);
            }
            QPushButton:disabled {
                background: #E5E5EA;
                color: #8E8E93;
            }
        """)
        self.replace_btn.setEnabled(False)
        self.replace_btn.setVisible(False)
        buttons_layout.addWidget(self.replace_btn)
        
        left_layout.addLayout(buttons_layout)
        left_layout.addStretch()
        
        # 右侧：扫描结果
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)
        
        # 标题
        result_header = QHBoxLayout()
        result_label = QLabel("扫描结果")
        result_label.setStyleSheet(f"font-size: 14px; font-weight: 600; color: {self.colors['text_primary']};")
        result_header.addWidget(result_label)
        
        self.result_stats = QLabel("尚未扫描")
        self.result_stats.setStyleSheet(
            f"font-size: 12px; color: {self.colors['text_secondary']}; padding: 6px 12px; "
            f"background: {self.colors['bg_secondary']}; border-radius: 4px;"
        )
        result_header.addWidget(self.result_stats)
        result_header.addStretch()
        
        right_layout.addLayout(result_header)
        
        # 结果表格
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(4)
        self.result_table.setHorizontalHeaderLabels(["文件", "行号", "原字符串", "替换为"])
        
        self.result_table.setStyleSheet(f"""
            QTableWidget {{
                font-size: 12px;
                gridline-color: {self.colors['table_grid']};
            }}
            QTableWidget::item {{
                padding: 6px;
                color: {self.colors['text_primary']};
            }}
        """)
        
        # 设置列宽
        header = self.result_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        
        self.result_table.setColumnWidth(0, 200)
        self.result_table.setColumnWidth(3, 150)
        
        right_layout.addWidget(self.result_table)
        
        # 添加到分割器
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([350, 650])
        
        main_layout.addWidget(splitter)
    
    def update_results(self, results: list):
        """更新扫描结果
        
        Args:
            results: [{'file': path, 'line': num, 'original': str, 'key': str}, ...]
        """
        from PyQt6.QtGui import QColor, QBrush
        
        self.result_table.setRowCount(0)
        
        if not results:
            self.result_stats.setText("✅ 未发现需要替换的硬编码字符串")
            self.result_stats.setStyleSheet(
                f"font-size: 12px; color: {self.colors['success']}; padding: 6px 12px; "
                f"background: {self.colors['bg_secondary']}; border-radius: 4px; font-weight: 500;"
            )
            self.replace_btn.setVisible(False)
            return
        
        # 显示统计
        self.result_stats.setText(f"⚠️ 发现 {len(results)} 处需要替换")
        self.result_stats.setStyleSheet(
            f"font-size: 12px; color: {self.colors['warning']}; padding: 6px 12px; "
            f"background: {self.colors['bg_secondary']}; border-radius: 4px; font-weight: 500;"
        )
        
        # 填充表格
        self.result_table.setRowCount(len(results))
        
        for row, item in enumerate(results):
            # 文件名（相对路径）
            file_item = QTableWidgetItem(item.get('file', ''))
            file_item.setToolTip(item.get('full_path', ''))
            self.result_table.setItem(row, 0, file_item)
            
            # 行号
            line_item = QTableWidgetItem(str(item.get('line', '')))
            line_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.result_table.setItem(row, 1, line_item)
            
            # 原字符串（橙色背景）
            original_item = QTableWidgetItem(item.get('original', ''))
            original_item.setBackground(QBrush(QColor("#FFF3E0")))
            original_item.setForeground(QBrush(QColor("#E65100")))
            self.result_table.setItem(row, 2, original_item)
            
            # 替换为（绿色背景）
            key_item = QTableWidgetItem(item.get('key', ''))
            key_item.setBackground(QBrush(QColor("#E8F5E9")))
            key_item.setForeground(QBrush(QColor("#2E7D32")))
            self.result_table.setItem(row, 3, key_item)
        
        # 显示替换按钮
        self.replace_btn.setVisible(True)
        self.replace_btn.setEnabled(True)

