"""测试用例: GIF格式图片不显示编辑按钮 | Excel行 9"""
import pytest
from conftest import BaseTest


@pytest.mark.skip(reason="需要聊天中存在GIF图片前置数据")
class TestGifImageNoEdit(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    def test_gif_image_no_edit_button(self):
        """操作: 选择GIF格式图片 | 预期: 不支持的格式不展示编辑按钮"""
        pass

    def teardown(self):
        pass
