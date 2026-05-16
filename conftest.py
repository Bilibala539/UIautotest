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
import subprocess
import shutil
import json
import io
from dotenv import load_dotenv
load_dotenv()

import allure
import paramiko
from scp import SCPClient

import time
import socket

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
_log_instance_id = os.environ.get("INSTANCE_ID", "0")
log_file = os.path.join(log_dir, f"test_{_log_timestamp}_inst{_log_instance_id}.html")

# 本次 session 的测试结果（供历史报告使用）
_test_results: list = []
_session_start_ts: float = time.time()

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


# ==================== 用例级别独立日志 ====================

# 每个用例对应一个独立的 HTML 日志文件，以用例文件名命名
_per_test_html_handler: Optional[HtmlFileHandler] = None
_per_test_log_file: Optional[str] = None


def _get_test_log_filename(item) -> str:
    """从 pytest item 提取用例文件名作为日志文件名"""
    # item.fspath 是测试文件的路径，取 stem（无扩展名）
    test_file_stem = os.path.splitext(os.path.basename(str(item.fspath)))[0]
    return os.path.join(log_dir, f"{test_file_stem}.html")


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    """每个用例开始前，创建以用例文件名命名的独立日志文件"""
    global _per_test_html_handler, _per_test_log_file

    _per_test_log_file = _get_test_log_filename(item)

    # 创建新的 HTML handler
    _per_test_html_handler = HtmlFileHandler(_per_test_log_file)
    _per_test_html_handler.setLevel(logging.INFO)
    _per_test_html_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    # 添加到根日志记录器
    root_logger.addHandler(_per_test_html_handler)
    logger.info(f"📝 用例日志: {_per_test_log_file}")


