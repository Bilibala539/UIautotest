"""
测试用例: 无公告时群主进入公告页，自动编辑态
Excel来源: Row 70
"""
from conftest import BaseTest


class Test无公告群主进入(BaseTest):
    """无公告时群主进入公告页，自动编辑态"""

    def setup(self):
        self.userA = self.users("userA")

    def test_无公告群主进入(self):
        """无公告时群主进入公告页，自动编辑态"""
        result = self.userA.open_group_announcement_page("吴彦祖")
        assert result, "应能进入群公告页"

    def teardown(self):
        pass
