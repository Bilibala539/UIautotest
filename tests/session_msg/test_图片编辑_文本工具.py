"""测试用例: 使用文本工具在图片上添加文字 | Excel行 25"""
from conftest import BaseTest

RECIPIENT = "grp.popoqa50"


class TestImageEditTextTool(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    def test_text_tool(self):
        """操作: 选中图片，选择文本工具，输入文本 | 预期: 图片上显示所输入的文本"""
        result = self.userA.add_text_in_image_editor(RECIPIENT, "测试文本")
        assert result, "文本工具添加文字应成功"

    def teardown(self):
        self.userA.aw.return_to_message_list()
