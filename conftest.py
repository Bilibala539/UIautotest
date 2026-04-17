"""
pytest fixture 配置文件
提供全局的测试设置和清理

设计说明：
- 设备(Device): Session级别，整个测试过程只启动一次
- 用户(User): Function级别，每个测试用例独立创建，不共享状态

平台选择规则 (优先级从高到低):
1. marker 标记: @pytest.mark.mumu 或 @pytest.mark.pc
2. 文件夹自动判断: tests/mumu/ → mumu, tests/win/ → pc
3. 默认值: mumu
"""
import os
import base64
from dotenv import load_dotenv
load_dotenv()

import time

import pyautogui
import pytest
import logging
from datetime import datetime
from typing import Optional, List, Dict

# 导入新的测试数据管理器
from config.user_data import UserManager
from utils.user import PPUser, PPDevice
from utils.devices import adb_connect, start_devices, Device
from typing import TYPE_CHECKING


# ==================== 平台判断工具函数 ====================

def _detect_platform(item) -> str:
    """
    检测测试用例的目标平台

    优先级:
    1. @pytest.mark.mumu / @pytest.mark.pc  (marker 标记优先)
    2. 文件路径中的 tests/win/ 或 tests/mumu/ (文件夹自动判断)
    3. 默认 "mumu"

    Args:
        item: pytest item (test node)

    Returns:
        str: "mumu" 或 "pc"
    """
    # 1. 检查 marker
    markers = [m.name for m in item.iter_markers()]
    if "pc" in markers:
        return "pc"
    if "mumu" in markers:
        return "mumu"

    # 2. 检查文件路径
    fspath = str(item.fspath).replace("\\", "/")
    if "/tests/win/" in fspath or "/tests/pc/" in fspath:
        return "pc"
    if "/tests/mumu/" in fspath:
        return "mumu"

    # 3. 默认
    return "mumu"

# ==================== 配置日志 ====================
# 使用项目根目录下的logs文件夹
log_dir = r"E:\UIAutotest\logs"
os.makedirs(log_dir, exist_ok=True)

# 创建 HTML 日志文件路径
_log_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_file = os.path.join(log_dir, f"test_{_log_timestamp}.html")

# ==================== HTML 日志 Handler ====================

