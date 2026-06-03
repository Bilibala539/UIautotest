"""
测试用例: 图片编辑 - 特殊场景与工具操作（多张图片/文本工具）
Excel来源: 会话区及消息.xlsx 行 21(多张图片编辑), 25(文本功能测试)
"""
from conftest import BaseTest

RECIPIENT = "grp.popoqa93"


class TestImageEditSpecialAndTools(BaseTest):
    """图片编辑特殊场景和工具操作测试"""

    def setup(self):
        self.userA = self.users("userA")

    def test_multi_image_edit_one(self):
        """
        测试场景: 消息中含有多张图片，对一张图片编辑
        操作: 消息中含有多张图片，对一张图片编辑
        预期: 进入图片编辑界面

        Excel行号: 21 (index 0-based)
        """
        self.userA.send_image_from_album(RECIPIENT)
        result = self.userA.edit_image_from_chat_message(RECIPIENT)
        assert result, "多张图片中编辑一张应成功进入编辑界面"

    def test_text_tool(self):
        """
        测试场景: 使用文本工具在图片上添加文字
        操作: 选中图片，选择文本工具，输入文本
        预期: 图片上显示所输入的文本

        Excel行号: 25 (index 0-based)
        """
        result = self.userA.add_text_in_image_editor(RECIPIENT, "测试文本")
        assert result, "文本工具添加文字应成功"

    def teardown(self):
        self.userA.aw.go_to_home()
