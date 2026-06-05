"""测试用例: 发送的二次确认弹窗图片显示正常 | Excel行 19"""
from conftest import BaseTest

RECIPIENT = "grp.popoqa50"


class TestImageEditSendConfirm(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    def test_send_preview_confirmation(self):
        """操作: 编辑完图片后发送，查看预览弹窗 | 预期: 预览弹窗显示正常"""
        result = self.userA.select_edit_send_image_from_album(RECIPIENT)
        assert result, "发送预览确认流程应正常"

    def teardown(self):
        self.userA.aw.return_to_message_list()
