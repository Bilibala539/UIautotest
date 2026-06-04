"""
测试用例: 转让群主按键可见（群主）
Excel来源: Row 33
"""
from conftest import BaseTest


class Test转让群主按键可见(BaseTest):
    """转让群主按键可见"""

    def setup(self):
        self.userA = self.users("userA")

    def test_转让群主按键可见(self):
        """进入群管理,验证可见转让群主按键"""
        result = self.userA.verify_in_group_management(
            group_identifier="测试1344",
            setting_name="转让群主"
        )
        assert result == "found", "群主应能看到转让群主按键"

    def teardown(self):
        pass
