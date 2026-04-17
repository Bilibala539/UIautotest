"""
测试用例: 收藏消息功能
探索来源: AI自主探索POPO App生成
"""
from conftest import BaseTest


class TestFavoriteMessage(BaseTest):
    """收藏消息功能测试"""

    def setup(self):
        self.userA = self.users("userA")
        self.userA.login()

    def test_favorite_message(self):
        """
        测试收藏消息功能

        步骤:
        1. 发送一条消息，留在聊天页面
        2. 长按该消息，点击收藏
        3. 验证已收藏toast出现
        4. 返回消息列表
        """
        message = self.userA.send_message(recipient="grp.popoqa93", isback=False)
        self.userA.favorite_message(message)
        self.userA.aw.press_back()

    def teardown(self):
        try:
            self.userA.logout()
        finally:
            self.userA.aw.stop_app()
