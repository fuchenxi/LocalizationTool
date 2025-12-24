#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查重去重标签页 - 重新设计版本
左侧：配置和操作
右侧：扫描结果（按语言分Tab显示）
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QGroupBox, QTextEdit,
    QTabWidget, QTableWidget, QTableWidgetItem, QSplitter,
    QHeaderView
)
from PyQt6.QtCore import Qt

from utils.constants import DELETE_BUTTON_STYLE, LARGE_BUTTON_STYLE
from utils.toast import Toast


class DeduplicateTab(QWidget):
    """查重去重标签页"""
    
    def __init__(self):
        super().__init__()
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
        desc_label = QLabel("扫描项目中所有语言文件，查找重复的 key-value 对")
        desc_label.setStyleSheet(
            "color: #666666; font-size: 12px; padding: 8px 0;"
        )
        left_layout.addWidget(desc_label)
        
        # 忽略文件夹配置
        ignore_group = QGroupBox("忽略文件夹配置")
        ignore_layout = QVBoxLayout()
        ignore_layout.setSpacing(8)
        
        ignore_hint = QLabel("扫描时忽略以下文件夹（使用 | 分隔）")
        ignore_hint.setStyleSheet("color: #8E8E93; font-size: 11px;")
        ignore_layout.addWidget(ignore_hint)
        
        self.ignore_folders_input = QLineEdit()
        self.ignore_folders_input.setText("Pods|DerivedData|build|Build|.git|Carthage")
        self.ignore_folders_input.setPlaceholderText("例如: Pods|DerivedData|build")
        self.ignore_folders_input.setMinimumHeight(28)
        ignore_layout.addWidget(self.ignore_folders_input)
        
        ignore_group.setLayout(ignore_layout)
        left_layout.addWidget(ignore_group)
        
        # 操作按钮
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(10)
        
        # 扫描按钮 - 主要操作，更突出
        self.scan_btn = QPushButton("🔍 开始扫描重复项")
        self.scan_btn.setMinimumHeight(40)
        self.scan_btn.setEnabled(False)
        buttons_layout.addWidget(self.scan_btn)
        
        # 确认删除按钮（初始隐藏）
        self.confirm_delete_btn = QPushButton("⚠️ 确认删除重复项")
        self.confirm_delete_btn.setMinimumHeight(40)
        self.confirm_delete_btn.setStyleSheet(DELETE_BUTTON_STYLE)
        self.confirm_delete_btn.setEnabled(False)
        self.confirm_delete_btn.setVisible(False)
        buttons_layout.addWidget(self.confirm_delete_btn)
        
        left_layout.addLayout(buttons_layout)
        
        # 操作日志
        log_group = QGroupBox("扫描日志")
        log_layout = QVBoxLayout()
        log_layout.setContentsMargins(8, 8, 8, 8)
        
        self.scan_log_text = QTextEdit()
        self.scan_log_text.setReadOnly(True)
        self.scan_log_text.setPlaceholderText("点击上方按钮开始扫描...")
        self.scan_log_text.setStyleSheet("font-size: 11px;")
        log_layout.addWidget(self.scan_log_text)
        
        log_group.setLayout(log_layout)
        left_layout.addWidget(log_group, 1)  # 给日志更多空间
        
        # ============ 右侧：扫描结果区域 ============
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)
        
        # 标题和统计信息在一行
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        
        result_label = QLabel("扫描结果")
        result_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #1D1D1F;")
        header_layout.addWidget(result_label)
        
        # 统计信息
        self.stats_label = QLabel("尚未扫描")
        self.stats_label.setStyleSheet(
            "font-size: 12px; color: #666; padding: 6px 12px; "
            "background: #F0F0F5; border-radius: 4px;"
        )
        header_layout.addWidget(self.stats_label)
        header_layout.addStretch()
        
        right_layout.addLayout(header_layout)
        
        # 结果 Tab（按语言分）
        self.result_tabs = QTabWidget()
        self.result_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #E5E5EA;
                border-radius: 8px;
                background: white;
            }
        """)
        right_layout.addWidget(self.result_tabs)
        
        # 添加提示页
        empty_widget = QWidget()
        empty_layout = QVBoxLayout(empty_widget)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        empty_label = QLabel("🔍\n\n点击左侧「开始扫描重复项」按钮\n查看扫描结果")
        empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_label.setStyleSheet("color: #8E8E93; font-size: 14px; line-height: 24px;")
        empty_layout.addWidget(empty_label)
        
        self.result_tabs.addTab(empty_widget, "等待扫描")
        
        # 添加到分割器
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        
        # 设置初始分割比例 (30% : 70%)
        splitter.setSizes([300, 700])
        
        main_layout.addWidget(splitter)
    
    def update_results(self, duplicates_info: dict):
        """更新扫描结果显示"""
        # 清空现有 tabs
        self.result_tabs.clear()
        
        if not duplicates_info:
            # 无重复项
            empty_widget = QWidget()
            empty_layout = QVBoxLayout(empty_widget)
            empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            success_label = QLabel("✅\n\n未发现重复项\n所有语言文件都很干净！")
            success_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            success_label.setStyleSheet("color: #34C759; font-size: 16px; line-height: 28px;")
            empty_layout.addWidget(success_label)
            
            self.result_tabs.addTab(empty_widget, "扫描结果")
            self.stats_label.setText("✅ 未发现重复项")
            self.stats_label.setStyleSheet(
                "font-size: 13px; color: #34C759; padding: 10px; "
                "background: #E8F5E9; border-radius: 6px; font-weight: 500;"
            )
            return
        
        # 更新统计信息
        total_count = sum(info['count'] for info in duplicates_info.values())
        lang_count = len(duplicates_info)
        self.stats_label.setText(f"⚠️ 发现 {total_count} 个重复项 • {lang_count} 个语言文件")
        self.stats_label.setStyleSheet(
            "font-size: 13px; color: #FF9500; padding: 10px; "
            "background: #FFF3E0; border-radius: 6px; font-weight: 500;"
        )
        
        # 为每个语言创建一个 Tab
        for lang_code, info in duplicates_info.items():
            count = info['count']
            details = info.get('details', {})
            file_path = info.get('file', '')
            
            # 创建表格显示重复项
            table = self.create_duplicates_table(details, file_path)
            
            # Tab 标签显示语言和数量
            tab_label = f"{lang_code} ({count})"
            self.result_tabs.addTab(table, tab_label)
    
    def create_duplicates_table(self, duplicates: dict, file_path: str = "") -> QTableWidget:
        """创建显示重复项的表格"""
        from PyQt6.QtGui import QColor, QBrush, QFont
        
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Key", "Value", "行号", "出现次数", "操作"])
        
        # 保存文件路径
        table.file_path = file_path
        
        # 设置表格属性
        table.setAlternatingRowColors(False)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectItems)  # 改为单元格选择
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setStyleSheet("""
            QTableWidget {
                font-size: 12px;
                gridline-color: #E5E5EA;
            }
            QTableWidget::item {
                padding: 6px;
            }
            QTableWidget::item:selected {
                background: #D0E8FF;
                color: #1D1D1F;
            }
        """)
        
        # 设置工具提示
        table.setToolTip("💡 双击 Key/Value/行号 可复制内容，点击「打开」按钮可跳转到编辑器")
        
        # 计算总行数
        total_rows = sum(len(occurrences) for occurrences in duplicates.values())
        table.setRowCount(total_rows)
        
        # 定义颜色
        header_bg = QColor("#FFF3E0")  # 橙色浅背景 - 标题行
        duplicate_bg = QColor("#FFEBEE")  # 红色浅背景 - 重复行
        header_fg = QColor("#E65100")  # 橙色深文字
        duplicate_fg = QColor("#C62828")  # 红色深文字
        
        # 填充数据
        row = 0
        for key, occurrences in duplicates.items():
            for i, (value, line_num) in enumerate(occurrences):
                # 第一行是标题行，其他是重复行
                is_header = (i == 0)
                bg_color = header_bg if is_header else duplicate_bg
                
                # Key
                key_item = QTableWidgetItem(key)
                key_item.setBackground(QBrush(bg_color))
                key_item.setData(Qt.ItemDataRole.UserRole, line_num)  # 保存行号
                if is_header:
                    key_item.setForeground(QBrush(header_fg))
                    from PyQt6.QtGui import QFont
                    font = QFont()
                    font.setBold(True)
                    key_item.setFont(font)
                table.setItem(row, 0, key_item)
                
                # Value
                value_item = QTableWidgetItem(value)
                value_item.setBackground(QBrush(bg_color))
                value_item.setData(Qt.ItemDataRole.UserRole, line_num)  # 保存行号
                if is_header:
                    value_item.setForeground(QBrush(header_fg))
                    font = QFont()
                    font.setBold(True)
                    value_item.setFont(font)
                else:
                    value_item.setForeground(QBrush(duplicate_fg))
                table.setItem(row, 1, value_item)
                
                # 行号
                line_item = QTableWidgetItem(str(line_num))
                line_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                line_item.setBackground(QBrush(bg_color))
                line_item.setData(Qt.ItemDataRole.UserRole, line_num)  # 保存行号
                if is_header:
                    line_item.setForeground(QBrush(header_fg))
                table.setItem(row, 2, line_item)
                
                # 出现次数（只在第一行显示）
                if i == 0:
                    count_item = QTableWidgetItem(f"{len(occurrences)} 次")
                    count_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    count_item.setBackground(QBrush(header_bg))
                    count_item.setForeground(QBrush(header_fg))
                    font = QFont()
                    font.setBold(True)
                    count_item.setFont(font)
                    table.setItem(row, 3, count_item)
                else:
                    empty_item = QTableWidgetItem("")
                    empty_item.setBackground(QBrush(duplicate_bg))
                    table.setItem(row, 3, empty_item)
                
                # 操作列 - 添加打开文件按钮
                action_item = QTableWidgetItem("打开")
                action_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                # 使用蓝色背景，让它看起来像按钮
                action_item.setBackground(QBrush(QColor("#E3F2FD")))
                action_item.setForeground(QBrush(QColor("#007AFF")))
                action_item.setData(Qt.ItemDataRole.UserRole, line_num)  # 保存行号
                font = QFont()
                font.setBold(True)
                action_item.setFont(font)
                table.setItem(row, 4, action_item)
                
                row += 1
        
        # 调整列宽
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        
        table.setColumnWidth(0, 220)
        table.setColumnWidth(4, 70)  # 操作列固定宽度（去掉图标后更窄）
        
        # 设置行高
        for i in range(total_rows):
            table.setRowHeight(i, 32)
        
        # 连接双击事件 - 用于复制内容
        table.cellDoubleClicked.connect(lambda row, col: self.on_cell_double_clicked(table, row, col))
        
        # 连接单击事件 - 用于操作列的点击
        table.cellClicked.connect(lambda row, col: self.on_cell_clicked(table, row, col))
        
        # 连接鼠标进入事件 - 显示手型光标
        table.cellEntered.connect(lambda row, col: self.on_cell_entered(table, row, col))
        table.setMouseTracking(True)  # 启用鼠标追踪
        
        return table
    
    def on_cell_entered(self, table: QTableWidget, row: int, col: int):
        """处理鼠标进入单元格事件 - 改变光标样式"""
        from PyQt6.QtGui import QCursor
        from PyQt6.QtCore import Qt
        
        # 如果是操作列，显示手型光标
        if col == 4:
            table.viewport().setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        else:
            table.viewport().setCursor(QCursor(Qt.CursorShape.ArrowCursor))
    
    def on_cell_double_clicked(self, table: QTableWidget, row: int, col: int):
        """处理表格单元格双击事件 - 复制内容到剪贴板"""
        from PyQt6.QtWidgets import QApplication
        
        # 如果是操作列，不处理
        if col == 4:
            return
        
        # 获取单元格内容
        item = table.item(row, col)
        if not item:
            return
        
        text = item.text()
        if text and text != "":
            # 复制到剪贴板
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            
            # 显示 Toast 提示
            column_names = ["Key", "Value", "行号", "出现次数"]
            column_name = column_names[col] if col < len(column_names) else ""
            
            # 截取文字（如果太长）
            display_text = text if len(text) <= 30 else text[:30] + "..."
            Toast.show_toast(self.window(), f"✅ 已复制: {display_text}", 1500)
    
    def on_cell_clicked(self, table: QTableWidget, row: int, col: int):
        """处理表格单元格单击事件 - 处理操作列的点击"""
        import os
        from PyQt6.QtGui import QCursor, QColor, QBrush
        from PyQt6.QtCore import Qt
        
        # 只处理操作列的点击
        if col != 4:
            return
        
        # 获取文件路径
        file_path = getattr(table, 'file_path', '')
        if not file_path or not os.path.exists(file_path):
            return
        
        # 获取行号
        item = table.item(row, 4)  # 从操作列获取
        if not item:
            return
        
        line_num = item.data(Qt.ItemDataRole.UserRole)
        if not line_num:
            return
        
        # 视觉反馈 - 临时改变背景色
        original_bg = item.background()
        item.setBackground(QBrush(QColor("#BBDEFB")))  # 深蓝色表示点击
        table.viewport().update()
        
        # 在日志中显示提示
        file_name = os.path.basename(os.path.dirname(file_path))  # 例如: en.lproj
        self.scan_log_text.append(f"📂 正在打开 {file_name}/Localizable.strings 第 {line_num} 行...")
        
        # 在编辑器中打开文件并跳转到指定行
        self.open_in_editor(file_path, line_num)
        
        # 恢复原背景色（延迟一点）
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(200, lambda: item.setBackground(original_bg))
    
    def open_in_editor(self, file_path: str, line_num: int):
        """在外部编辑器中打开文件并跳转到指定行
        
        优先在已打开的 Xcode 中打开文件
        """
        import subprocess
        import shutil
        
        try:
            # 优先尝试在已打开的 Xcode 中打开
            if self.open_in_xcode(file_path, line_num):
                return
            
            # 如果 Xcode 方式失败，尝试其他编辑器
            editors = [
                # VSCode
                ('code', lambda: subprocess.run(['code', '-g', f'{file_path}:{line_num}'], check=False)),
                # Sublime Text
                ('subl', lambda: subprocess.run(['subl', f'{file_path}:{line_num}'], check=False)),
                # Atom
                ('atom', lambda: subprocess.run(['atom', f'{file_path}:{line_num}'], check=False)),
            ]
            
            # 查找可用的编辑器
            for cmd, open_func in editors:
                if shutil.which(cmd):
                    open_func()
                    return
            
            # 如果没有找到专用编辑器，尝试用系统默认方式打开
            # macOS
            subprocess.run(['open', file_path], check=False)
            
        except Exception as e:
            print(f"打开编辑器失败: {e}")
    
    def open_in_xcode(self, file_path: str, line_num: int) -> bool:
        """在 Xcode 中打开文件并跳转到指定行
        
        优先使用 xed 命令（简单直接）
        
        Returns:
            bool: 成功返回 True，失败返回 False
        """
        import subprocess
        
        try:
            # 方法1: 使用 xed 命令（Xcode 自带）
            # -l 参数指定行号
            result = subprocess.run(
                ['xed', '--line', str(line_num), file_path],
                capture_output=True,
                timeout=3
            )
            
            if result.returncode == 0:
                return True
            
            # 方法2: 如果上面失败，尝试不带行号参数
            subprocess.run(['xed', file_path], check=False)
            return True
                
        except subprocess.TimeoutExpired:
            # 超时，尝试不等待
            try:
                subprocess.Popen(['xed', '--line', str(line_num), file_path])
                return True
            except:
                return False
        except FileNotFoundError:
            # xed 命令不存在
            return False
        except Exception as e:
            print(f"Xcode 打开失败: {e}")
            return False
