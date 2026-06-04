"""
测试用例: 开启允许申请加入群组开关
Excel来源: Row 91
"""
from conftest import BaseTest


class Test允许申请加群_开启(BaseTest):
    def setup(self):
        self.userA = self.users("userA")

    def test_允许申请加群_开启(self):
        """在群管理中切换允许申请加入群组开关"""
        result = self.userA.toggle_group_management_switch(
            group_identifier="测试1344",
            setting_name="允许"
        )
        assert result, "应能切换允许申请加群开关"

    def teardown(self):
        pass
