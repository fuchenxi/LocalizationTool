#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
保存和读取用户配置
"""

import json
import os
from typing import Optional


class ConfigManager:
    """配置管理器"""
    
    # 配置文件路径
    CONFIG_FILE = os.path.expanduser("~/.ios_localization_tool.json")
    
    @staticmethod
    def save_config(config: dict):
        """保存配置"""
        try:
            with open(ConfigManager.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    @staticmethod
    def load_config() -> dict:
        """加载配置"""
        if not os.path.exists(ConfigManager.CONFIG_FILE):
            return {}
        
        try:
            with open(ConfigManager.CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置失败: {e}")
            return {}
    
    @staticmethod
    def get_last_project_path() -> Optional[str]:
        """获取上次的项目路径"""
        config = ConfigManager.load_config()
        path = config.get('last_project_path')
        
        # 检查路径是否仍然存在
        if path and os.path.exists(path):
            return path
        return None
    
    @staticmethod
    def save_last_project_path(path: str):
        """保存项目路径"""
        config = ConfigManager.load_config()
        config['last_project_path'] = path
        ConfigManager.save_config(config)
    
    @staticmethod
    def get_last_import_folder() -> str:
        """获取上次的导入文件夹路径"""
        config = ConfigManager.load_config()
        path = config.get('last_import_folder', os.path.expanduser("~/Downloads"))
        
        # 检查路径是否存在
        if os.path.exists(path):
            return path
        return os.path.expanduser("~/Downloads")
    
    @staticmethod
    def save_last_import_folder(path: str):
        """保存导入文件夹路径"""
        config = ConfigManager.load_config()
        config['last_import_folder'] = path
        ConfigManager.save_config(config)

