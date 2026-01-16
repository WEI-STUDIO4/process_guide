# Skill Axis Assistance Prompt

一个专业的GUI应用程序，用于录制、管理和引导用户按特定顺序执行键盘鼠标操作。支持组合键、鼠标事件和自定义引导提示。

![版本](https://img.shields.io/badge/版本-2.0-blue)
![Python](https://img.shields.io/badge/Python-3.6%2B-green)
![许可证](https://img.shields.io/badge/许可证-MIT-yellow)

## 🌟 主要特性

### 🎯 核心功能
- **智能录制**：录制键盘按键、鼠标点击、滚轮操作及组合键
- **SAAP格式**：专有文件格式，保存完整工序方案
- **实时引导**：独立置顶窗口显示当前操作提示
- **循环模式**：支持无限循环训练，ESC键随时退出
- **全面支持**：Ctrl、Alt、Shift等修饰键完美支持

### 🎨 个性化设置
- **颜色自定义**：可调文字颜色、背景颜色
- **透明背景**：支持半透明提示窗口
- **置顶显示**：无边框窗口，始终显示在最前
- **屏幕定位**：自动定位在屏幕右上角

### 📁 文件管理
- **专有格式**：`.saap` (Skill Axis Assistance Prompt) 扩展名
- **完整元数据**：创建时间、修改时间、工序数量
- **导入导出**：标准JSON兼容，便于数据交换
- **自动加载**：智能加载最近使用文件

## 📦 安装要求

### 基础要求
- Python 3.6 或更高版本
- tkinter库（Python自带）

### 可选依赖（用于录制功能）
```bash
pip install keyboard mouse
```

### 快速开始
```bash
# 克隆仓库
git clone https://github.com/yourusername/process-key-guide.git
cd process-key-guide

# 安装依赖
pip install -r requirements.txt

# 运行程序
python process_guide.py
```

## 🚀 使用方法

### 1. 创建新方案
1. 点击"新建"按钮创建空白方案
2. 使用"添加工序"手动添加步骤
3. 或使用"录制工序"自动录制操作序列

### 2. 录制工序
```plaintext
支持的操作类型：
• 单个按键：A, 1, F1, ESC, SPACE, ENTER
• 组合按键：Ctrl+C, Shift+A, Ctrl+Shift+S
• 鼠标操作：左键、右键、滚轮上下
• 组合鼠标：Ctrl+左键，Shift+滚轮
```

### 3. 开始引导
1. 添加至少一个工序
2. 点击"开始引导"按钮
3. 屏幕右上角显示提示窗口
4. 按提示执行操作
5. 按ESC键可随时退出

### 4. 文件操作
- **保存**：保存到当前`.saap`文件
- **另存为**：导出为新`.saap`文件
- **加载**：打开现有`.saap`文件
- **自动保存**：程序关闭时自动保存设置

## 🗂️ 文件结构

```
process-key-guide/
├── process_guide.py      # 主程序文件
├── requirements.txt      # 依赖说明
├── README.md            # 说明文档
├── build.py             # 打包脚本（可选）
├── default.saap         # 示例方案文件
└── docs/                # 详细文档
    ├── tutorial.md      # 使用教程
    └── api-reference.md # API参考
```

## 📊 SAAP文件格式

### 文件结构
```json
{
  "metadata": {
    "format": "SAAP",
    "version": "1.0",
    "created": "2026-01-16 10:30:00",
    "modified": "2026-01-16 10:35:00",
    "process_count": 5
  },
  "settings": {
    "loop_guide": false,
    "text_color": "#FF0000",
    "bg_color": "#FFFF00",
    "transparent": false
  },
  "processes": [
    {
      "display_name": "步骤1",
      "key": "CTRL+C"
    }
  ]
}
```

### 扩展名含义
- **SAAP**：Skill Axis Assistance Prompt
- **.saap**：专用格式，确保数据完整性
- **兼容性**：可导入导出为标准JSON

## 🔧 开发指南

### 代码结构
```python
# 核心类
- SAAPFileManager      # 文件管理
- GuideWindow         # 引导窗口
- KeyEventRecorder    # 事件录制
- ProcessGuideApp     # 主应用
- RecordProcessesDialog # 录制对话框
- ProcessDialog       # 工序对话框
```

### 扩展开发
1. **插件系统**：添加自定义操作处理器
2. **脚本支持**：支持Python脚本定义复杂工序
3. **网络同步**：多设备间同步方案
4. **统计分析**：记录训练数据和效果

### 打包发布
```bash
# 使用提供的打包脚本
python build.py

# 生成文件
dist/ProcessKeyGuide.exe       # 可执行文件
dist/ProcessKeyGuide-windows.zip # 打包文件
```

## 🎮 使用场景

### 教育培训
- **软件教学**：Photoshop、Office等软件操作培训
- **游戏训练**：游戏连招、技能组合练习
- **数据录入**：标准化数据输入流程

### 生产力工具
- **工作流自动化**：重复性操作序列化
- **测试验证**：软件功能测试步骤
- **辅助工具**：为特殊需求用户提供操作引导

### 专业应用
- **工业控制**：设备操作流程标准化
- **医疗设备**：医疗设备操作培训
- **实验室操作**：实验步骤精确执行

## 🛠️ 技术特点

### 跨平台兼容
- 基于Python和tkinter，支持Windows、macOS、Linux
- 轻量级依赖，易于部署
- 原生UI体验，响应迅速

### 性能优化
- 异步事件处理，不阻塞UI
- 内存高效，支持大型工序序列
- 实时响应，延迟低于50ms

### 安全性
- 本地文件存储，数据不外传
- 无网络连接要求
- 开源代码，可审计

## 📈 版本历史

### v2.0 (当前)
- 新增SAAP专用文件格式
- 支持组合键和鼠标操作
- 改进的事件录制系统
- 优化的用户界面

### v1.0
- 基础工序管理功能
- 独立引导窗口
- 颜色自定义
- 循环模式支持

## 🤝 贡献指南

我们欢迎各种形式的贡献！

### 报告问题
1. 在Issues页面创建新问题
2. 描述问题的详细步骤
3. 附上相关截图或错误信息

### 提交代码
1. Fork本仓库
2. 创建功能分支 (`git checkout -b feature/新功能`)
3. 提交更改 (`git commit -m '添加新功能'`)
4. 推送到分支 (`git push origin feature/新功能`)
5. 创建Pull Request

### 代码规范
- 遵循PEP 8代码风格
- 添加适当的注释
- 编写单元测试
- 更新相关文档

## 📝 许可证

本项目采用MIT许可证。详见 [LICENSE](LICENSE) 文件。

## 📞 联系方式

- **GitHub Issues**: [报告问题](https://github.com/yourusername/process-key-guide/issues)
- **邮箱**: your-email@example.com
- **讨论区**: [GitHub Discussions](https://github.com/yourusername/process-key-guide/discussions)

## 🙏 致谢

感谢所有贡献者和用户的支持！

### 特别感谢
- `keyboard` 和 `mouse` 库的开发者
- 所有提交反馈的用户
- 开源社区的持续支持

---

**提示**: 首次使用建议查看 `docs/tutorial.md` 中的详细教程。

**Star ⭐ 本项目如果对你有帮助！**
