# 大小写匹配功能说明

## 🎯 功能说明

在字符串替换功能中，可以选择是否区分大小写进行匹配。

---

## ⚙️ 配置选项

### 字符串替换 Tab - 扫描配置
```
☐ 扫描 Objective-C 文件 (.m, .mm)
☐ 扫描 Swift 文件 (.swift)
☐ 区分大小写  ← 橙色标记，默认不勾选
```

---

## 🔄 两种模式

### 模式 1: 不区分大小写（默认）⭐ 推荐

#### 匹配逻辑
```
多语言文件:
"action_cancel" = "Cancel";

代码中:
Localized(@"cancel")  ← 小写，也能匹配
Localized(@"CANCEL")  ← 大写，也能匹配
Localized(@"Cancel")  ← 混合，也能匹配

全部替换为:
Localized(@"action_cancel")
```

#### 适用场景
- ✅ 代码中大小写不统一
- ✅ 手动输入可能有大小写差异
- ✅ 容错性要求高

---

### 模式 2: 区分大小写

#### 匹配逻辑
```
多语言文件:
"action_cancel" = "Cancel";

代码中:
Localized(@"Cancel")  ✅ 精确匹配，会替换
Localized(@"cancel")  ❌ 大小写不同，不替换
Localized(@"CANCEL")  ❌ 大小写不同，不替换
```

#### 适用场景
- ✅ 需要精确匹配
- ✅ 避免误替换
- ✅ 大小写有特殊含义

---

## 📊 大小写不匹配的 Key

### 显示位置
在"字符串替换" Tab 左下角的"大小写不匹配的 Key"区域。

### 显示内容
```
以下 Key 在多语言文件中找不到（可能是大小写问题）：

action_Cancel   ← 首字母大写，但文件中是 action_cancel
FINISH_BUTTON   ← 全大写，但文件中是 finish_button
Welcome_Text    ← 驼峰，但文件中是 welcome_text
```

### 使用方法
```
1. 扫描完成后，查看此区域
2. 如果有内容，说明这些 Key 在多语言文件中找不到
3. 可以直接复制去排查：
   - 双击内容全选
   - Cmd+C 复制
   - 在 Xcode 中搜索
4. 检查是否：
   - Key 拼写错误
   - 大小写不一致
   - 多语言文件中缺失
```

---

## 💡 使用建议

### 默认不区分大小写
```
优点：
✅ 容错性好
✅ 匹配率高
✅ 减少手动排查

缺点：
⚠️ 可能误匹配（极少）
```

### 何时启用区分大小写
```
场景 1: 大小写有不同含义
例如: "Yes" vs "yes"

场景 2: 需要精确控制
避免任何误匹配

场景 3: 调试问题
排查为什么某些字符串没被替换
```

---

## 📝 使用示例

### 示例 1: 大小写不统一的代码

#### 多语言文件
```
"action_cancel" = "Cancel";
"action_ok" = "OK";
```

#### 代码中（不统一）
```objc
// 各种大小写
Localized(@"Cancel")   // 首字母大写
Localized(@"cancel")   // 全小写
Localized(@"CANCEL")   // 全大写
Localized(@"OK")       // 全大写
Localized(@"ok")       // 全小写
```

#### 不区分大小写（推荐）
```
✓ 全部匹配并替换为:
Localized(@"action_cancel")
Localized(@"action_ok")
```

#### 区分大小写
```
⚠ 只有精确匹配的会替换:
Localized(@"Cancel")  → action_cancel ✅
Localized(@"cancel")  → 不替换 ❌
Localized(@"CANCEL")  → 不替换 ❌
Localized(@"OK")      → action_ok ✅
Localized(@"ok")      → 不替换 ❌
```

---

### 示例 2: 排查未匹配的 Key

#### 输入的 Key 列表
```
action_cancel
action_ok
welcome_text
FINISH_BUTTON    ← 大写
Start_Button     ← 驼峰
```

#### 多语言文件中
```
"action_cancel" = "Cancel";
"action_ok" = "OK";
"welcome_text" = "Welcome";
"finish_button" = "Finish";  ← 小写
"start_button" = "Start";    ← 小写
```

#### 扫描结果（不区分大小写）
```
大小写不匹配的 Key:
FINISH_BUTTON
Start_Button

原因：
多语言文件中是 finish_button 和 start_button
但输入列表中是 FINISH_BUTTON 和 Start_Button
```

#### 解决方法
```
方法 1: 修正 Key 列表
FINISH_BUTTON → finish_button
Start_Button → start_button

方法 2: 在多语言文件中添加
"FINISH_BUTTON" = "Finish";
"Start_Button" = "Start";
```

---

## 🔍 故障排除

### 问题: 应该匹配的没有匹配

**检查**:
1. 查看"大小写不匹配的 Key"区域
2. 复制 Key 去多语言文件中搜索
3. 对比大小写是否一致

**解决**:
- 修正 Key 的大小写
- 或在多语言文件中添加对应的 Key

### 问题: 不应该匹配的被匹配了

**检查**:
1. 是否启用了"区分大小写"
2. 查看扫描结果中的"原字符串"

**解决**:
- 勾选"区分大小写"
- 或修改多语言文件避免冲突

---

## ✅ 最佳实践

### 1. 默认不区分大小写
大多数情况下，不区分大小写更方便。

### 2. 使用小写 Key
建议在多语言文件中统一使用小写：
```
✓ action_cancel
✓ welcome_text
✓ finish_button

✗ Action_Cancel
✗ WELCOME_TEXT
✗ FinishButton
```

### 3. 扫描后检查
每次扫描后查看"大小写不匹配的 Key"：
- 如果为空：✓ 完美
- 如果有内容：需要排查

### 4. 复制排查
未匹配的 Key 可以直接复制：
```
1. 双击内容全选
2. Cmd+C 复制
3. 在 Xcode 中搜索
4. 检查多语言文件
```

---

**灵活的匹配模式，满足不同需求！** ✨

