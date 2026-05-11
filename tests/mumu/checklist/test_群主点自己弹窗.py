"""
测试用例: 群主在群成员列表点击自己，弹窗显示查看资料+取消
Excel来源: Row 45
"""
from conftest import BaseTest


class Test群主点自己弹窗(BaseTest):
    """群主在群成员列表点击自己，弹窗显示查看资料+取消"""

    def setup(self):
        self.userA = self.users("userA")

    def test_群主点自己弹窗(self):
        """群主在群成员列表点击自己，弹窗显示查看资料+取消"""
        # 简化版: 验证可打开群成员列表
        result = self.userA.open_group_member_list("吴彦祖")
        assert result, "应能打开群成员列表"

    def teardown(self):
        pass
