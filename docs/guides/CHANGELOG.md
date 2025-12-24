# 更新日志

## 🔧 重要修复 - 删除重复项逻辑

### 问题
之前的 `remove_duplicates` 方法会：
- ❌ 删除所有注释
- ❌ 删除所有空行
- ❌ 重写整个文件
- ❌ 导致 Git diff 显示整个文件都变更

### 修复后
现在的 `remove_duplicates` 方法会：
- ✅ 保留所有注释（`//` 和 `/* */`）
- ✅ 保留所有空行
- ✅ 保留文件原有结构
- ✅ 只删除重复的 key-value 行
- ✅ Git diff 只显示删除的行

### 示例对比

#### 原始文件
```objc
// App 配置
"app_name" = "MyApp";

// 按钮文字
"action_cancel" = "Cancel";  // 第一次出现
"action_ok" = "OK";

//<!-- ========== 1.0.0 新增 ========== -->
"new_feature" = "New Feature";
//<!-- ========== 1.0.0 新增 ========== -->

// 重复了
"action_cancel" = "取消";  // 第二次出现（保留这个）
```

#### 删除后（之前的错误方式）
```objc
"app_name" = "MyApp";
"action_ok" = "OK";
"new_feature" = "New Feature";
"action_cancel" = "取消";
```
❌ 所有注释和空行都没了！

#### 删除后（修复后的正确方式）
```objc
// App 配置
"app_name" = "MyApp";

// 按钮文字
"action_ok" = "OK";

//<!-- ========== 1.0.0 新增 ========== -->
"new_feature" = "New Feature";
//<!-- ========== 1.0.0 新增 ========== -->

// 重复了
"action_cancel" = "取消";  // 第二次出现（保留这个）
```
✅ 只删除了重复的那一行，其他完全保留！

### Git Diff 效果

#### 之前（整个文件都变了）
```diff
- // App 配置
- "app_name" = "MyApp";
- 
- // 按钮文字
- "action_cancel" = "Cancel";
- "action_ok" = "OK";
- 
- //<!-- ========== 1.0.0 新增 ========== -->
- "new_feature" = "New Feature";
- //<!-- ========== 1.0.0 新增 ========== -->
- 
- // 重复了
- "action_cancel" = "取消";
+ "app_name" = "MyApp";
+ "action_ok" = "OK";
+ "new_feature" = "New Feature";
+ "action_cancel" = "取消";
```

#### 修复后（只显示删除的行）
```diff
  // App 配置
  "app_name" = "MyApp";
  
  // 按钮文字
- "action_cancel" = "Cancel";
  "action_ok" = "OK";
  
  //<!-- ========== 1.0.0 新增 ========== -->
  "new_feature" = "New Feature";
  //<!-- ========== 1.0.0 新增 ========== -->
  
  // 重复了
  "action_cancel" = "取消";
```

完美！✨

---

## 📝 技术细节

### 新算法流程

```python
# 1. 读取文件，保留所有行（包括注释和空行）
lines = read_all_lines()

# 2. 第一遍扫描：记录每个 key 出现的所有行号
for line in lines:
    if is_key_value(line):
        key_positions[key].append(line_number)

# 3. 第二遍：标记要删除的行号
for key, positions in key_positions:
    if len(positions) > 1:
        # 保留最后一个，删除前面的
        lines_to_remove.add(positions[:-1])

# 4. 第三遍：重写文件，跳过标记的行
for i, line in enumerate(lines):
    if i not in lines_to_remove:
        write(line)
```

### 关键改进
1. **保留原始行**：不重新格式化，原样保留
2. **只标记重复行**：不影响其他内容
3. **最小化变更**：只删除必要的行
4. **Git 友好**：diff 清晰易读

---

**现在删除重复项是安全且优雅的！** ✅

