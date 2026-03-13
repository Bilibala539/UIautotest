"""
测试用例: 进入群聊
"""
import pytest


class TestEnterGroup:
    """测试进入群聊功能"""

    def setup(self):
        """
        测试前初始化
        - 实例化用户
        - 用户登录
        """
        self.userA = self.users("userA")
        self.userA.login()

    def test_enter_group(self):
        """
        测试进入群聊功能
        
        步骤:
        1. 确保在消息tab页
        2. 在会话列表中点击群聊"POPO通知服务测试"
        3. 验证进入群聊界面（显示"名群成员"）
        """
        result = self.userA.aw.enter_group("POPO通知服务测试")
        assert result, "进入群聊失败"

    def teardown(self):
        """
        测试后清理
        - 用户退登
        """
        if hasattr(self, 'userA'):
            self.userA.logout()
