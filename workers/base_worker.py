#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Worker 基类
提供公共功能和统一的错误处理
"""

import os
from typing import List, Optional, Dict
from PyQt6.QtCore import QThread, pyqtSignal

from models import ProjectInfoExtractor
from utils.constants import DEFAULT_IGNORE_FOLDERS


class BaseWorker(QThread):
    """Worker 基类，提供公共功能"""
    
    # 统一的进度信号
    progress = pyqtSignal(str)
    
    # 注意：finished 信号由各子类自己定义，因为不同 worker 需要不同的参数类型
    
    def __init__(self, project_path: str = None, ignore_folders: List[str] = None):
        super().__init__()
        self.project_path = project_path
        self.ignore_folders = ignore_folders or DEFAULT_IGNORE_FOLDERS.copy()
        self._should_stop = False
    
    def validate_project_path(self) -> bool:
        """验证项目路径（子类需要自己调用 finished.emit）"""
        if not self.project_path:
            return False
        
        if not os.path.exists(self.project_path):
            return False
        
        if not os.path.isdir(self.project_path):
            return False
        
        return True
    
    def find_lproj_folders(self) -> Optional[Dict[str, str]]:
        """查找所有 .lproj 文件夹（不带错误处理，由子类处理）"""
        try:
            lproj_folders = ProjectInfoExtractor.find_lproj_folders(
                self.project_path, 
                self.ignore_folders
            )
            
            if not lproj_folders:
                return None
            
            return lproj_folders
            
        except Exception as e:
            return None
    
    def emit_error(self, operation: str, error: Exception):
        """统一的错误报告（子类需要自己实现 finished.emit）"""
        error_msg = f"{operation}失败: {str(error)}"
        # 子类需要自己调用 finished.emit
        return error_msg
    
    def stop(self):
        """停止工作线程"""
        self._should_stop = True
    
    def check_stopped(self) -> bool:
        """检查是否应该停止"""
        return self._should_stop