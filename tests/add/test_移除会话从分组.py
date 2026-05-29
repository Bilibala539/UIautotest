"""
测试用例: 给会话移除分组
前置条件: "测试测试"会话已添加到"皮皮"分组
"""
from conftest import BaseTest


class TestRemoveConversationFromGroup(BaseTest):
    """给会话移除分组测试"""

    def setup(self):
        self.userA = self.users("userA")
        self.group_name = self.userA.aw.setup_owner_group("会话分组测试群")

    def test_remove_conversation_from_group(self):
        self.userA.add_conversation_to_group(self.group_name, "测试分组")
        self.userA.remove_conversation_from_group(self.group_name, "测试分组")

    def teardown(self):
        try:
            self.userA.aw.delete_team(self.group_name)
        except Exception:
            pass
