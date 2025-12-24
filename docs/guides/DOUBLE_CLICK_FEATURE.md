# 双击跳转功能

## 🎯 功能说明

在扫描结果的表格中，**双击任意行**可以直接在外部编辑器中打开对应的 `.strings` 文件，并自动跳转到该行。

---

## 💡 使用方法

### 1. 扫描重复项
点击"开始扫描重复项"按钮，等待扫描完成。

### 2. 查看结果
在右侧的语言 Tab 中查看扫描结果。

### 3. 双击跳转
在表格中**双击任意一行**：
- 自动在编辑器中打开对应的 `.strings` 文件
- 光标自动定位到对应的行号

---

## 🖥️ 支持的编辑器

程序会按以下优先级尝试打开编辑器：

| 编辑器 | 方式 | 跳转支持 | 优先级 |
|--------|------|----------|--------|
| **Xcode** | AppleScript | ✅ 在已打开的项目中打开 | 1 |
| **VSCode** | `code` | ✅ 精确跳转到行 | 2 |
| **Sublime Text** | `subl` | ✅ 精确跳转到行 | 3 |
| **Atom** | `atom` | ✅ 精确跳转到行 | 4 |
| **系统默认** | `open` | ⚠️ 仅打开文件 | 5 |

### ⭐ Xcode 特殊优化

如果您的 Xcode 项目已经打开，双击表格行时会：
1. ✅ **激活已打开的 Xcode 窗口**
2. ✅ **在当前项目中打开对应文件**
3. ✅ **自动跳转到指定行号**

**无需打开新窗口，直接在您的项目中定位！** 🎯

---

## 🔧 配置编辑器

### VSCode (推荐)

确保 `code` 命令已安装：

```bash
# 在 VSCode 中按 Cmd+Shift+P
# 输入 "Shell Command: Install 'code' command in PATH"
# 点击安装
```

验证：
```bash
which code
# 应输出: /usr/local/bin/code
```

### Xcode

Xcode 自带 `xed` 命令，无需配置。

验证：
```bash
which xed
# 应输出: /usr/bin/xed
```

### Sublime Text

添加到 PATH：
```bash
# 创建软链接
ln -s "/Applications/Sublime Text.app/Contents/SharedSupport/bin/subl" /usr/local/bin/subl
```

验证：
```bash
which subl
# 应输出: /usr/local/bin/subl
```

---

## 📊 跳转示例

### 双击前
```
┌────────────────────────────────────────┐
│ Key          Value         行号  次数 │
├────────────────────────────────────────┤
│ action_cancel  Cancel      12    2   │  ← 双击这一行
│ action_cancel  取消        935       │
└────────────────────────────────────────┘
```

### 双击后
```
VSCode 自动打开:
/path/to/project/en.lproj/Localizable.strings

并跳转到第 12 行:
   11|
   12| "action_cancel" = "Cancel";  ← 光标在这里
   13|
```

---

## 🎨 视觉提示

### 鼠标悬停
- 鼠标移到表格行上时，光标变为**手型**（pointer）
- 提示可以点击

### 工具提示
- 鼠标悬停在表格上会显示：
  > 💡 双击任意行可在编辑器中打开对应文件并跳转到该行

---

## 🔍 技术细节

### 数据存储
每个表格单元格使用 `Qt.ItemDataRole.UserRole` 存储行号：
```python
item.setData(Qt.ItemDataRole.UserRole, line_num)
```

### 文件路径
表格对象保存文件路径：
```python
table.file_path = "/path/to/en.lproj/Localizable.strings"
```

### 打开命令

不同编辑器的命令格式：

#### Xcode（优先）- AppleScript
```applescript
tell application "Xcode"
    activate
    open "/path/to/file.strings"
    
    -- 跳转到第 12 行
    tell application "System Events"
        keystroke "l" using {command down}  -- Cmd+L
        keystroke "12"
        keystroke return
    end tell
end tell
```

**优势**：
- ✅ 在已打开的 Xcode 项目中打开文件
- ✅ 无需打开新窗口
- ✅ 保持当前工作环境

#### VSCode
```bash
code -g /path/to/file.strings:12
```

#### Sublime Text
```bash
subl /path/to/file.strings:12
```

#### Atom
```bash
atom /path/to/file.strings:12
```

#### 系统默认（降级方案）
```bash
# 如果 AppleScript 失败，使用 xed
xed -l 12 /path/to/file.strings

# 如果没有找到任何编辑器
open /path/to/file.strings
```

---

## ⚡ 快速工作流

1. **扫描重复项** → 查看结果
2. **双击某一行** → 在编辑器中打开
3. **查看上下文** → 决定保留哪个
4. **返回工具** → 点击"确认删除重复项"
5. **完成** → Git 只显示删除的行

---

## 🐛 故障排除

### 双击没反应
**可能原因**：
- 没有安装支持的编辑器
- 编辑器命令未添加到 PATH

**解决方法**：
1. 检查是否安装了 VSCode、Xcode 等编辑器
2. 运行 `which code` 检查命令是否可用
3. 如果命令不存在，按上面的"配置编辑器"说明添加

### 只打开文件，没有跳转到行
**可能原因**：
- 使用了系统默认的 `open` 命令
- 默认编辑器不支持行号参数

**解决方法**：
- 安装并配置 VSCode 或其他支持的编辑器

### 打开了错误的文件
**可能原因**：
- 文件路径有误（极少发生）

**解决方法**：
- 检查扫描日志，确认文件路径正确

---

## 💡 使用技巧

### 1. 快速查看上下文
双击可以快速看到重复项前后的代码，帮助你决定保留哪个。

### 2. 批量检查
在不同的语言 Tab 之间切换，双击查看各个语言的重复项。

### 3. 对比值的差异
双击第一个值，查看内容，然后关闭。
再双击第二个值，对比差异。

### 4. 验证删除结果
删除重复项后，双击剩余的行，确认保留的是正确的值。

---

**享受高效的工作流！** ✨

