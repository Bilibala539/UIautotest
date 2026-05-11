"""
测试用例: 添加会话到会话盒子
探索补全: 从聊天设置页面点击"添加到会话盒子"
"""
from conftest import BaseTest


class TestAddToSessionBox(BaseTest):
    """添加会话到会话盒子测试"""

    def setup(self):
        """测试前初始化"""
        self.userA = self.users("userA")

    def test_add_to_session_box(self):
        """
        测试场景: 将会话添加到会话盒子
        入口: 聊天设置页面 → "添加到会话盒子"
        预期: 会话被添加到盒子，设置中"添加到会话盒子"消失
        """
        # 使用消息列表中可见的群聊（确认在正文区域y>250，非盒子内）
        self.userA.add_to_session_box("工作日历")

    def teardown(self):
        """测试后清理 - 从盒子中移出"""
        self.userA.remove_from_session_box("工作日历")
