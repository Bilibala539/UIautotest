"""
测试用例: P2P文本消息透出
覆盖文字用例: P2P文本消息透出
"""
import time
import random
from conftest import BaseTest


class TestP2PTextMessagePreview(BaseTest):
    """P2P文本消息透出: userB向userA发送文本，userA在消息列表验证显示消息内容"""

    def setup(self):
        self.userA = self.users("userA")
        self.userB = self.users("userB")

    def test_p2p_text_message_preview(self):
        """
        P2P文本消息透出:
        userB向userA发送文本消息，userA在消息列表验证显示消息内容
        """
        msg_content = f"P2P测试{random.randint(1000, 9999)}"

        # userB向userA发文本
        self.userB.send_message("popoqa50", msg_content, isback=True)
        time.sleep(2)

        # userA验证消息列表中显示该文本
        pos = self.userA.aw.find_text_by_ocr(msg_content, timeout=10)
        assert pos, f"userA消息列表未看到P2P文本透出: {msg_content}"

    def teardown(self):
        pass
