"""
测试用例: 会话最新一条消息透出
探索来源: AI自主探索POPO App生成
用例描述: 收到一条消息后，会话列表中透出展示此消息内容
"""
import time

from conftest import BaseTest


class TestSessionLatestMessageDisplay(BaseTest):
    """会话最新一条消息透出 测试类"""

    def setup(self):
        self.userA = self.users("userA")

    def test_latest_message_displayed_in_session_list(self):
        """
        发送一条消息后，返回会话列表，验证最新消息在会话列表中透出展示
        """
        # 发送一条带随机数字的消息，返回消息列表页
        message = self.userA.send_message(
            recipient="grp.popoqa93",
            message=None,  # 自动生成随机数字消息
            isback=True
        )

        time.sleep(1)

        # 在消息列表页验证刚发送的消息内容可见（透出展示）
        self.userA.aw.find_text_by_ocr(message, timeout=5)

    def teardown(self):
        pass
