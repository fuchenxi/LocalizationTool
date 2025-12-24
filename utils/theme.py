#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主题管理工具
支持亮色和暗黑模式
"""

import sys
from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QPalette, QColor


def is_dark_mode() -> bool:
    """检测系统是否处于暗黑模式"""
    if sys.platform == 'darwin':  # macOS
        try:
            import subprocess
            result = subprocess.run(
                ['defaults', 'read', '-g', 'AppleInterfaceStyle'],
                capture_output=True,
                text=True,
                timeout=1
            )
            return result.returncode == 0 and 'Dark' in result.stdout
        except:
            # 如果无法检测，默认返回 False
            return False
    elif sys.platform == 'win32':  # Windows
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            )
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return value == 0
        except:
            return False
    else:  # Linux 或其他
        # 尝试从环境变量读取
        import os
        gtk_theme = os.environ.get('GTK_THEME', '').lower()
        return 'dark' in gtk_theme
    
    return False


def get_theme_colors(is_dark: bool = None) -> dict:
    """获取主题颜色
    
    Args:
        is_dark: 是否暗黑模式，None 则自动检测
    
    Returns:
        包含所有主题颜色的字典
    """
    # 强制使用 light 模式
    return {
        # 背景色
        'bg_main': '#F5F5F7',           # 主背景
        'bg_card': '#FFFFFF',           # 卡片背景
        'bg_secondary': '#F0F0F5',      # 次要背景
        'bg_hover': '#E5E5EA',          # Hover 背景
        
        # 文字颜色
        'text_primary': '#1D1D1F',     # 主文字
        'text_secondary': '#666666',   # 次要文字
        'text_tertiary': '#8E8E93',     # 第三级文字
        
        # 边框颜色
        'border': '#E5E5EA',            # 标准边框
        'border_focus': '#007AFF',      # Focus 边框
        
        # 状态颜色
        'success': '#34C759',           # 成功
        'warning': '#FF9500',           # 警告
        'error': '#FF3B30',             # 错误
        
        # 按钮颜色
        'button_bg': '#007AFF',          # 按钮背景
        'button_bg_hover': '#0051D5',   # 按钮 Hover
        'button_bg_pressed': '#003DA5', # 按钮 Pressed
        
        # 表格颜色
        'table_header_bg': '#F5F5F7',   # 表格头部背景
        'table_grid': '#F5F5F7',        # 表格网格线
        'table_selected': '#007AFF',     # 表格选中
        
        # 其他
        'shadow': 'rgba(0, 0, 0, 0.1)', # 阴影
    }
    
    # 以下代码保留，但不会执行
    if is_dark is None:
        is_dark = is_dark_mode()
    
    if is_dark:
        return {
            # 背景色
            'bg_main': '#1C1C1E',           # 主背景
            'bg_card': '#2C2C2E',           # 卡片背景
            'bg_secondary': '#3A3A3C',      # 次要背景
            'bg_hover': '#48484A',          # Hover 背景
            
            # 文字颜色
            'text_primary': '#FFFFFF',      # 主文字
            'text_secondary': '#EBEBF5',    # 次要文字
            'text_tertiary': '#8E8E93',     # 第三级文字
            
            # 边框颜色
            'border': '#38383A',            # 标准边框
            'border_focus': '#007AFF',      # Focus 边框
            
            # 状态颜色
            'success': '#34C759',           # 成功
            'warning': '#FF9500',           # 警告
            'error': '#FF3B30',              # 错误
            
            # 按钮颜色
            'button_bg': '#007AFF',          # 按钮背景
            'button_bg_hover': '#0051D5',   # 按钮 Hover
            'button_bg_pressed': '#003DA5', # 按钮 Pressed
            
            # 表格颜色
            'table_header_bg': '#2C2C2E',    # 表格头部背景
            'table_grid': '#38383A',        # 表格网格线
            'table_selected': '#007AFF',     # 表格选中
            
            # 其他
            'shadow': 'rgba(0, 0, 0, 0.3)', # 阴影
        }
    else:
        return {
            # 背景色
            'bg_main': '#F5F5F7',           # 主背景
            'bg_card': '#FFFFFF',           # 卡片背景
            'bg_secondary': '#F0F0F5',      # 次要背景
            'bg_hover': '#E5E5EA',          # Hover 背景
            
            # 文字颜色
            'text_primary': '#1D1D1F',     # 主文字
            'text_secondary': '#666666',   # 次要文字
            'text_tertiary': '#8E8E93',     # 第三级文字
            
            # 边框颜色
            'border': '#E5E5EA',            # 标准边框
            'border_focus': '#007AFF',      # Focus 边框
            
            # 状态颜色
            'success': '#34C759',           # 成功
            'warning': '#FF9500',           # 警告
            'error': '#FF3B30',             # 错误
            
            # 按钮颜色
            'button_bg': '#007AFF',          # 按钮背景
            'button_bg_hover': '#0051D5',   # 按钮 Hover
            'button_bg_pressed': '#003DA5', # 按钮 Pressed
            
            # 表格颜色
            'table_header_bg': '#F5F5F7',   # 表格头部背景
            'table_grid': '#F5F5F7',        # 表格网格线
            'table_selected': '#007AFF',     # 表格选中
            
            # 其他
            'shadow': 'rgba(0, 0, 0, 0.1)', # 阴影
        }


def get_main_style(is_dark: bool = None) -> str:
    """获取主样式表（支持暗黑模式）"""
    colors = get_theme_colors(is_dark)
    
    return f"""
    QMainWindow {{
        background: {colors['bg_main']};
    }}
    QGroupBox {{
        font-weight: 600;
        font-size: 14px;
        border: 2px solid {colors['border']};
        border-radius: 10px;
        margin-top: 16px;
        padding-top: 16px;
        background: {colors['bg_card']};
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 16px;
        padding: 0 8px;
        color: {colors['text_primary']};
    }}
    QPushButton {{
        padding: 10px 20px;
        border-radius: 8px;
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                    stop:0 {colors['button_bg']}, stop:1 {colors['button_bg_hover']});
        color: white;
        border: none;
        font-size: 14px;
        font-weight: 500;
    }}
    QPushButton:hover {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                    stop:0 {colors['button_bg_hover']}, stop:1 {colors['button_bg_pressed']});
    }}
    QPushButton:pressed {{
        background: {colors['button_bg_pressed']};
    }}
    QPushButton:disabled {{
        background: {colors['bg_secondary']};
        color: {colors['text_tertiary']};
    }}
    QLineEdit {{
        padding: 10px 12px;
        border: 2px solid {colors['border']};
        border-radius: 8px;
        background: {colors['bg_card']};
        color: {colors['text_primary']};
        font-size: 13px;
        selection-background-color: {colors['button_bg']};
        selection-color: white;
    }}
    QLineEdit:focus {{
        border: 2px solid {colors['border_focus']};
    }}
    QTextEdit {{
        border: 2px solid {colors['border']};
        border-radius: 8px;
        background: {colors['bg_card']};
        color: {colors['text_primary']};
        padding: 8px;
        font-size: 13px;
        font-family: 'SF Mono', 'Menlo', monospace;
        selection-background-color: {colors['button_bg']};
        selection-color: white;
    }}
    QTabWidget::pane {{
        border: none;
        background: {colors['bg_card']};
        top: 0px;
    }}
    QTabBar {{
        background: {colors['bg_main']};
        border-right: 1px solid {colors['border']};
        width: 200px;
    }}
    QTabBar::tab {{
        padding: 14px 20px;
        margin-bottom: 2px;
        border-top-left-radius: 0px;
        border-bottom-left-radius: 0px;
        border-top-right-radius: 0px;
        border-bottom-right-radius: 0px;
        background: transparent;
        color: {colors['text_tertiary']};
        font-size: 14px;
        font-weight: 500;
        min-width: 180px;
        max-width: 200px;
        text-align: left;
        border: none;
    }}
    QTabBar::tab:selected {{
        background: {colors['bg_card']};
        color: {colors['button_bg']};
        border-right: 3px solid {colors['button_bg']};
        font-weight: 600;
    }}
    QTabBar::tab:hover:!selected {{
        background: {colors['bg_hover']};
        color: {colors['text_primary']};
    }}
    QTableWidget {{
        border: 2px solid {colors['border']};
        border-radius: 8px;
        background: {colors['bg_card']};
        color: {colors['text_primary']};
        gridline-color: {colors['table_grid']};
        font-size: 13px;
    }}
    QTableWidget::item {{
        padding: 8px;
        color: {colors['text_primary']};
    }}
    QTableWidget::item:selected {{
        background: {colors['table_selected']};
        color: white;
    }}
    QHeaderView::section {{
        background: {colors['table_header_bg']};
        padding: 8px;
        border: none;
        border-bottom: 2px solid {colors['border']};
        font-weight: 600;
        font-size: 13px;
        color: {colors['text_primary']};
    }}
    QLabel {{
        color: {colors['text_primary']};
    }}
    QComboBox {{
        padding: 8px 12px;
        border: 2px solid {colors['border']};
        border-radius: 8px;
        background: {colors['bg_card']};
        color: {colors['text_primary']};
        font-size: 13px;
    }}
    QComboBox:hover {{
        border: 2px solid {colors['border_focus']};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 30px;
    }}
    QComboBox QAbstractItemView {{
        border: 2px solid {colors['border']};
        border-radius: 8px;
        background: {colors['bg_card']};
        color: {colors['text_primary']};
        selection-background-color: {colors['button_bg']};
        selection-color: white;
    }}
    QListWidget {{
        border: 2px solid {colors['border']};
        border-radius: 8px;
        background: {colors['bg_card']};
        color: {colors['text_primary']};
        font-size: 12px;
        padding: 4px;
    }}
    QListWidget::item {{
        padding: 8px;
        border-radius: 4px;
        margin: 2px;
        color: {colors['text_primary']};
    }}
    QListWidget::item:selected {{
        background: {colors['button_bg']};
        color: white;
    }}
    QListWidget::item:hover:!selected {{
        background: {colors['bg_hover']};
    }}
    QCheckBox {{
        color: {colors['text_primary']};
        font-size: 12px;
    }}
    QCheckBox::indicator {{
        width: 22px;
        height: 22px;
        border-radius: 5px;
        border: 2px solid {colors['border']};
        background-color: {colors['bg_card']};
    }}
    QCheckBox::indicator:checked {{
        background-color: {colors['button_bg']};
        border: 2px solid {colors['button_bg']};
    }}
    QCheckBox::indicator:hover {{
        border: 2px solid {colors['border_focus']};
    }}
"""


def get_delete_button_style(is_dark: bool = None) -> str:
    """获取删除按钮样式（支持暗黑模式）"""
    colors = get_theme_colors(is_dark)
    
    return f"""
    QPushButton {{
        font-size: 13px;
        font-weight: 500;
        padding: 10px 20px;
        border-radius: 8px;
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                    stop:0 {colors['error']}, stop:1 #D32F26);
        color: white;
        border: none;
    }}
    QPushButton:hover {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                    stop:0 #D32F26, stop:1 #B71C1C);
    }}
    QPushButton:pressed {{
        background: #B71C1C;
    }}
    QPushButton:disabled {{
        background: {colors['bg_secondary']};
        color: {colors['text_tertiary']};
    }}
"""

