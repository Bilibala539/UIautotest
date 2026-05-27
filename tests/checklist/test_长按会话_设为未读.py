"""
测试用例: 左滑操作-设为未读
功能点: 会话列表左滑操作（Android通过长按实现）
操作步骤: 长按会话，点击设为未读
预期结果: 会话出现未读红点
注意: POPO Android端长按操作栏中不包含"设为未读"选项，仅iOS有此功能
"""
import pytest
from conftest import BaseTest


@pytest.mark.skip(reason="POPO Android端长按菜单不包含'设为未读'选项，仅iOS有此功能")
class TestLongPressMarkUnread(BaseTest):
    """长按-设为未读"""

    def setup(self):
        self.userA = self.users("userA")

    def test_long_press_mark_unread(self):
        """
        步骤:
        1. 在消息列表页长按一个非置顶的会话
        2. 点击"设为未读"
        3. 验证会话出现未读标记
        """
        # 使用"超极长的"（非置顶、已读的会话）
        self.userA.mark_conversation_as_unread("超极长的")

    def teardown(self):
        """清理：设回已读"""
        self.userA.mark_conversation_as_read("超极长的")
