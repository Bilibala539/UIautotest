"""测试用例: 从本地相册选择图片进入编辑界面 | Excel行 5"""
from conftest import BaseTest

RECIPIENT = "grp.popoqa50"


class TestEditLocalAlbumImage(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    def test_edit_local_album_image(self):
        """操作: 从本地相册选择图片，点击编辑 | 预期: 进入图片编辑界面"""
        result = self.userA.select_edit_send_image_from_album(RECIPIENT)
        assert result, "从本地相册选择图片编辑并发送应成功"

    def teardown(self):
        self.userA.aw.return_to_message_list()
