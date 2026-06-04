"""
测试用例: 无管理员时群管理页显示
Excel来源: Row 29
"""
from conftest import BaseTest


class Test无管理员显示(BaseTest):
    def setup(self):
        self.userA = self.users("userA")

    def test_无管理员显示(self):
        """进入群管理子页面,验证能看到群管理员入口"""
        result = self.userA.click_in_group_management(
            group_identifier="测试1344",
            click_text="群管理员",
            verify_text="管理员"
        )
        assert result, "应该能进入群管理员页面"

    def teardown(self):
        pass
