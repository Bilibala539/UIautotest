"""
测试用例: 群主解散群组 (验证按钮可见)
Excel来源: Row 37
"""
from conftest import BaseTest


class Test群主解散单人群(BaseTest):
    def setup(self):
        self.userA = self.users("userA")

    def test_群主解散单人群(self):
        """在群管理中验证解散群组按钮存在"""
        # 群主专属的解散群组按钮在群管理最底部
        result = self.userA.verify_in_group_management(
            group_identifier="测试1344",
            setting_name="解散群组"
        )
        assert result == "found", "群主应能看到解散群组按键"

    def teardown(self):
        pass
