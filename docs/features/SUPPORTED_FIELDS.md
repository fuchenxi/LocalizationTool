# 支持的配置字段

## 📋 完整字段列表

工具支持从 `Info.plist` 和 `project.pbxproj` 读取以下配置字段。

---

## 📱 版本号 (Version)

### Info.plist
```xml
<key>CFBundleShortVersionString</key>
<string>1.2.0</string>
```

### project.pbxproj（按优先级）
```
1. MARKETING_VERSION = 1.2.0;                              ← 推荐，Xcode 11+
2. INFOPLIST_KEY_CFBundleShortVersionString = 1.2.0;      ← Xcode 13+
3. CURRENT_PROJECT_VERSION = 1;                            ← 构建号
```

### 读取优先级
```
1. Info.plist: CFBundleShortVersionString
   ↓ (如果是变量或未找到)
2. project.pbxproj: MARKETING_VERSION
   ↓ (如果未找到)
3. project.pbxproj: INFOPLIST_KEY_CFBundleShortVersionString
   ↓ (如果未找到)
4. project.pbxproj: CURRENT_PROJECT_VERSION
```

---

## 🏷️ App 名称 (App Name)

### Info.plist
```xml
<!-- 优先级 1: 显示名称 -->
<key>CFBundleDisplayName</key>
<string>ChillFit</string>

<!-- 优先级 2: Bundle 名称 -->
<key>CFBundleName</key>
<string>ChillFit</string>
```

### project.pbxproj（按优先级）
```
1. INFOPLIST_KEY_CFBundleDisplayName = ChillFit;          ← 推荐，Xcode 13+ ⭐
2. INFOPLIST_KEY_CFBundleName = ChillFit;                 ← Xcode 13+
3. PRODUCT_NAME = ChillFit;                                ← 传统方式
```

### 读取优先级
```
1. Info.plist: CFBundleDisplayName
   ↓ (如果未找到)
2. Info.plist: CFBundleName
   ↓ (如果是变量或未找到)
3. project.pbxproj: INFOPLIST_KEY_CFBundleDisplayName  ⭐ 你的项目用这个
   ↓ (如果未找到)
4. project.pbxproj: INFOPLIST_KEY_CFBundleName
   ↓ (如果未找到)
5. project.pbxproj: PRODUCT_NAME
```

---

## 🆔 Bundle ID

### Info.plist
```xml
<key>CFBundleIdentifier</key>
<string>com.company.chillfit</string>
```

### project.pbxproj（按优先级）
```
1. PRODUCT_BUNDLE_IDENTIFIER = com.company.chillfit;      ← 推荐
2. INFOPLIST_KEY_CFBundleIdentifier = com.company.chillfit; ← Xcode 13+
```

### 读取优先级
```
1. Info.plist: CFBundleIdentifier
   ↓ (如果是变量或未找到)
2. project.pbxproj: PRODUCT_BUNDLE_IDENTIFIER
   ↓ (如果未找到)
3. project.pbxproj: INFOPLIST_KEY_CFBundleIdentifier
```

---

## 🔄 读取流程

### 完整流程图
```
开始
  ↓
查找 .xcodeproj
  ↓
查找 Info.plist
  ↓
从 Info.plist 读取 (如果存在)
  ↓
检查是否有 Unknown 字段
  ↓
从 project.pbxproj 补充信息
  ↓
合并结果
  ↓
显示在界面
```

### 代码逻辑
```python
# 1. 从 Info.plist 读取
info = read_from_plist()

# 2. 如果有字段是 Unknown，从 pbxproj 补充
if info['version'] == 'Unknown' or info['app_name'] == 'Unknown':
    pbxproj_info = read_from_pbxproj()
    
    # 补充缺失的字段
    if info['version'] == 'Unknown':
        info['version'] = pbxproj_info['version']
    
    if info['app_name'] == 'Unknown':
        info['app_name'] = pbxproj_info['app_name']
    
    # ... 其他字段
```

---

## 📊 常见项目类型

### 类型 1: 传统项目（Xcode 12 及以前）

#### Info.plist
```xml
<key>CFBundleShortVersionString</key>
<string>1.2.0</string>
<key>CFBundleDisplayName</key>
<string>ChillFit</string>
```

#### project.pbxproj
```
PRODUCT_NAME = "$(TARGET_NAME)";
PRODUCT_BUNDLE_IDENTIFIER = com.company.chillfit;
```

