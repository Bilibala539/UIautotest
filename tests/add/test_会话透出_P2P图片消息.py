"""
测试用例: P2P图片消息透出
覆盖文字用例: P2P图片消息透出
"""
import os
import time

import pytest
from conftest import BaseTest


class TestP2PImageMessagePreview(BaseTest):
    """P2P图片消息透出: userB向userA发送图片，userA在消息列表验证显示[图片]"""

    def setup(self):
        if os.environ.get("INSTANCE_ID"):
            pytest.skip("需要双设备跨进程通讯，并行模式下跳过")
        self.userA = self.users("userA")
        self.userB = self.users("userB")

    def test_p2p_image_message_preview(self):
        """
        P2P图片消息透出:
        userB向userA发送一张图片，userA在消息列表验证显示[图片]
        """
        # userB向userA发送图片
        self.userB.send_image_from_album(self.userA.uid)
        time.sleep(2)

        # userB返回消息列表
        self.userB.aw.press_back()
        time.sleep(1)

        # userA验证消息列表中显示图片透出
        pos = self.userA.aw.find_text_by_ocr("图片", timeout=10)
        assert pos, "userA消息列表未看到P2P图片消息透出"

    def teardown(self):
        pass
