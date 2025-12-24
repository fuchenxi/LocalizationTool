# 快速入门指南

## 📦 项目结构

```
iOS-LocalizationTool/
├── 📄 main.py                      # 入口文件（20行代码）
├── 📄 main_old.py                  # 旧版本备份
├── 📄 requirements.txt             # 依赖列表
├── 📄 README.md                    # 使用说明
├── 📄 ARCHITECTURE.md              # 架构详细说明
├── 📄 QUICKSTART.md                # 本文件
│
├── 📁 models/                      # 业务逻辑（纯数据处理）
│   ├── localization_parser.py     # .strings 文件解析/写入/去重
│   └── project_info.py            # iOS 项目信息提取
│
├── 📁 views/                       # UI 界面（纯界面组件）
│   ├── main_window.py             # 主窗口 + 控制器
│   ├── info_tab.py                # 项目信息页面
│   ├── deduplicate_tab.py         # 查重去重页面
│   └── import_tab.py              # 导入多语言页面
│
├── 📁 workers/                     # 后台线程（异步任务）
│   ├── scan_worker.py             # 扫描重复项
│   ├── deduplicate_worker.py      # 删除重复项
│   └── import_worker.py           # 导入多语言
│
└── 📁 utils/                       # 工具和配置
    └── constants.py                # 常量（样式、默认配置）
```

## 🎯 核心设计理念

### 单一职责原则
- **Models**: 只负责数据处理，不知道 UI 存在
- **Views**: 只负责界面展示，不包含业务逻辑
- **Workers**: 只负责后台任务，通过信号通信
- **MainWindow**: 作为控制器，协调各模块

### 模块独立性
每个文件都可以独立理解和修改：
- 修改解析逻辑 → 只改 `models/localization_parser.py`
- 修改界面样式 → 只改 `views/xxx_tab.py` 或 `utils/constants.py`
- 添加新功能 → 添加新的 tab 和 worker

## 📝 代码量统计

| 文件 | 行数 | 职责 |
|------|------|------|
| main.py | ~20 | 程序入口 |
| models/localization_parser.py | ~140 | 文件解析/去重 |
| models/project_info.py | ~100 | 项目信息提取 |
| workers/scan_worker.py | ~60 | 扫描线程 |
| workers/deduplicate_worker.py | ~50 | 删除线程 |
| workers/import_worker.py | ~100 | 导入线程 |
| views/main_window.py | ~300 | 主控制器 |
| views/info_tab.py | ~60 | 信息页面 |
| views/deduplicate_tab.py | ~100 | 去重页面 |
| views/import_tab.py | ~60 | 导入页面 |
| utils/constants.py | ~70 | 常量定义 |
| **总计** | **~1060** | **vs 旧版 1026** |

> 代码量基本不变，但结构清晰 100 倍！

## 🔍 如何阅读代码

### 1️⃣ 从入口开始
```python
# main.py - 只有 20 行
from views import MainWindow

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
```

### 2️⃣ 查看主窗口
```python
# views/main_window.py
class MainWindow(QMainWindow):
    def __init__(self):
        # 创建 3 个 Tab
        self.info_tab = InfoTab()
        self.deduplicate_tab = DeduplicateTab()
        self.import_tab = ImportTab()
        
        # 连接事件
        self.deduplicate_tab.scan_btn.clicked.connect(self.scan_duplicates)
```

### 3️⃣ 理解数据流
```
用户点击按钮
    ↓
MainWindow 处理事件
    ↓
创建 Worker 线程
    ↓
Worker 调用 Model 处理数据
    ↓
发送信号更新 View
```

## 🛠️ 修改示例

### 例子 1: 修改按钮样式
```python
# 只需修改 utils/constants.py
LARGE_BUTTON_STYLE = """
    QPushButton {
        font-size: 18px;  # 从 16px 改为 18px
        font-weight: bold;
    }
"""
```

### 例子 2: 修改去重逻辑
```python
# 只需修改 models/localization_parser.py
@staticmethod
def remove_duplicates(file_path: str) -> int:
    # 在这里修改去重算法
    # 不需要关心 UI 和线程
    pass
```

### 例子 3: 添加新功能
```bash
# 1. 创建新的 Tab
touch views/export_tab.py

# 2. 创建新的 Worker  
touch workers/export_worker.py

# 3. 在 main_window.py 中注册
# self.export_tab = ExportTab()
# self.tab_widget.addTab(self.export_tab, "📤 导出")
```

## 🎨 设计模式应用

### MVC 模式
- **Model**: `models/` - 数据和业务逻辑
- **View**: `views/*_tab.py` - UI 组件
- **Controller**: `views/main_window.py` - 事件处理

### 观察者模式
- Worker 发送信号 (progress, finished)
- MainWindow 监听信号并更新 UI

### 策略模式
- `LocalizationParser` 提供多种策略：
  - 解析、写入、追加、去重、统计

## 📊 依赖关系

```
main.py
  └─ views/main_window.py
       ├─ views/info_tab.py
       ├─ views/deduplicate_tab.py
       ├─ views/import_tab.py
       ├─ models/project_info.py
       ├─ models/localization_parser.py
       ├─ workers/scan_worker.py
       ├─ workers/deduplicate_worker.py
       ├─ workers/import_worker.py
       └─ utils/constants.py
```

### 依赖方向
- Views → Models ✅ (View 可以使用 Model)
- Models → Views ❌ (Model 不知道 View)
- Workers → Models ✅ (Worker 调用 Model)
- Models ← → Models ❌ (Model 之间独立)

## 🚀 扩展指南

### 添加"批量重命名"功能

1. **创建 Model 方法**
```python
# models/localization_parser.py
@staticmethod
def rename_keys(file_path: str, old_prefix: str, new_prefix: str):
    # 实现重命名逻辑
    pass
```

2. **创建 Worker**
```python
# workers/rename_worker.py
class RenameWorker(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def run(self):
        LocalizationParser.rename_keys(...)
```

3. **创建 View**
```python
# views/rename_tab.py
class RenameTab(QWidget):
    def __init__(self):
        # 添加输入框、按钮等 UI
        pass
```

4. **在 MainWindow 注册**
```python
# views/main_window.py
self.rename_tab = RenameTab()
self.rename_tab.rename_btn.clicked.connect(self.rename_keys)
self.tab_widget.addTab(self.rename_tab, "✏️ 批量重命名")
```

## 💡 最佳实践

### ✅ 好的做法
- 新功能添加新文件，不修改现有文件
- 每个类/函数只做一件事
- 使用类型提示（typing）
- 添加文档字符串
- 信号槽机制通信

### ❌ 避免的做法
- 不要在 Model 中导入 PyQt
- 不要在 View 中写业务逻辑
- 不要在主线程做耗时操作
- 不要在一个文件中混合多个职责

## 📚 学习路径

1. **初级**: 阅读 `main.py` 和 `views/main_window.py`
2. **中级**: 理解 Models 和 Workers 的实现
3. **高级**: 添加新功能，修改现有逻辑
4. **专家**: 重构优化，添加测试

## 🔗 相关文档

- [README.md](README.md) - 使用说明
- [ARCHITECTURE.md](ARCHITECTURE.md) - 详细架构说明
- [requirements.txt](requirements.txt) - 依赖列表

---

**设计原则**: 简单、清晰、可维护 > 一切

如有疑问，查看对应模块的代码即可，每个文件都很短小易懂！

