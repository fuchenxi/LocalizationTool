#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口
管理所有标签页和事件处理
"""

import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QFileDialog, QTabWidget
)
from PyQt6.QtCore import Qt, QThread
from PyQt6.QtGui import QPixmap

from views.info_tab import InfoTab
from views.deduplicate_tab import DeduplicateTab
from views.import_tab import ImportTab
from views.export_tab import ExportTab
from views.compare_tab import CompareTab
from views.length_compare_tab import LengthCompareTab
from views.replace_tab import ReplaceTab
from views.extract_keys_tab import ExtractKeysTab
from views.language_mapping_dialog import LanguageMappingDialog

from workers import (
    ScanDuplicatesWorker, DeduplicateWorker, ImportWorker,
    ExportWorker, CompareWorker, ScanStringsWorker, ReplaceStringsWorker,
    LengthCompareWorker
)
from workers.extract_keys_worker import ExtractKeysWorker

from models.project_info import ProjectInfoExtractor
from utils.theme import get_main_style
from utils.config import ConfigManager
from utils.toast import Toast


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.project_path = None
        self.languages = []
        
        # 初始化 UI
        self.init_ui()
        
        # 加载上次的项目路径
        last_path = ConfigManager.get_last_project_path()
        if last_path:
            self.set_project_path(last_path)
    
    def init_ui(self):
        """初始化 UI"""
        self.setWindowTitle("iOS 多语言管理工具")
        self.setMinimumSize(1200, 800)
        
        # 应用主题样式
        self.setStyleSheet(get_main_style())
        
        # 创建中央 widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局 - 水平布局：左侧导航 + 右侧内容
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 顶部工具栏：项目路径选择（需要单独处理）
        # 先创建内容区域容器
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        toolbar = self.create_toolbar()
        content_layout.addWidget(toolbar)
        
        # 创建水平布局：左侧导航 + 右侧内容
        content_horizontal = QHBoxLayout()
        content_horizontal.setContentsMargins(0, 0, 0, 0)
        content_horizontal.setSpacing(0)
        
        # 先创建右侧内容区域（使用 QStackedWidget 替代 QTabWidget）
        from PyQt6.QtWidgets import QStackedWidget
        self.content_stack = QStackedWidget()
        
        # 创建各个 Tab
        self.info_tab = InfoTab()
        self.deduplicate_tab = DeduplicateTab()
        self.import_tab = ImportTab()
        self.export_tab = ExportTab()
        self.compare_tab = CompareTab()
        self.length_compare_tab = LengthCompareTab()
        self.replace_tab = ReplaceTab()
        self.extract_keys_tab = ExtractKeysTab()
        
        # 添加到堆叠窗口
        self.content_stack.addWidget(self.info_tab)
        self.content_stack.addWidget(self.deduplicate_tab)
        self.content_stack.addWidget(self.import_tab)
        self.content_stack.addWidget(self.export_tab)
        self.content_stack.addWidget(self.compare_tab)
        self.content_stack.addWidget(self.length_compare_tab)
        self.content_stack.addWidget(self.replace_tab)
        self.content_stack.addWidget(self.extract_keys_tab)
        
        # 设置默认显示第一个
        self.content_stack.setCurrentIndex(0)
        
        # 现在创建左侧导航栏（此时 content_stack 已存在）
        self.sidebar = self.create_sidebar()
        content_horizontal.addWidget(self.sidebar)
        content_horizontal.addWidget(self.content_stack, 1)  # 占据剩余空间
        
        content_layout.addLayout(content_horizontal, 1)
        
        main_layout.addWidget(content_container, 1)
        
        # 连接事件
        self.connect_events()
        
        # 初始化导入标签页（加载 ZIP 文件列表并启用按钮）
        self.init_import_tab()
    
    def create_toolbar(self):
        """创建顶部工具栏"""
        toolbar = QWidget()
        toolbar.setFixedHeight(60)
        toolbar.setStyleSheet("""
            QWidget {
                background: white;
                border-bottom: 1px solid #E5E5EA;
            }
        """)
        
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(12)
        
        # 项目路径标签
        path_label = QLabel("项目路径:")
        path_label.setStyleSheet("font-size: 13px; font-weight: 500; color: #1D1D1F;")
        layout.addWidget(path_label)
        
        # 路径显示
        self.path_label = QLabel("未选择项目")
        self.path_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #666666;
                padding: 6px 12px;
                background: #F0F0F5;
                border-radius: 6px;
            }
        """)
        layout.addWidget(self.path_label, 1)
        
        # 选择按钮
        self.select_btn = QPushButton("选择项目")
        self.select_btn.setFixedHeight(36)
        self.select_btn.clicked.connect(self.select_project)
        layout.addWidget(self.select_btn)
        
        return toolbar
    
    def create_sidebar(self):
        """创建左侧导航栏"""
        from PyQt6.QtWidgets import QListWidget, QListWidgetItem
        
        sidebar = QListWidget()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("""
            QListWidget {
                background: #F5F5F7;
                border: none;
                border-right: 1px solid #E5E5EA;
                outline: none;
            }
            QListWidget::item {
                padding: 14px 20px;
                border: none;
                color: #8E8E93;
                font-size: 14px;
                font-weight: 500;
            }
            QListWidget::item:selected {
                background: #FFFFFF;
                color: #007AFF;
                border-right: 3px solid #007AFF;
                font-weight: 600;
            }
            QListWidget::item:hover:!selected {
                background: #E5E5EA;
                color: #1D1D1F;
            }
        """)
        
        # 添加导航项
        nav_items = [
            ("📱 项目信息", 0),
            ("🔍 查重去重", 1),
            ("📥 导入多语言", 2),
            ("📤 导出多语言", 3),
            ("🔎 对比多语言", 4),
            ("📏 长度对比", 5),
            ("🔄 字符串替换", 6),
            ("🔑 提取 Key", 7),
        ]
        
        for text, index in nav_items:
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, index)
            sidebar.addItem(item)
        
        # 连接点击事件（此时 content_stack 已经存在）
        sidebar.currentRowChanged.connect(self.on_nav_item_changed)
        
        # 设置默认选中第一项（这会触发信号，但此时 content_stack 已存在）
        sidebar.setCurrentRow(0)
        
        return sidebar
    
    def on_nav_item_changed(self, index: int):
        """导航项切换"""
        # 添加安全检查
        if hasattr(self, 'content_stack') and 0 <= index < self.content_stack.count():
            self.content_stack.setCurrentIndex(index)
    
    def connect_events(self):
        """连接所有事件"""
        # 查重去重
        self.deduplicate_tab.scan_btn.clicked.connect(self.scan_duplicates)
        self.deduplicate_tab.confirm_delete_btn.clicked.connect(self.delete_duplicates)
        
        # 导入多语言
        self.import_tab.change_folder_btn.clicked.connect(self.change_import_folder)
        self.import_tab.refresh_btn.clicked.connect(self.refresh_import_list)
        self.import_tab.import_btn.clicked.connect(self.import_strings)
        
        # 导出多语言
        self.export_tab.export_btn.clicked.connect(self.export_strings)
        
        # 对比多语言
        self.compare_tab.compare_btn.clicked.connect(self.compare_languages)
        
        # 长度对比
        self.length_compare_tab.compare_btn.clicked.connect(self.compare_lengths)
        
        # 字符串替换
        self.replace_tab.scan_btn.clicked.connect(self.scan_strings)
        self.replace_tab.replace_btn.clicked.connect(self.replace_strings)
        
        # 提取 Key
        self.extract_keys_tab.extract_btn.clicked.connect(self.extract_keys)
        self.extract_keys_tab.copy_btn.clicked.connect(self.copy_extracted_keys)
        self.extract_keys_tab.save_btn.clicked.connect(self.save_extracted_keys)
    
    def init_import_tab(self):
        """初始化导入标签页"""
        # 如果有保存的文件夹路径，加载文件列表并启用按钮
        if self.import_tab.current_folder and os.path.exists(self.import_tab.current_folder):
            self.import_tab.load_zip_files()
            self.import_tab.change_folder_btn.setEnabled(True)
            self.import_tab.refresh_btn.setEnabled(True)
    
    def select_project(self):
        """选择项目路径"""
        last_path = ConfigManager.get_last_project_path()
        default_path = last_path if last_path else os.path.expanduser("~")
        
        path = QFileDialog.getExistingDirectory(
            self,
            "选择 iOS 项目文件夹",
            default_path
        )
        
        if path:
            self.set_project_path(path)
    
    def set_project_path(self, path: str):
        """设置项目路径并更新所有 Tab"""
        self.project_path = path
        self.path_label.setText(path)
        self.path_label.setToolTip(path)
        
        # 保存路径
        ConfigManager.save_last_project_path(path)
        
        # 更新项目信息
        self.update_project_info()
        
        # 更新语言列表
        self.update_languages()
        
        # 启用相关按钮
        self.deduplicate_tab.scan_btn.setEnabled(True)
        self.compare_tab.compare_btn.setEnabled(True)
        self.length_compare_tab.compare_btn.setEnabled(True)
        self.replace_tab.scan_btn.setEnabled(True)
        self.export_tab.export_btn.setEnabled(True)
    
    def update_project_info(self):
        """更新项目信息 Tab"""
        if not self.project_path:
            return
        
        try:
            # 获取项目信息
            app_info = ProjectInfoExtractor.get_app_info(self.project_path)
            
            # 更新显示
            self.info_tab.app_name_label.setText(f"App 名称: {app_info.get('app_name', 'Unknown')}")
            version = app_info.get('version', 'Unknown')
            self.info_tab.version_label.setText(f"版本号: {version}")
            self.info_tab.bundle_id_label.setText(f"Bundle ID: {app_info.get('bundle_id', 'Unknown')}")
            
            # 自动填充导入标签页的版本号
            self.import_tab.set_version(version)
            
            # 加载图标
            icon_path = ProjectInfoExtractor.find_app_icon(self.project_path)
            if icon_path and os.path.exists(icon_path):
                pixmap = QPixmap(icon_path)
                if not pixmap.isNull():
                    # 缩放图标
                    scaled_pixmap = pixmap.scaled(
                        100, 100,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.info_tab.icon_label.setPixmap(scaled_pixmap)
        except Exception as e:
            print(f"更新项目信息失败: {e}")
    
    def update_languages(self):
        """更新语言列表"""
        if not self.project_path:
            return
        
        try:
            lproj_folders = ProjectInfoExtractor.find_lproj_folders(self.project_path)
            self.languages = list(lproj_folders.keys())
            
            # 更新各个 Tab 的语言列表
            self.compare_tab.update_languages(self.languages)
            self.length_compare_tab.update_languages(self.languages)
            self.extract_keys_tab.update_languages(self.languages)
        except Exception as e:
            print(f"更新语言列表失败: {e}")
    
    # ============ 查重去重相关方法 ============
    
    def scan_duplicates(self):
        """扫描重复项"""
        if not self.project_path:
            return
        
        # 获取忽略文件夹配置
        ignore_text = self.deduplicate_tab.ignore_folders_input.text()
        ignore_folders = [f.strip() for f in ignore_text.split('|') if f.strip()]
        
        # 清空日志
        self.deduplicate_tab.scan_log_text.clear()
        self.deduplicate_tab.scan_log_text.append("开始扫描...")
        
        # 禁用按钮
        self.deduplicate_tab.scan_btn.setEnabled(False)
        
        # 创建 Worker
        self.scan_worker = ScanDuplicatesWorker(self.project_path, ignore_folders)
        self.scan_worker.progress.connect(self.on_scan_progress)
        self.scan_worker.finished.connect(self.on_scan_finished)
        self.scan_worker.start()
    
    def on_scan_progress(self, message: str):
        """扫描进度更新"""
        self.deduplicate_tab.scan_log_text.append(message)
    
    def on_scan_finished(self, success: bool, message: str, duplicates_info: dict):
        """扫描完成"""
        self.deduplicate_tab.scan_btn.setEnabled(True)
        self.deduplicate_tab.scan_log_text.append(message)
        
        if success:
            self.deduplicate_tab.update_results(duplicates_info)
            if duplicates_info:
                self.deduplicate_tab.confirm_delete_btn.setVisible(True)
                self.deduplicate_tab.confirm_delete_btn.setEnabled(True)
            else:
                self.deduplicate_tab.confirm_delete_btn.setVisible(False)
    
    def delete_duplicates(self):
        """删除重复项"""
        if not self.project_path:
            return
        
        # 获取忽略文件夹配置
        ignore_text = self.deduplicate_tab.ignore_folders_input.text()
        ignore_folders = [f.strip() for f in ignore_text.split('|') if f.strip()]
        
        # 清空日志
        self.deduplicate_tab.scan_log_text.clear()
        self.deduplicate_tab.scan_log_text.append("开始删除重复项...")
        
        # 禁用按钮
        self.deduplicate_tab.confirm_delete_btn.setEnabled(False)
        
        # 创建 Worker
        self.deduplicate_worker = DeduplicateWorker(self.project_path, ignore_folders)
        self.deduplicate_worker.progress.connect(self.on_delete_progress)
        self.deduplicate_worker.finished.connect(self.on_delete_finished)
        self.deduplicate_worker.start()
    
    def on_delete_progress(self, message: str):
        """删除进度更新"""
        self.deduplicate_tab.scan_log_text.append(message)
    
    def on_delete_finished(self, success: bool, message: str, deleted_count: int):
        """删除完成"""
        self.deduplicate_tab.confirm_delete_btn.setEnabled(True)
        self.deduplicate_tab.scan_log_text.append(message)
        
        if success:
            Toast.show_toast(self, f"✅ 成功删除 {deleted_count} 个重复项", 2000)
            # 重新扫描
            self.scan_duplicates()
    
    # ============ 导入多语言相关方法 ============
    
    def change_import_folder(self):
        """更改导入文件夹"""
        last_folder = ConfigManager.get_last_import_folder()
        folder = QFileDialog.getExistingDirectory(
            self,
            "选择包含 ZIP 文件的文件夹",
            last_folder
        )
        
        if folder:
            self.import_tab.current_folder = folder
            self.import_tab.folder_input.setText(folder)
            ConfigManager.save_last_import_folder(folder)
            self.import_tab.load_zip_files()
            self.import_tab.change_folder_btn.setEnabled(True)
            self.import_tab.refresh_btn.setEnabled(True)
    
    def refresh_import_list(self):
        """刷新导入列表"""
        self.import_tab.load_zip_files()
    
    def import_strings(self):
        """导入多语言"""
        zip_path = self.import_tab.get_selected_zip_path()
        if not zip_path or not self.project_path:
            return
        
        # 获取项目中的语言列表
        project_languages = ProjectInfoExtractor.find_lproj_folders(self.project_path)
        if not project_languages:
            Toast.show_toast(self, "项目中未找到 .lproj 文件夹", 2000)
            return
        
        # 弹出语言映射对话框
        dialog = LanguageMappingDialog(zip_path, project_languages, self)
        if dialog.exec() != dialog.DialogCode.Accepted:
            return
        
        # 获取映射关系
        language_mappings = dialog.get_mappings()
        if not language_mappings:
            Toast.show_toast(self, "没有配置任何语言映射", 2000)
            return
        
        # 从输入框获取版本号（如果没有输入则使用日期时间）
        version = self.import_tab.get_version()
        
        # 创建 Worker（传入语言映射）
        self.import_worker = ImportWorker(zip_path, self.project_path, version, language_mappings)
        self.import_worker.progress.connect(self.on_import_progress)
        self.import_worker.finished.connect(self.on_import_finished)
        self.import_worker.start()
        
        # 禁用按钮
        self.import_tab.import_btn.setEnabled(False)
    
    def on_import_progress(self, message: str):
        """导入进度更新"""
        # 这里可以添加导入日志显示
        print(message)
    
    def on_import_finished(self, success: bool, message: str):
        """导入完成"""
        self.import_tab.import_btn.setEnabled(True)
        Toast.show_toast(self, message, 2000)
    
    # ============ 导出多语言相关方法 ============
    
    def export_strings(self):
        """导出多语言"""
        if not self.project_path:
            return
        
        key_list = self.export_tab.get_key_list()
        export_strings = self.export_tab.strings_checkbox.isChecked()
        export_xml = self.export_tab.xml_checkbox.isChecked()
        
        if not export_strings and not export_xml:
            Toast.show_toast(self, "请至少选择一种导出格式", 2000)
            return
        
        # 清空日志
        self.export_tab.export_log_text.clear()
        self.export_tab.export_log_text.append("开始导出...")
        
        # 禁用按钮
        self.export_tab.export_btn.setEnabled(False)
        
        # 创建 Worker
        self.export_worker = ExportWorker(
            self.project_path,
            export_strings,
            export_xml,
            key_list if key_list else None
        )
        self.export_worker.progress.connect(self.on_export_progress)
        self.export_worker.finished.connect(self.on_export_finished)
        self.export_worker.start()
    
    def on_export_progress(self, message: str):
        """导出进度更新"""
        self.export_tab.export_log_text.append(message)
    
    def on_export_finished(self, success: bool, message: str):
        """导出完成"""
        self.export_tab.export_btn.setEnabled(True)
        self.export_tab.export_log_text.append(message)
        Toast.show_toast(self, message, 2000)
    
    # ============ 对比多语言相关方法 ============
    
    def compare_languages(self):
        """对比多语言"""
        if not self.project_path:
            return
        
        base_lang = self.compare_tab.base_lang_combo.currentText()
        if not base_lang:
            Toast.show_toast(self, "请选择基准语言", 2000)
            return
        
        # 清空日志
        self.compare_tab.compare_log_text.clear()
        self.compare_tab.compare_log_text.append(f"开始对比，基准语言: {base_lang}...")
        
        # 禁用按钮
        self.compare_tab.compare_btn.setEnabled(False)
        
        # 创建 Worker
        self.compare_worker = CompareWorker(self.project_path, base_lang)
        self.compare_worker.progress.connect(self.on_compare_progress)
        self.compare_worker.finished.connect(self.on_compare_finished)
        self.compare_worker.start()
    
    def on_compare_progress(self, message: str):
        """对比进度更新"""
        self.compare_tab.compare_log_text.append(message)
    
    def on_compare_finished(self, success: bool, message: str, missing_keys: dict):
        """对比完成"""
        self.compare_tab.compare_btn.setEnabled(True)
        self.compare_tab.compare_log_text.append(message)
        
        if success:
            self.compare_tab.update_results(missing_keys)
    
    # ============ 字符串替换相关方法 ============
    
    def scan_strings(self):
        """扫描字符串"""
        if not self.project_path:
            return
        
        # 获取 Key 列表
        key_text = self.replace_tab.key_input.toPlainText()
        keys = [k.strip() for k in key_text.split('\n') if k.strip()]
        
        if not keys:
            Toast.show_toast(self, "请输入要处理的 Key 列表", 2000)
            return
        
        # 获取配置
        scan_oc = self.replace_tab.scan_oc_checkbox.isChecked()
        scan_swift = self.replace_tab.scan_swift_checkbox.isChecked()
        case_sensitive = self.replace_tab.case_sensitive_checkbox.isChecked()
        
        # 禁用按钮
        self.replace_tab.scan_btn.setEnabled(False)
        
        # 创建 Worker
        self.scan_strings_worker = ScanStringsWorker(
            self.project_path,
            keys,
            scan_oc,
            scan_swift,
            case_sensitive
        )
        self.scan_strings_worker.progress.connect(self.on_scan_strings_progress)
        self.scan_strings_worker.finished.connect(self.on_scan_strings_finished)
        self.scan_strings_worker.start()
    
    def on_scan_strings_progress(self, message: str):
        """扫描字符串进度更新"""
        # 可以添加到日志
        print(message)
    
    def on_scan_strings_finished(self, success: bool, message: str, results: list, mismatch_keys: list):
        """扫描字符串完成"""
        self.replace_tab.scan_btn.setEnabled(True)
        
        if success:
            self.replace_tab.update_results(results)
            if mismatch_keys:
                self.replace_tab.mismatch_text.setPlainText('\n'.join(mismatch_keys))
        else:
            Toast.show_toast(self, message, 2000)
    
    def replace_strings(self):
        """替换字符串"""
        if not self.project_path:
            return
        
        # 获取 Key 列表
        key_text = self.replace_tab.key_input.toPlainText()
        keys = [k.strip() for k in key_text.split('\n') if k.strip()]
        
        if not keys:
            return
        
        # 获取配置
        scan_oc = self.replace_tab.scan_oc_checkbox.isChecked()
        scan_swift = self.replace_tab.scan_swift_checkbox.isChecked()
        case_sensitive = self.replace_tab.case_sensitive_checkbox.isChecked()
        
        # 禁用按钮
        self.replace_tab.replace_btn.setEnabled(False)
        
        # 创建 Worker
        self.replace_strings_worker = ReplaceStringsWorker(
            self.project_path,
            keys,
            scan_oc,
            scan_swift,
            case_sensitive
        )
        self.replace_strings_worker.progress.connect(self.on_replace_strings_progress)
        self.replace_strings_worker.finished.connect(self.on_replace_strings_finished)
        self.replace_strings_worker.start()
    
    def on_replace_strings_progress(self, message: str):
        """替换进度更新"""
        print(message)
    
    def on_replace_strings_finished(self, success: bool, message: str, replaced_count: int):
        """替换完成"""
        self.replace_tab.replace_btn.setEnabled(True)
        Toast.show_toast(self, message, 2000)
    
    # ============ 提取 Key 相关方法 ============
    
    def extract_keys(self):
        """提取 Key"""
        if not self.project_path:
            return
        
        language = self.extract_keys_tab.get_selected_language()
        if not language:
            Toast.show_toast(self, "请选择语言", 2000)
            return
        
        # 禁用按钮
        self.extract_keys_tab.extract_btn.setEnabled(False)
        
        # 创建 Worker
        self.extract_keys_worker = ExtractKeysWorker(self.project_path, language)
        self.extract_keys_worker.progress.connect(self.on_extract_keys_progress)
        self.extract_keys_worker.finished.connect(self.on_extract_keys_finished)
        self.extract_keys_worker.start()
    
    def on_extract_keys_progress(self, message: str):
        """提取进度更新"""
        # 移除日志显示，使用 Toast 提示重要信息
        pass
    
    def on_extract_keys_finished(self, success: bool, message: str, keys: list, key_values: dict = None):
        """提取完成"""
        self.extract_keys_tab.extract_btn.setEnabled(True)
        
        if success:
            # 传入 key-values 字典
            self.extract_keys_tab.update_results(keys, key_values)
            Toast.show_toast(self, f"✅ {message}", 2000)
        else:
            Toast.show_toast(self, f"❌ {message}", 2000)
    
    def copy_extracted_keys(self):
        """复制提取的 Key"""
        from PyQt6.QtWidgets import QApplication
        keys_text = self.extract_keys_tab.keys_text.toPlainText()
        if keys_text:
            clipboard = QApplication.clipboard()
            clipboard.setText(keys_text)
            Toast.show_toast(self, f"✅ 已复制 {len(keys_text.splitlines())} 个 Key", 1500)
    
    def save_extracted_keys(self):
        """保存提取的 Key"""
        keys_text = self.extract_keys_tab.keys_text.toPlainText()
        if not keys_text:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存 Key 列表",
            "keys.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(keys_text)
                Toast.show_toast(self, f"✅ 已保存到 {file_path}", 2000)
            except Exception as e:
                Toast.show_toast(self, f"保存失败: {e}", 2000)
    
    # ============ 长度对比相关方法 ============
    
    def compare_lengths(self):
        """长度对比"""
        if not self.project_path:
            return
        
        target_languages = self.length_compare_tab.get_selected_target_languages()
        if not target_languages:
            Toast.show_toast(self, "请至少选择一个目标语言", 2000)
            return
        
        compare_mode = self.length_compare_tab.get_compare_mode()
        base_lang = self.length_compare_tab.get_base_lang() if compare_mode == "base_lang" else None
        min_diff_percent = self.length_compare_tab.get_min_diff_percent()
        
        # 清空日志
        self.length_compare_tab.compare_log_text.clear()
        self.length_compare_tab.compare_log_text.append(f"开始对比，目标语言: {', '.join(target_languages)}...")
        
        # 禁用按钮
        self.length_compare_tab.compare_btn.setEnabled(False)
        
        # 创建 Worker
        self.length_compare_worker = LengthCompareWorker(
            self.project_path,
            target_languages,
            compare_mode,
            base_lang,
            min_diff_percent
        )
        self.length_compare_worker.progress.connect(self.on_length_compare_progress)
        self.length_compare_worker.finished.connect(self.on_length_compare_finished)
        self.length_compare_worker.start()
    
    def on_length_compare_progress(self, message: str):
        """长度对比进度更新"""
        self.length_compare_tab.compare_log_text.append(message)
    
    def on_length_compare_finished(self, success: bool, message: str, results: dict):
        """长度对比完成"""
        self.length_compare_tab.compare_btn.setEnabled(True)
        self.length_compare_tab.compare_log_text.append(message)
        
        if success:
            self.length_compare_tab.update_results(results)
            if results:
                Toast.show_toast(self, f"✅ {message}", 2000)
            else:
                Toast.show_toast(self, "✅ 未发现变长的字段", 2000)
        else:
            Toast.show_toast(self, f"❌ {message}", 2000)