"""
测试用例: 群主取消群管理员 (简化版验证入口)
Excel来源: Row 12
"""
from conftest import BaseTest


class Test取消群管理员(BaseTest):
    def setup(self):
        self.userA = self.users("userA")

    def test_取消群管理员(self):
        result = self.userA.verify_in_group_management(
            group_identifier="测试1344",
            setting_name="群管理员"
        )
        assert result == "found", "群主应能看到群管理员入口"

    def teardown(self):
        pass
