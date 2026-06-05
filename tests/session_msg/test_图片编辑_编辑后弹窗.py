"""测试用例: 编辑完成后弹出操作弹窗 | Excel行 18"""
from conftest import BaseTest

RECIPIENT = "grp.popoqa50"


class TestImageEditDonePopup(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    def test_edit_done_popup(self):
        """操作: 编辑完图片，点击完成 | 预期: 弹出操作弹窗，显示发送给同事或群组"""
        result = self.userA.select_edit_send_image_from_album(RECIPIENT)
        assert result, "编辑完成后发送流程应正常"

    def teardown(self):
        self.userA.aw.return_to_message_list()
