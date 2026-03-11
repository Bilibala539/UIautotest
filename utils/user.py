"""
用户和设备定义模块
提供PPUser和PPDevice类用于测试用户和MuMu模拟器设备管理

用户通过 user.aw.xxx() 方式调用AW方法
"""
import logging
from typing import Optional

from utils.aw import AWHelper

logger = logging.getLogger(__name__)


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
        
        # 设备窗口信息（由devices.py设置）
        self.pos = (0, 0)
        self.size = (540, 960)
        self.window_name = ""
        self.is_ready = False

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
    """
    测试用户类
    
    通过 user.aw 属性访问所有AW方法
    
    使用示例:
        user = PPUser(uid="test@example.com", password="123456", device=device)
        
        # 低级操作
        user.aw.tap(100, 200)
        user.aw.input("hello")
        
        # 中级操作
        user.aw.click_text("登录")
        user.aw.input_text("输入邮箱", user.uid)
        
        # 高级操作
        user.aw.login(user.uid, user.password)
    """

    def __init__(self, uid: str, password: str, device: PPDevice, env: str = "test3",
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
        
        # 初始化AW Helper（通过aw属性访问所有AW方法）
        self._aw: Optional[AWHelper] = None

    @property
    def aw(self) -> AWHelper:
        """
        获取AW Helper实例
        
        通过此属性访问所有AW方法:
        - user.aw.tap(x, y)
        - user.aw.click_text("登录")
        - user.aw.login(uid, password)
        
        Returns:
            AWHelper: AW帮助类实例
        """
        if self._aw is None:
            self._aw = AWHelper(self.device.instance_id)
        return self._aw

    def login(self) -> bool:
        """
        执行用户登录
        
        使用AW高级方法完成登录流程
        
        Returns:
            bool: 登录是否成功
        """
        logger.info(f"🔐 {self.uid} 正在登录到设备 {self.device.device_serial}")
        
        result = self.aw.login(self.uid, self.password)
        
        if result:
            self._logged_in = True
            logger.info(f"✅ {self.uid} 登录成功")
        else:
            logger.error(f"❌ {self.uid} 登录失败")
        
        return result

    def logout(self) -> bool:
        """
        执行用户退出登录

        Returns:
            bool: 退出是否成功
        """
        logger.info(f"🚪 {self.uid} 正在退出登录")
        
        result = self.aw.logout()
        
        if result:
            self._logged_in = False
            logger.info(f"✅ {self.uid} 已退出登录")
        
        return result

    @property
    def is_logged_in(self) -> bool:
        """检查用户是否已登录"""
        return self._logged_in

    def __repr__(self):
        return f"PPUser(uid='{self.uid}', device={self.device})"


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    # 测试示例
    device = PPDevice(device_port=16384, instance_id=0)
    user = PPUser(
        uid="test@example.com",
        password="password123",
        device=device,
        env="test03"
    )
    print(user)
    print(f"AW Helper: {user.aw}")
    
    # 测试AW方法调用
    # user.aw.click_text("登录")
    # user.aw.input_text("输入邮箱", "test@example.com")
