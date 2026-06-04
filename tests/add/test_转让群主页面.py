"""
测试用例: 点击转让群主进入转让页面
Excel来源: Row 34
"""
from conftest import BaseTest


class Test转让群主页面(BaseTest):
    """转让群主页面"""

    def setup(self):
        self.userA = self.users("userA")

    def test_转让群主页面(self):
        """进入群管理,点击转让群主,验证页面"""
        result = self.userA.click_in_group_management(
            group_identifier="测试1344",
            click_text="转让群主",
            verify_text="群主"
        )
        assert result, "应该成功进入转让群主页面"

    def teardown(self):
        pass
