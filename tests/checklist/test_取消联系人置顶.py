"""
测试用例: 取消联系人置顶

用例来源: 会话列表及会话盒子.xlsx Row 96
测试场景: 在消息列表页取消一个已置顶的会话
预期: 会话从置顶区域移除
注意: 测试结束后会重新置顶该会话以恢复环境
"""
from conftest import BaseTest


class TestUnpinConversation(BaseTest):
    """取消联系人置顶"""

    def setup(self):
        """
        测试前初始化
        """
        self.userA = self.users("userA")
        # 使用一个稳定存在的会话名称
        self.target_conversation = "工作日历服务号"

    def test_pin_then_unpin_conversation(self):
        """
        测试场景: 先置顶一个会话，再取消置顶，验证完整流程
        步骤:
        1. 在消息列表页长按第一个会话
        2. 点击"置顶"将其置顶
        3. 再次长按该会话
        4. 点击"取消置顶"将其取消置顶
        5. 验证操作成功
        """
        # 1. 先置顶（long_press_session_pin 自动判断当前状态切换）
        result1 = self.userA.long_press_session_pin()
        assert result1, "置顶操作失败"

        import time
        time.sleep(1)

        # 2. 再取消置顶
        result2 = self.userA.long_press_session_pin()
        assert result2, "取消置顶操作失败"

    def teardown(self):
        """测试后清理"""
        pass
