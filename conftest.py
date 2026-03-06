"""
pytest fixture 配置文件
提供全局的测试设置和清理

设计说明：
- 设备(Device): Session级别，整个测试过程只启动一次
- 用户(User): Function级别，每个测试用例独立创建，不共享状态
"""
import time

import pytest
import os
import logging
from datetime import datetime
from typing import Optional, List, Dict

# 导入新的测试数据管理器
from config.user_data import UserManager
from utils.user import PPUser, PPDevice
from utils.devices import adb_connect, start_devices, Device

# 配置日志
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"{log_dir}/test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    失败自动截图
    """
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        driver = None
        # 尝试从测试函数参数中获取driver
        if hasattr(item, 'funcargs'):
            for arg_name, arg_value in item.funcargs.items():
                if hasattr(arg_value, 'get_screenshot_as_png'):
                    driver = arg_value
                    break

        if driver:
            screenshot_dir = "screenshots"
            os.makedirs(screenshot_dir, exist_ok=True)
            screenshot_path = os.path.join(screenshot_dir,
                                           f"{item.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            driver.save_screenshot(screenshot_path)
            logger.info(f"失败截图已保存: {screenshot_path}")


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
    """
    
    # 预定义的用户配置
    USER_CONFIGS: Dict[str, dict] = {
        "userA": {
            "uid": "grp.popoqa125@corp.netease.com",
            "password": "popoGrp@2020",
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
    
    def __init__(self, device_manager: DeviceManager):
        """
        初始化用户工厂
        
        Args:
            device_manager: 设备管理器实例
        """
        self._device_manager = device_manager
        self._created_users: Dict[str, PPUser] = {}
        self._device_index: int = 0
        logger.debug("👤 UsersFactory 新实例创建")
    
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
        
        # 确保有足够的设备
        needed_devices = self._device_index + 1
        self._device_manager.ensure_devices(needed_devices)
        
        # 获取设备
        device = self._device_manager.get_device(self._device_index)
        self._device_index += 1
        
        # 获取用户配置
        config = self.USER_CONFIGS[user_key]
        
        # 创建PPDevice对象
        pp_device = PPDevice(device_port=device.adb_port, instance_id=device.instance_id)
        pp_device.pos = device.pos
        pp_device.size = device.size
        pp_device.window_name = device.window_name
        pp_device.is_ready = device.is_ready
        
        # 创建用户实例
        user = PPUser(
            uid=config["uid"],
            password=config["password"],
            device=pp_device,
            env=config["env"],
            name=config.get("name", ""),
            need_login=True
        )
        
        # 缓存用户（同一用例内）
        self._created_users[user_key] = user
        
        logger.info(f"✅ 创建用户 {user_key}: {user.uid} -> 设备 {pp_device.adb_address}")
        
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


# ==================== Pytest Fixtures ====================

@pytest.fixture(scope="session")
def device_manager():
    """
    设备管理器 fixture - Session级别
    
    整个测试Session共享同一个设备管理器，
    设备只启动一次。
    """
    manager = get_device_manager()
    yield manager
    logger.info("📱 Session结束，设备管理器清理完成")


@pytest.fixture(scope="function")
def users(device_manager):
    """
    用户工厂 fixture - Function级别
    
    每个测试用例（function）获得独立的用户工厂，
    用户状态不会跨用例共享。
    
    使用方式:
        def test_example(users):
            UserA = users("userA")  # 创建用户A
            UserB = users("userB")  # 创建用户B
            
            UserA.login()  # 登录
            # ... 测试逻辑 ...
        
        def test_another(users):
            UserA = users("userA")  # 这是一个全新的UserA实例！
            # UserA 是未登录状态
    
    Yields:
        UsersFactory: 用户工厂实例
    """
    factory = UsersFactory(device_manager)
    logger.info("👤 ===== 新用例开始，创建新的UsersFactory =====")
    
    yield factory
    
    # 清理当前用例的用户
    logger.info("👤 ===== 用例结束，清理用户状态 =====")
    factory.cleanup()


@pytest.fixture(scope="session")
def test_user_manager():
    return UserManager("config/users_info.json")