_HTML_HEADER = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Test Log</title>
<style>
  body {{ font-family: Consolas, monospace; background: #1e1e1e; color: #d4d4d4; margin: 0; padding: 16px; }}
  .log-entry {{ padding: 2px 4px; border-bottom: 1px solid #2d2d2d; white-space: pre-wrap; word-break: break-all; }}
  .INFO  {{ color: #9cdcfe; }}
  .WARNING {{ color: #dcdcaa; }}
  .ERROR {{ color: #f44747; }}
  .DEBUG {{ color: #6a9955; }}
  .fail-block {{ margin: 12px 0; padding: 12px; border: 2px solid #f44747; border-radius: 6px; background: #2d1e1e; }}
  .screenshot-block {{ margin: 12px 0; padding: 12px; border: 2px solid #3a3a5c; border-radius: 6px; background: #1e1e2d; }}
  .fail-title {{ color: #f44747; font-weight: bold; font-size: 1.1em; margin-bottom: 8px; }}
  .screenshot-block .fail-title {{ color: #9cdcfe; }}
  .fail-img {{ max-width: 100%; border: 1px solid #555; border-radius: 4px; margin-top: 8px; display: block; }}
</style>
</head>
<body>
"""

_HTML_FOOTER = "</body></html>\n"


class HtmlFileHandler(logging.Handler):
    """将日志输出为 HTML 文件，支持在用例失败时内嵌截图"""

    def __init__(self, filepath: str):
        super().__init__()
        self._filepath = filepath
        # 写入 HTML 头部
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(_HTML_HEADER)

    def emit(self, record: logging.LogRecord):
        try:
            msg = self.format(record)
            level = record.levelname
            # 转义 HTML 特殊字符
            safe_msg = msg.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            line = f'<div class="log-entry {level}">{safe_msg}</div>\n'
            with open(self._filepath, 'a', encoding='utf-8') as f:
                f.write(line)
        except Exception:
            self.handleError(record)

    def append_screenshot(self, label: str, screenshot_path: str, img_b64: str = None):
        """
        在日志当前位置追加一张截图块。

        Args:
            label:           标题描述文字
            screenshot_path: 图片磁盘路径（用于展示，img_b64 为空时从此路径读取）
            img_b64:         已编码的 base64 字符串（可选，传入则跳过文件读取）
        """
        try:
            if img_b64 is None:
                with open(screenshot_path, 'rb') as f:
                    img_b64 = base64.b64encode(f.read()).decode('utf-8')
            # 根据 label 是否含 FAIL 决定样式
            css_class = 'fail-block' if 'FAIL' in label or '❌' in label or '⚠️' in label else 'screenshot-block'
            block = (
                f'<div class="{css_class}">'
                f'<div class="fail-title">{label}</div>'
                f'<div style="font-size:0.85em;color:#888;">路径: {screenshot_path}</div>'
                f'<img class="fail-img" src="data:image/png;base64,{img_b64}" />'
                f'</div>\n'
            )
            with open(self._filepath, 'a', encoding='utf-8') as f:
                f.write(block)
        except Exception as e:
            with open(self._filepath, 'a', encoding='utf-8') as f:
                f.write(f'<div class="log-entry ERROR">截图内嵌失败: {e}</div>\n')

    def append_fail_screenshot(self, test_name: str, screenshot_path: str):
        """在日志末尾追加失败用例截图块（兼容旧调用，内部转发到 append_screenshot）"""
        self.append_screenshot(f"❌ 用例失败截图: {test_name}", screenshot_path)

    def close(self):
        # 写入 HTML 尾部
        try:
            with open(self._filepath, 'a', encoding='utf-8') as f:
                f.write(_HTML_FOOTER)
        except Exception:
            pass
        super().close()


# 获取根日志记录器并清除已有的handlers（解决basicConfig不生效的问题）
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# 清除已有的handlers
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

# 创建 HTML 文件 handler
html_handler = HtmlFileHandler(log_file)
html_handler.setLevel(logging.INFO)
html_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# 创建控制台 handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# 添加handlers到根日志记录器
root_logger.addHandler(html_handler)
root_logger.addHandler(console_handler)

logger = logging.getLogger(__name__)
logger.info(f"📝 日志文件: {log_file}")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    失败自动截图，并将截图内嵌到 HTML 日志文件中
    """
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        # 尝试从测试类实例的用户对象中获取 aw (AWBase)，进行截图
        aw = None
        instance = getattr(item, 'instance', None)
        if instance is not None:
            # 遍历实例属性，找到 PPUser 类型的用户，取其 aw 对象
            for attr_val in vars(instance).values():
                if hasattr(attr_val, 'aw') and hasattr(attr_val.aw, 'take_screenshot'):
                    aw = attr_val.aw
                    break

        if aw is not None:
            screenshot_dir = os.path.join(os.path.dirname(log_file), '..', 'screenshots')
            screenshot_dir = os.path.normpath(screenshot_dir)
            os.makedirs(screenshot_dir, exist_ok=True)
            screenshot_path = os.path.join(
                screenshot_dir,
                f"FAIL_{item.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            )
            img = aw.take_screenshot(save_path=screenshot_path)
            if img is not None:
                logger.info(f"📸 用例失败截图已保存: {screenshot_path}")
                # 将截图内嵌到 HTML 日志
                html_handler.append_fail_screenshot(item.nodeid, screenshot_path)
            else:
                logger.warning(f"⚠️ 用例失败截图失败（截图返回空）: {item.nodeid}")
        else:
            logger.warning(f"⚠️ 未找到可截图的用户对象，跳过失败截图: {item.nodeid}")


# ==================== 设备管理器 (Session级别) ====================

class DeviceManager:
    """
    设备管理器 - Session级别单例
    负责管理MuMu模拟器设备的生命周期
    
    特点：
    - 设备在整个测试Session只启动一次
    - 支持动态扩展设备数量
    """
    
    _instance: Optional['DeviceManager'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._devices_list: List[Device] = []
        self._max_devices_started: int = 0
        self._initialized = True
        logger.info("📱 DeviceManager 初始化完成")
    
    def ensure_devices(self, count: int) -> List[Device]:
        """
        确保有足够数量的设备可用
        
        Args:
            count: 需要的设备数量
            
        Returns:
            List[Device]: 可用的设备列表
        """
        if count <= self._max_devices_started:
            # 已有足够设备
            return self._devices_list[:count]
        
        # 需要启动更多设备
        logger.info(f"🚀 需要 {count} 个设备，当前 {self._max_devices_started} 个，正在启动...")
        self._devices_list = start_devices(count)
        self._max_devices_started = count
        
        return self._devices_list[:count]
    
    def get_device(self, index: int) -> Optional[Device]:
        """
        获取指定索引的设备
        
        Args:
            index: 设备索引
            
        Returns:
            Optional[Device]: 设备对象，不存在则返回None
        """
        if index < len(self._devices_list):
            return self._devices_list[index]
        return None
    
    @property
    def devices(self) -> List[Device]:
        """获取所有已启动的设备"""
        return self._devices_list.copy()


# 全局设备管理器实例
_device_manager: Optional[DeviceManager] = None


def get_device_manager() -> DeviceManager:
    """获取全局设备管理器实例"""
    global _device_manager
    if _device_manager is None:
        _device_manager = DeviceManager()
    return _device_manager


# ==================== 用户工厂 (Function级别) ====================

class UsersFactory:
    """
    用户工厂类 - 每个测试用例独立
    负责创建用户实例并分配设备
    
    特点：
    - 每个测试用例创建新的工厂实例
    - 用户状态不会跨用例共享
    - 设备从全局DeviceManager获取
    - 自动根据 platform 参数选择 MuMu / PC 平台
    """

    # 预定义的用户配置
    USER_CONFIGS: Dict[str, dict] = {
        "userA": {
            "uid": "grp.popoqa67@corp.netease.com",
            "password": "Lazermlfy1@",
            "env": "test03",
            "name": "测试用户A"
        },
        "userB": {
            "uid": "grp.popoqa93@corp.netease.com",
            "password": "123Ykhwl",
            "env": "test03",
            "name": "测试用户B"
        },
        "userC": {
            "uid": "grp.popoqa129@corp.netease.com",
            "password": "Popoqa163",
            "env": "test03",
            "name": "测试用户C"
        },
        "grp125": {
            "uid": "grp.popoqa125@corp.netease.com",
            "password": "popoGrp@2020",
            "env": "test03",
            "name": "grp125"
        },
        "grp93": {
            "uid": "grp.popoqa93@corp.netease.com",
            "password": "123Ykhwl",
            "env": "test03",
            "name": "grp93"
        },
        "grp129": {
            "uid": "grp.popoqa129@corp.netease.com",
            "password": "Popoqa163",
            "env": "test03",
            "name": "grp129"
        },
        "grp52": {
            "uid": "grp.popoqa52@corp.netease.com",
            "password": "Popoqa163",
            "env": "test03",
            "name": "grp52"
        },
        "grpmax": {
            "uid": "grp.superpopo@corp.netease.com",
            "password": "Superqa@163",
            "env": "test03",
            "name": "grpmax"
        }
    }
    
    def __init__(self, device_manager: DeviceManager, platform: str = "mumu"):
        """
        初始化用户工厂
        
        Args:
            device_manager: 设备管理器实例
            platform: 目标平台 ('mumu' 或 'pc')
        """
        self._device_manager = device_manager
        self._platform = platform
        self._created_users: Dict[str, PPUser] = {}
        self._device_index: int = 0
        logger.debug(f"👤 UsersFactory 新实例创建 (platform={platform})")
    
    def __call__(self, user_key: str) -> PPUser:
        """
        创建用户实例
        
        Args:
            user_key: 用户配置键名
            
        Returns:
            PPUser: 用户实例
            
        Raises:
            ValueError: 如果用户配置不存在
        """
        # 同一个工厂内，相同user_key返回同一个用户
        if user_key in self._created_users:
            return self._created_users[user_key]
        
        # 检查用户配置
        if user_key not in self.USER_CONFIGS:
            raise ValueError(f"❌ 未找到用户配置: {user_key}，可用配置: {list(self.USER_CONFIGS.keys())}")
        
        # 获取用户配置
        config = self.USER_CONFIGS[user_key]
        
        # 根据平台决定是否需要设备
        pp_device = None
        if self._platform == "mumu":
            # MuMu 端需要启动模拟器设备
            needed_devices = self._device_index + 1
            self._device_manager.ensure_devices(needed_devices)
            device = self._device_manager.get_device(self._device_index)
            self._device_index += 1
            
            pp_device = PPDevice(device_port=device.adb_port, instance_id=device.instance_id)
            pp_device.pos = device.pos
            pp_device.size = device.size
            pp_device.window_name = device.window_name
            pp_device.is_ready = device.is_ready
        
        # 创建用户实例（带 platform 参数）
        user = PPUser(
            uid=config["uid"],
            password=config["password"],
            device=pp_device,
            platform=self._platform,
            env=config["env"],
            name=config.get("name", ""),
            need_login=True
        )
        
        # 缓存用户（同一用例内）
        self._created_users[user_key] = user
        
        if self._platform == "mumu":
            logger.info(f"✅ 创建用户 {user_key}: {user.uid} -> 设备 {pp_device.adb_address} (MuMu)")
        else:
            logger.info(f"✅ 创建用户 {user_key}: {user.uid} (PC)")
        
        return user
    
    def get_all_users(self) -> Dict[str, PPUser]:
        """获取当前用例中所有已创建的用户"""
        return self._created_users.copy()
    
    def cleanup(self) -> None:
        """
        清理当前用例的所有用户状态
        在teardown时调用
        """
        for user_key, user in self._created_users.items():
            if user.is_logged_in:
                logger.info(f"🚪 清理用户 {user_key}: 执行退登")
                user.logout()
        self._created_users.clear()
        self._device_index = 0


# ==================== 测试基类 ====================

class BaseTest:
    """
    测试基类 - 所有测试类继承此类

    提供 self.users 类型声明，使 IDE 能正确识别：
    - self.users("userA") → PPUser
    - self.userA.login() / self.userA.aw.click_text() 等全链路提示

    使用方式:
        class TestXXX(BaseTest):
            def setup(self):
                self.userA = self.users("userA")
                self.userA.login()
    """

    users: "UsersFactory"


# ==================== Pytest Fixtures ====================

@pytest.fixture(scope="session")
def device_manager():
    """
    设备管理器 fixture - Session级别
    
    整个测试Session共享同一个设备管理器，
    设备只启动一次。
    """
    pyautogui.hotkey('win', 'd')
    time.sleep(0.5)
    manager = get_device_manager()
    yield manager

    logger.info("📱 Session结束，设备管理器清理完成")


@pytest.fixture(scope="function")
def users(device_manager, request):
    """
    用户工厂 fixture - Function级别
    
    自动根据文件夹位置或marker标记判断平台:
    - tests/mumu/ 下的用例 → platform="mumu"
    - tests/win/ 下的用例 → platform="pc"
    - @pytest.mark.mumu → platform="mumu"
    - @pytest.mark.pc → platform="pc"
    
    使用方式:
        class TestExample:
            def setup(self):
                self.userA = self.users("userA")
                self.userA.login()
            
            def test_example(self):
                pass
            
            def teardown(self):
                self.userA.logout()
    
    Yields:
        UsersFactory: 用户工厂实例
    """
    # 自动检测平台
    platform = _detect_platform(request.node)
    logger.info(f"🎯 检测到平台: {platform} (用例: {request.node.nodeid})")

    factory = UsersFactory(device_manager, platform=platform)
    logger.info(f"👤 ===== 新用例开始，创建新的UsersFactory (platform={platform}) =====")
    
    # 自动注入到测试类实例 (支持 setup/teardown 使用)
    if request.instance is not None:
        request.instance.users = factory
    
    yield factory
    
    # 清理当前用例的用户
    logger.info("👤 ===== 用例结束，清理用户状态 =====")
    factory.cleanup()


@pytest.fixture(scope="function", autouse=True)
def _inject_users_and_run_setup_teardown(users, request):
    """
    自动注入 users 到测试类实例，并执行 setup/teardown 方法
    autouse=True 确保自动执行
    """
    instance = request.instance
    
    if instance is not None:
        # 注入 users 到测试类实例
        instance.users = users
        
        # 执行 setup 方法（如果存在）
        if hasattr(instance, 'setup') and callable(getattr(instance, 'setup')):
            logger.info("🔧 执行 setup() 方法")
            instance.setup()
    
    yield
    
    # 执行 teardown 方法（如果存在）
    if instance is not None:
        if hasattr(instance, 'teardown') and callable(getattr(instance, 'teardown')):
            logger.info("🧹 执行 teardown() 方法")
            instance.teardown()


@pytest.fixture(scope="session")
def test_user_manager():
    return UserManager("config/users_info.json")
