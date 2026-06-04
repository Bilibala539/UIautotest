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
        self.userA.aw._ensure_message_page()

    def test_edit_local_album_image(self):
        """
        测试场景: 从本地相册选择图片进入编辑界面
        预期: 进入图片编辑界面（底部工具栏出现）
        Excel行号: 5
        """
        result = self.userA.select_edit_send_image_from_album(RECIPIENT)
        assert result, "从本地相册选择图片编辑并发送应成功"

    @pytest.mark.skip(reason="需要聊天中存在GIF图片前置数据，暂跳过")
    def test_gif_image_no_edit_button(self):
        """
        测试场景: GIF格式图片不显示编辑按钮
        预期: 不支持的格式不展示编辑按钮
        Excel行号: 9
        """
        pass

    def teardown(self):
        self.userA.aw.return_to_message_list()


class TestImageEditPermission(BaseTest):
    """图片编辑权限限制测试"""

    def setup(self):
        self.userA = self.users("userA")

    @pytest.mark.skip(reason="需要群管理员权限设置转发保存限制，前置条件复杂")
    def test_group_restrict_forward_save(self):
        """Excel行号: 11"""
        pass

    @pytest.mark.skip(reason="需要群管理员权限设置内容安全，前置条件复杂")
    def test_content_security_all_enabled(self):
        """Excel行号: 12"""
        pass

    def teardown(self):
        pass