@pytest.hookimpl(trylast=True)
def pytest_runtest_teardown(item, nextitem):
    """每个用例结束后，关闭用例级别的日志 handler"""
    global _per_test_html_handler, _per_test_log_file

    if _per_test_html_handler is not None:
        root_logger.removeHandler(_per_test_html_handler)
        _per_test_html_handler.close()
        _per_test_html_handler = None


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    失败自动截图，并将截图内嵌到 HTML 日志文件中；
    每条用例执行完毕后在控制台输出 HTML 日志链接。
    """
    outcome = yield
    rep = outcome.get_result()

    # 确定当前日志文件路径（优先用例级别日志）
    current_log = _per_test_log_file or log_file

    # ---- 用例 call 阶段结束后，在控制台打印 HTML 日志链接 ----
    if rep.when == "call":
        _result_emoji = "✅" if rep.passed else ("❌" if rep.failed else "⚠️")
        _log_url = "file:///" + current_log.replace("\\", "/")
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
            test_file_stem = os.path.splitext(os.path.basename(str(item.fspath)))[0]
            screenshot_path = os.path.join(
                screenshot_dir,
                f"FAIL_{test_file_stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            )
            img = aw.take_screenshot(save_path=screenshot_path)
            if img is not None:
                logger.info(f"📸 用例失败截图已保存: {screenshot_path}")
                # 将截图内嵌到 HTML 日志（全局 + 用例级别）
                html_handler.append_fail_screenshot(item.nodeid, screenshot_path)
                if _per_test_html_handler is not None:
                    _per_test_html_handler.append_fail_screenshot(item.nodeid, screenshot_path)
                # 同步附加到 Allure 报告
                allure.attach.file(
                    screenshot_path,
                    name="失败截图",
                    attachment_type=allure.attachment_type.PNG
                )
            else:
                logger.warning(f"⚠️ 用例失败截图失败（截图返回空）: {item.nodeid}")
        else:
            logger.warning(f"⚠️ 未找到可截图的用户对象，跳过失败截图: {item.nodeid}")

    # ---- 用例通过时，清理该用例期间产生的中间截图 ----
    if rep.when == "call" and rep.passed:
        _cleanup_intermediate_screenshots()

    # ---- 收集结果供历史报告使用 ----
    if rep.when == "call":
        test_file_stem = os.path.splitext(os.path.basename(str(item.fspath)))[0]
        _test_results.append({
            "name": item.name,
            "node_id": item.nodeid,
            "file": test_file_stem,
            "status": "passed" if rep.passed else ("failed" if rep.failed else "skipped"),
            "duration": round(getattr(rep, "duration", 0), 2),
            "log": f"{test_file_stem}.html",
        })


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
            "uid": "grp.popoqa73@corp.netease.com",
            "password": "Lazermlfy1@",
            "env": "test03",
            "name": "grp73"
        },
        "userC": {
            "uid": "grp.popoqa74@corp.netease.com",
            "password": "Lazermlfy1@",
            "env": "test03",
            "name": "grp74"
        },
        "userD": {
            "uid": "grp.popoqa75@corp.netease.com",
            "password": "Lazermlfy1@",
            "env": "test03",
            "name": "grp75"
        },
        "grpmax": {
            "uid": "grp.superpopo@corp.netease.com",
            "password": "Superqa@163",
            "env": "test03",
            "name": "grpmax"
        },
        "wangying43": {
            "uid": "wangying43@corp.netease.com",
            "password": "Qwe1234!!",
            "env": "prod",
            "name": "王英"
        },

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

        # 并行执行支持：INSTANCE_ID 环境变量指定设备索引 + 账号映射
        instance_id = os.environ.get("INSTANCE_ID")
        if instance_id is not None:
            self._instance_id = int(instance_id)
            self._device_index = self._instance_id
            # 每个实例绑定不同账号，避免登录 session 互踢
            # instance 0 → userA, instance 1 → userB, instance 2 → userC, instance 3 → userD
            _ACCOUNT_KEYS = ["userA", "userB", "userC", "userD"]
            if self._instance_id < len(_ACCOUNT_KEYS):
                self._user_key_map = {"userA": _ACCOUNT_KEYS[self._instance_id]}
            else:
                self._user_key_map = {}
        else:
            self._instance_id = 0
            self._device_index = 0
            self._user_key_map = {}
        logger.info(f"👤 UsersFactory 初始化 (platform={platform}, instance_id={self._instance_id}, scope=session)")
    
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
        # 并行模式：将 "userA" 重映射到实例专属账号（避免同一账号多设备登录互踢）
        if user_key in self._user_key_map:
            user_key = self._user_key_map[user_key]

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
        logger.info("🧹 ================================================== Session 结束，清理用户缓存 ==================================================")
        self._created_users.clear()
        self._device_index = 0
        logger.info("✅ ================================================== Session 清理完成 ==================================================")


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
        try:
            pyautogui.hotkey('win', 'd')
            time.sleep(0.5)
        except pyautogui.FailSafeException:
            logger.warning("⚠️ pyautogui failsafe 触发，跳过 Win+D（ADB 模式不需要）")
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
    logger.info(f"👤 ================================================== Session 开始，创建 UsersFactory (platform={platform}) ==================================================")

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
                logger.info("================================================== 🔧 执行 setup() 方法 ==================================================")
                instance.setup()

            setup_success = True
        except Exception:
            # setup 或 login 失败时，先关闭所有用户的 POPO，避免下一个用例看到脏状态
            logger.error("❌ setup/login 阶段失败，执行清理...")
            for user_key, user in users.get_all_users().items():
                logger.info(f"📱 [cleanup] 关闭 POPO: {user_key}")
                user.close_app()
                # 标记为未登录，确保下一个用例会重新 login
                user._logged_in = False
            raise  # 重新抛出异常，让 pytest 标记为 ERROR

    yield

    # teardown 阶段
    if instance is not None and setup_success:
        # 先执行用户自定义 teardown 方法（此时 POPO 还在运行，用户可执行业务清理操作）
        if hasattr(instance, 'teardown') and callable(getattr(instance, 'teardown')):
            logger.info("================================================== 🧹 执行 teardown() 方法 ==================================================")
            try:
                instance.teardown()
            except Exception as e:
                logger.warning(f"⚠️ 用户 teardown() 执行异常（不影响退登流程）: {e}")

        # 然后为所有用户退登并关闭 POPO
        for user_key, user in users.get_all_users().items():
            if user.is_logged_in:
                try:
                    # 第一次尝试：正常 logout（从当前页面直接退登）
                    logger.info(f"🚪 [auto] 退登用户: {user_key} ({user.uid})")
                    user.logout()
                except Exception as e:
                    # 正常 logout 失败（用例失败后页面状态未知）
                    # 降级策略：force-stop → 标记未登录（放弃退登，下次用例重新登录）
                    logger.warning(f"⚠️ [auto] 退登失败: {user_key}, force-stop 并标记未登录: {e}")
                    user.close_app()
                    user._logged_in = False

            logger.info(f"📱 [auto] 关闭 POPO: {user_key}")
            user.close_app()
            user._logged_in = False


@pytest.fixture(scope="session")
def test_user_manager():
    return UserManager("config/users_info.json")


# ==================== Allure 报告生成与远程上传 ====================

_REPORT_HOST     = "10.220.28.125"
_REPORT_USER     = "popoqa91"
_REPORT_PASS     = "123456"
_REPORT_REMOTE_DIR = "/var/www/html/reports"
_PLATFORM        = "Android"
_PROJECT         = "POPO-Android"


def pytest_sessionfinish(session, exitstatus):
    _generate_and_upload_allure_report()


def _generate_and_upload_allure_report():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    allure_results = os.path.join(base_dir, "allure-results")
    allure_report = os.path.join(base_dir, "allure-report")

    if not os.path.isdir(allure_results):
        logger.warning("allure-results 目录不存在，跳过报告生成")
        return

    # 先保存本次会话快照（日志 + session.json）
    sessions_dir, session_data = _save_session_data(base_dir)

    # 保留历史趋势：把上次报告的 history/ 拷回 allure-results/history/
    history_src = os.path.join(allure_report, "history")
    history_dst = os.path.join(allure_results, "history")
    if os.path.isdir(history_src):
        if os.path.isdir(history_dst):
            shutil.rmtree(history_dst)
        shutil.copytree(history_src, history_dst)
        logger.info("📜 已还原历史数据到 allure-results/history/")

    # 写入语言配置，强制报告界面显示中文
    props_path = os.path.join(allure_results, "allure.properties")
    with open(props_path, "w", encoding="utf-8") as f:
        f.write("allure.report.language=zh\n")

    # 查找 allure 可执行文件（兼容 PATH 未刷新的情况）
    allure_cmd = (
        shutil.which("allure")
        or shutil.which("allure.bat")
        or r"C:\tools\allure-2.27.0\bin\allure.bat"
    )

    # 生成 Allure HTML 报告
    try:
        subprocess.run(
            [allure_cmd, "generate", allure_results, "-o", allure_report, "--clean"],
            check=True, capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        logger.info("✅ Allure 报告生成完成")
    except FileNotFoundError:
        logger.error("❌ allure 命令未找到，请先安装 Allure CLI：choco install allure")
        return
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Allure 报告生成失败: {e.stderr}")
        return

    # 将报告界面语言强制改为中文（app.js 默认硬编码为 en）
    app_js = os.path.join(allure_report, "app.js")
    index_html = os.path.join(allure_report, "index.html")
    if os.path.isfile(app_js):
        content = open(app_js, "r", encoding="utf-8").read()
        content = content.replace('language:"en"', 'language:"zh"', 1)
        open(app_js, "w", encoding="utf-8").write(content)
    if os.path.isfile(index_html):
        content = open(index_html, "r", encoding="utf-8").read()
        content = content.replace('lang="en"', 'lang="zh"', 1)
        # 注入自定义 CSS（在 styles.css 之后）
        content = content.replace(
            '<link rel="stylesheet" type="text/css" href="styles.css">',
            '<link rel="stylesheet" type="text/css" href="styles.css">\n'
            '    <link rel="stylesheet" type="text/css" href="custom.css">'
        )
        open(index_html, "w", encoding="utf-8").write(content)
    logger.info("🌐 报告语言已切换为中文")

    # 生成自定义 CSS（美化样式）
    custom_css_path = os.path.join(allure_report, "custom.css")
    _write_custom_css(custom_css_path)
    logger.info("🎨 自定义样式已写入")

    # 生成测试历史页面
    _write_history_html(os.path.join(allure_report, "history.html"))
    logger.info("📊 测试历史页面已生成")

    # 上传到远程服务器
    ssh = None
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(_REPORT_HOST, username=_REPORT_USER, password=_REPORT_PASS, timeout=30)
        logger.info(f"🔐 SSH 连接成功: {_REPORT_USER}@{_REPORT_HOST}")

        stdin, stdout, stderr = ssh.exec_command(f"mkdir -p {_REPORT_REMOTE_DIR}/sessions")
        stdout.channel.recv_exit_status()

        # 上传 allure-report/
        with SCPClient(ssh.get_transport()) as scp:
            scp.put(allure_report, _REPORT_REMOTE_DIR, recursive=True)

        # 从远端拉取历史、合并本次数据、上传回去（远端是唯一数据源）
        sftp = ssh.open_sftp()
        _sync_remote_history(sftp, session_data)

        # 上传本次 session 目录（logs + session.json）
        session_subdir = os.path.join(sessions_dir, _log_timestamp)
        if os.path.isdir(session_subdir):
            with SCPClient(ssh.get_transport()) as scp:
                scp.put(session_subdir, f"{_REPORT_REMOTE_DIR}/sessions", recursive=True)
        sftp.close()

        logger.info(f"✅ 全部上传完成 → http://{_REPORT_HOST}/reports/allure-report/history.html")

        # 上传成功后清理本地中间文件（释放磁盘空间）
        _cleanup_local_artifacts(base_dir)
    except Exception as e:
        logger.error(f"❌ 报告上传失败: {e}")
    finally:
        if ssh:
            ssh.close()


def _cleanup_local_artifacts(base_dir: str):
    """删除本地 allure-results / allure-report 临时目录。"""
    for name in ("allure-results", "allure-report", "sessions"):
        path = os.path.join(base_dir, name)
        if os.path.isdir(path):
            try:
                shutil.rmtree(path)
                logger.info(f"🧹 已清理本地: {name}/")
            except Exception as e:
                logger.warning(f"⚠️ 清理 {name}/ 失败: {e}")


def _write_custom_css(path: str):
    css = r"""/* ===== POPO UIAutotest — Allure 报告美化 ===== */
