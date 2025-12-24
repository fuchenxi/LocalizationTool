#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
常量定义
"""

import os
from .theme import get_main_style, get_delete_button_style, get_theme_colors, is_dark_mode

# 默认忽略的文件夹
DEFAULT_IGNORE_FOLDERS = ['Pods', 'DerivedData', 'build', 'Build', '.git', 'Carthage']

# 默认导出路径
DEFAULT_EXPORT_PATH = os.path.expanduser("~/Desktop")

# 进度报告频率（每处理 N 个文件报告一次）
PROGRESS_REPORT_INTERVAL = 10

# 获取主题颜色
THEME_COLORS = get_theme_colors()
IS_DARK_MODE = is_dark_mode()

# 现代化样式表（自动适配暗黑模式）
MAIN_STYLE = get_main_style()

DELETE_BUTTON_STYLE = get_delete_button_style()

LARGE_BUTTON_STYLE = """
    QPushButton {
        font-size: 13px;
        font-weight: 500;
    }
"""
