"""
测试用例: 打开群设置
"""
import pytest


class TestOpenGroupSettings:
    """测试打开群设置功能"""

    def setup(self):
        """
        测试前初始化
        - 实例化用户
        - 用户登录
        """
        self.userA = self.users("userA")
        self.userA.login()

    def test_open_group_settings(self):
        """
        测试打开群设置功能
        
        步骤:
        1. 进入群聊"POPO通知服务测试"
        2. 点击顶部群名称区域
        3. 验证进入群设置页面（显示"设置"和"群成员"）
        """
        # 先进入群聊
        self.userA.aw.enter_group("POPO通知服务测试")
        
        # 打开群设置
        result = self.userA.aw.open_group_settings()
        assert result, "打开群设置失败"

    def teardown(self):
        """
        测试后清理
        - 用户退登
        """
        if hasattr(self, 'userA'):
            self.userA.logout()
