"""
测试用例: 群主可见添加成员入口
Excel来源: Row 62
"""
from conftest import BaseTest


class Test添加成员入口可见(BaseTest):
    """群主可见添加成员入口"""

    def setup(self):
        self.userA = self.users("userA")

    def test_添加成员入口可见(self):
        """群主可见添加成员入口"""
        result = self.userA.verify_group_setting_default(
            group_identifier="吴彦祖",
            setting_name="添加"
        )
        assert result == "found", "群主应能看到添加成员入口"

    def teardown(self):
        pass
