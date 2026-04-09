# Android UI 自动化测试框架

基于 pytest + MuMu模拟器 + ADB 的安卓 UI 自动化测试框架，支持图像识别和 OCR 定位。

## 📋 功能特性

- ✅ **图像识别定位**: 基于 OpenCV 模板匹配
- ✅ **OCR 文字识别**: 基于 PaddleOCR
- ✅ **MuMu模拟器支持**: 原生ADB控制，无需Appium
- ✅ **随机账号登录**: 从账号池中随机选择账号
- ✅ **独立测试文件**: 每个用例文件包含 setup/teardown
- ✅ **自动截图**: 失败时自动保存截图
- ✅ **日志记录**: 详细的测试日志
- ✅ **HTML 报告**: 生成美观的测试报告

## 🚀 快速开始

### 1. 环境准备

#### 软件要求
- Python 3.8+
- 网易MuMu模拟器12 (MuMu Player)
- Windows 操作系统

#### 安装MuMu模拟器
1. 从官网下载 MuMu模拟器12: https://mumu.163.com/
2. 安装到默认路径或自定义路径
3. 创建模拟器实例

### 2. 安装依赖

```bash
# 克隆项目
git clone <repository-url>
cd UIAutotest

# 创建虚拟环境（可选）
python -m venv venv
venv\Scripts\activate

# 安装Python依赖
pip install -r requirements.txt
```

### 3. 配置项目

#### 修改MuMu安装路径
编辑 `utils/devices.py`，修改MuMu安装路径：
```python
MUMU_INSTALL_PATH = r"D:\MuMuPlayer\nx_main"  # 修改为你的MuMu安装路径
```

#### 配置测试账号
编辑 `config/users_info.json`，添加测试账号信息。

### 4. 运行测试

```bash
# 运行所有测试
pytest

# 运行单个测试文件
pytest tests/test01.py -v

# 运行指定测试方法
pytest tests/test01.py::TestClass::test_method -v

# 生成HTML报告
pytest --html=reports/report.html --self-contained-html
```

## 📁 项目结构

```
UIAutotest/
├── conftest.py              # pytest全局配置和fixtures
├── requirements.txt         # Python依赖
├── README.md               # 项目说明
├── config/                 # 配置文件
│   ├── user_data.py        # 用户数据管理
│   └── users_info.json     # 测试账号配置
├── tests/                  # 测试用例
│   └── test01.py           # 示例测试文件
├── utils/                  # 工具模块
│   ├── devices.py          # 设备管理（MuMu模拟器）
│   ├── image_recognition.py # 图像识别
│   ├── ocr_recognition.py  # OCR文字识别
│   ├── user.py             # 用户对象定义
│   └── actions_words/      # 操作封装
│       └── login_actions.py # MuMu操作类
├── templates/              # 图像模板（用于图像识别）
├── screenshots/            # 测试截图
├── reports/                # 测试报告
└── logs/                   # 日志文件
```

## 🔧 核心API

### MuMuActions - 设备操作类

```python
from utils.actions_words.login_actions import MuMuActions

# 初始化
actions = MuMuActions(device_port=7555)

# 点击操作
actions.tap(x=100, y=200)

# 输入文本
actions.input_text("Hello World")

# 按键事件
actions.press_key(keycode=4)  # 返回键

# 截屏
screenshot = actions.take_screenshot()
```

### 图像识别

```python
from utils.image_recognition import aw_find_by_image

# 查找图像位置
position = aw_find_by_image(device_port=7555, template_name="button.png", threshold=0.8)
if position:
    x, y = position
    actions.tap(x, y)
```

### OCR文字识别

```python
from utils.ocr_recognition import aw_find_by_ocr

# 查找文字位置
position = aw_find_by_ocr(device_port=7555, text="确认")
if position:
    x, y = position
    actions.tap(x, y)
```

## 📝 编写测试用例

```python
import pytest
from utils.image_recognition import aw_find_by_image
from utils.ocr_recognition import aw_find_by_ocr
from utils.actions_words.login_actions import MuMuActions

class TestExample:
    """示例测试类"""
    
    def test_login_flow(self, users):
        """测试登录流程"""
        # 获取设备端口
        user = users[0]
        device_port = user.device.device_port
        
        # 初始化操作类
        actions = MuMuActions(device_port)
        
        # 使用图像识别点击登录按钮
        login_btn = aw_find_by_image(device_port, "login_button.png")
        assert login_btn is not None, "未找到登录按钮"
        actions.tap(login_btn[0], login_btn[1])
        
        # 使用OCR识别确认文字
        confirm = aw_find_by_ocr(device_port, "登录成功")
        assert confirm is not None, "登录失败"
```

## 🔗 MuMu模拟器ADB端口规则

| 模拟器实例 | ADB端口 |
|-----------|---------|
| 主实例(0) | 7555    |
| 实例1     | 7556    |
| 实例2     | 7557    |
| 实例N     | 7555+N  |

## 📊 测试报告

测试完成后，HTML报告生成在 `reports/` 目录下。

```bash
# 生成报告
pytest --html=reports/report.html --self-contained-html
```

## 🛠 常见问题

### Q: ADB连接失败？
确保MuMu模拟器已启动，并且端口正确。可以手动测试：
```bash
adb connect 127.0.0.1:7555
adb devices
```

### Q: 图像识别失败？
1. 确保模板图片清晰，分辨率与模拟器匹配
2. 调整threshold阈值（0.6-0.9之间）
3. 检查templates目录下是否有对应图片

### Q: OCR识别不准确？
1. PaddleOCR对中文支持较好
2. 确保文字清晰可见
3. 可以指定region参数限定识别区域

## 📄 许可证

MIT License
