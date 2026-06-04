"""
测试用例: 图片编辑 - 编辑后功能（取消/发送/转发）
Excel来源: 会话区及消息.xlsx 行 14(取消), 15(发送), 16(转发)
"""
import time
from conftest import BaseTest

RECIPIENT = "grp.popoqa93"


class TestImageEditAfterActions(BaseTest):
    """图片编辑后取消、发送、转发功能测试"""

    def setup(self):
        self.userA = self.users("userA")
        self.userA.aw._ensure_message_page()

    def test_edit_then_cancel(self):
        """
        测试场景: 编辑图片后点击取消
        预期: 退出编辑模式，返回预览页
        Excel行号: 14
        """
        self.userA.enter_image_editor_from_album(RECIPIENT)
        result = self.userA.cancel_image_edit()
        assert result, "取消编辑后应返回预览页"

    def test_edit_then_send(self):
        """
        测试场景: 编辑图片后点击发送
        预期: 编辑后图片被发送出去
        Excel行号: 15
        """
        result = self.userA.select_edit_send_image_from_album(RECIPIENT)
        assert result, "编辑后发送图片应成功"

    def test_edit_then_forward(self):
        """
        测试场景: 编辑图片后转发
        预期: 编辑后图片被转发出去
        Excel行号: 16
        """
        self.userA.enter_image_editor_from_album(RECIPIENT)
        self.userA.aw.click_image("IMAGE_EDITOR_DONE_BUTTON", region="HALF_DOWN", timeout=10)
        time.sleep(1)
        self.userA.aw.text_exists("发送给同事或群组")
        self.userA.aw.click_image("IMAGE_EDITOR_FORWARD", region="HALF_DOWN")
        time.sleep(1)
        self.userA.aw.click_text("搜索", region="HALF_UP")
        self.userA.aw.input_text("grp.popoqa50")
        time.sleep(1)
        self.userA.aw.click_image("SELECT_CANCEL", dy=308)
        time.sleep(2)

    def teardown(self):
        self.userA.aw.return_to_message_list()
