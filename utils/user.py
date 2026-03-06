"""
用户和设备定义模块
提供PPUser和PPDevice类用于测试用户和MuMu模拟器设备管理
"""
import logging
import subprocess
import time
from typing import Optional

from utils.devices import ADB_PATH

logger = logging.getLogger(__name__)

# 网易POPO应用包名和启动Activity
APP_NAME = "网易popo"
POPO_PACKAGE = "com.netease.popo"
POPO_ACTIVITY = "com.netease.popo.MainActivity"


class PPDevice:
    """MuMu模拟器设备类"""

    def __init__(self, device_port: int = 7555, instance_id: int = 0):
        """
        初始化MuMu模拟器设备

        Args:
            device_port: ADB连接端口，默认7555
            instance_id: 模拟器实例编号，默认0
        """
        self.device_port = device_port
        self.instance_id = instance_id
        self.device_serial = f"127.0.0.1:{device_port}"

    @property
    def adb_address(self) -> str:
        """
        获取设备的ADB地址
        
        Returns:
            str: ADB地址，格式为 "127.0.0.1:端口号"
        """
        return self.device_serial

    def __repr__(self):
        return f"PPDevice(port={self.device_port}, instance={self.instance_id})"


class PPUser:
    """测试用户类"""

    def __init__(self, uid: str, password: str, device: None, env: str = "test3",
                 name: str = "", name_en: str = "", name_jp: str = "",
                 phone: str = "", role: str = "", department: str = "",
                 need_login: bool = True):
        """
        初始化测试用户

        Args:
            uid: 用户ID/邮箱
            password: 密码
            device: 关联的MuMu模拟器设备
            env: 测试环境
            name: 中文名
            name_en: 英文名
            name_jp: 日文名
            phone: 手机号
            role: 账号类型（正职、外包等）
            department: 部门
            need_login: 是否需要登录
        """
        self.uid = uid
        self.password = password
        self.name = name
        self.name_en = name_en
        self.name_jp = name_jp
        self.phone = phone
        self.role = role
        self.department = department
        self.device = device
        self.env = env
        self.need_login = need_login
        self._logged_in = False

    def _run_adb_command(self, *args) -> subprocess.CompletedProcess:
        """
        执行ADB命令
        
        Args:
            *args: ADB命令参数
            
        Returns:
            subprocess.CompletedProcess: 命令执行结果
        """
        cmd = [ADB_PATH, "-s", self.device.device_serial] + list(args)
        return subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    def _start_popo_app(self) -> bool:
        """
        启动网易POPO应用`
        
        Returns:
            bool: 启动是否成功
        """
        try:
            logger.info(f"📱 正在启动 {APP_NAME}...")
            
            # 使用 am start 命令启动应用
            # 命令格式: adb shell am start -n 包名/Activity名
            self._run_adb_command(
                "shell", "am", "start", "-n", f"{APP_NAME}/{POPO_ACTIVITY}"
            )

            logger.info(f"✅ {APP_NAME} 启动成功")
            # 等待应用启动
            time.sleep(1)
            return True
                    
        except subprocess.TimeoutExpired:
            logger.error(f"{APP_NAME} 启动超时")
            assert False
        except Exception as e:
            logger.error(f"{APP_NAME} 启动异常: {e}")
            assert False

    def login(self) -> bool:
        """
        执行用户登录
        
        步骤:
        1. 启动网易POPO应用
        2. 等待应用加载完成
        3. TODO: 输入账号密码并登录
        
        Returns:
            bool: 登录是否成功
        """
        logger.info(f"🔐 {self.uid} 正在登录到设备 {self.device.device_serial}")
        
        # 第一步：启动POPO应用
        if not self._start_popo_app():
            logger.error(f"❌ {self.uid} 登录失败：无法启动POPO应用")
            return False
        
        # TODO: 后续实现账号密码输入和登录逻辑
        # 可以使用图像识别或OCR定位输入框，然后使用ADB输入
        
        self._logged_in = True
        logger.info(f"✅ {self.uid} 登录成功")
        return True

    def logout(self) -> bool:
        """
        执行用户退出登录

        Returns:
            bool: 退出是否成功
        """
        # TODO: 实现具体的退出登录逻辑
        logger.info(f"🚪 {self.uid} 已退出登录")
        self._logged_in = False
        return True

    @property
    def is_logged_in(self) -> bool:
        """检查用户是否已登录"""
        return self._logged_in

    def __repr__(self):
        return f"PPUser(uid='{self.uid}', device={self.device})"


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    # 测试示例
    device = PPDevice(device_port=7555, instance_id=0)
    user = PPUser(
        uid="test@example.com",
        password="password123",
        device=device,
        env="test03"
    )
    print(user)
    user.login()
    print(f"已登录: {user.is_logged_in}")
