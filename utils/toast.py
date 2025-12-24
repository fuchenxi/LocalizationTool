#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Toast 提示组件
"""

from PyQt6.QtWidgets import QLabel, QGraphicsOpacityEffect
from PyQt6.QtCore import QTimer, QPropertyAnimation, QEasingCurve, Qt, QPoint
from PyQt6.QtGui import QFont


class Toast(QLabel):
    """Toast 提示框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("""
            QLabel {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                  stop:0 rgba(52, 199, 89, 240),
                                                  stop:1 rgba(48, 176, 79, 240));
                color: white;
                padding: 12px 24px;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 600;
                border: 2px solid rgba(255, 255, 255, 100);
            }
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 透明度效果
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        
    @staticmethod
    def show_toast(parent, message: str, duration: int = 2000):
        """显示 Toast 提示
        
        Args:
            parent: 父窗口
            message: 提示信息
            duration: 显示时长（毫秒），默认 2000ms
        """
        toast = Toast(parent)
        toast.setText(message)
        toast.adjustSize()
        
        # 计算位置（父窗口底部居中）
        if parent:
            parent_rect = parent.geometry()
            toast_width = toast.width()
            toast_height = toast.height()
            
            # 在父窗口底部，向上偏移 60px
            x = parent_rect.x() + (parent_rect.width() - toast_width) // 2
            y = parent_rect.y() + parent_rect.height() - toast_height - 60
            
            toast.move(x, y)
        
        # 显示
        toast.show()
        
        # 淡入动画
        toast.fade_in()
        
        # 定时淡出并关闭
        QTimer.singleShot(duration - 300, toast.fade_out)
        QTimer.singleShot(duration, toast.close)
    
    def fade_in(self):
        """淡入动画"""
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(200)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.animation.start()
    
    def fade_out(self):
        """淡出动画"""
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.animation.start()

