"""
测试用例: 图片编辑 - 编辑后流程（完成弹窗/发送确认）
Excel来源: 会话区及消息.xlsx 行 18(编辑后弹窗), 19(发送二次确认弹窗)
"""
from conftest import BaseTest

RECIPIENT = "grp.popoqa93"


class TestImageEditAfterFlow(BaseTest):
    """图片编辑完成后的操作弹窗和确认流程"""

    def setup(self):
        self.userA = self.users("userA")

    def test_edit_done_popup(self):
        """
        测试场景: 编辑完成后弹出操作弹窗
        操作: 编辑完图片，点击完成，查看表现
        预期: 点击完成弹出操作弹窗，显示发送给同事或群组、保存到相册

        Excel行号: 18 (index 0-based)
        """
        result = self.userA.edit_image_done_check_popup(RECIPIENT)
        assert result, "编辑完成后应弹出操作弹窗"

    def test_send_preview_confirmation(self):
        """
        测试场景: 发送的二次确认弹窗图片显示正常
        操作: 编辑完图片后发送，查看预览弹窗的图片显示是否正常
        预期: 发送的预览弹窗显示的图片和编辑后的一致

        Excel行号: 19 (index 0-based)
        """
        self.userA.send_image_from_album(RECIPIENT)
        result = self.userA.edit_image_from_chat_message(RECIPIENT)
        assert result, "编辑后转发流程应成功（包含预览确认）"

    def teardown(self):
        self.userA.aw.go_to_home()
