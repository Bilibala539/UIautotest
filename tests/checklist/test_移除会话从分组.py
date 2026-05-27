"""
测试用例: 给会话移除分组
前置条件: "测试测试"会话已添加到"皮皮"分组
"""
from conftest import BaseTest


class TestRemoveConversationFromGroup(BaseTest):
    """给会话移除分组测试"""

    def setup(self):
        """测试前初始化"""
        self.userA = self.users("userA")

    def test_remove_conversation_from_group(self):
        """
        测试场景: 给会话移除分组
        步骤:
        1. 进入"测试测试"聊天设置页
        2. 点击"会话分组"
        3. 点击已选分组旁的"×"取消
        4. 验证分组已移除
        """
        # 先确保会话在分组中（前置条件）
        self.userA.add_conversation_to_group("测试测试", "哦哦厉害")

        # 执行移除操作
        self.userA.remove_conversation_from_group("测试测试", "哦哦厉害")

    def teardown(self):
        """测试后清理"""
        pass
