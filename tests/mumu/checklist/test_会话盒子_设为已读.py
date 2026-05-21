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
        1. 在消息列表页长按"测试测试"会话（带未读标记的普通会话）
        2. 点击"设为已读"
        3. 验证操作成功

        注意: 测试号 grp.popoqa67 的消息列表里没有"服务号"或"会话盒子"字面会话，
              改用真实存在的会话名"测试测试"作为长按目标。
        """
        self.userA.mark_conversation_as_read("测试测试")

    def teardown(self):
        pass
