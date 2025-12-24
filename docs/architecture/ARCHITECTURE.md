# 项目架构说明

## 📁 目录结构

```
iOS-LocalizationTool/
├── main.py                         # 程序入口（简洁）
├── main_old.py                     # 旧版本备份
├── requirements.txt                # 依赖列表
├── README.md                       # 使用说明
├── ARCHITECTURE.md                 # 架构说明（本文件）
│
├── models/                         # 业务逻辑层（Model）
│   ├── __init__.py
│   ├── localization_parser.py     # 多语言文件解析器
│   └── project_info.py            # iOS 项目信息提取器
│
├── views/                          # 视图层（View）
│   ├── __init__.py
│   ├── main_window.py             # 主窗口（控制器功能）
│   ├── info_tab.py                # 项目信息标签页
│   ├── deduplicate_tab.py         # 查重去重标签页
│   └── import_tab.py              # 导入多语言标签页
│
├── workers/                        # 后台工作线程
│   ├── __init__.py
│   ├── scan_worker.py             # 扫描重复项线程
│   ├── deduplicate_worker.py      # 删除重复项线程
│   └── import_worker.py           # 导入多语言线程
│
└── utils/                          # 工具模块
    ├── __init__.py
    └── constants.py                # 常量定义（样式、配置等）
```

## 🏗️ 设计模式

### MVC 架构
采用 **MVC (Model-View-Controller)** 设计模式：

- **Model（models/）**: 负责数据处理和业务逻辑
  - `LocalizationParser`: .strings 文件的解析、写入、去重
  - `ProjectInfoExtractor`: iOS 项目信息提取

- **View（views/）**: 负责 UI 界面展示
  - `MainWindow`: 主窗口，同时承担 Controller 职责
  - `InfoTab`: 项目信息展示
  - `DeduplicateTab`: 查重去重界面
  - `ImportTab`: 导入多语言界面

- **Controller（views/main_window.py）**: 控制逻辑
  - 事件处理
  - 数据流转
  - 状态管理

### 多线程模式
使用 **QThread** 进行耗时操作，避免 UI 阻塞：

- `ScanDuplicatesWorker`: 后台扫描重复项
- `DeduplicateWorker`: 后台删除重复项
- `ImportWorker`: 后台导入多语言文件

### 模块化设计
- **高内聚**: 每个模块职责单一明确
- **低耦合**: 模块间通过接口交互
- **易扩展**: 新增功能只需添加新的 Tab 和 Worker

## 📋 各模块职责

### models/localization_parser.py
**职责**: 处理 .strings 文件的所有操作
- `parse_strings_file()`: 解析文件为字典
- `write_strings_file()`: 写入字典到文件
- `append_strings_with_version()`: 追加内容带版本号注释
- `remove_duplicates()`: 删除重复项
- `count_duplicates()`: 统计重复项数量

### models/project_info.py
**职责**: 提取 iOS 项目信息
- `find_info_plist()`: 查找 Info.plist 文件
- `get_app_info()`: 获取 App 名称、版本号、Bundle ID
- `find_app_icon()`: 查找 App 图标
- `find_lproj_folders()`: 查找所有语言文件夹

### workers/scan_worker.py
**职责**: 后台扫描重复项
- 继承 QThread
- 发送进度信号
- 返回扫描结果

### workers/deduplicate_worker.py
**职责**: 后台删除重复项
- 继承 QThread
- 发送进度信号
- 返回删除数量

### workers/import_worker.py
**职责**: 后台导入多语言
- 继承 QThread
- 解压 zip 文件
- 导入到对应语言文件
- 添加版本号注释

### views/main_window.py
**职责**: 主窗口和控制逻辑
- 管理 Tab 切换
- 处理用户交互
- 协调 Model 和 Worker
- 更新 View 显示

### views/info_tab.py
**职责**: 展示项目信息
- App 图标
- App 名称
- 版本号
- Bundle ID
- Info.plist 路径

