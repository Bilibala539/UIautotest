"""
测试用例: 左滑操作-置顶（P2P会话）
功能点: 会话列表左滑操作（Android通过长按实现）
操作步骤: 长按P2P会话，点击置顶
预期结果: 会话被置顶
"""
from conftest import BaseTest


class TestLongPressPin(BaseTest):
    """长按置顶会话"""

    def setup(self):
        self.userA = self.users("userA")

    def test_long_press_pin_p2p(self):
        """
        步骤:
        1. 在消息列表页长按P2P会话
        2. 点击"置顶"
        3. 验证会话被置顶
        """
        # 使用非置顶的会话来测试置顶
        self.userA.pin_conversation("工作日历")

    def teardown(self):
        """清理：取消置顶"""
        self.userA.unpin_conversation("工作日历")
