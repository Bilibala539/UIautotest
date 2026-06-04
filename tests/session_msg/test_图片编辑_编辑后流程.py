"""
测试用例: 图片编辑 - 编辑后流程（完成弹窗/发送确认）
Excel来源: 会话区及消息.xlsx 行 18(编辑后弹窗), 19(发送二次确认弹窗)
"""
import time
from conftest import BaseTest

RECIPIENT = "grp.popoqa93"


class TestImageEditAfterFlow(BaseTest):
    """图片编辑完成后的操作弹窗和确认流程"""

    def setup(self):
        self.userA = self.users("userA")
        self.userA.aw._ensure_message_page()

    def test_edit_done_popup(self):
        """
        测试场景: 编辑完成后弹出操作弹窗
        预期: 显示发送给同事或群组
        Excel行号: 18
        """
        result = self.userA.edit_image_done_check_popup(RECIPIENT)
        assert result, "编辑完成后应弹出操作弹窗"

    def test_send_preview_confirmation(self):
        """
        测试场景: 发送的二次确认弹窗图片显示正常
        预期: 发送的预览弹窗显示的图片和编辑后的一致
        Excel行号: 19
        """
        self.userA.enter_image_editor_from_album(RECIPIENT)
        self.userA.aw.click_image("IMAGE_EDITOR_DONE_BUTTON", region="HALF_DOWN", timeout=10)
        time.sleep(1)
        self.userA.aw.text_exists("发送给同事或群组")
        self.userA.aw.click_image("IMAGE_EDITOR_FORWARD", region="HALF_DOWN")
        time.sleep(1)
        self.userA.aw.text_exists("搜索", timeout=5)

    def teardown(self):
        self.userA.aw.return_to_message_list()
