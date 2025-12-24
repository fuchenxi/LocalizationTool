#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iOS 项目信息提取器
负责提取项目的各种信息：版本号、App名称、图标等
"""

import os
import re
import plistlib
from typing import Dict, List, Optional


class ProjectInfoExtractor:
    """提取 iOS 项目信息"""
    
    @staticmethod
    def find_info_plist(project_path: str) -> Optional[str]:
        """查找 Info.plist 文件"""
        # 递归查找，优先选择最浅层级的 Info.plist
        candidates = []
        
        for root, dirs, files in os.walk(project_path):
            # 排除不需要的目录
            dirs[:] = [d for d in dirs if d not in ['Pods', 'build', 'Build', 'DerivedData', '.git', 'Carthage']]
            
            if 'Info.plist' in files:
                plist_path = os.path.join(root, 'Info.plist')
                depth = plist_path.replace(project_path, '').count(os.sep)
                candidates.append((depth, plist_path))
        
        # 返回最浅层级的 Info.plist
        if candidates:
            candidates.sort(key=lambda x: x[0])
            return candidates[0][1]
        
        return None
    
    @staticmethod
    def get_app_info(project_path: str) -> Dict[str, str]:
        """获取应用信息：版本号、App 名称
        
        优先级：
        1. 尝试从 Info.plist 读取
        2. 如果失败，从 project.pbxproj 读取
        """
        info = {
            'version': 'Unknown',
            'app_name': 'Unknown',
            'bundle_id': 'Unknown'
        }
        
        # 1. 先尝试从 Info.plist 读取
        plist_path = ProjectInfoExtractor.find_info_plist(project_path)
        if plist_path and os.path.exists(plist_path):
            try:
                with open(plist_path, 'rb') as f:
                    plist_data = plistlib.load(f)
                
                # 获取版本号
                if 'CFBundleShortVersionString' in plist_data:
                    info['version'] = plist_data['CFBundleShortVersionString']
                
                # 获取 App 名称
                if 'CFBundleName' in plist_data:
                    info['app_name'] = plist_data['CFBundleName']
                elif 'CFBundleDisplayName' in plist_data:
                    info['app_name'] = plist_data['CFBundleDisplayName']
                
                # 获取 Bundle ID
                if 'CFBundleIdentifier' in plist_data:
                    info['bundle_id'] = plist_data['CFBundleIdentifier']
                    
            except Exception as e:
                print(f"读取 Info.plist 出错: {e}")
        
        # 2. 如果 Info.plist 中没有获取到信息，尝试从 project.pbxproj 读取
        if info['version'] == 'Unknown' or info['app_name'] == 'Unknown' or info['bundle_id'] == 'Unknown':
            pbxproj_info = ProjectInfoExtractor.get_info_from_pbxproj(project_path)
            
            # 补充缺失的信息
            if info['version'] == 'Unknown' and pbxproj_info.get('version') != 'Unknown':
                info['version'] = pbxproj_info['version']
            
            if info['app_name'] == 'Unknown' and pbxproj_info.get('app_name') != 'Unknown':
                info['app_name'] = pbxproj_info['app_name']
            
            if info['bundle_id'] == 'Unknown' and pbxproj_info.get('bundle_id') != 'Unknown':
                info['bundle_id'] = pbxproj_info['bundle_id']
        
        return info
    
    @staticmethod
    def find_xcodeproj(project_path: str) -> Optional[str]:
        """查找 .xcodeproj 文件"""
        for item in os.listdir(project_path):
            if item.endswith('.xcodeproj'):
                return os.path.join(project_path, item)
        
        # 递归查找（只搜索一层）
        for root, dirs, files in os.walk(project_path):
            if root == project_path:
                continue
            for dir_name in dirs:
                if dir_name.endswith('.xcodeproj'):
                    return os.path.join(root, dir_name)
            break  # 只搜索一层
        
        return None
    
    @staticmethod
    def get_info_from_pbxproj(project_path: str) -> Dict[str, str]:
        """从 project.pbxproj 文件读取项目信息"""
        info = {
            'version': 'Unknown',
            'app_name': 'Unknown',
            'bundle_id': 'Unknown'
        }
        
        # 查找 .xcodeproj 文件
        xcodeproj_path = ProjectInfoExtractor.find_xcodeproj(project_path)
        if not xcodeproj_path:
            return info
        
        # 读取 project.pbxproj 文件
        pbxproj_path = os.path.join(xcodeproj_path, 'project.pbxproj')
        if not os.path.exists(pbxproj_path):
            return info
        
        try:
            with open(pbxproj_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取版本号（按优先级尝试多个字段）
            version_fields = [
                'MARKETING_VERSION',
                'INFOPLIST_KEY_CFBundleShortVersionString',
                'CURRENT_PROJECT_VERSION'
            ]
            
            for field in version_fields:
                if info['version'] != 'Unknown':
                    break
                version_match = re.search(rf'{field}\s*=\s*([^;]+);', content)
                if version_match:
                    version = version_match.group(1).strip().strip('"')
                    if version and not version.startswith('$('):
                        info['version'] = version
                        break
            
            # 提取 App 名称（按优先级尝试多个字段）
            name_fields = [
                'INFOPLIST_KEY_CFBundleDisplayName',  # Xcode 13+ 显示名称
                'INFOPLIST_KEY_CFBundleName',          # Xcode 13+ Bundle 名称
                'PRODUCT_NAME'                         # 传统产品名称
            ]
            
            for field in name_fields:
                if info['app_name'] != 'Unknown':
                    break
                name_match = re.search(rf'{field}\s*=\s*([^;]+);', content)
                if name_match:
                    name = name_match.group(1).strip().strip('"')
                    if name and not name.startswith('$('):
                        info['app_name'] = name
                        break
            
            # 提取 Bundle ID（按优先级尝试多个字段）
            bundle_fields = [
                'PRODUCT_BUNDLE_IDENTIFIER',
                'INFOPLIST_KEY_CFBundleIdentifier'
            ]
            
            for field in bundle_fields:
                if info['bundle_id'] != 'Unknown':
                    break
                bundle_match = re.search(rf'{field}\s*=\s*([^;]+);', content)
                if bundle_match:
                    bundle_id = bundle_match.group(1).strip().strip('"')
                    if bundle_id and not bundle_id.startswith('$('):
                        info['bundle_id'] = bundle_id
                        break
            
        except Exception as e:
            print(f"读取 project.pbxproj 出错: {e}")
        
        return info
    
    @staticmethod
    def find_app_icon(project_path: str) -> Optional[str]:
        """查找应用图标"""
        # 查找 Assets.xcassets/AppIcon.appiconset
        for root, dirs, files in os.walk(project_path):
            if 'AppIcon.appiconset' in dirs:
                icon_dir = os.path.join(root, 'AppIcon.appiconset')
                # 查找最大的图标文件
                icon_files = [f for f in os.listdir(icon_dir) if f.endswith('.png')]
                if icon_files:
                    # 优先选择 1024x1024 的图标
                    for icon in icon_files:
                        if '1024' in icon:
                            return os.path.join(icon_dir, icon)
                    # 否则返回第一个
                    return os.path.join(icon_dir, icon_files[0])
        
        return None
    
    @staticmethod
    def find_lproj_folders(project_path: str, ignore_folders: List[str] = None) -> Dict[str, str]:
        """查找所有 .lproj 文件夹"""
        if ignore_folders is None:
            ignore_folders = ['Pods', 'build', 'Build', 'DerivedData', '.git', 'Carthage']
        
        lproj_folders = {}
        
        for root, dirs, files in os.walk(project_path):
            # 排除忽略的目录
            dirs[:] = [d for d in dirs if d not in ignore_folders]
            
            for dir_name in dirs:
                if dir_name.endswith('.lproj'):
                    # 提取语言代码 (例如: en.lproj -> en)
                    lang_code = dir_name.replace('.lproj', '')
                    lproj_path = os.path.join(root, dir_name)
                    lproj_folders[lang_code] = lproj_path
        
        return lproj_folders

