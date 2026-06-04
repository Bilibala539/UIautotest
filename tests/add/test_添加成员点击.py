"""
测试用例: 点击添加成员进入选人界面
Excel来源: Row 63
"""
from conftest import BaseTest


class Test添加成员点击(BaseTest):
    def setup(self):
        self.userA = self.users("userA")

    def test_添加成员点击(self):
        """点击群设置中的添加按钮进入选人界面"""
        # 添加成员入口在群设置第一级
        result = self.userA.click_in_group_settings(
            group_identifier="测试1344",
            click_text="添加",
            verify_text="联系人"  # 选人界面有"联系人"tab
        )
        assert result, "应该成功进入选人界面"

    def teardown(self):
        pass
