"""
测试用例: 图片编辑 - 入口验证与格式限制
Excel来源: 会话区及消息.xlsx 行 5(编辑本地相册图片), 9(编辑动态图片)
"""
import pytest
from conftest import BaseTest

RECIPIENT = "grp.popoqa93"


class TestImageEditEntryAndFormat(BaseTest):
    """图片编辑入口与格式限制测试"""

    def setup(self):
        self.userA = self.users("userA")

    def test_edit_local_album_image(self):
        """
        测试场景: 从本地相册选择图片进入编辑界面
        操作: 从本地相册选择图片，点击「编辑」
        预期: 进入图片编辑界面（底部工具栏出现）

        Excel行号: 5 (index 0-based)
        """
        result = self.userA.select_edit_send_image_from_album(RECIPIENT)
        assert result, "从本地相册选择图片进入编辑界面应成功"

    def test_gif_image_no_edit_button(self):
        """
        测试场景: GIF格式图片不显示编辑按钮
        操作: 选择GIF格式图片，查看是否显示「编辑」按钮
        预期: 不支持的格式不展示编辑按钮

        Excel行号: 9 (index 0-based)
        注意: 需要聊天中存在GIF图片，长按查看时不应有编辑选项
        """
        self.userA.send_message(recipient=RECIPIENT)
        self.userA.aw.click_text("GIF", timeout=5)
        edit_pos = self.userA.aw.find_text_by_ocr("编辑", timeout=3)
        assert edit_pos is None, "GIF图片不应显示编辑按钮"
        self.userA.aw.press_back()

    def teardown(self):
        self.userA.aw.go_to_home()


class TestImageEditPermission(BaseTest):
    """图片编辑权限限制测试"""

    def setup(self):
        self.userA = self.users("userA")

    @pytest.mark.skip(reason="需要群管理员权限设置转发保存限制，前置条件复杂")
    def test_group_restrict_forward_save(self):
        """
        测试场景: 群组限制包含图片消息的转发和保存时无法编辑
        操作: 打开限制群组包含图片消息的转发和保存设置，选择图片点击「编辑」
        预期: 弹出限制提示，无法进入编辑界面

        Excel行号: 11 (index 0-based)
        """
        pass

    @pytest.mark.skip(reason="需要群管理员权限设置内容安全，前置条件复杂")
    def test_content_security_all_enabled(self):
        """
        测试场景: 内容安全设置全部打开时无法编辑图片
        操作: 群组的内容安全设置全部打开，选择图片点击「编辑」
        预期: 弹出限制提示，无法进入编辑界面

        Excel行号: 12 (index 0-based)
        """
        pass

    def teardown(self):
        self.userA.aw.go_to_home()
