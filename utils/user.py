"""
用户和设备定义模块
提供PPUser和PPDevice类用于测试用户和设备管理

支持 MuMu 和 PC 两个平台，通过 platform 参数切换。
用户通过 user.aw.xxx() 方式调用AW方法。
"""
import logging
from typing import Optional

from utils.aw import create_aw, AWHelper
from utils.aw.search_region import Normal

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
        """获取设备的ADB地址"""
        return self.device_serial

    def __repr__(self):
        return f"PPDevice(port={self.device_port}, instance={self.instance_id})"


class PPUser:
    """
    测试用户类
    
    支持 MuMu 和 PC 两个平台，通过 platform 参数切换。
    通过 user.aw 属性访问所有AW方法。
    
    使用示例:
        # MuMu 端
        user = PPUser(uid="test@example.com", password="123456",
                      device=device, platform="mumu")
        
        # PC 端
        user = PPUser(uid="test@example.com", password="123456",
                      platform="pc")
        
        # 调用方式完全一致
        user.aw.click_text("登录")
        user.aw.login(user.uid, user.password)
    """

    def __init__(self, uid: str, password: str,
                 device: Optional[PPDevice] = None,
                 platform: str = "mumu",
                 env: str = "test3",
                 name: str = "", name_en: str = "", name_jp: str = "",
                 phone: str = "", role: str = "", department: str = "",
                 need_login: bool = True):
        """
        初始化测试用户

        Args:
            uid: 用户ID/邮箱
            password: 密码
            device: 关联的MuMu模拟器设备 (platform='mumu' 时必传)
            platform: 平台类型 ('mumu' 或 'pc')
            env: 测试环境
            name: 中文名
            name_en: 英文名
            name_jp: 日文名
            phone: 手机号
            role: 账号类型
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
        self.platform = platform
        self.env = env
        self.need_login = need_login
        self._logged_in = False

        # AW 实例延迟初始化
        self._aw: Optional[AWHelper] = None

    @property
    def aw(self) -> AWHelper:
        """
        获取AW实例

        根据 platform 自动选择对应的驱动和业务类:
        - platform='mumu': MuMuDriver + MuMuBusiness
        - platform='pc': PCDriver + PCBusiness

        Returns:
            MuMuBusiness 或 PCBusiness 实例
        """
        if self._aw is None:
            if self.platform == "mumu":
                assert self.device is not None, "MuMu 平台必须指定 device"
                self._aw = create_aw(platform="mumu", instance_id=self.device.instance_id)
            elif self.platform == "pc":
                self._aw = create_aw(platform="pc")
            else:
                raise ValueError(f"不支持的平台: {self.platform}")
        return self._aw

    def login(self) -> bool:
        """执行用户登录"""
        logger.info(f"🔐 {self.uid} 正在登录 (平台: {self.platform})")
        self.aw.login(self.uid, self.password)

    def logout(self) -> bool:
        """执行用户退出登录"""
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

    # ==================== 便捷业务方法 ====================

    def create_team(self) -> bool:
        """创建群组"""
        return self.aw.create_team()

    def delete_team(self) -> bool:
        """解散群组"""
        return self.aw.delete_team()

    def send_message(self, recipient: str, message: str) -> bool:
        """发送消息"""
        # return self.aw.send_p2p_message(recipient, message)

    def search(self, tab="全部", text=""):
        """大搜"""
        return self.aw.search(tab, text)

    # ==================== 断言方法 ====================
    def click_image(self, image_name: str, threshold: float = 0.8,
                    timeout: int = 10, dx: int = 0, dy: int = 0, region=Normal.ALL) -> bool:
        """点击图片"""
        return self.aw.click_image(image_name, threshold, timeout, dx, dy, region)

    def image_exists(self, template_name: str, threshold: float = 0.8,
                     timeout: int = 5,
                     region=Normal.ALL):
        """断言图片存在"""
        return self.aw.image_exists(template_name, threshold, timeout, region)

    def click_text(self, text: str, timeout: int = 10,
                   dx: int = 0, dy: int = 0, region=Normal.ALL) -> bool:
        """点击文字"""
        return self.aw.click_text(text, timeout, dx, dy, region=region)

    def text_exists(self, text: str, timeout: int = 5,
                    region=Normal.ALL):
        """断言文字存在"""
        return self.aw.text_exists(text, timeout, region)

    def input_text(self, text: str) -> bool:
        """输入文本"""
        return self.aw.input_text(text)

    def tap(self, x: int, y: int, dx: int = 0, dy: int = 0) -> bool:
        """点击坐标"""
        return self.aw.tap(x, y, dx, dy)

    def wait_and_click_text(self, text: str, timeout: int = 10) -> bool:
        """等待文字出现并点击"""
        if self.aw.text_exists(text, timeout):
            return self.aw.click_text(text)
        return False

    def wait_and_click_image(self, image_name: str, timeout: int = 10) -> bool:
        """等待图片出现并点击"""
        if self.aw.image_exists(image_name, timeout=timeout):
            return self.aw.click_image(image_name)
        return False

    def __repr__(self):
        return f"PPUser(uid='{self.uid}', platform='{self.platform}', device={self.device})"


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    # MuMu 端示例
    device = PPDevice(device_port=16384, instance_id=0)
    user_mumu = PPUser(
        uid="test@example.com",
        password="password123",
        device=device,
        platform="mumu",
        env="test03"
    )
    print(user_mumu)
    print(f"AW Helper: {user_mumu.aw}")

    # PC 端示例
    user_pc = PPUser(
        uid="test@example.com",
        password="password123",
        platform="pc",
        env="test03"
    )
    print(user_pc)
    print(f"AW Helper: {user_pc.aw}")
