"""
测试用例: P2P消息透出-图片/视频/撤回/合并/表情
功能点: P2P场景下收到各类消息后，会话列表正确展示透出内容
操作步骤: userB向userA直接发送各类消息，userA在消息列表验证透出
预期结果: 显示最新一条消息：【人名】+内容标识
"""
import time
import pytest
from conftest import BaseTest


class TestP2PMessagePreview(BaseTest):
    """P2P消息透出系列"""

    def setup(self):
        self.userA = self.users("userA")
        self.userB = self.users("userB")

    def test_p2p_image_message_preview(self):
        """
        P2P图片消息透出:
        userB向userA发送一张图片，userA在消息列表验证显示[图片]
        """
        # userB向userA发送图片
        self.userB.send_image_from_album("popoqa50")
        time.sleep(2)

        # userB返回消息列表
        self.userB.aw.press_back()
        time.sleep(1)

        # userA验证消息列表中显示图片透出
        pos = self.userA.aw.find_text_by_ocr("图片", timeout=10)
        assert pos, "userA消息列表未看到P2P图片消息透出"

    def test_p2p_text_message_preview(self):
        """
        P2P文本消息透出:
        userB向userA发送文本消息，userA在消息列表验证显示消息内容
        """
        import random
        msg_content = f"P2P测试{random.randint(1000,9999)}"

        # userB向userA发文本
        self.userB.send_message("popoqa50", msg_content, isback=True)
        time.sleep(2)

        # userA验证消息列表中显示该文本
        pos = self.userA.aw.find_text_by_ocr(msg_content, timeout=10)
        assert pos, f"userA消息列表未看到P2P文本透出: {msg_content}"

    def test_p2p_撤回_message_preview(self):
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
