"""测试用例: 消息中含有多张图片，对一张图片编辑 | Excel行 21"""
from conftest import BaseTest

RECIPIENT = "grp.popoqa50"


class TestMultiImageEdit(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    def test_multi_image_edit_one(self):
        """操作: 消息中含有多张图片，对一张图片编辑 | 预期: 进入图片编辑界面"""
        result = self.userA.enter_image_editor_from_album(RECIPIENT)
        assert result, "应成功进入图片编辑界面"

    def teardown(self):
        self.userA.aw.return_to_message_list()
