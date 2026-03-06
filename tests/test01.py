"""
测试用例: 登录功能测试
"""
import pytest


class TestLogin:
    """登录功能测试类"""

    @pytest.fixture(autouse=True)
    def setup(self, users):
        """
        测试前初始化
        - 实例化用户
        - 用户登录
        """
        # 实例化用户（只创建一个用户，只启动一个设备）
        self.userA = users("userA")
        
        # 获取设备信息
        print(f"用户A设备ADB地址: {self.userA.device.adb_address}")
        print(f"用户A设备端口: {self.userA.device.device_port}")
        
        # 用户登录
        self.userA.login()

    def test_login_success(self):
        """
        测试用户登录成功场景
        """
        # 验证用户已登录
        assert self.userA.is_logged_in, "用户应该已登录"
        
        # 获取设备ADB地址
        adb_address = self.userA.device.adb_address
        print(f"✅ 用户A登录成功，设备: {adb_address}")
        
        # 获取用户信息
        print(f"用户UID: {self.userA.uid}")
        print(f"用户名: {self.userA.name}")
        
        # 验证设备信息
        assert self.userA.device is not None
        assert self.userA.device.adb_address is not None

    def teardown(self):
        """
        测试后清理
        - 用户退登
        """
        if hasattr(self, 'userA') and self.userA.is_logged_in:
            self.userA.logout()
            print("✅ 用户A已退出登录")
