"""
测试用例: 开启允许申请加入群组开关
Excel来源: Row 91
"""
from conftest import BaseTest


class Test允许申请加群_开启(BaseTest):
    def setup(self):
        self.userA = self.users("userA")
        self.group_name = self.userA.setup_owner_group("测试1344")

    def test_允许申请加群_开启(self):
        """在群管理中切换允许申请加入群组开关"""
        result = self.userA.toggle_group_management_switch(
            group_identifier=self.group_name,
            setting_name="允许"
        )
        assert result, "应能切换允许申请加群开关"

    def teardown(self):
        pass
