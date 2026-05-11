"""
测试用例: 盒子-关闭
功能点: 会话盒子操作
操作步骤: Android长按会话盒子，点击关闭
预期结果: 盒子在列表中关闭
"""
from conftest import BaseTest


class TestBoxClose(BaseTest):
    """会话盒子-关闭"""

    def setup(self):
        self.userA = self.users("userA")

    def test_box_close(self):
        """
        步骤:
        1. 在消息列表页长按"会话盒子"
        2. 点击"关闭"
        3. 验证盒子从消息列表消失
        """
        self.userA.close_conversation_box("会话盒子")

    def teardown(self):
        pass
