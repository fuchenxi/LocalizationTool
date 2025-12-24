#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
常量定义
"""

from .theme import get_main_style, get_delete_button_style, get_theme_colors, is_dark_mode

# 默认忽略的文件夹
DEFAULT_IGNORE_FOLDERS = ['Pods', 'DerivedData', 'build', 'Build', '.git', 'Carthage']

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
