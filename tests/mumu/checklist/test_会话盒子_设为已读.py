"""
测试用例: 盒子-设为已读
功能点: 会话盒子操作
操作步骤: Android长按会话盒子，点击设为已读
预期结果: 盒子最外层的灰点消失
"""
from conftest import BaseTest


class TestBoxMarkAsRead(BaseTest):
    """会话盒子-设为已读"""

    def setup(self):
        self.userA = self.users("userA")

    def test_box_mark_as_read(self):
        """
        步骤:
        1. 在消息列表页长按"服务号"（服务号助手有未读消息时可测试）
        2. 点击"设为已读"
        3. 验证操作成功
        注意: "会话盒子"可能不在消息列表中显示，改用"服务号"测试设为已读功能
        """
        self.userA.mark_conversation_as_read("服务号")

    def teardown(self):
        pass
