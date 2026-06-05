"""测试用例: 编辑图片后点击取消 | Excel行 14"""
from conftest import BaseTest

RECIPIENT = "grp.popoqa50"


class TestImageEditCancel(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    def test_edit_then_cancel(self):
        """操作: 编辑图片后，点击取消 | 预期: 退出编辑模式，图片不会被保存"""
        self.userA.enter_image_editor_from_album(RECIPIENT)
        result = self.userA.cancel_image_edit()
        assert result, "取消编辑后应返回预览页"

    def teardown(self):
        self.userA.aw.return_to_message_list()