#### 读取结果
```
✓ 版本号: 1.2.0 (来自 Info.plist)
✓ App 名称: ChillFit (来自 Info.plist)
✓ Bundle ID: com.company.chillfit (来自 project.pbxproj)
```

---

### 类型 2: 现代项目（Xcode 13+）⭐

#### Info.plist
```xml
<key>CFBundleShortVersionString</key>
<string>$(MARKETING_VERSION)</string>
<key>CFBundleDisplayName</key>
<string>$(INFOPLIST_KEY_CFBundleDisplayName)</string>
```

#### project.pbxproj
```
MARKETING_VERSION = 1.2.0;
INFOPLIST_KEY_CFBundleDisplayName = ChillFit;  ← 你的项目
PRODUCT_BUNDLE_IDENTIFIER = com.company.chillfit;
```

#### 读取结果
```
⚠ Info.plist 中是变量引用
✓ 版本号: 1.2.0 (来自 project.pbxproj: MARKETING_VERSION)
✓ App 名称: ChillFit (来自 project.pbxproj: INFOPLIST_KEY_CFBundleDisplayName)
✓ Bundle ID: com.company.chillfit (来自 project.pbxproj)
```

---

### 类型 3: 简化项目

#### 没有 Info.plist

#### project.pbxproj
```
MARKETING_VERSION = 1.2.0;
INFOPLIST_KEY_CFBundleDisplayName = ChillFit;
PRODUCT_BUNDLE_IDENTIFIER = com.company.chillfit;
```

#### 读取结果
```
⚠ 未找到 Info.plist 文件，将尝试从 project.pbxproj 读取
✓ 版本号: 1.2.0 (来自 project.pbxproj)
✓ App 名称: ChillFit (来自 project.pbxproj)
✓ Bundle ID: com.company.chillfit (来自 project.pbxproj)
```

---

## 🔍 变量过滤

### 常见变量引用
```
$(MARKETING_VERSION)      ← 跳过
$(TARGET_NAME)            ← 跳过
$(PRODUCT_NAME)           ← 跳过
$(PRODUCT_BUNDLE_IDENTIFIER) ← 跳过
```

### 过滤逻辑
```python
if value.startswith('$('):
    # 这是变量引用，不是实际值，跳过
    continue
```

---

## 📝 Xcode 13+ 新字段

Xcode 13 引入了新的配置方式，使用 `INFOPLIST_KEY_` 前缀：

| 旧字段 (Info.plist) | 新字段 (project.pbxproj) |
|---------------------|--------------------------|
| CFBundleShortVersionString | INFOPLIST_KEY_CFBundleShortVersionString |
| CFBundleDisplayName | INFOPLIST_KEY_CFBundleDisplayName ⭐ |
| CFBundleName | INFOPLIST_KEY_CFBundleName |
| CFBundleIdentifier | INFOPLIST_KEY_CFBundleIdentifier |

**工具已全面支持新旧两种方式！** ✅

---

## 💡 为什么读取不到？

### 检查清单

#### 1. 检查项目路径
```
✓ 是否选择了正确的项目根目录？
✓ 目录中是否包含 .xcodeproj 文件？
```

#### 2. 检查日志
```
查看日志中的信息：
- 是否找到 .xcodeproj？
- 是否找到 Info.plist？
- 读取了哪些字段？
```

#### 3. 手动检查 project.pbxproj
```bash
# 打开 project.pbxproj 文件
open ProjectName.xcodeproj/project.pbxproj

# 搜索以下字段
INFOPLIST_KEY_CFBundleDisplayName
MARKETING_VERSION
PRODUCT_BUNDLE_IDENTIFIER
```

---

## 🎯 你的项目 (ChillFit)

根据你提供的信息：

```
INFOPLIST_KEY_CFBundleDisplayName = ChillFit;
```

**现在工具已支持此字段！** 应该能正确读取到 "ChillFit" 了。

### 预期日志输出
```
正在加载项目信息...
✓ 找到 Xcode 项目: YourProject.xcodeproj
✓ 找到 Info.plist: YourPath/Info.plist
✓ 成功读取版本号: 1.2.0
✓ 成功读取应用名称: ChillFit          ← 应该能看到这个
✓ 成功读取 Bundle ID: com.xxx.chillfit
✓ 项目信息加载完成: ChillFit v1.2.0
```

---

**请重新选择项目路径，应该能正确读取 ChillFit 了！** 🎉

