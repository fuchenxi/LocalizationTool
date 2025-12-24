# 字符串替换功能指南

## 🎯 功能说明

自动将代码中硬编码的字符串替换为多语言 Key，实现国际化。

---

## 💡 使用场景

### 问题
代码中虽然使用了多语言函数，但传入的是硬编码的 Value 而不是 Key：
```objc
// Objective-C
label.text = Localized(@"取消");        // ❌ 硬编码 Value
button.title = D_Localized(@"确定");    // ❌ 硬编码 Value

// Swift
title = Localized("欢迎使用");          // ❌ 硬编码 Value
subtitle = "开始".localized             // ❌ 硬编码 Value
```

### 解决方案
将函数中的 Value 替换为对应的 Key：
```objc
// Objective-C
label.text = Localized(@"action_cancel");     // ✅ 使用 Key
button.title = D_Localized(@"action_ok");     // ✅ 使用 Key

// Swift
title = Localized("welcome_text");            // ✅ 使用 Key
subtitle = "start_button".localized           // ✅ 使用 Key
```

**工作原理**：
1. 只扫描多语言函数调用中的字符串
2. 检查传入的是 Value 还是 Key
3. 如果是 Value，替换为对应的 Key
4. 保持函数调用格式不变

---

## 🔄 工作流程

### 1. 准备 Key 列表
```
复制需要处理的 Key：
action_cancel
action_ok
welcome_text
...
```

### 2. 粘贴到工具
```
切换到"字符串替换" Tab
    ↓
粘贴 Key 列表到左侧输入框
    ↓
每行一个 Key
```

### 3. 配置扫描选项
```
✓ 扫描 Objective-C 文件 (.m, .mm)
✓ 扫描 Swift 文件 (.swift)
```

### 4. 开始扫描
```
点击"开始扫描"
    ↓
工具会：
1. 读取多语言文件，建立 Value → Key 映射
2. 扫描代码文件，查找硬编码的 Value
3. 在右侧显示所有匹配结果
```

### 5. 查看结果
```
右侧表格显示：
┌──────────────────────────────────────────────┐
│ 文件          │ 行号 │ 原字符串  │ 替换为    │
├──────────────────────────────────────────────┤
│ VC.m          │ 45   │ 取消      │ action_cancel │
│ Helper.swift  │ 123  │ 确定      │ action_ok     │
└──────────────────────────────────────────────┘
```

### 6. 确认替换
```
检查结果无误后
    ↓
点击"确认替换"
    ↓
弹出确认对话框
    ↓
点击"Yes"
    ↓
自动替换所有硬编码字符串
```

### 7. 验证修改
```
在 Xcode 中查看 Git diff
    ↓
确认替换正确
    ↓
提交代码 ✅
```

---

## 📊 界面布局

```
┌───────────────────────────────────────────────────┐
│  左侧 (35%)              右侧 (65%)               │
│  ┌──────────────┐       ┌──────────────────────┐ │
│  │ Key 列表输入 │       │ 扫描结果  发现 X 处  │ │
│  │              │       ├──────────────────────┤ │
│  │ action_cancel│       │ 文件 │ 行 │ 原 │ 新 │ │
│  │ action_ok    │       │ VC.m │ 45│取消│key │ │
│  │ welcome_text │       │ ...  │...│... │... │ │
│  │              │       └──────────────────────┘ │
│  └──────────────┘                                │
│  ┌──────────────┐                                │
│  │ ✓ OC 文件    │                                │
│  │ ✓ Swift文件  │                                │
│  └──────────────┘                                │
│  [🔍 开始扫描]                                   │
│  [🔄 确认替换]                                   │
└───────────────────────────────────────────────────┘
```

---

## 🔍 扫描逻辑

### 建立映射
```
1. 读取所有语言文件夹 (.lproj)
2. 解析 Localizable.strings
3. 建立映射表：
   {
     "取消": "action_cancel",
     "确定": "action_ok",
     "欢迎": "welcome_text"
   }
```

### 扫描代码
```
1. 遍历所有 .m, .mm, .swift 文件
2. 查找字符串字面量：
   - @"..."  (Objective-C)
   - "..."   (Swift/OC)
3. 检查字符串是否在映射表中
4. 跳过已经使用 NSLocalizedString 的
5. 记录文件、行号、原字符串、对应的 Key
```

---

## 🔄 替换规则

### Objective-C
```objc
// 替换前（在多语言函数中使用硬编码 Value）
Localized(@"取消")
D_Localized(@"确定")
enLocalized(@"开始")

// 替换后（替换为 Key）
Localized(@"action_cancel")
D_Localized(@"action_ok")
enLocalized(@"start_button")
```

### Swift
```swift
// 替换前
Localized("取消")
D_Localized("确定")
"欢迎使用".localized

// 替换后
Localized("action_cancel")
D_Localized("action_ok")
"welcome_text".localized
```

### 说明
- ✅ **只扫描多语言函数调用中的字符串**
- ✅ 只替换字符串内容（Value → Key）
- ✅ 保持函数调用格式不变
- ✅ 不添加或移除任何函数包装

---

## ⚠️ 注意事项

### 1. 提交代码
**替换前务必提交当前代码！**
- 方便通过 Git diff 查看修改
- 出错可以快速回滚
- 确保修改可追溯

### 2. 检查结果
替换前仔细查看扫描结果：
- 确认文件路径正确
- 确认行号正确
- 确认原字符串和 Key 的对应关系
- 确认不会误替换

