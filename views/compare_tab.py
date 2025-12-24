#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对比多语言标签页
对比不同语言的 key-value，找出缺失的翻译
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QPushButton, QGroupBox, QTextEdit,
    QTableWidget, QTableWidgetItem, QSplitter,
    QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QBrush, QFont
from utils.theme import get_theme_colors


class CompareTab(QWidget):
    """对比多语言标签页"""
    
    def __init__(self):
        super().__init__()
        self.colors = get_theme_colors()
        self.init_ui()
    
    def init_ui(self):
        # 主布局 - 水平分割
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # ============ 左侧：配置区域 ============
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(16)
        
        # 说明文字 - 简化
        desc_label = QLabel(
            "对比不同语言的 key-value，找出缺失的翻译。选择一个基准语言，工具会检查其他语言是否缺少该语言的 key。"
        )
        desc_label.setStyleSheet(
            f"color: {self.colors['text_secondary']}; font-size: 12px; padding: 8px 0;"
        )
        desc_label.setWordWrap(True)
        left_layout.addWidget(desc_label)
        
        # 基准语言选择
        base_lang_group = QGroupBox("基准语言")
        base_lang_layout = QVBoxLayout()
        base_lang_layout.setSpacing(8)
        
        base_lang_hint = QLabel("选择作为对比基准的语言（通常是 en）：")
        base_lang_hint.setStyleSheet(f"color: {self.colors['text_tertiary']}; font-size: 11px;")
        base_lang_layout.addWidget(base_lang_hint)
        
        self.base_lang_combo = QComboBox()
        self.base_lang_combo.setMinimumHeight(28)
        self.base_lang_combo.setStyleSheet(f"""
            QComboBox {{
                padding: 8px 12px;
                border: 2px solid {self.colors['border']};
                border-radius: 8px;
                background: {self.colors['bg_card']};
                color: {self.colors['text_primary']};
                font-size: 13px;
            }}
            QComboBox:hover {{
                border: 2px solid {self.colors['border_focus']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox QAbstractItemView {{
                border: 2px solid {self.colors['border']};
                border-radius: 8px;
                background: {self.colors['bg_card']};
                color: {self.colors['text_primary']};
                selection-background-color: {self.colors['button_bg']};
                selection-color: white;
            }}
        """)
        base_lang_layout.addWidget(self.base_lang_combo)
        
        base_lang_group.setLayout(base_lang_layout)
        left_layout.addWidget(base_lang_group)
        
        # 操作按钮
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(10)
        
        # 对比按钮
        self.compare_btn = QPushButton("🔍 开始对比")
        self.compare_btn.setMinimumHeight(40)
        self.compare_btn.setEnabled(False)
        buttons_layout.addWidget(self.compare_btn)
        
        left_layout.addLayout(buttons_layout)
        
        # 对比日志
        log_group = QGroupBox("对比日志")
        log_layout = QVBoxLayout()
        log_layout.setContentsMargins(8, 8, 8, 8)
        
        self.compare_log_text = QTextEdit()
        self.compare_log_text.setReadOnly(True)
        self.compare_log_text.setPlaceholderText("点击上方按钮开始对比...")
        self.compare_log_text.setStyleSheet("font-size: 11px;")
        log_layout.addWidget(self.compare_log_text)
        
        log_group.setLayout(log_layout)
        left_layout.addWidget(log_group, 1)  # 给日志更多空间
        
        # ============ 右侧：对比结果区域 ============
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)
        
        # 标题和统计信息在一行
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        
        result_label = QLabel("对比结果")
        result_label.setStyleSheet(f"font-size: 14px; font-weight: 600; color: {self.colors['text_primary']};")
        header_layout.addWidget(result_label)
        
        # 统计信息
        self.stats_label = QLabel("尚未对比")
        self.stats_label.setStyleSheet(
            f"font-size: 12px; color: {self.colors['text_secondary']}; padding: 6px 12px; "
            f"background: {self.colors['bg_secondary']}; border-radius: 4px;"
        )
        header_layout.addWidget(self.stats_label)
        header_layout.addStretch()
        
        right_layout.addLayout(header_layout)
        
        # 结果表格
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(3)
        self.result_table.setHorizontalHeaderLabels(["语言", "缺失的 Key", "缺失数量"])
        self.result_table.setAlternatingRowColors(True)
        self.result_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.result_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.result_table.setStyleSheet(f"""
            QTableWidget {{
                font-size: 12px;
                gridline-color: {self.colors['table_grid']};
            }}
            QTableWidget::item {{
                padding: 8px;
                color: {self.colors['text_primary']};
            }}
            QTableWidget::item:selected {{
                background: {self.colors['table_selected']};
                color: white;
            }}
        """)
        
        # 设置列宽
        header = self.result_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        
        self.result_table.setColumnWidth(0, 120)
        self.result_table.setColumnWidth(2, 100)
        
        # 创建一个容器 widget 来包含表格或提示信息
        self.result_container = QWidget()
        self.result_container_layout = QVBoxLayout(self.result_container)
        self.result_container_layout.setContentsMargins(0, 0, 0, 0)
        self.result_container_layout.addWidget(self.result_table)
        
        # 添加提示页（初始显示）
        self.empty_widget = QWidget()
        empty_layout = QVBoxLayout(self.empty_widget)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.empty_label = QLabel("🔍\n\n点击左侧「开始对比」按钮\n查看对比结果")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet(f"color: {self.colors['text_tertiary']}; font-size: 14px; line-height: 24px;")
        empty_layout.addWidget(self.empty_label)
        
        self.result_container_layout.addWidget(self.empty_widget)
        self.result_table.setVisible(False)
        
        right_layout.addWidget(self.result_container)
        
        # 添加到分割器
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        
        # 设置初始分割比例 (30% : 70%)
        splitter.setSizes([300, 700])
        
        main_layout.addWidget(splitter)
    
    def update_languages(self, languages: list):
        """更新语言列表"""
        self.base_lang_combo.clear()
        self.base_lang_combo.addItems(languages)
        
        # 默认选择 en（如果存在）
        if 'en' in languages:
            index = languages.index('en')
            self.base_lang_combo.setCurrentIndex(index)
    
    def update_results(self, missing_keys: dict):
        """更新对比结果显示
        
        Args:
            missing_keys: {lang_code: [key1, key2, ...]}
        """
        if not missing_keys:
            # 无缺失项
            self.result_table.setVisible(False)
            self.empty_widget.setVisible(True)
            self.empty_label.setText("✅\n\n所有语言都完整！\n没有缺失的 key")
            self.empty_label.setStyleSheet(f"color: {self.colors['success']}; font-size: 16px; line-height: 28px;")
            self.stats_label.setText("✅ 所有语言都完整")
            self.stats_label.setStyleSheet(
                f"font-size: 13px; color: {self.colors['success']}; padding: 10px; "
                f"background: {self.colors['bg_secondary']}; border-radius: 6px; font-weight: 500;"
            )
            return
        
        # 有缺失项，显示表格
        self.empty_widget.setVisible(False)
        self.result_table.setVisible(True)
        self.result_table.setRowCount(0)
        
        # 更新统计信息
        total_missing = sum(len(keys) for keys in missing_keys.values())
        lang_count = len(missing_keys)
        self.stats_label.setText(f"⚠️ 发现 {total_missing} 个缺失项 • {lang_count} 个语言文件")
        self.stats_label.setStyleSheet(
            f"font-size: 13px; color: {self.colors['warning']}; padding: 10px; "
            f"background: {self.colors['bg_secondary']}; border-radius: 6px; font-weight: 500;"
        )
        
        # 填充数据
        self.result_table.setRowCount(len(missing_keys))
        
        row = 0
        for lang_code, keys in sorted(missing_keys.items()):
            # 语言代码
            lang_item = QTableWidgetItem(lang_code)
            lang_item.setFont(QFont("", -1, QFont.Weight.Bold))
            self.result_table.setItem(row, 0, lang_item)
            
            # 缺失的 Key（用逗号分隔）
            keys_text = ", ".join(keys)
            keys_item = QTableWidgetItem(keys_text)
            keys_item.setToolTip(keys_text)  # 鼠标悬停显示完整内容
            self.result_table.setItem(row, 1, keys_item)
            
            # 缺失数量
            count_item = QTableWidgetItem(str(len(keys)))
            count_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            count_item.setForeground(QBrush(QColor(self.colors['error'])))
            font = QFont()
            font.setBold(True)
            count_item.setFont(font)
            self.result_table.setItem(row, 2, count_item)
            
            row += 1
        
        # 设置行高
        for i in range(len(missing_keys)):
            self.result_table.setRowHeight(i, 40)

