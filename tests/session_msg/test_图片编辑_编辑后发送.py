"""测试用例: 编辑图片后点击发送 | Excel行 15"""
from conftest import BaseTest

RECIPIENT = "grp.popoqa50"


class TestImageEditSend(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    def test_edit_then_send(self):
        """操作: 编辑图片后，点击发送 | 预期: 编辑后图片被发送出去"""
        result = self.userA.select_edit_send_image_from_album(RECIPIENT)
        assert result, "编辑后发送图片应成功"

    def teardown(self):
        self.userA.aw.return_to_message_list()
