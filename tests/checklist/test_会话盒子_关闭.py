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
        1. 在消息列表页长按顶部会话盒子区的"ChatGPT"
        2. 点击"关闭"
        3. 验证盒子从顶部消失

        注意: 测试号的会话盒子区只有 ChatGPT/网易内购福/广州行政助等具体盒子，
              没有字面"会话盒子"的项；ChatGPT 名字最唯一不易撞名。
        """
        self.userA.close_conversation_box("ChatGPT")

    def teardown(self):
        pass
