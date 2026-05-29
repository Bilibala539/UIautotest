"""
测试用例: 长按会话添加到待处理
覆盖文字用例: 长按会话添加到待处理
"""
from conftest import BaseTest


class TestLongPressSessionAddToPending(BaseTest):
    """验证长按会话添加到待处理/处理完成"""

    def setup(self):
        """测试前初始化"""
        self.userA = self.users("userA")

    def test_long_press_add_to_pending(self):
        """
        验证长按会话添加到待处理/处理完成
        覆盖用例: 添加到待处理
        预期: 长按后弹出菜单，点击添加到待处理或处理完成
        """
        result = self.userA.long_press_session_add_to_pending()
        assert result in ("添加到待处理", "处理完成"), f"操作结果异常: {result}"

    def teardown(self):
        """测试后清理"""
        pass
