"""测试用例: 图片编辑权限限制 | Excel行 11, 12"""
import pytest
from conftest import BaseTest


@pytest.mark.skip(reason="需要群管理员权限设置，前置条件复杂")
class TestImageEditPermission(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    @pytest.mark.parametrize("scenario", [
        "群组限制包含图片消息的转发和保存",
        "内容安全设置全部打开",
    ])
    def test_image_edit_permission(self, scenario):
        """预期: 弹出限制提示，无法进入编辑界面"""
        pass

    def teardown(self):
        pass
