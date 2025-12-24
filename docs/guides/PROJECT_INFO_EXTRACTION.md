# 项目信息提取说明

## 🎯 多源读取策略

工具会从**多个位置**读取项目信息，确保最大兼容性。

---

## 📁 信息来源

### 优先级 1: Info.plist
```
位置: 
- ProjectName/Info.plist
- ProjectName/Resources/Info.plist
- ProjectName/Supporting Files/Info.plist

读取字段:
- CFBundleShortVersionString → 版本号
- CFBundleName → App 名称
- CFBundleDisplayName → App 显示名称
- CFBundleIdentifier → Bundle ID
```

### 优先级 2: project.pbxproj
```
位置:
- ProjectName.xcodeproj/project.pbxproj

读取字段（按优先级）:

版本号:
1. MARKETING_VERSION
2. INFOPLIST_KEY_CFBundleShortVersionString (Xcode 13+)
3. CURRENT_PROJECT_VERSION

App 名称:
1. INFOPLIST_KEY_CFBundleDisplayName (Xcode 13+) ⭐ 新增
2. INFOPLIST_KEY_CFBundleName (Xcode 13+)
3. PRODUCT_NAME

Bundle ID:
1. PRODUCT_BUNDLE_IDENTIFIER
2. INFOPLIST_KEY_CFBundleIdentifier
```

### 合并策略
```
如果 Info.plist 中缺失某个字段
    ↓
尝试从 project.pbxproj 读取
    ↓
补充缺失的信息
```

---

## 🔍 查找逻辑

### 1. 查找 .xcodeproj

#### 查找顺序
```
1. 在项目根目录查找 *.xcodeproj
2. 在子目录中查找（只搜索一层）
```

#### 示例
```
/Users/xxx/MyProject/
├── MyProject.xcodeproj/  ← 在这里找到
│   └── project.pbxproj
├── MyProject/
│   └── Info.plist
└── ...
```

### 2. 查找 Info.plist

#### 查找策略
```
递归搜索，优先选择最浅层级的 Info.plist
排除目录: Pods, build, Build, DerivedData, .git, Carthage
```

#### 优先级
```
深度 1: ProjectName/Info.plist           ← 优先
深度 2: ProjectName/Resources/Info.plist
深度 3: ProjectName/App/Info.plist
...
```

---

## 📊 读取示例

### 场景 1: 标准项目结构

#### 项目结构
```
MyApp/
├── MyApp.xcodeproj/
│   └── project.pbxproj
├── MyApp/
│   ├── Info.plist       ← 包含所有信息
│   └── ...
└── ...
```

#### 读取结果
```
✓ 找到 Xcode 项目: MyApp.xcodeproj
✓ 找到 Info.plist: MyApp/Info.plist
✓ 成功读取版本号: 1.2.0
✓ 成功读取应用名称: MyApp
✓ 成功读取 Bundle ID: com.company.myapp
```

### 场景 2: Info.plist 信息不全

#### 项目结构
```
MyApp/
├── MyApp.xcodeproj/
│   └── project.pbxproj  ← 包含 MARKETING_VERSION
├── MyApp/
│   └── Info.plist       ← 版本号是变量 $(MARKETING_VERSION)
└── ...
```

#### Info.plist 内容
```xml
<key>CFBundleShortVersionString</key>
<string>$(MARKETING_VERSION)</string>
```

#### 读取过程
```
1. 读取 Info.plist → version = "$(MARKETING_VERSION)" (变量)
2. 发现是变量，标记为 Unknown
3. 读取 project.pbxproj → version = "1.2.0"
4. 补充版本号信息
```

#### 读取结果
```
✓ 找到 Xcode 项目: MyApp.xcodeproj
✓ 找到 Info.plist: MyApp/Info.plist
⚠ Info.plist 中版本号是变量
✓ 从 project.pbxproj 读取版本号: 1.2.0
✓ 成功读取应用名称: MyApp
✓ 成功读取 Bundle ID: com.company.myapp
```

### 场景 3: 无 Info.plist

#### 项目结构
```
MyApp/
├── MyApp.xcodeproj/
│   └── project.pbxproj  ← 所有信息都在这里
└── MyApp/
    └── (没有 Info.plist)
```

#### 读取过程
```
1. 查找 Info.plist → 未找到
2. 直接读取 project.pbxproj
3. 提取所有可用信息
```

