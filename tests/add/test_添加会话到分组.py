"""
测试用例: 给会话添加分组
探索补全: 从聊天设置页面进入会话分组，将会话添加到分组
         注意: "会话分组"选项仅在不在会话盒子中的会话的设置页面中显示
"""
from conftest import BaseTest


class TestAddConversationToGroup(BaseTest):
    """给会话添加分组测试"""

    def setup(self):
        self.userA = self.users("userA")
        self.group_name = self.userA.aw.setup_owner_group("会话分组测试群")

    def test_add_conversation_to_group(self):
        self.userA.add_conversation_to_group(self.group_name, group_name="测试分组")

    def teardown(self):
        try:
            self.userA.aw.delete_team(self.group_name)
        except Exception:
            pass
