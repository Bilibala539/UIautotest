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


# ==================== 中间截图清理 ====================


def _cleanup_intermediate_screenshots() -> None:
    """
    清理用例执行期间产生的中间截图文件

    仅删除 failed_ocr_* 和 failed_find_* 开头的中间截图，
    保留 FAIL_ 开头的用例失败截图。
    用例通过时调用，确保通过的用例不留下调试截图。
    """
    screenshot_dir = os.path.join(os.path.dirname(log_file), '..', 'screenshots')
    screenshot_dir = os.path.normpath(screenshot_dir)
    if not os.path.exists(screenshot_dir):
        return

    cleaned = 0
    for filename in os.listdir(screenshot_dir):
        # 只清理中间截图（OCR/图像匹配失败时产生的），保留用例失败截图(FAIL_)
        if filename.startswith('failed_ocr_') or filename.startswith('failed_find_'):
            filepath = os.path.join(screenshot_dir, filename)
            try:
                os.remove(filepath)
                cleaned += 1
            except OSError:
                pass

    if cleaned > 0:
        logger.info(f"🧹 已清理 {cleaned} 张中间截图（用例通过，无需保留调试截图）")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    失败自动截图，并将截图内嵌到 HTML 日志文件中；
    每条用例执行完毕后在控制台输出 HTML 日志链接。
    """
    outcome = yield
    rep = outcome.get_result()

    # ---- 用例 call 阶段结束后，在控制台打印 HTML 日志链接 ----
    if rep.when == "call":
        _result_emoji = "✅" if rep.passed else ("❌" if rep.failed else "⚠️")
        _log_url = "file:///" + log_file.replace("\\", "/")
        # 直接写入 stderr 以确保在 pytest 捕获日志时依然可见
        import sys
        sys.stderr.write(
            f"\n{'='*60}\n"
            f"{_result_emoji} 用例: {item.nodeid}\n"
            f"📋 HTML日志: {_log_url}\n"
            f"{'='*60}\n\n"
        )
        sys.stderr.flush()

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

    # ---- 用例通过时，清理该用例期间产生的中间截图 ----
    if rep.when == "call" and rep.passed:
        _cleanup_intermediate_screenshots()


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


# ==================== 用户工厂 (Session级别) ====================

class UsersFactory:
    """
    用户工厂类 - Session 级别共享
    负责创建用户实例、分配设备、管理登录态

    特点：
    - 整个 Session 共享同一个工厂实例
    - 首次调用 users("userA") 时启动设备 + 登录（只执行一次）
    - 后续调用返回缓存的用户实例
    - Session 结束时统一退登
    - 每个用例通过 open_app / close_app 管理应用生命周期
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
        logger.info(f"👤 UsersFactory 初始化 (platform={platform}, scope=session)")
    
    def __call__(self, user_key: str) -> PPUser:
        """
        获取或创建用户实例

        首次调用时：启动设备 → 创建用户（不登录，登录由每条用例的生命周期管理）
        后续调用时：直接返回缓存的用户实例

        Args:
            user_key: 用户配置键名

        Returns:
            PPUser: 用户实例

        Raises:
            ValueError: 如果用户配置不存在
        """
        # 相同 user_key 返回同一个用户实例（设备绑定不变）
        if user_key in self._created_users:
            user = self._created_users[user_key]
            # 缓存命中但用户未登录（上一条用例 teardown 已退登），自动重新登录
            if not user.is_logged_in:
                logger.info(f"🔐 [auto] 用户 {user_key} 未登录，自动登录: {user.uid}")
                user.login()
            return user

        # 分布式节点过滤：如果配置了 NODE_USERS，只创建本节点负责的用户
        from utils.distributed import get_node_users
        node_users = get_node_users()
        if node_users and user_key not in node_users:
            raise ValueError(
                f"❌ 用户 {user_key} 不在当前节点负责的用户列表中。"
                f"当前节点 NODE_USERS={node_users}，"
                f"请在环境变量 NODE_USERS 中添加 {user_key}，"
                f"或在不涉及此用户的节点上跳过此用例"
            )

        # 检查用户配置
        if user_key not in self.USER_CONFIGS:
            raise ValueError(f"❌ 未找到用户配置: {user_key}，可用配置: {list(self.USER_CONFIGS.keys())}")

        # 获取用户配置
        config = self.USER_CONFIGS[user_key]

        skip_device_setup = os.environ.get("SKIP_SESSION_LOGIN") == "1"

        # 根据平台决定是否需要设备
        pp_device = None
        if self._platform == "mumu":
            if skip_device_setup:
                # 跳过设备启动 — 模拟器已在运行，直接创建 PPDevice
                from utils.devices import get_device_port_by_instance
                instance_id = self._device_index
                port = get_device_port_by_instance(instance_id)
                self._device_index += 1
                pp_device = PPDevice(device_port=port, instance_id=instance_id)
                pp_device.size = (540, 960)
                pp_device.is_ready = True
                logger.info(f"⏭️ SKIP_SESSION_LOGIN: 复用已运行设备 instance={instance_id} port={port}")
            else:
                # MuMu 端需要启动模拟器设备
                needed_devices = self._device_index + 1
                self._device_manager.ensure_devices(needed_devices)
                device = self._device_manager.get_device(self._device_index)
                if device is None:
                    raise RuntimeError(
                        f"❌ 无法获取设备 index={self._device_index}，"
                        f"已启动设备数={len(self._device_manager.devices)}，"
                        f"请检查模拟器是否正常启动"
                    )
                self._device_index += 1

                pp_device = PPDevice(device_port=device.adb_port, instance_id=device.instance_id)
                pp_device.pos = device.pos
                pp_device.size = device.size
                pp_device.window_name = device.window_name
                pp_device.is_ready = device.is_ready

        # 创建用户实例（带 platform 参数，不立即登录）
        user = PPUser(
            uid=config["uid"],
            password=config["password"],
            device=pp_device,
            platform=self._platform,
            env=config["env"],
            name=config.get("name", ""),
            need_login=True,
        )

        if self._platform == "mumu":
            logger.info(f"✅ 创建用户 {user_key}: {user.uid} -> 设备 {pp_device.adb_address} (MuMu)")
        else:
            logger.info(f"✅ 创建用户 {user_key}: {user.uid} (PC)")

        # 缓存用户实例
        self._created_users[user_key] = user

        # 首次创建时自动登录（login 包含: 打开 POPO → 登录 → 进入消息列表页）
        if not user.is_logged_in:
            logger.info(f"🔐 [auto] 首次创建，自动登录用户: {user_key} ({user.uid})")
            user.login()

        return user
    
    def get_all_users(self) -> Dict[str, PPUser]:
        """获取当前用例中所有已创建的用户"""
        return self._created_users.copy()
    
    def session_cleanup(self) -> None:
        """
        Session 结束时的清理操作
        每条用例已在结束时退登，此处仅清理缓存
        """
        logger.info("🧹 ===== Session 结束，清理用户缓存 =====")
        self._created_users.clear()
        self._device_index = 0
        logger.info("✅ ===== Session 清理完成 =====")