* { box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei",
               "Segoe UI", Roboto, sans-serif !important;
  background: #f0f2f5 !important;
  color: #1f2937 !important;
}
.side-nav {
  background: linear-gradient(180deg, #1e2d4d 0%, #16213a 100%) !important;
  box-shadow: 2px 0 12px rgba(0,0,0,0.25) !important;
  border-right: none !important;
}
.side-nav__brand {
  background: rgba(255,255,255,0.05) !important;
  border-bottom: 1px solid rgba(255,255,255,0.08) !important;
  padding: 18px 16px !important;
}
.side-nav__brand-text {
  color: #ffffff !important;
  font-weight: 700 !important;
  font-size: 15px !important;
}
.side-nav__link {
  color: rgba(255,255,255,0.65) !important;
  border-radius: 8px !important;
  margin: 2px 8px !important;
  transition: all 0.2s ease !important;
}
.side-nav__link:hover {
  background: rgba(255,255,255,0.1) !important;
  color: #ffffff !important;
}
.side-nav__link_active {
  background: linear-gradient(90deg, #4f9cf9 0%, #3b82f6 100%) !important;
  color: #ffffff !important;
  box-shadow: 0 2px 8px rgba(79,156,249,0.4) !important;
}
.side-nav__text { font-size: 13px !important; font-weight: 500 !important; }
.side-nav__footer { border-top: 1px solid rgba(255,255,255,0.08) !important; }
.app__header {
  background: #ffffff !important;
  box-shadow: 0 1px 8px rgba(0,0,0,0.08) !important;
  border-bottom: none !important;
}
.app__content { background: #f0f2f5 !important; padding: 20px !important; }
.widget {
  background: #ffffff !important;
  border-radius: 12px !important;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06) !important;
  border: none !important;
  transition: box-shadow 0.2s ease !important;
}
.widget:hover { box-shadow: 0 4px 20px rgba(0,0,0,0.1) !important; }
.widget__title {
  font-size: 13px !important;
  font-weight: 600 !important;
  color: #6b7280 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.5px !important;
}
.chart__fill_status_passed  { fill: #10b981 !important; }
.chart__fill_status_failed  { fill: #ef4444 !important; }
.chart__fill_status_broken  { fill: #f59e0b !important; }
.chart__fill_status_skipped { fill: #94a3b8 !important; }
.chart__fill_status_unknown { fill: #cbd5e1 !important; }
.chart__legend-icon_status_passed  { background: #10b981 !important; }
.chart__legend-icon_status_failed  { background: #ef4444 !important; }
.chart__legend-icon_status_broken  { background: #f59e0b !important; }
.chart__legend-icon_status_skipped { background: #94a3b8 !important; }
.t-status_passed,  .label_status_passed  { color: #10b981 !important; }
.t-status_failed,  .label_status_failed  { color: #ef4444 !important; }
.t-status_broken,  .label_status_broken  { color: #f59e0b !important; }
.t-status_skipped, .label_status_skipped { color: #94a3b8 !important; }
.label_status_passed  { background: #ecfdf5 !important; border-radius: 4px !important; padding: 1px 6px !important; }
.label_status_failed  { background: #fef2f2 !important; border-radius: 4px !important; padding: 1px 6px !important; }
.label_status_broken  { background: #fffbeb !important; border-radius: 4px !important; padding: 1px 6px !important; }
.label_status_skipped { background: #f8fafc !important; border-radius: 4px !important; padding: 1px 6px !important; }
.table { border-radius: 10px !important; overflow: hidden !important; background: #ffffff !important; box-shadow: 0 2px 10px rgba(0,0,0,0.05) !important; }
.table__head { background: #f8fafc !important; }
.table__row:hover { background: #f0f9ff !important; }
.test-result { border-radius: 8px !important; margin-bottom: 4px !important; transition: all 0.15s ease !important; }
.test-result:hover { box-shadow: 0 2px 10px rgba(0,0,0,0.08) !important; }
.trend__bar_status_passed  { background: #10b981 !important; }
.trend__bar_status_failed  { background: #ef4444 !important; }
.trend__bar_status_broken  { background: #f59e0b !important; }
.trend__bar_status_skipped { background: #94a3b8 !important; }
.search__input { border-radius: 8px !important; border: 1.5px solid #e5e7eb !important; transition: border-color 0.2s !important; }
.search__input:focus { border-color: #3b82f6 !important; outline: none !important; box-shadow: 0 0 0 3px rgba(59,130,246,0.1) !important; }
.tab__item_active { border-bottom-color: #3b82f6 !important; color: #3b82f6 !important; }
.log { background: #1e293b !important; color: #e2e8f0 !important; border-radius: 8px !important; font-family: Consolas, monospace !important; font-size: 12px !important; line-height: 1.6 !important; }
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #f1f5f9; }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(css)


def _save_session_data(base_dir: str):
    """保存本次会话日志快照和 session.json（不再写 index/history，由远端同步负责）"""
    import hashlib
    sessions_dir = os.path.join(base_dir, "sessions")
    session_dir  = os.path.join(sessions_dir, _log_timestamp)
    os.makedirs(session_dir, exist_ok=True)

    # 日志文件用 ASCII 安全名拷贝（避免 SCP 中文乱码）
    logs_src = os.path.join(base_dir, "logs")
    logs_dst = os.path.join(session_dir, "logs")
    os.makedirs(logs_dst, exist_ok=True)
    log_name_map: dict = {}
    if os.path.isdir(logs_src):
        for f in os.listdir(logs_src):
            if f.endswith(".html"):
                safe = "log_" + hashlib.md5(f.encode("utf-8")).hexdigest()[:10] + ".html"
                log_name_map[f] = safe
                shutil.copy2(os.path.join(logs_src, f), os.path.join(logs_dst, safe))

    total    = len(_test_results)
    passed   = sum(1 for t in _test_results if t["status"] == "passed")
    failed   = sum(1 for t in _test_results if t["status"] == "failed")
    skipped  = total - passed - failed
    duration = round(time.time() - _session_start_ts, 1)
    safe_tests = [dict(t, log=log_name_map.get(t["log"], t["log"])) for t in _test_results]

    session_data = {
        "id":       _log_timestamp,
        "ts":       datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "platform": _PLATFORM,
        "project":  _PROJECT,
        "host":     socket.gethostname(),
        "ip":       socket.gethostbyname(socket.gethostname()),
        "total": total, "passed": passed, "failed": failed,
        "skipped": skipped, "duration": duration,
        "tests": safe_tests,
    }
    with open(os.path.join(session_dir, "session.json"), "w", encoding="utf-8") as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)

    logger.info(f"📁 会话快照已保存: sessions/{_log_timestamp}/")
    return sessions_dir, session_data


def _sync_remote_history(sftp, session_data: dict):
    """
    从远端下载 index.json / test_history.json，合并本次数据后上传回去。
    远端是唯一数据源，本地删除不影响历史。
    """
    remote_dir = f"{_REPORT_REMOTE_DIR}/sessions"

    def _download_json(remote_path: str, default):
        try:
            buf = io.BytesIO()
            sftp.getfo(remote_path, buf)
            return json.loads(buf.getvalue().decode("utf-8"))
        except Exception:
            return default

    def _upload_json(remote_path: str, data):
        buf = io.BytesIO(json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"))
        sftp.putfo(buf, remote_path)

    # ── index.json ──────────────────────────────────────────────────
    index = _download_json(f"{remote_dir}/index.json", {"sessions": []})
    sid   = session_data["id"]
    index["sessions"] = [s for s in index["sessions"] if s["id"] != sid]
    index["sessions"].insert(0, {k: session_data[k]
                                 for k in ("id","ts","platform","project","host","ip","total","passed","failed","skipped","duration")})
    _upload_json(f"{remote_dir}/index.json", index)

    # ── test_history.json ────────────────────────────────────────────
    hist = _download_json(f"{remote_dir}/test_history.json", {})
    for t in session_data["tests"]:
        key = t["node_id"]
        hist.setdefault(key, [])
        hist[key] = [r for r in hist[key] if r["session_id"] != sid]
        hist[key].append({"session_id": sid, "platform": _PLATFORM,
                          "status": t["status"],
                          "duration": t["duration"], "log": t["log"]})
    _upload_json(f"{remote_dir}/test_history.json", hist)

    logger.info("🔄 远端 index.json / test_history.json 已同步")


def _write_history_html(path: str):
    tpl = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", "history.html")
    if os.path.isfile(tpl):
        shutil.copy2(tpl, path)
        return
    # 兜底：模板不存在时写占位页
    html = r"""<!DOCTYPE html>
<html lang="zh"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>POPO UIAutotest · 测试历史</title>
<style>
:root{--blue:#3b82f6;--green:#10b981;--red:#ef4444;--amber:#f59e0b;--slate:#94a3b8;--bg:#f0f2f5;--card:#fff;--text:#1f2937;--muted:#6b7280;--border:#e5e7eb;--r:12px}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;background:var(--bg);color:var(--text);min-height:100vh}
.hdr{background:linear-gradient(135deg,#1e2d4d,#2d4a8a);color:#fff;padding:20px 32px;display:flex;align-items:center;justify-content:space-between;box-shadow:0 2px 12px rgba(0,0,0,.2)}
.hdr-title{font-size:22px;font-weight:700;letter-spacing:-.3px}.hdr-sub{font-size:13px;opacity:.7;margin-top:2px}
.hdr-link{color:rgba(255,255,255,.8);font-size:13px;text-decoration:none;border:1px solid rgba(255,255,255,.3);padding:6px 14px;border-radius:6px;transition:all .2s}.hdr-link:hover{background:rgba(255,255,255,.1);color:#fff}
.main{max-width:1200px;margin:0 auto;padding:24px}
.summary{display:flex;gap:16px;margin-bottom:24px}
.sc{background:var(--card);border-radius:var(--r);padding:16px 24px;flex:1;box-shadow:0 2px 8px rgba(0,0,0,.05)}
.sc .val{font-size:28px;font-weight:700}.sc .lbl{font-size:12px;color:var(--muted);margin-top:4px;text-transform:uppercase;letter-spacing:.5px}
.card{background:var(--card);border-radius:var(--r);box-shadow:0 2px 10px rgba(0,0,0,.05);overflow:hidden}
table{width:100%;border-collapse:collapse}
thead th{background:#f8fafc;font-size:12px;font-weight:600;color:var(--muted);text-transform:uppercase;letter-spacing:.5px;padding:12px 16px;text-align:left;border-bottom:1px solid var(--border)}
tbody tr{transition:background .15s;cursor:pointer}
tbody tr:hover{background:#f0f9ff}
tbody td{padding:14px 16px;font-size:14px;border-bottom:1px solid var(--border)}
tbody tr:last-child td{border-bottom:none}
.rate-bar{display:flex;align-items:center;gap:10px}
.rate-bar-bg{flex:1;height:6px;background:#e5e7eb;border-radius:3px;overflow:hidden;min-width:80px}
.rate-bar-fill{height:100%;border-radius:3px}
.rate-pct{font-size:13px;font-weight:600;min-width:42px;text-align:right}
.counts{display:flex;gap:8px}
.cb{display:flex;align-items:center;gap:4px;font-size:12px;font-weight:600;padding:2px 8px;border-radius:4px}
.cb.p{background:#ecfdf5;color:#10b981}.cb.f{background:#fef2f2;color:#ef4444}.cb.s{background:#f8fafc;color:#94a3b8}
.btn{background:var(--blue);color:#fff;border:none;padding:7px 16px;border-radius:7px;font-size:13px;font-weight:500;cursor:pointer;transition:all .2s;white-space:nowrap}
.btn:hover{background:#2563eb;box-shadow:0 2px 8px rgba(59,130,246,.4)}
.btn-sm{padding:4px 10px;font-size:12px;border-radius:5px}
.btn-log{background:#7c3aed}.btn-log:hover{background:#6d28d9;box-shadow:0 2px 8px rgba(124,58,237,.4)}
.btn-back{background:none;border:none;color:var(--blue);cursor:pointer;font-size:14px;font-weight:500;display:flex;align-items:center;gap:4px;padding:6px 0}.btn-back:hover{color:#2563eb}
.badge{display:inline-flex;align-items:center;gap:4px;font-size:12px;font-weight:600;padding:3px 9px;border-radius:4px}
.badge.p{background:#ecfdf5;color:#059669}.badge.f{background:#fef2f2;color:#dc2626}.badge.s{background:#f8fafc;color:#6b7280}
.dots{display:flex;gap:3px;align-items:center}
.dot{width:10px;height:10px;border-radius:50%}.dot.p{background:#10b981}.dot.f{background:#ef4444}.dot.s{background:#d1d5db}.dot.x{background:#e5e7eb;border:1px dashed #d1d5db}
.detail-hdr{display:flex;align-items:center;gap:16px;margin-bottom:20px}
.detail-title{font-size:18px;font-weight:700}.detail-time{font-size:13px;color:var(--muted);margin-top:2px}
.stats-row{display:flex;gap:16px;margin-bottom:24px;align-items:flex-start}
.stat-cards{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;flex:1}
.stat-card{background:var(--card);border-radius:10px;padding:16px;box-shadow:0 2px 8px rgba(0,0,0,.05);text-align:center}
.stat-card .n{font-size:28px;font-weight:700}.stat-card .l{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px;margin-top:4px}
.stat-card.p .n{color:#10b981}.stat-card.f .n{color:#ef4444}.stat-card.s .n{color:#94a3b8}
.donut-wrap{background:var(--card);border-radius:10px;padding:16px 20px;box-shadow:0 2px 8px rgba(0,0,0,.05);display:flex;align-items:center;gap:16px}
.donut-label{font-size:22px;font-weight:700}.donut-sub{font-size:11px;color:var(--muted)}
.exp-row{background:#f8fafc;display:none}
.exp-row td{padding:12px 16px 12px 32px}
.hist-expand h4{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px}
.hist-list{display:flex;flex-direction:column;gap:4px}
.hist-item{display:flex;align-items:center;gap:12px;font-size:12px;color:var(--muted)}
.hist-item .hd{width:8px;height:8px;border-radius:50%;flex-shrink:0}
.loading{text-align:center;padding:60px;color:var(--muted);font-size:15px}
.empty{text-align:center;padding:60px;color:var(--muted)}
.empty-icon{font-size:48px;margin-bottom:12px}.empty-text{font-size:15px}
@keyframes spin{to{transform:rotate(360deg)}}
.spinner{width:32px;height:32px;border:3px solid #e5e7eb;border-top-color:var(--blue);border-radius:50%;animation:spin .8s linear infinite;display:inline-block;margin-bottom:12px}
</style></head><body>
<div class="hdr">
  <div><div class="hdr-title">测试历史</div><div class="hdr-sub">POPO UIAutotest</div></div>
  <a class="hdr-link" href="index.html">返回 Allure ↗</a>
</div>
<div class="main" id="app"><div class="loading"><div class="spinner"></div><br>加载中...</div></div>
<script>
const BASE='../sessions';
let allSessions=[],testHistory={};

function route(){const h=location.hash,m=h.match(/^#s\/(.+)$/);m?renderDetail(m[1]):renderList();}
window.addEventListener('hashchange',route);

async function loadData(){
  try{
    const[a,b]=await Promise.all([fetch(BASE+'/index.json'),fetch(BASE+'/test_history.json')]);
    allSessions=(await a.json()).sessions||[];
    testHistory=b.ok?await b.json():{};
  }catch(e){allSessions=[];testHistory={};}
}

async function loadSession(id){
  const r=await fetch(BASE+'/'+id+'/session.json');
  if(!r.ok)throw new Error('not found');
  return r.json();
}

const pct=(p,t)=>t===0?0:Math.round(p/t*100);
const dur=(s)=>s>=60?Math.floor(s/60)+'m '+(s%60).toFixed(0)+'s':s.toFixed(1)+'s';
const rc=(p)=>p>=90?'#10b981':p>=70?'#f59e0b':'#ef4444';
function dot(s){
  if(s==='passed')return'<span class="dot p" title="通过"></span>';
  if(s==='failed')return'<span class="dot f" title="失败"></span>';
  if(s==='skipped')return'<span class="dot s" title="跳过"></span>';
  return'<span class="dot x"></span>';
}
function histDots(nodeId){
  const h=(testHistory[nodeId]||[]).slice(-10);
  return h.length?h.map(r=>dot(r.status)).join(''):'<span style="color:#d1d5db;font-size:12px">暂无</span>';
}

function renderList(){
  const app=document.getElementById('app');
  if(!allSessions.length){
    app.innerHTML='<div class="empty"><div class="empty-icon">📭</div><div class="empty-text">暂无测试历史，运行测试后自动生成</div></div>';
    return;
  }
  const avg=Math.round(allSessions.reduce((s,x)=>s+pct(x.passed,x.total),0)/allSessions.length);
  app.innerHTML=`
  <div class="summary">
    <div class="sc"><div class="val">${allSessions.length}</div><div class="lbl">总执行次数</div></div>
    <div class="sc"><div class="val" style="color:${rc(avg)}">${avg}%</div><div class="lbl">平均通过率</div></div>
    <div class="sc"><div class="val">${allSessions.reduce((s,x)=>s+x.total,0)}</div><div class="lbl">累计执行用例</div></div>
    <div class="sc"><div class="val" style="font-size:18px">${allSessions[0]?.ts||'—'}</div><div class="lbl">最近执行</div></div>
  </div>
  <div class="card"><table>
    <thead><tr><th>执行时间</th><th>通过率</th><th>用例统计</th><th>耗时</th><th></th></tr></thead>
    <tbody>${allSessions.map(s=>{
      const r=pct(s.passed,s.total),c=rc(r);
      return`<tr onclick="location.hash='#s/${s.id}'">
        <td><strong>${s.ts}</strong></td>
        <td><div class="rate-bar"><div class="rate-bar-bg"><div class="rate-bar-fill" style="width:${r}%;background:${c}"></div></div><span class="rate-pct" style="color:${c}">${r}%</span></div></td>
        <td><div class="counts"><span class="cb p">✓ ${s.passed}</span><span class="cb f">✗ ${s.failed}</span>${s.skipped?`<span class="cb s">— ${s.skipped}</span>`:''}</div></td>
        <td>${dur(s.duration)}</td>
        <td><button class="btn btn-sm" onclick="event.stopPropagation();location.hash='#s/${s.id}'">查看详情 →</button></td>
      </tr>`;
    }).join('')}</tbody>
  </table></div>`;
}

async function renderDetail(id){
  const app=document.getElementById('app');
  app.innerHTML='<div class="loading"><div class="spinner"></div><br>加载会话数据...</div>';
  let s;
  try{s=await loadSession(id);}
  catch(e){app.innerHTML='<div class="empty"><div class="empty-icon">⚠️</div><div class="empty-text">数据加载失败</div></div>';return;}
  const r=pct(s.passed,s.total),c=rc(r);
  app.innerHTML=`
  <div class="detail-hdr">
    <button class="btn-back" onclick="location.hash=''">← 返回列表</button>
    <div><div class="detail-title">测试会话详情</div><div class="detail-time">${s.ts} &nbsp;|&nbsp; 耗时 ${dur(s.duration)}</div></div>
  </div>
  <div class="stats-row">
    <div class="stat-cards">
      <div class="stat-card"><div class="n">${s.total}</div><div class="l">总用例</div></div>
      <div class="stat-card p"><div class="n">${s.passed}</div><div class="l">通过</div></div>
      <div class="stat-card f"><div class="n">${s.failed}</div><div class="l">失败</div></div>
      <div class="stat-card s"><div class="n">${s.skipped}</div><div class="l">跳过</div></div>
    </div>
    <div class="donut-wrap">${mkDonut(r,c)}<div><div class="donut-label" style="color:${c}">${r}%</div><div class="donut-sub">通过率</div></div></div>
  </div>
  <div class="card"><table>
    <thead><tr><th>用例名称</th><th>状态</th><th>耗时</th><th>日志</th><th>历史记录（近10次）</th></tr></thead>
    <tbody>${(s.tests||[]).map((t,i)=>{
      const sc=t.status==='passed'?'p':t.status==='failed'?'f':'s';
      const sl=t.status==='passed'?'✓ 通过':t.status==='failed'?'✗ 失败':'— 跳过';
      const logUrl=BASE+'/'+s.id+'/logs/'+t.log;
      return`<tr onclick="toggle('exp${i}')">
        <td><span style="color:var(--blue);cursor:pointer">${t.name}</span></td>
        <td><span class="badge ${sc}">${sl}</span></td>
        <td>${dur(t.duration)}</td>
        <td><button class="btn btn-sm btn-log" onclick="event.stopPropagation();window.open('${logUrl}','_blank')">📋 日志</button></td>
        <td><div class="dots">${histDots(t.node_id)}</div></td>
      </tr>
      <tr class="exp-row" id="exp${i}"><td colspan="5">${mkHistExpand(t.node_id,s.id)}</td></tr>`;
    }).join('')}</tbody>
  </table></div>`;
}

function toggle(id){const r=document.getElementById(id);if(r)r.style.display=r.style.display==='table-row'?'none':'table-row';}

function mkHistExpand(nodeId,curId){
  const h=(testHistory[nodeId]||[]).slice().reverse().slice(0,15);
  if(!h.length)return'<div class="hist-expand"><p style="color:var(--muted);font-size:13px">暂无历史记录</p></div>';
  const dc=s=>s==='passed'?'#10b981':s==='failed'?'#ef4444':'#94a3b8';
  const dl=s=>s==='passed'?'通过':s==='failed'?'失败':'跳过';
  return`<div class="hist-expand"><h4>执行历史（最近 ${h.length} 次）</h4><div class="hist-list">${
    h.map(r=>`<div class="hist-item"><span class="hd" style="background:${dc(r.status)}"></span><span style="min-width:140px;font-family:monospace">${r.session_id}</span><span style="color:${dc(r.status)};font-weight:600">${dl(r.status)}</span><span>${dur(r.duration)}</span>${r.session_id===curId?'<span style="color:var(--blue)">← 当前</span>':''}</div>`).join('')
  }</div></div>`;
}

function mkDonut(p,c){
  const r=30,circ=2*Math.PI*r,dash=circ*p/100;
  return`<svg width="80" height="80" viewBox="0 0 80 80"><circle cx="40" cy="40" r="${r}" fill="none" stroke="#e5e7eb" stroke-width="8"/><circle cx="40" cy="40" r="${r}" fill="none" stroke="${c}" stroke-width="8" stroke-dasharray="${dash} ${circ-dash}" stroke-linecap="round" transform="rotate(-90 40 40)"/></svg>`;
}

(async()=>{await loadData();route();})();
</script></body></html>"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
