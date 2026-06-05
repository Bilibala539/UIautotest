"""测试用例: 编辑图片后转发 | Excel行 16"""
from conftest import BaseTest

RECIPIENT = "grp.popoqa50"


class TestImageEditForward(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    def test_edit_then_forward(self):
        """操作: 编辑图片后，点击转发 | 预期: 编辑后图片被转发出去"""
        result = self.userA.select_edit_send_image_from_album(RECIPIENT)
        assert result, "编辑后转发图片应成功"

    def teardown(self):
        self.userA.aw.return_to_message_list()
