"""
测试用例: 左滑操作-待处理
功能点: 会话列表左滑操作（Android通过长按实现）
操作步骤: 长按会话，点击待处理
预期结果: 会话被添加到待处理分组
"""
from conftest import BaseTest


class TestLongPressPending(BaseTest):
    """长按-待处理"""

    def setup(self):
        self.userA = self.users("userA")

    def test_long_press_pending(self):
        """
        步骤:
        1. 在消息列表页长按会话
        2. 点击"待处理"
        3. 验证操作成功
        """
        self.userA.add_conversation_to_pending("工作日历")

    def teardown(self):
        pass