# ==================== 测试基类 ====================

class BaseTest:
    """
    测试基类 - 所有测试类继承此类

    提供 self.users 类型声明，使 IDE 能正确识别：
    - self.users("userA") → PPUser
    - self.userA.aw.click_text() 等全链路提示

    生命周期 (每条用例独立):
    - setup: 获取用户实例
    - 框架自动: 登录 → 打开 POPO → 进入消息列表页
    - 执行测试方法
    - 框架自动: 退登 → 关闭 POPO

    使用方式:
        class TestXXX(BaseTest):
            def setup(self):
                self.userA = self.users("userA")

            def test_example(self):
                self.userA.send_message(...)

            def teardown(self):
                pass
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
    if os.environ.get("SKIP_SESSION_LOGIN") != "1":
        pyautogui.hotkey('win', 'd')
        time.sleep(0.5)
    manager = get_device_manager()
    yield manager

    logger.info("📱 Session结束，设备管理器清理完成")


@pytest.fixture(scope="session")
def users(device_manager):
    """
    用户工厂 fixture - Session 级别

    整个测试 Session 共享同一个 UsersFactory 实例。
    首次调用 users("userA") 时触发: 启动设备 → 创建用户实例。
    登录/退登由每条用例的 _auto_app_lifecycle 自动管理。

    平台选择规则:
    1. 环境变量 PLATFORM=pc → PC端
    2. 默认 → MuMu端

    Yields:
        UsersFactory: 用户工厂实例 (Session 级别共享)
    """
    platform = os.environ.get("PLATFORM", "mumu")
    factory = UsersFactory(device_manager, platform=platform)
    logger.info(f"👤 ===== Session 开始，创建 UsersFactory (platform={platform}) =====")

    yield factory

    # Session 结束：统一退登清理
    factory.session_cleanup()


@pytest.fixture(scope="function", autouse=True)
def _auto_app_lifecycle(users, request):
    """
    每个测试用例的完整生命周期管理 (autouse=True)

    生命周期:
    1. [setup] 注入 users 到测试类 + 执行用户自定义 setup()
       （setup 中调用 self.users("userA") 时自动触发 login，确保后续业务操作可执行）
    2. [yield] 执行测试方法
    3. [teardown 前] 为所有已创建的用户执行: 退登 → 关闭 POPO
       （正常退登失败时降级为 force-stop → 重启 → 再退登）
    4. [teardown] 执行用户自定义 teardown()
    """
    instance = request.instance

    setup_success = False

    if instance is not None:
        # 注入 users 到测试类实例
        instance.users = users

        try:
            # 执行用户自定义 setup 方法
            # setup 中调用 self.users("userA") 时会自动触发 login（打开 POPO → 登录 → 进入消息列表页）
            # 因此 setup 中后续的业务操作（如 open_message_settings）可以正常执行
            if hasattr(instance, 'setup') and callable(getattr(instance, 'setup')):
                logger.info("🔧 执行 setup() 方法")
                instance.setup()

            setup_success = True
        except Exception:
            # setup 或 login 失败时，先关闭所有用户的 POPO，避免下一个用例看到脏状态
            logger.error("❌ setup/login 阶段失败，执行清理...")
            for user_key, user in users.get_all_users().items():
                logger.info(f"📱 [cleanup] 关闭 POPO: {user_key}")
                user.close_app()
            raise  # 重新抛出异常，让 pytest 标记为 ERROR

    yield

    # teardown 阶段
    if instance is not None and setup_success:
        # 先执行用户自定义 teardown 方法（此时 POPO 还在运行，用户可执行业务清理操作）
        if hasattr(instance, 'teardown') and callable(getattr(instance, 'teardown')):
            logger.info("🧹 执行 teardown() 方法")
            instance.teardown()

        # 然后为所有用户退登并关闭 POPO
        for user_key, user in users.get_all_users().items():
            if user.is_logged_in:
                try:
                    # 第一次尝试：正常 logout（从当前页面直接退登）
                    logger.info(f"🚪 [auto] 退登用户: {user_key} ({user.uid})")
                    user.logout()
                except Exception as e:
                    # 正常 logout 失败（用例失败后页面状态未知）
                    # 降级策略：force-stop → 重新打开 POPO（已登录态直接进消息列表页）→ 再次 logout
                    logger.warning(f"⚠️ [auto] 正常退登失败: {user_key}, 降级为重启退登: {e}")
                    user.close_app()
                    time.sleep(1)
                    user.open_app()
                    # 第二次 logout：此时一定在消息列表页，不再捕获异常，让错误暴露
                    user.logout()

            logger.info(f"📱 [auto] 关闭 POPO: {user_key}")
            user.close_app()


@pytest.fixture(scope="session")
def test_user_manager():
    return UserManager("config/users_info.json")
