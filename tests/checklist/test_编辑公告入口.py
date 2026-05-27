"""
测试用例: 点击群公告后点输入栏，显示发布按钮
Excel来源: Row 76
"""
from conftest import BaseTest


class Test编辑公告入口(BaseTest):
    """点击群公告后点输入栏，显示发布按钮"""

    def setup(self):
        self.userA = self.users("userA")

    def test_编辑公告入口(self):
        """点击群公告后点输入栏，显示发布按钮"""
        result = self.userA.open_group_announcement_page("吴彦祖")
        assert result, "应能进入群公告编辑面板"

    def teardown(self):
        pass
