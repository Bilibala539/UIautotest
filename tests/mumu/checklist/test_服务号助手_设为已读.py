"""
测试用例: 服务号助手-设为已读
功能点: 会话盒子操作
操作步骤: 长按服务号助手，设为已读
预期结果: 服务号最外层的灰点消失
"""
from conftest import BaseTest


class TestServiceAccountMarkAsRead(BaseTest):
    """服务号助手-设为已读"""

    def setup(self):
        self.userA = self.users("userA")

    def test_service_account_mark_as_read(self):
        """
        步骤:
        1. 在消息列表页长按"服务号助手"
        2. 点击"设为已读"
        3. 验证灰点消失
        """
        self.userA.long_press_session_toggle_read_status()

    def teardown(self):
        pass
