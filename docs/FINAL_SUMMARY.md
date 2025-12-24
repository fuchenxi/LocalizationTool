# iOS 多语言管理工具 - 完整功能总结

## 🎯 工具概述

一个专为 iOS 开发者打造的多语言管理工具，支持 ChillFit 等项目的自定义多语言处理逻辑。

---

## ✨ 四大核心功能

### 1. 📱 项目信息展示
- 自动提取 App 图标（圆角显示，填充满）
- 显示 App 名称（支持 Xcode 13+ 的 INFOPLIST_KEY_CFBundleDisplayName）
- 显示版本号（支持 MARKETING_VERSION）
- 显示 Bundle ID
- 多源读取：Info.plist + project.pbxproj

### 2. 🔍 查重去重
- **左右分栏布局** - 配置区 (30%) + 结果区 (70%)
- **按语言分 Tab** - 每个语言独立显示
- **详细表格** - Key、Value、行号、出现次数、操作
- **颜色区分** - 🟠 橙色标题行，🔴 红色重复行
- **双击复制** - 任意单元格双击复制内容，Toast 提示
- **点击打开** - 在 Xcode 中打开文件并跳转到对应行
- **安全删除** - 保留所有注释和空行，Git diff 只显示删除的行

### 3. 📥 导入多语言
- **智能 ZIP 列表** - 自动扫描文件夹，列出所有 ZIP
- **按时间排序** - 最新文件在最上面，默认选中
- **文件信息** - 显示名称、大小、修改时间
- **灵活选择** - 可更改文件夹，可刷新列表
- **版本注释** - 导入内容用版本号注释包裹

### 4. 🔄 字符串替换 ⭐ 新功能
- **自动扫描** - 根据 Key 列表查找硬编码字符串
- **智能跳过** - 自动识别已多语言化的代码
- **支持自定义函数** - Localized()、D_Localized() 等
- **预览结果** - 显示文件、行号、原字符串、替换后的 Key
- **简单替换** - 只替换字符串内容，不添加函数包装

---

## 🎨 设计特色

### 现代化 UI
- 🍎 苹果风格设计语言
- 💫 渐变按钮、圆角卡片
- 🎨 iOS 配色方案
- ✨ 丰富的交互反馈

### Toast 提示
- 💚 绿色渐变背景
- 🔘 圆角 + 白边
- 💫 淡入淡出动画
- ⏱️ 1.5 秒后自动消失

### 统一规范
- 📐 统一的字号（11-15px）
- 📏 统一的间距（8-30px）
- 🎨 统一的颜色（#007AFF 蓝色主题）
- 🔘 统一的圆角（4-20px）

---

## 🛠️ 技术架构

### MVC 设计模式
```
models/      - 业务逻辑（数据处理）
views/       - UI 界面（界面组件）
workers/     - 后台线程（异步任务）
utils/       - 工具模块（常量、Toast）
```

### 代码组织
```
15 个模块文件
平均 50-200 行/文件
职责清晰，易于维护
```

### 文档完善
```
docs/
├── architecture/ - 架构设计（3 份）
├── features/     - 功能特性（4 份）
└── guides/       - 使用指南（8 份）
```

---

## 🎯 支持的项目配置

### Xcode 13+ 配置字段
```
✅ INFOPLIST_KEY_CFBundleDisplayName  (App 名称)
✅ INFOPLIST_KEY_CFBundleName
✅ MARKETING_VERSION  (版本号)
✅ PRODUCT_BUNDLE_IDENTIFIER  (Bundle ID)
```

### 传统配置字段
```
✅ CFBundleDisplayName
✅ CFBundleName
✅ CFBundleShortVersionString
✅ CFBundleIdentifier
```

### 自定义多语言函数
```
OC:
✅ Localized(@"")
✅ LocaRemoveTaglized(@"")
✅ enLocalized(@"")
✅ D_Localized(@"")
✅ D_enLocalized(@"")

Swift:
✅ Localized("")
✅ D_Localized("")
✅ LocalizedFormat("", args)
✅ locaRemoveTaglized("")
✅ "".localized
```