#### 读取结果
```
✓ 找到 Xcode 项目: MyApp.xcodeproj
⚠ 未找到 Info.plist 文件，将尝试从 project.pbxproj 读取
✓ 从 project.pbxproj 读取版本号: 1.2.0
✓ 从 project.pbxproj 读取应用名称: MyApp
✓ 从 project.pbxproj 读取 Bundle ID: com.company.myapp
```

---

## 🔧 project.pbxproj 解析

### 文件格式
project.pbxproj 是一个文本格式的项目配置文件。

### 关键配置

#### 版本号
```
MARKETING_VERSION = 1.2.0;
```
或
```
CURRENT_PROJECT_VERSION = 1;
```

#### 产品名称
```
PRODUCT_NAME = MyApp;
```
或
```
PRODUCT_NAME = "$(TARGET_NAME)";  ← 变量，跳过
```

#### Bundle ID
```
PRODUCT_BUNDLE_IDENTIFIER = com.company.myapp;
```

### 正则表达式

#### 提取版本号
```python
re.search(r'MARKETING_VERSION\s*=\s*([^;]+);', content)
```

#### 提取产品名称
```python
re.search(r'PRODUCT_NAME\s*=\s*([^;]+);', content)
```

#### 提取 Bundle ID
```python
re.search(r'PRODUCT_BUNDLE_IDENTIFIER\s*=\s*([^;]+);', content)
```

### 变量过滤
```python
# 跳过变量引用
if name.startswith('$('):
    # 这是变量，不是实际值
    continue
```

---

## ✅ 支持的项目类型

### ✓ 标准 iOS 项目
- 有 Info.plist
- 有 .xcodeproj
- 配置在 plist 中

### ✓ 现代 iOS 项目
- Info.plist 中使用变量
- 实际配置在 project.pbxproj
- 使用 MARKETING_VERSION

### ✓ 简化项目
- 无 Info.plist
- 所有配置在 project.pbxproj

### ✓ 复杂项目
- 多个 Target
- 多个 Info.plist
- 使用 xcconfig 文件

---

## 🔍 调试信息

### 日志输出示例

#### 成功读取
```
正在加载项目信息...
✓ 找到 Xcode 项目: MyApp.xcodeproj
✓ 找到 Info.plist: MyApp/Info.plist
✓ 成功读取版本号: 1.2.0
✓ 成功读取应用名称: MyApp
✓ 成功读取 Bundle ID: com.company.myapp
✓ 成功加载应用图标
✓ 项目信息加载完成: MyApp v1.2.0
```

#### 部分失败
```
正在加载项目信息...
✓ 找到 Xcode 项目: MyApp.xcodeproj
⚠ 未找到 Info.plist 文件，将尝试从 project.pbxproj 读取
✓ 成功读取版本号: 1.2.0
✓ 成功读取应用名称: MyApp
⚠ 无法读取 Bundle ID
⚠ 未找到应用图标
⚠ 部分项目信息未能读取，功能不受影响
```

---

## 💡 故障排除

### 问题：所有信息都是 Unknown

#### 可能原因
1. 项目路径不正确
2. 不是标准的 Xcode 项目
3. Info.plist 和 project.pbxproj 都使用变量

#### 解决方法
1. 确认选择的是项目根目录（包含 .xcodeproj 的目录）
2. 检查日志，查看查找过程
3. 手动查看 project.pbxproj 确认配置位置

### 问题：版本号读取错误

#### 可能原因
1. 读取到了测试 Target 的 Info.plist
2. 版本号是变量引用

#### 解决方法
1. 查看日志中显示的 Info.plist 路径
2. 如果路径不对，可能需要调整项目结构
3. 工具会自动尝试从 project.pbxproj 读取

---

## 🎯 最佳实践

### 项目结构建议
```
ProjectName/
├── ProjectName.xcodeproj/
│   └── project.pbxproj           ← 包含 MARKETING_VERSION
├── ProjectName/
│   ├── Info.plist                ← 主 Target 的配置
│   ├── Assets.xcassets/
│   │   └── AppIcon.appiconset/
│   └── *.lproj/
│       └── Localizable.strings
└── ...
```

### 配置建议
- 版本号统一在 project.pbxproj 中设置 MARKETING_VERSION
- Info.plist 中使用 `$(MARKETING_VERSION)` 引用
- Bundle ID 在 project.pbxproj 中设置

---

**现在支持多种项目结构，兼容性更强！** ✨

