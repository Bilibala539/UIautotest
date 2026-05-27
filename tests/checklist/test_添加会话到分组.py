"""
测试用例: 给会话添加分组
探索补全: 从聊天设置页面进入会话分组，将会话添加到分组
         注意: "会话分组"选项仅在不在会话盒子中的会话的设置页面中显示
"""
from conftest import BaseTest


class TestAddConversationToGroup(BaseTest):
    """给会话添加分组测试"""

    def setup(self):
        """测试前初始化"""
        self.userA = self.users("userA")

    def test_add_conversation_to_group(self):
        """
        测试场景: 给会话添加分组
        入口: 聊天设置页面 → 会话分组 → 点击分组名旁的"+"
        预期: 会话被添加到分组
        注: 使用"工作日历"服务号(不在会话盒子中,其设置中有"会话分组"选项)
        """
        # 将"测试测试"群添加到"哦哦厉害"分组
        self.userA.add_conversation_to_group("测试测试", group_name="哦哦厉害")

    def teardown(self):
        """测试后清理"""
        pass
