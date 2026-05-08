"""
测试用例: 收藏消息功能
探索来源: AI自主探索POPO App生成
"""
from conftest import BaseTest


class TestFavoriteMessage(BaseTest):
    """收藏消息功能测试"""

    def setup(self):
        self.userA = self.users("userA")

    def test_favorite_message(self):
        """
        测试收藏消息功能

        步骤:
        1. 进入与grp.popoqa93的聊天
        2. 发送一条消息（留在聊天页面）
        3. 长按该消息，点击收藏
        4. 验证已收藏toast出现
        5. 返回消息列表
        """
        # 发送消息并留在聊天页面（isback=False）
        message = self.userA.send_message(recipient="grp.popoqa93", isback=False)
        # 收藏该消息
        self.userA.favorite_message(message)
        self.userA.aw.press_back()

    def teardown(self):
        pass
