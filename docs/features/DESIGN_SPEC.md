# 设计规范文档

## 🎨 统一设计规范

本文档定义了 iOS 多语言管理工具的所有 UI 设计规范，确保整个应用的一致性和专业性。

---

## 📐 尺寸规范

### 间距
```
页面边距 (Padding):
├── 主 Tab 内容区: 30px (顶部) 30px (其他)
├── 查重 Tab 特殊: 15px (更紧凑)
└── 组件间距: 12-20px

组件内部间距:
├── GroupBox 内部: 8-12px
├── 布局间距: 8-15px
└── 按钮间距: 10px
```

### 组件高度
```
输入框 (QLineEdit): 32px
按钮 (QPushButton): 38px (标准) / 32px (小)
表格行高: 32px
图标尺寸: 100x100px
```

### 字号
```
标题: 14px (font-weight: 600)
正文: 13px (font-weight: 500)
次要文字: 12px
提示文字: 11px
辅助文字: 11px (color: #8E8E93)
表格内容: 12px
日志文字: 11px (等宽字体)
```

---

## 🎨 颜色规范

### 主色调
```
主蓝色 (Primary Blue):
├── #007AFF - 主色
├── #0051D5 - Hover
└── #003DA5 - Pressed

背景色:
├── #F5F5F7 - 页面背景
├── #FFFFFF - 卡片背景
└── #F0F0F5 - 浅色背景块
```

### 文字颜色
```
├── #1D1D1F - 主文字 (深灰)
├── #666666 - 说明文字 (中灰)
└── #8E8E93 - 辅助文字 (浅灰)
```

### 边框颜色
```
├── #E5E5EA - 标准边框
└── #007AFF - Focus 边框
```

### 状态颜色
```
成功 (Success):
└── #34C759 - 绿色

警告 (Warning):
├── #FF9500 - 橙色
├── #FFF3E0 - 橙色浅背景
└── #E65100 - 橙色深文字

错误 (Error):
├── #FF3B30 - 红色
├── #FFEBEE - 红色浅背景
└── #C62828 - 红色深文字
```

### 表格颜色
```
标题行 (Header):
├── 背景: #FFF3E0 (橙色浅)
├── 文字: #E65100 (橙色深)
└── 字重: Bold

重复行 (Duplicate):
├── 背景: #FFEBEE (红色浅)
├── 文字: #C62828 (红色深)
└── 字重: Normal

表格网格线:
└── #E5E5EA
```

---

## 🔘 组件规范

### 按钮 (QPushButton)

#### 标准按钮
```css
padding: 10px 20px;
border-radius: 8px;
font-size: 13px;
font-weight: 500;
min-height: 38px;

渐变背景:
- 正常: #007AFF → #0051D5
- Hover: #0051D5 → #003DA5
- Pressed: #003DA5
- Disabled: #E5E5EA (文字: #8E8E93)
```

#### 删除按钮 (危险操作)
```css
渐变背景:
- 正常: #FF3B30 → #D32F26
- Hover: #D32F26 → #B71C1C
- Pressed: #B71C1C
```

#### 小按钮 (如"浏览")
```css
width: 70px;
min-height: 32px;
```

### 输入框 (QLineEdit)
```css
padding: 10px 12px;
border: 2px solid #E5E5EA;
border-radius: 8px;
font-size: 13px;
min-height: 32px;

Focus 状态:
border: 2px solid #007AFF;
```

### 分组框 (QGroupBox)
```css
font-weight: 600;
font-size: 14px;
border: 2px solid #E5E5EA;
border-radius: 10px;
background: white;
margin-top: 16px;
padding-top: 16px;
```

### 标签页 (QTabWidget)
```css
Tab:
- padding: 10px 20px
- font-size: 13px
- font-weight: 500
- border-radius: 8px 8px 0 0

Selected:
- background: white
- color: #007AFF
- border-bottom: 3px solid #007AFF

Hover (未选中):
- background: #E5E5EA
```

### 表格 (QTableWidget)
```css
font-size: 12px;
gridline-color: #E5E5EA;
border: 2px solid #E5E5EA;
border-radius: 8px;

Item:
- padding: 6px
- row-height: 32px

Header:
- background: #F5F5F7
- font-weight: 600
- border-bottom: 2px solid #E5E5EA

Selected:
- background: #007AFF
- color: white
```

