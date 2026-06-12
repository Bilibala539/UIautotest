"""
测试用例: 群主点群管理员,跳转到详情页
Excel来源: Row 28
"""
from conftest import BaseTest


class Test群管理员详情页(BaseTest):
    def setup(self):
        self.userA = self.users("userA")

    def test_群管理员详情页(self):
        """进入群管理,点击群管理员,验证跳转"""
        result = self.userA.click_in_group_management(
            group_identifier="测试1344",
            click_text="群管理员",
            verify_text="管理员"
        )
        assert result, "应该成功进入管理员详情页"

    def teardown(self):
        pass
