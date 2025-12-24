#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目信息标签页
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from utils.theme import get_theme_colors


class InfoTab(QWidget):
    """项目信息标签页"""
    
    def __init__(self):
        super().__init__()
        self.colors = get_theme_colors()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 应用信息展示
        info_layout = QHBoxLayout()
        info_layout.setSpacing(40)
        
        # 左侧：图标
        icon_layout = QVBoxLayout()
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(100, 100)
        self.icon_label.setScaledContents(False)  # 改为 False，保持宽高比
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet(
            f"border: 2px solid {self.colors['border']}; "
            f"background: {self.colors['bg_main']}; "
            "border-radius: 20px;"  # 更圆润的圆角
        )
        icon_layout.addWidget(self.icon_label)
        icon_layout.addStretch()
        info_layout.addLayout(icon_layout)
        
        # 右侧：详细信息
        details_layout = QVBoxLayout()
        details_layout.setSpacing(12)
        
        self.app_name_label = QLabel("App 名称: -")
        self.app_name_label.setStyleSheet(f"font-size: 15px; font-weight: 600; color: {self.colors['text_primary']};")
        
        self.version_label = QLabel("版本号: -")
        self.version_label.setStyleSheet(f"font-size: 14px; font-weight: 500; color: {self.colors['text_primary']};")
        
        self.bundle_id_label = QLabel("Bundle ID: -")
        self.bundle_id_label.setStyleSheet(f"font-size: 13px; font-weight: 400; color: {self.colors['text_tertiary']};")
        self.bundle_id_label.setWordWrap(True)
        
        details_layout.addWidget(self.app_name_label)
        details_layout.addWidget(self.version_label)
        details_layout.addWidget(self.bundle_id_label)
        details_layout.addStretch()
        
        info_layout.addLayout(details_layout, 1)
        
        layout.addLayout(info_layout)
        layout.addStretch()

