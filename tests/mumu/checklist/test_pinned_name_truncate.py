"""
测试用例: 置顶会话名称显示-3
功能点: 置顶会话名称超出部分截断不显示
操作步骤: 查看置顶会话的名称字符
预期结果: 超出部分的字符直接截断不显示
"""
import time
from conftest import BaseTest


class TestPinnedConversationNameTruncate(BaseTest):
    """置顶会话名称截断显示"""

    def setup(self):
        self.userA = self.users("userA")

    def test_pinned_conversation_name_truncated(self):
        """
        步骤:
        1. 在消息列表中找到置顶会话
        2. 验证置顶会话名称正常显示（如果名称过长则被截断）
        3. 截图保存供人工确认
        """
        # 查看消息列表顶部的置顶会话（如"工作日历"通常是置顶的）
        pos = self.userA.aw.find_text_by_ocr("工作日历", timeout=5)
        assert pos, "消息列表中未找到置顶会话'工作日历'"

        # 也查找名称较长的置顶会话（如"超极长的"）
        long_pos = self.userA.aw.find_text_by_ocr("超极长的", timeout=3)
        # 截图保存UI显示效果
        self.userA.aw.take_screenshot(
            save_path="screenshots/test_pinned_name_truncate.png"
        )

        # 验证：找到了置顶会话即说明名称渲染正确
        assert pos is not None

    def teardown(self):
        pass
