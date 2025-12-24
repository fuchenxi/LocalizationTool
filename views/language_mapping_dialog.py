#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语言映射对话框
用于配置 ZIP 文件中的语言代码与项目语言代码的映射关系
"""

import os
import zipfile
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QTableWidget, QTableWidgetItem, QComboBox,
    QPushButton, QCheckBox, QHeaderView, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from utils.theme import get_theme_colors
from utils.config import ConfigManager
from PyQt6.QtGui import QColor, QFont

# 常见语言代码别名映射
LANGUAGE_ALIASES = {
    # 下划线格式 → 标准格式
    'pt_br': 'pt-BR',
    'pt_pt': 'pt-PT',
    'zh_cn': 'zh-Hans',
    'zh_tw': 'zh-Hant',
    'zh_hk': 'zh-Hant-HK',
    'es_mx': 'es-MX',
    'es_es': 'es-ES',
    'en_us': 'en',
    'en_gb': 'en-GB',
    'fr_fr': 'fr',
    'fr_ca': 'fr-CA',
    'de_de': 'de',
    'ja_jp': 'ja',
    'ko_kr': 'ko',
    
    # 其他常见别名
    'zh': 'zh-Hans',
    'iw': 'he',  # Hebrew
    'in': 'id',  # Indonesian
    'tl': 'fil', # Filipino
}


class LanguageMappingDialog(QDialog):
    """语言映射对话框"""
    
    def __init__(self, zip_path: str, project_languages: dict, parent=None):
        """
        初始化对话框
        
        Args:
            zip_path: ZIP 文件路径
            project_languages: 项目中的语言 {lang_code: lproj_path}
            parent: 父窗口
        """
        super().__init__(parent)
        self.zip_path = zip_path
        self.project_languages = project_languages
        self.colors = get_theme_colors()
        self.mappings = {}  # {zip_lang: project_lang}
        
        # 解析 ZIP 获取语言列表
        self.zip_languages = self.parse_zip_languages()
        
        # 加载已保存的映射配置
        self.saved_mappings = ConfigManager.get_language_mappings()
        
        self.init_ui()
        self.apply_smart_matching()
    
    def parse_zip_languages(self) -> list:
        """解析 ZIP 文件中的语言列表"""
        languages = []
        try:
            with zipfile.ZipFile(self.zip_path, 'r') as zf:
                for name in zf.namelist():
                    if name.endswith('.strings'):
                        # 提取语言代码（去掉路径和扩展名）
                        basename = os.path.basename(name)
                        lang_code = os.path.splitext(basename)[0]
                        if lang_code and lang_code not in languages:
                            languages.append(lang_code)
        except Exception as e:
            print(f"解析 ZIP 失败: {e}")
        return sorted(languages)
    
    def init_ui(self):
        """初始化 UI"""
        self.setWindowTitle("语言映射确认")
        self.setMinimumWidth(680)
        self.setMinimumHeight(480)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # 标题区域
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(4)
        
        title_label = QLabel("语言映射确认")
        title_label.setStyleSheet(f"""
            font-size: 22px;
            font-weight: 600;
            color: {self.colors['text_primary']};
            padding: 0;
            letter-spacing: -0.3px;
        """)
        title_layout.addWidget(title_label)
        
        subtitle_label = QLabel(f"检测到 ZIP 中包含 {len(self.zip_languages)} 个语言文件，请确认映射关系")
        subtitle_label.setStyleSheet(f"""
            font-size: 13px;
            color: {self.colors['text_secondary']};
            padding: 0;
        """)
        title_layout.addWidget(subtitle_label)
        
        layout.addWidget(title_container)
        
        # 映射表格
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ZIP 语言", "项目语言", "状态"])
        self.table.setRowCount(len(self.zip_languages))
        
        # 设置表头样式
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 140)
        self.table.setColumnWidth(2, 110)
        
        # 设置表格样式（苹果风格）
        self.table.setStyleSheet(f"""
            QTableWidget {{
                border: none;
                border-radius: 12px;
                background: {self.colors['bg_card']};
                gridline-color: transparent;
                selection-background-color: transparent;
                outline: none;
            }}
            QTableWidget::item {{
                padding: 0px;
                border: none;
                background: transparent;
            }}
            QTableWidget::item:selected {{
                background: transparent;
            }}
            QHeaderView::section {{
                background: transparent;
                color: {self.colors['text_secondary']};
                padding: 10px 16px;
                border: none;
                border-bottom: 1px solid {self.colors['border']};
                font-weight: 600;
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            QComboBox {{
                padding: 10px 14px;
                padding-right: 36px;
                border: 1.5px solid {self.colors['border']};
                border-radius: 10px;
                background: {self.colors['bg_card']};
                color: {self.colors['text_primary']};
                font-size: 15px;
                font-weight: 400;
                min-height: 36px;
                max-height: 36px;
            }}
            QComboBox:hover {{
                border: 1.5px solid {self.colors['border_focus']};
                background: {self.colors['bg_secondary']};
            }}
            QComboBox:focus {{
                border: 1.5px solid {self.colors['button_bg']};
                background: {self.colors['bg_card']};
                outline: none;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 36px;
                background: transparent;
                border-left: 1px solid {self.colors['border']};
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid {self.colors['text_secondary']};
                width: 0;
                height: 0;
                margin-right: 12px;
            }}
            QComboBox QAbstractItemView {{
                border: 1px solid {self.colors['border']};
                border-radius: 10px;
                background: {self.colors['bg_card']};
                color: {self.colors['text_primary']};
                selection-background-color: {self.colors['button_bg']};
                selection-color: white;
                padding: 6px;
                outline: none;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 10px 14px;
                border-radius: 6px;
                min-height: 20px;
                font-size: 15px;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background: {self.colors['bg_hover']};
            }}
            QComboBox QAbstractItemView::item:selected {{
                background: {self.colors['button_bg']};
                color: white;
            }}
        """)
        
        # 设置行高
        self.table.verticalHeader().setDefaultSectionSize(60)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)  # 禁用选择
        
        # 项目语言列表（用于下拉框）
        project_lang_list = ["(跳过)"] + sorted(self.project_languages.keys())
        
        # 填充表格
        self.combo_boxes = []
        self.status_labels = []  # 用于存储状态标签
        
        for row, zip_lang in enumerate(self.zip_languages):
            # ZIP 语言（只读标签，使用 QLabel）
            zip_label = QLabel(zip_lang)
            zip_label.setStyleSheet(f"""
                QLabel {{
                    padding: 10px 16px;
                    color: {self.colors['text_primary']};
                    font-size: 15px;
                    font-weight: 500;
                    font-family: 'SF Mono', 'Menlo', 'Monaco', monospace;
                    background: transparent;
                    border: none;
                }}
            """)
            zip_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.table.setCellWidget(row, 0, zip_label)
            
            # 项目语言（下拉框）
            combo = QComboBox()
            combo.addItems(project_lang_list)
            combo.currentTextChanged.connect(lambda text, r=row: self.on_mapping_changed(r))
            self.combo_boxes.append(combo)
            self.table.setCellWidget(row, 1, combo)
            
            # 状态（使用 QLabel 显示徽章样式）
            status_label = QLabel("")
            status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.status_labels.append(status_label)
            self.table.setCellWidget(row, 2, status_label)
        
        layout.addWidget(self.table, 1)
        
        # 记住映射复选框
        self.remember_checkbox = QCheckBox("记住这些映射规则（下次自动应用）")
        self.remember_checkbox.setChecked(True)
        self.remember_checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {self.colors['text_secondary']};
                font-size: 13px;
                spacing: 10px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid {self.colors['border']};
                background: {self.colors['bg_card']};
            }}
            QCheckBox::indicator:checked {{
                background: {self.colors['button_bg']};
                border: 2px solid {self.colors['button_bg']};
            }}
            QCheckBox::indicator:hover {{
                border: 2px solid {self.colors['border_focus']};
            }}
        """)
        layout.addWidget(self.remember_checkbox)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setFixedSize(88, 36)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {self.colors['button_bg']};
                border: none;
                border-radius: 8px;
                font-weight: 500;
                font-size: 15px;
            }}
            QPushButton:hover {{
                background: {self.colors['bg_hover']};
            }}
            QPushButton:pressed {{
                background: {self.colors['bg_secondary']};
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        button_layout.addSpacing(8)
        
        confirm_btn = QPushButton("确认导入")
        confirm_btn.setFixedSize(100, 36)
        confirm_btn.setStyleSheet(f"""
            QPushButton {{
                background: {self.colors['button_bg']};
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 15px;
            }}
            QPushButton:hover {{
                background: {self.colors['button_bg_hover']};
            }}
            QPushButton:pressed {{
                background: {self.colors['button_bg_pressed']};
            }}
        """)
        confirm_btn.clicked.connect(self.on_confirm)
        button_layout.addWidget(confirm_btn)
        
        layout.addLayout(button_layout)

    def update_status(self, row: int):
        """更新状态列（使用徽章样式）"""
        combo = self.combo_boxes[row]
        status_label = self.status_labels[row]
        selected = combo.currentText()
        
        if selected == "(跳过)":
            status_label.setText("跳过")
            status_label.setStyleSheet(f"""
                QLabel {{
                    padding: 4px 12px;
                    background: {self.colors['bg_secondary']};
                    color: {self.colors['text_secondary']};
                    border-radius: 12px;
                    font-size: 12px;
                    font-weight: 500;
                }}
            """)
        elif selected:
            # 检查是否是自动匹配还是手动选择
            zip_lang = self.zip_languages[row]
            auto_match = self.find_best_match(zip_lang)
            if auto_match == selected:
                status_label.setText("自动匹配")
                status_label.setStyleSheet(f"""
                    QLabel {{
                        padding: 4px 12px;
                        background: #E8F5E9;
                        color: #2E7D32;
                        border-radius: 12px;
                        font-size: 12px;
                        font-weight: 500;
                    }}
                """)
            else:
                status_label.setText("手动选择")
                status_label.setStyleSheet(f"""
                    QLabel {{
                        padding: 4px 12px;
                        background: #FFF3E0;
                        color: #E65100;
                        border-radius: 12px;
                        font-size: 12px;
                        font-weight: 500;
                    }}
                """)
        else:
            status_label.setText("未配置")
            status_label.setStyleSheet(f"""
                QLabel {{
                    padding: 4px 12px;
                    background: #FFEBEE;
                    color: #C62828;
                    border-radius: 12px;
                    font-size: 12px;
                    font-weight: 500;
                }}
            """)

    def apply_smart_matching(self):
        """应用智能匹配"""
        for row, zip_lang in enumerate(self.zip_languages):
            combo = self.combo_boxes[row]
            matched_lang = self.find_best_match(zip_lang)
            
            if matched_lang:
                # 找到匹配，设置下拉框
                index = combo.findText(matched_lang)
                if index >= 0:
                    combo.setCurrentIndex(index)
            
            self.update_status(row)
    
    def find_best_match(self, zip_lang: str) -> str:
        """
        找到最佳匹配的项目语言
        
        匹配策略（按优先级）：
        1. 已保存的用户映射
        2. 精确匹配
        3. 内置别名映射
        4. 规范化匹配（忽略大小写和分隔符）
        5. 前缀匹配
        """
        project_langs = list(self.project_languages.keys())
        zip_lang_lower = zip_lang.lower()
        
        # 1. 已保存的用户映射
        if zip_lang in self.saved_mappings:
            saved = self.saved_mappings[zip_lang]
            if saved in project_langs:
                return saved
        
        # 2. 精确匹配
        if zip_lang in project_langs:
            return zip_lang
        
        # 3. 内置别名映射
        if zip_lang_lower in LANGUAGE_ALIASES:
            alias = LANGUAGE_ALIASES[zip_lang_lower]
            if alias in project_langs:
                return alias
        
        # 4. 规范化匹配（下划线转连字符，大小写规范化）
        normalized = zip_lang.replace('_', '-')
        for proj_lang in project_langs:
            if normalized.lower() == proj_lang.lower():
                return proj_lang
        
        # 尝试常见的大小写变体
        # pt_br -> pt-BR
        parts = zip_lang.replace('-', '_').split('_')
        if len(parts) == 2:
            variant = f"{parts[0].lower()}-{parts[1].upper()}"
            if variant in project_langs:
                return variant
        
        # 5. 前缀匹配（如 pt_br 匹配 pt）
        base_lang = zip_lang.split('_')[0].split('-')[0].lower()
        for proj_lang in project_langs:
            if proj_lang.lower() == base_lang:
                return proj_lang
        
        return None
    
    def on_mapping_changed(self, row: int):
        """映射改变时更新状态"""
        self.update_status(row)
    
    def update_status(self, row: int):
        """更新状态列（使用徽章样式）"""
        combo = self.combo_boxes[row]
        status_label = self.status_labels[row]  # 使用 status_labels 而不是 table.item
        selected = combo.currentText()
        
        if selected == "(跳过)":
            status_label.setText("跳过")
            status_label.setStyleSheet(f"""
                QLabel {{
                    padding: 4px 12px;
                    background: {self.colors['bg_secondary']};
                    color: {self.colors['text_secondary']};
                    border-radius: 12px;
                    font-size: 12px;
                    font-weight: 500;
                }}
            """)
        elif selected:
            # 检查是否是自动匹配还是手动选择
            zip_lang = self.zip_languages[row]
            auto_match = self.find_best_match(zip_lang)
            if auto_match == selected:
                status_label.setText("自动匹配")
                status_label.setStyleSheet(f"""
                    QLabel {{
                        padding: 4px 12px;
                        background: #E8F5E9;
                        color: #2E7D32;
                        border-radius: 12px;
                        font-size: 12px;
                        font-weight: 500;
                    }}
                """)
            else:
                status_label.setText("手动选择")
                status_label.setStyleSheet(f"""
                    QLabel {{
                        padding: 4px 12px;
                        background: #FFF3E0;
                        color: #E65100;
                        border-radius: 12px;
                        font-size: 12px;
                        font-weight: 500;
                    }}
                """)
        else:
            status_label.setText("未配置")
            status_label.setStyleSheet(f"""
                QLabel {{
                    padding: 4px 12px;
                    background: #FFEBEE;
                    color: #C62828;
                    border-radius: 12px;
                    font-size: 12px;
                    font-weight: 500;
                }}
            """)
    
    def on_confirm(self):
        """确认导入"""
        # 收集映射关系
        self.mappings = {}
        for row, zip_lang in enumerate(self.zip_languages):
            combo = self.combo_boxes[row]
            project_lang = combo.currentText()
            if project_lang and project_lang != "(跳过)":
                self.mappings[zip_lang] = project_lang
        
        # 保存映射配置
        if self.remember_checkbox.isChecked():
            ConfigManager.save_language_mappings(self.mappings)
        
        self.accept()
    
    def get_mappings(self) -> dict:
        """获取映射关系"""
        return self.mappings

