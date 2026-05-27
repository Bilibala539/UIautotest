"""
测试用例: 关闭仅群主和管理员可编辑公告开关
Excel来源: Row 69
"""
from conftest import BaseTest


class Test仅群主可编辑公告_关闭(BaseTest):
    def setup(self):
        self.userA = self.users("userA")

    def test_仅群主可编辑公告_关闭(self):
        """切换公告编辑权限开关"""
        result = self.userA.toggle_group_management_switch(
            group_identifier="测试1344",
            setting_name="可编辑"
        )
        assert result, "应能切换公告编辑权限开关"

    def teardown(self):
        pass
