"""
测试用例: 回复消息功能
探索来源: AI自主探索POPO App生成
"""
from conftest import BaseTest


class TestReplyMessage(BaseTest):
    """回复消息功能测试"""

    def setup(self):
        self.userA = self.users("userA")
        self.userA.login()

    def test_reply_message(self):
        """
        测试回复消息功能

        步骤:
        1. 发送一条消息，留在聊天页面
        2. 长按该消息，点击回复
        3. 输入回复内容并发送
        4. 返回消息列表
        """
        message = self.userA.send_message(recipient="grp.popoqa93", isback=False)
        self.userA.reply_message(message, "reply_test_content")
        self.userA.aw.press_back()

    def teardown(self):
        try:
            self.userA.logout()
        finally:
            self.userA.aw.stop_app()