### views/deduplicate_tab.py
**职责**: 查重去重界面
- 忽略文件夹配置
- 扫描按钮
- 结果显示
- 确认删除按钮

### views/import_tab.py
**职责**: 导入多语言界面
- ZIP 文件选择
- 导入按钮

### utils/constants.py
**职责**: 全局常量定义
- 默认配置
- 样式表
- 常用常量

## 🔄 数据流

### 扫描重复项流程
```
用户点击"扫描" 
    ↓
MainWindow.scan_duplicates() 
    ↓
创建 ScanDuplicatesWorker 
    ↓
Worker 调用 ProjectInfoExtractor.find_lproj_folders()
    ↓
Worker 调用 LocalizationParser.count_duplicates()
    ↓
发送 progress 信号 → 更新 UI
    ↓
发送 finished 信号 → MainWindow.on_scan_finished()
    ↓
更新 DeduplicateTab 显示结果
```

### 删除重复项流程
```
用户确认删除
    ↓
MainWindow.confirm_delete_duplicates()
    ↓
创建 DeduplicateWorker
    ↓
Worker 调用 LocalizationParser.remove_duplicates()
    ↓
发送 progress 信号 → 更新 UI
    ↓
发送 finished 信号 → MainWindow.on_delete_finished()
    ↓
显示删除结果
```

### 导入多语言流程
```
用户选择 ZIP 并确认
    ↓
MainWindow.import_strings()
    ↓
创建 ImportWorker
    ↓
解压 ZIP 文件
    ↓
调用 ProjectInfoExtractor.find_lproj_folders()
    ↓
调用 LocalizationParser.append_strings_with_version()
    ↓
发送 progress 信号 → 更新 UI
    ↓
发送 finished 信号 → MainWindow.on_import_finished()
    ↓
显示导入结果
```

## 🎯 优势

### 1. 可维护性
- 代码结构清晰，每个文件职责单一
- 修改某个功能不影响其他模块

### 2. 可扩展性
- 新增功能只需添加新的 Tab 和对应的 Worker
- 例如：添加"导出多语言"功能
  1. 创建 `views/export_tab.py`
  2. 创建 `workers/export_worker.py`
  3. 在 `main_window.py` 中注册

### 3. 可测试性
- Model 层可独立测试业务逻辑
- Worker 层可测试异步操作
- View 层可测试 UI 交互

### 4. 可读性
- 文件名即功能名
- 代码结构一目了然
- 新人容易上手

## 🔧 如何添加新功能

### 示例：添加"导出多语言"功能

1. **创建 Worker**
```python
# workers/export_worker.py
class ExportWorker(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def run(self):
        # 导出逻辑
        pass
```

2. **创建 View**
```python
# views/export_tab.py
class ExportTab(QWidget):
    def __init__(self):
        # UI 初始化
        pass
```

3. **在 MainWindow 中注册**
```python
# views/main_window.py
self.export_tab = ExportTab()
self.export_tab.export_btn.clicked.connect(self.export_strings)
self.tab_widget.addTab(self.export_tab, "📤 导出多语言")
```

4. **添加事件处理**
```python
def export_strings(self):
    self.export_worker = ExportWorker(...)
    self.export_worker.finished.connect(self.on_export_finished)
    self.export_worker.start()
```

## 📝 代码规范

- 所有文件使用 UTF-8 编码
- 使用中文注释和文档字符串
- 遵循 PEP 8 代码风格
- 类名使用 PascalCase
- 函数名使用 snake_case
- 常量使用 UPPER_CASE

## 🚀 未来优化方向

1. **配置文件**: 将用户设置保存到配置文件
2. **日志系统**: 使用 logging 模块替代 print
3. **单元测试**: 添加 pytest 测试用例
4. **异常处理**: 更详细的错误处理和用户提示
5. **国际化**: 支持多语言界面（i18n）

