"""
测试用例: 发送群消息
"""
import pytest


class TestSendGroupMessage:
    """测试发送群消息功能"""

    def setup(self):
        """
        测试前初始化
        - 实例化用户
        - 用户登录
        """
        self.userA = self.users("userA")
        self.userA.login()

    def test_send_group_message(self):
        """
        测试发送群消息功能
        
        步骤:
        1. 进入群聊"POPO通知服务测试"
        2. 点击输入框
        3. 输入消息内容
        4. 点击发送
        5. 验证消息发送成功
        """
        # 先进入群聊
        self.userA.aw.enter_group("POPO通知服务测试")
        
        # 发送消息
        result = self.userA.aw.send_group_message("这是一条测试消息")
        assert result, "群消息发送失败"

    def teardown(self):
        """
        测试后清理
        - 用户退登
        """
        if hasattr(self, 'userA'):
            self.userA.logout()
