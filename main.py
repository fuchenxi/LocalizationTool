#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iOS 多语言管理工具 - 主入口
功能：
1. 选择项目路径，提取并展示 App 图标、版本号、App 名称
2. 一键查重、删除重复的 key-value，只保留最后一个
3. 选择下载的 zip 包，一键导入到项目对应的语言文件中
"""

import sys
from PyQt6.QtWidgets import QApplication
from views import MainWindow


def main():
    """程序入口"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # 使用 Fusion 风格
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
