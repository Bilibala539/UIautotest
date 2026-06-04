"""
测试用例: 仅群主可编辑信息开关
Excel来源: Row 31
"""
from conftest import BaseTest


class Test仅群主可编辑信息(BaseTest):
    def setup(self):
        self.userA = self.users("userA")
        self.group_name = self.userA.setup_owner_group("自动化群管理测试群")

    def test_仅群主可编辑信息(self):
        """在群管理中切换仅群主可编辑开关"""
        result = self.userA.toggle_group_management_switch(
            group_identifier=self.group_name,
            setting_name="仅群主"
        )
        assert result, "应能切换仅群主可编辑开关"

    def teardown(self):
        try:
            self.userA.delete_team(self.group_name)
        except Exception:
            pass
