"""
测试用例: P2P撤回消息透出
覆盖文字用例: P2P撤回消息透出
"""
import time
from conftest import BaseTest


class TestP2PRecallMessagePreview(BaseTest):
    """P2P撤回消息透出: userB向userA发送消息后撤回，userA验证显示撤回提示"""

    def setup(self):
        self.userA = self.users("userA")
        self.userB = self.users("userB")

    def test_p2p_recall_message_preview(self):
        """
        P2P撤回消息透出:
        userB向userA发送消息后撤回，userA在消息列表验证显示撤回提示
        """
        # userB先发送一条消息
        self.userB.send_message("popoqa50", "待撤回消息", isback=False)
        time.sleep(2)

        # userB撤回消息（长按最后一条消息，点击撤回）
        self.userB.aw.long_press_text("待撤回消息", timeout=5)
        time.sleep(1)
        self.userB.aw.click_text("撤回", timeout=5)
        time.sleep(2)

        # userB返回消息列表
        self.userB.aw.press_back()
        time.sleep(1)

        # userA验证消息列表中显示撤回提示
        pos = self.userA.aw.find_text_by_ocr("撤回", timeout=10)
        assert pos, "userA消息列表未看到P2P撤回消息透出"

    def teardown(self):
        pass
