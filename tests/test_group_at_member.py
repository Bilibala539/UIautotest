"""
测试用例: @群成员
"""
import pytest


class TestAtGroupMember:
    """测试@群成员功能"""

    def setup(self):
        """
        测试前初始化
        - 实例化用户
        - 用户登录
        """
        self.userA = self.users("userA")
        self.userA.login()

    def test_at_group_member(self):
        """
        测试@群成员功能
        
        步骤:
        1. 进入群聊"POPO通知服务测试"
        2. 点击底部工具栏的@按钮
        3. 选择要@的成员（悠哈哈）
        4. 输入附加消息
        5. 点击发送
        6. 验证@成功
        """
        # 先进入群聊
        self.userA.aw.enter_group("POPO通知服务测试")
        
        # @成员
        result = self.userA.aw.at_group_member("悠哈哈", "请查看这条消息")
        assert result, "@群成员失败"

    def teardown(self):
        """
        测试后清理
        - 用户退登
        """
        if hasattr(self, 'userA'):
            self.userA.logout()
