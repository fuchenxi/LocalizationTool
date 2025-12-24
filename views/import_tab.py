#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导入多语言标签页 - 重新设计版
"""

import os
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QListWidget,
    QListWidgetItem, QSizePolicy
)
from PyQt6.QtCore import Qt

from utils.constants import LARGE_BUTTON_STYLE
from utils.config import ConfigManager
from utils.theme import get_theme_colors


class ImportTab(QWidget):
    """导入多语言标签页"""
    
    def __init__(self):
        super().__init__()
        # 从配置中加载上次的文件夹路径
        self.current_folder = ConfigManager.get_last_import_folder()
        self.colors = get_theme_colors()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 说明文字 - 更简洁
        desc_label = QLabel("选择 ZIP 文件，自动解压并导入到项目")
        desc_label.setStyleSheet(
            f"color: {self.colors['text_secondary']}; font-size: 12px; padding: 4px 0;"
        )
        layout.addWidget(desc_label)
        
        # 文件夹路径选择 - 去掉GroupBox，使用更简洁的设计
        folder_container = QWidget()
        folder_container.setStyleSheet(f"""
            QWidget {{
                background: {self.colors['bg_card']};
                border-radius: 8px;
            }}
        """)
        folder_layout = QVBoxLayout(folder_container)
        folder_layout.setContentsMargins(16, 12, 16, 12)
        folder_layout.setSpacing(10)  # 稍微增加间距
        # 确保容器有最小高度和宽度，防止压缩
        folder_container.setMinimumHeight(90)
        folder_container.setMinimumWidth(400)  # 确保有足够宽度显示按钮
        folder_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)  # 水平扩展，垂直固定
        
        # 标题
        folder_title = QLabel("选择文件夹")
        folder_title.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {self.colors['text_primary']};")
        folder_layout.addWidget(folder_title)
        
        # 路径输入和按钮 - 固定高度，防止压缩
        folder_select_layout = QHBoxLayout()
        folder_select_layout.setSpacing(8)
        folder_select_layout.setContentsMargins(0, 0, 0, 0)  # 确保没有额外边距
        
        self.folder_input = QLineEdit()
        self.folder_input.setText(self.current_folder)
        self.folder_input.setReadOnly(True)
        self.folder_input.setFixedHeight(36)  # 固定高度，确保文字不被压缩
        self.folder_input.setMinimumWidth(200)  # 设置最小宽度，防止过度压缩
        self.folder_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)  # 水平扩展，垂直固定
        # 确保输入框文字不被压缩，有足够的内边距
        self.folder_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
            }
        """)
        folder_select_layout.addWidget(self.folder_input, 1)  # 给输入框更多空间，但允许压缩
        
        self.change_folder_btn = QPushButton("更改")
        self.change_folder_btn.setFixedSize(70, 36)  # 固定尺寸，绝对不压缩
        self.change_folder_btn.setEnabled(False)
        self.change_folder_btn.setVisible(True)  # 确保始终可见
        self.change_folder_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)  # 完全固定尺寸
        # 确保按钮即使disabled也清晰可见 - 使用明确的背景色和文字色
        self.change_folder_btn.setStyleSheet(f"""
            QPushButton {{
                background: {self.colors['button_bg']};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:disabled {{
                background: {self.colors['bg_secondary']};
                color: {self.colors['text_primary']};
                border: 1px solid {self.colors['border']};
            }}
            QPushButton:hover:!disabled {{
                background: {self.colors['button_bg_hover']};
            }}
        """)
        folder_select_layout.addWidget(self.change_folder_btn, 0)  # 固定宽度，不扩展，不压缩
        
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.setFixedSize(70, 36)  # 固定尺寸，绝对不压缩
        self.refresh_btn.setEnabled(False)
        self.refresh_btn.setVisible(True)  # 确保始终可见
        self.refresh_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)  # 完全固定尺寸
        # 确保按钮即使disabled也清晰可见 - 使用明确的背景色和文字色
        self.refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background: {self.colors['button_bg']};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:disabled {{
                background: {self.colors['bg_secondary']};
                color: {self.colors['text_primary']};
                border: 1px solid {self.colors['border']};
            }}
            QPushButton:hover:!disabled {{
                background: {self.colors['button_bg_hover']};
            }}
        """)
        folder_select_layout.addWidget(self.refresh_btn, 0)  # 固定宽度，不扩展，不压缩
        
        folder_layout.addLayout(folder_select_layout)
        layout.addWidget(folder_container)
        
        # ZIP 文件列表 - 去掉GroupBox，使用更简洁的设计
        list_container = QWidget()
        list_container.setStyleSheet(f"""
            QWidget {{
                background: {self.colors['bg_card']};
                border-radius: 8px;
            }}
        """)
        list_layout = QVBoxLayout(list_container)
        list_layout.setContentsMargins(16, 12, 16, 12)
        list_layout.setSpacing(8)
        
        # 标题行：标题 + 文件数量
        list_header_layout = QHBoxLayout()
        list_header_layout.setSpacing(8)
        
        list_title = QLabel("ZIP 文件列表")
        list_title.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {self.colors['text_primary']};")
        list_header_layout.addWidget(list_title)
        
        self.file_count_label = QLabel("")
        self.file_count_label.setStyleSheet(
            f"color: {self.colors['button_bg']}; font-size: 11px; font-weight: 500; "
            f"padding: 2px 8px; background: {self.colors['bg_secondary']}; border-radius: 4px;"
        )
        list_header_layout.addWidget(self.file_count_label)
        list_header_layout.addStretch()
        
        list_layout.addLayout(list_header_layout)
        
        # 文件列表 - 使用更简洁的边框样式
        self.zip_list = QListWidget()
        self.zip_list.setMinimumHeight(200)
        self.zip_list.setStyleSheet(f"""
            QListWidget {{
                border: 1px solid {self.colors['border']};
                border-radius: 6px;
                background: {self.colors['bg_card']};
                color: {self.colors['text_primary']};
                font-size: 12px;
                padding: 4px;
            }}
            QListWidget::item {{
                padding: 10px 8px;
                border-radius: 4px;
                margin: 1px;
                color: {self.colors['text_primary']};
            }}
            QListWidget::item:selected {{
                background: {self.colors['button_bg']};
                color: white;
            }}
            QListWidget::item:hover:!selected {{
                background: {self.colors['bg_hover']};
            }}
        """)
        self.zip_list.setAlternatingRowColors(False)
        self.zip_list.itemSelectionChanged.connect(self.on_selection_changed)
        list_layout.addWidget(self.zip_list)
        
        layout.addWidget(list_container, 1)  # 给列表更多空间
        
        # 版本号输入
        version_container = QWidget()
        version_container.setStyleSheet(f"""
            QWidget {{
                background: {self.colors['bg_card']};
                border-radius: 8px;
            }}
        """)
        version_layout = QVBoxLayout(version_container)
        version_layout.setContentsMargins(16, 12, 16, 12)
        version_layout.setSpacing(8)
        
        version_title = QLabel("版本号")
        version_title.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {self.colors['text_primary']};")
        version_layout.addWidget(version_title)
        
        self.version_input = QLineEdit()
        self.version_input.setPlaceholderText("例如: v1.2.3 或 1.0.0（留空则使用日期时间）")
        self.version_input.setFixedHeight(36)
        self.version_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px 12px;
                border: 1px solid {self.colors['border']};
                border-radius: 6px;
                background: {self.colors['bg_card']};
                font-size: 13px;
                color: {self.colors['text_primary']};
            }}
            QLineEdit:focus {{
                border: 2px solid {self.colors['button_bg']};
            }}
        """)
        version_layout.addWidget(self.version_input)
        
        layout.addWidget(version_container)
        
        # 导入按钮 - 固定在底部，更突出
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.import_btn = QPushButton("📥 开始导入")
        self.import_btn.setFixedHeight(40)  # 固定高度
        self.import_btn.setMinimumWidth(200)
        self.import_btn.setEnabled(False)
        button_layout.addWidget(self.import_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
    
    def load_zip_files(self):
        """加载当前文件夹下的所有 ZIP 文件"""
        self.zip_list.clear()
        
        if not os.path.exists(self.current_folder):
            return
        
        try:
            # 查找所有 .zip 文件
            zip_files = []
            for file in os.listdir(self.current_folder):
                if file.endswith('.zip'):
                    file_path = os.path.join(self.current_folder, file)
                    # 获取文件信息
                    stat = os.stat(file_path)
                    zip_files.append({
                        'name': file,
                        'path': file_path,
                        'size': stat.st_size,
                        'mtime': stat.st_mtime
                    })
            
            # 按修改时间倒序排列（最新的在前面）
            zip_files.sort(key=lambda x: x['mtime'], reverse=True)
            
            # 添加到列表
            for file_info in zip_files:
                # 格式化文件信息
                size_mb = file_info['size'] / (1024 * 1024)
                mtime = datetime.fromtimestamp(file_info['mtime']).strftime('%Y-%m-%d %H:%M:%S')
                
                # 显示格式：文件名 | 大小 | 修改时间
                display_text = f"{file_info['name']}  |  {size_mb:.2f} MB  |  {mtime}"
                
                item = QListWidgetItem(display_text)
                item.setData(Qt.ItemDataRole.UserRole, file_info['path'])  # 保存完整路径
                
                # 第一个（最新的）文件用不同颜色标记
                if len(self.zip_list) == 0:
                    item.setForeground(Qt.GlobalColor.blue)
                
                self.zip_list.addItem(item)
            
            # 默认选中第一个（最新的）
            if self.zip_list.count() > 0:
                self.zip_list.setCurrentRow(0)
                self.import_btn.setEnabled(True)
                # 更新文件数量标签
                self.file_count_label.setText(f"{len(zip_files)} 个文件")
            else:
                self.import_btn.setEnabled(False)
                self.file_count_label.setText("0 个文件")
                
                # 显示空状态提示
                empty_item = QListWidgetItem("📭 当前文件夹没有 ZIP 文件")
                empty_item.setForeground(Qt.GlobalColor.gray)
                empty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                empty_item.setFlags(Qt.ItemFlag.NoItemFlags)  # 不可选中
                self.zip_list.addItem(empty_item)
                
        except Exception as e:
            print(f"加载 ZIP 文件列表失败: {e}")
            self.file_count_label.setText("加载失败")
    
    def on_selection_changed(self):
        """选择改变时的处理"""
        # 更新导入按钮状态
        has_selection = self.zip_list.currentItem() is not None
        if has_selection:
            # 检查选中的项是否有有效路径（不是空状态提示）
            path = self.get_selected_zip_path()
            self.import_btn.setEnabled(bool(path))
        else:
            self.import_btn.setEnabled(False)
    
    def get_selected_zip_path(self) -> str:
        """获取选中的 ZIP 文件路径"""
        current_item = self.zip_list.currentItem()
        if current_item:
            path = current_item.data(Qt.ItemDataRole.UserRole)
            return path if path else ""
        return ""
    
    def set_version(self, version: str):
        """设置版本号"""
        if version and version != 'Unknown':
            self.version_input.setText(version)
    
    def get_version(self) -> str:
        """获取版本号"""
        version = self.version_input.text().strip()
        if not version:
            # 如果没有输入，使用默认的日期时间格式
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return version

