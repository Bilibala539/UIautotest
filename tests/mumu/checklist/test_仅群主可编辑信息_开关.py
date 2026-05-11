"""
测试用例: 仅群主可编辑信息开关
Excel来源: Row 31
"""
from conftest import BaseTest


class Test仅群主可编辑信息(BaseTest):
    def setup(self):
        self.userA = self.users("userA")

    def test_仅群主可编辑信息(self):
        """在群管理中切换仅群主可编辑开关"""
        result = self.userA.toggle_group_management_switch(
            group_identifier="测试1344",
            setting_name="仅群主"
        )
        assert result, "应能切换仅群主可编辑开关"

    def teardown(self):
        pass