### 3. 验证修改
替换后立即验证：
- 在 Xcode 中查看 Git diff
- 运行项目测试功能
- 确认多语言显示正常

### 4. 已多语言化的代码
工具会自动跳过已经使用多语言函数的代码：

#### Objective-C
```objc
// 已多语言化，会跳过
Localized(@"action_cancel")
LocaRemoveTaglized(@"action_ok")
enLocalized(@"welcome_text")
D_Localized(@"title")
D_enLocalized(@"subtitle")

// 硬编码，会替换
@"取消"
```

#### Swift
```swift
// 已多语言化，会跳过
Localized("action_cancel")
D_Localized("action_ok")
LocalizedFormat("welcome_text", args)
locaRemoveTaglized("title")
"key".localized

// 硬编码，会替换
"取消"
```

#### 支持的自定义函数
- `Localized()`
- `LocaRemoveTaglized()` / `locaRemoveTaglized()`
- `enLocalized()`
- `D_Localized()`
- `D_enLocalized()`
- `LocalizedFormat()`
- `LocalizedFormatValue()`
- `.localized` (Swift 属性语法)

---

## 📝 使用示例

### 示例 1: 批量替换按钮文字

#### 1. 准备 Key 列表
```
action_cancel
action_ok
action_confirm
action_delete
```

#### 2. 扫描结果
```
┌────────────────────────────────────────────┐
│ ViewController.m  │ 45  │ 取消  │ action_cancel  │
│ ViewController.m  │ 67  │ 确定  │ action_ok      │
│ SettingsVC.m      │ 123 │ 确认  │ action_confirm │
│ Helper.swift      │ 89  │ 删除  │ action_delete  │
└────────────────────────────────────────────┘
```

#### 3. 替换后
```objc
// ViewController.m 第 45 行
// 之前: button.setTitle(Localized(@"取消"), for: .normal);
// 之后: button.setTitle(Localized(@"action_cancel"), for: .normal);
```

---

### 示例 2: 替换 Swift 代码

#### 多语言文件
```
"welcome_text" = "欢迎使用 ChillFit";
"start_button" = "开始";
```

#### 代码中
```swift
// 之前（函数中传入硬编码 Value）
titleLabel.text = Localized("欢迎使用 ChillFit")
startButton.setTitle("开始".localized, for: .normal)

// 之后（替换为 Key）
titleLabel.text = Localized("welcome_text")
startButton.setTitle("start_button".localized, for: .normal)
```

### 示例 3: ChillFit 实际场景

#### 多语言文件
```
"measure_heart_rate" = "测量心率";
"action_cancel" = "取消";
"finish_button" = "完成";
```

#### 代码中
```objc
// 之前
measureLabel.text = D_Localized(@"测量心率");
cancelBtn.title = Localized(@"取消");
finishBtn.title = enLocalized(@"完成");

// 之后
measureLabel.text = D_Localized(@"measure_heart_rate");
cancelBtn.title = Localized(@"action_cancel");
finishBtn.title = enLocalized(@"finish_button");
```

---

## 🎨 视觉设计

### 表格颜色
```
原字符串列: 🟠 橙色背景 (#FFF3E0) + 橙色文字
替换为列:   🟢 绿色背景 (#E8F5E9) + 绿色文字
```

**语义**：
- 橙色 = 警告（需要替换）
- 绿色 = 安全（替换后的结果）

### 按钮颜色
```
扫描按钮: 蓝色渐变
替换按钮: 橙色渐变（警告操作）
```

---

## ⚡ 性能优化

### 智能跳过
- 自动排除 Pods、build 等目录
- 只扫描 .m, .mm, .swift 文件
- 跳过已多语言化的代码

### 批量处理
- 按文件分组处理
- 从后往前替换（避免行号偏移）
- 一次写入，减少 I/O

---

## 🔍 故障排除

### 问题：扫描时间太长
**原因**：项目文件太多

**解决**：
- 确认排除了 Pods 目录
- 取消不需要的文件类型
- 项目正常情况下 1-5 秒内完成

### 问题：未找到匹配
**原因**：
- Key 对应的 Value 在代码中不存在
- Value 已经被替换为多语言 Key

**解决**：
- 检查多语言文件中的 Value
- 手动在代码中搜索确认

### 问题：误替换
**原因**：相同的字符串在不同上下文有不同含义

**解决**：
- 查看扫描结果，取消勾选不需要替换的
- 或手动在 Git diff 中恢复误替换的部分

---

## 💡 最佳实践

### 1. 分批处理
不要一次粘贴太多 Key，建议：
- 10-20 个 Key 一批
- 扫描 → 检查 → 替换 → 验证
- 重复此流程

### 2. 先测试
先用几个 Key 测试：
- 确认功能正常
- 熟悉工作流程
- 再批量处理

### 3. 及时提交
每批替换完成后立即提交：
- 小步提交，易于回滚
- Commit 信息清晰
- 便于 Code Review

### 4. 运行测试
替换后运行项目：
- 确认界面显示正常
- 确认多语言切换正常
- 确认无编译错误

---

## 📋 工作清单

```
□ 提交当前代码
□ 准备 Key 列表
□ 粘贴到工具
□ 开始扫描
□ 检查结果
□ 确认替换
□ 查看 Git diff
□ 运行测试
□ 提交修改
```

---

**让国际化变得简单！** 🌍✨

