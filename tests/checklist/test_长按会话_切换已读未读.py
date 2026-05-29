"""
测试用例: 长按会话切换已读未读
覆盖文字用例: 长按会话设为未读
"""
from conftest import BaseTest


class TestLongPressSessionToggleReadStatus(BaseTest):
    """验证长按会话切换已读/未读状态"""

    def setup(self):
        """测试前初始化"""
        self.userA = self.users("userA")

    def test_long_press_toggle_read_status(self):
        """
        验证长按会话切换已读/未读状态
        预期: 长按后弹出菜单（可能需要滑动），找到"设为未读"或"设为已读"并点击
        """
        result = self.userA.long_press_session_toggle_read_status()
        assert result in ("设为未读", "设为已读"), f"操作结果异常: {result}"

    def teardown(self):
        """测试后清理"""
        pass
