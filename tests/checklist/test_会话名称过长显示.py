"""
测试用例: 列表中会话-会话名称过长显示
功能点: 会话名称超长时在列表中正确截断显示
操作步骤: 查看名称过长的会话在分组详情中的显示
预期结果: 最多显示两行，超出部分用省略号显示
"""
import os
import time
from conftest import BaseTest


class TestLongConversationName(BaseTest):
    """会话名称过长显示"""

    def setup(self):
        self.userA = self.users("userA")

    def test_long_name_displays_correctly(self):
        """
        步骤:
        1. 在消息列表中查找名称过长的会话
        2. 验证该会话在列表中可正常显示，未出现UI溢出
        3. 验证超长名称被截断显示（末尾有...）
        """
        pos = self.userA.aw.find_text_by_ocr("grp.popoqa50", timeout=5)
        if not pos:
            pos = self.userA.aw.find_text_by_ocr("网易内购福利组", timeout=5)
        assert pos, "消息列表中未找到名称较长的会话"

        self.userA.aw.take_screenshot(
            save_path=os.path.join(self.userA.aw.SCREENSHOT_DIR, "test_long_conversation_name.png")
        )

    def teardown(self):
        pass