---

## 🔄 字符串替换逻辑

### 替换效果

#### Objective-C
```objc
// 替换前
button.setTitle(@"取消", for: .normal);
label.text = @"确定";

// 替换后
button.setTitle(@"action_cancel", for: .normal);
label.text = @"action_ok";
```

#### Swift
```swift
// 替换前
button.setTitle("取消", for: .normal)
label.text = "欢迎"

// 替换后
button.setTitle("action_cancel", for: .normal)
label.text = "welcome_text"
```

### 跳过规则
```
以下代码不会被替换（已多语言化）：
✅ Localized(@"action_cancel")
✅ D_Localized("action_ok")
✅ "welcome_text".localized
✅ LocaRemoveTaglized(@"title")
```

---

## 📋 完整工作流程

### 典型使用场景
```
1. 打开工具，选择项目路径
   ↓
2. 查看项目信息（App 名称、版本号、图标）
   ↓
3. 查重去重
   - 扫描重复项
   - 双击复制内容
   - 点击"打开"查看上下文
   - 确认删除
   ↓
4. 导入多语言
   - 查看 ZIP 列表（最新的已选中）
   - 点击导入
   ↓
5. 字符串替换（可选）
   - 粘贴 Key 列表
   - 扫描硬编码字符串
   - 查看结果
   - 确认替换
   ↓
6. 在 Xcode 中查看 Git diff
   ↓
7. 测试并提交代码 ✅
```

---

## 🎁 核心优势

### 1. 高效
- ⚡ 自动化操作，减少手动工作
- ⚡ 智能列表，快速定位文件
- ⚡ 多线程处理，界面不卡顿

### 2. 安全
- 🛡️ 保留文件结构（注释、空行）
- 🛡️ Git 友好（最小化变更）
- 🛡️ 二次确认（危险操作）

### 3. 智能
- 🧠 多源读取配置
- 🧠 自动跳过已多语言化的代码
- 🧠 智能排序和选择

### 4. 专业
- 💎 现代化 UI 设计
- 💎 完整的文档体系
- 💎 清晰的代码架构

---

## 📊 数据统计

### 代码规模
```
入口文件: 29 行
模块文件: 15 个
总代码量: ~2000 行
文档数量: 15 份
```

### 支持的操作
```
4 个主要功能 Tab
10+ 种配置字段
8+ 种多语言函数
3+ 种文件类型
```

---

## 🚀 快速开始

### 安装
```bash
pip install -r requirements.txt
```

### 运行
```bash
python3 main.py
```

### 使用
1. 选择项目路径
2. 根据需要切换不同的 Tab
3. 按照界面提示操作
4. 查看操作日志了解进度

---

## 📚 完整文档

查看 [docs/README.md](docs/README.md) 获取所有文档索引。

### 推荐阅读
- **新用户**: [QUICKSTART.md](docs/architecture/QUICKSTART.md)
- **功能说明**: [FEATURES.md](docs/features/FEATURES.md)
- **字符串替换**: [STRING_REPLACE_GUIDE.md](docs/guides/STRING_REPLACE_GUIDE.md)
- **导入指南**: [IMPORT_GUIDE.md](docs/guides/IMPORT_GUIDE.md)

---

## 💡 特色功能亮点

### ⭐ 最有用的功能
1. **智能 ZIP 列表** - 自动选中最新文件，省去手动查找
2. **双击复制 + Toast** - 快速提取信息，优雅反馈
3. **点击打开文件** - 在 Xcode 中精准定位
4. **字符串替换** - 批量替换硬编码，自动国际化
5. **保留文件结构** - Git diff 清晰，易于 Review

### 🏆 设计理念
- **简单** - 操作直观，无需学习
- **高效** - 减少重复劳动
- **安全** - 保留原有结构
- **专业** - 企业级品质

---

**一个为 iOS 开发者精心打造的专业工具！** 🎊

