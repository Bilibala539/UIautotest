"""
Appium 配置文件
包含设备配置、应用配置和服务器配置
"""

# 设备和应用配置
DESIRED_CAPABILITIES = {
    "platformName": "Android",
    "platformVersion": "11.0",
    "deviceName": "emulator-5554",  # 通过 adb devices 查看
    "appPackage": "com.example.app",  # 替换为实际应用包名
    "appActivity": ".MainActivity",   # 替换为实际主Activity
    "automationName": "UiAutomator2",
    "noReset": True,        # 不重置应用状态
    "fullReset": False,     # 不完全重置
    "newCommandTimeout": 300,
    "unicodeKeyboard": True,
    "resetKeyboard": True,
    "autoGrantPermissions": True,  # 自动授予权限
    "ensureWebviewsHavePages": True,
    "acceptInsecureCerts": True
}

# Appium 服务器配置
APPIUM_SERVER_CONFIG = {
    "host": "127.0.0.1",
    "port": 4723,
    "url": "http://127.0.0.1:4723/wd/hub"
}

# 等待配置
WAIT_CONFIG = {
    "implicit_wait": 10,    # 隐式等待时间（秒）
    "explicit_wait": 30,    # 显式等待时间（秒）
    "polling_interval": 0.5 # 轮询间隔（秒）
}

# 图像识别配置
IMAGE_RECOGNITION_CONFIG = {
    "default_threshold": 0.8,
    "template_path": "./templates/"
}

# OCR配置 - PaddleOCR专用
OCR_CONFIG = {
    "lang": "ch",           # 语言: ch(中文), en(英文), fr(法语)等
    "use_gpu": False,       # 是否使用GPU加速
    "det_db_box_thresh": 0.5,    # 检测框阈值
    "det_db_unclip_ratio": 1.6   # 检测框扩展比例
}