### 文本框 (QTextEdit)
```css
border: 2px solid #E5E5EA;
border-radius: 8px;
padding: 8px;
font-size: 11px;
font-family: 'SF Mono', 'Menlo', monospace;
```

---

## 📱 各标签页规范

### 项目信息 Tab
```
边距: 30px
间距: 40px (横向)

图标:
- 尺寸: 100x100px
- 圆角: 18px
- 边框: 2px solid #E5E5EA
- 背景: #F5F5F7

信息文字:
- 主信息: 14px, font-weight: 500
- 路径信息: 12px, color: #8E8E93
- 行间距: 12px
```

### 查重去重 Tab
```
主布局: 左右分栏 (Splitter)
- 初始比例: 30% : 70%
- 可拖动调整

左侧配置区:
- 边距: 15px
- 间距: 12px
- 按钮高度: 38px

右侧结果区:
- 标题: 14px, font-weight: 600
- 统计信息: 12px, 圆角卡片
- Tab 按语言分组
- 表格显示详细信息
```

### 导入多语言 Tab
```
边距: 30px
间距: 20px

说明文字:
- 字号: 12px
- 背景: #F0F0F5
- 圆角: 6px

输入框: 32px
按钮: 38px
```

---

## 🎯 交互规范

### Hover 效果
```
按钮: 背景渐变加深
Tab: 背景变为 #E5E5EA
输入框: 无变化 (Focus 才有边框变化)
```

### Focus 效果
```
输入框: 边框变为 #007AFF
Tab: 无特殊效果 (Selected 有底部边框)
```

### Press 效果
```
按钮: 背景变为最深色
```

### Disabled 效果
```
按钮: 
- 背景: #E5E5EA
- 文字: #8E8E93

输入框: 
- 背景: #F5F5F7
```

---

## 📊 表格数据展示规范

### 重复项表格

#### 颜色语义
```
标题行 (每组重复项的第一行):
- 背景: #FFF3E0 (橙色浅)
- 文字: #E65100 (橙色深)
- 字重: Bold
- 含义: 这是重复项的主 key

重复行 (重复的行):
- 背景: #FFEBEE (红色浅)
- 文字: #C62828 (红色深)
- 字重: Normal
- 含义: 这些是重复的值
```

#### 列宽设置
```
Key: 220px (可调整)
Value: 自动伸缩 (Stretch)
行号: 自适应内容 (ResizeToContents)
出现次数: 自适应内容 (ResizeToContents)
```

#### 数据显示规则
```
Key 列: 每个重复项的所有行都显示
Value 列: 显示具体值
行号: 显示文件中的行号
出现次数: 只在第一行显示 "X 次"
```

---

## 🔤 字体规范

### 系统字体
```
macOS: SF Pro / SF Mono
Windows: Segoe UI / Consolas
Linux: -apple-system, Ubuntu
```

### 等宽字体 (代码/日志)
```
优先级:
1. SF Mono (macOS)
2. Menlo (macOS 备选)
3. Consolas (Windows)
4. monospace (通用)
```

---

## ✅ 检查清单

### 新增组件时需要检查：
- [ ] 字号是否符合规范 (11-14px)
- [ ] 间距是否合理 (8-30px)
- [ ] 颜色是否使用规范色
- [ ] 圆角是否统一 (4-10px)
- [ ] 边框是否使用 #E5E5EA
- [ ] Hover/Focus/Press 状态是否定义
- [ ] Disabled 状态是否定义
- [ ] 与其他组件是否协调

### 修改现有组件时需要确认：
- [ ] 不影响其他组件的视觉一致性
- [ ] 字号、颜色、间距保持统一
- [ ] 符合整体设计语言

---

## 📝 设计原则

1. **一致性优先**: 相同类型的组件保持一致的样式
2. **层次清晰**: 通过字号、颜色、间距建立视觉层次
3. **留白充足**: 避免拥挤，给内容呼吸空间
4. **颜色克制**: 只在需要强调的地方使用强色
5. **交互明确**: 状态变化要明显但不突兀
6. **易于阅读**: 字号适中，对比度足够
7. **专业简洁**: 避免过度装饰，保持专业感

---

**遵循本规范，确保应用的一致性和专业性！** ✨

