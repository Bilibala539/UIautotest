"""测试用例: 发送文件消息后文件tab自动显示 | Excel行 33"""
import pytest
from conftest import BaseTest


@pytest.mark.skip(reason="当前App版本中发送文件不会自动创建独立的文件标签页tab")
class TestFileTabAutoShow(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    def test_file_tab_auto_show(self):
        """操作: 在任意会话中发送一条文件消息 | 预期: 文件标签页tab自动显示"""
        pass

    def teardown(self):
        pass
