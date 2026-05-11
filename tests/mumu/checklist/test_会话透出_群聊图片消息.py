"""
测试用例: 会话盒子/会话列表消息透出-图片消息
功能点: 收到图片消息后会话列表正确展示"[图片]"透出
操作步骤: userB向群发送一条图片消息，userA在消息列表验证
预期结果: 显示最新一条消息的透出提示（包含[图片]标识）
"""
import time
from conftest import BaseTest


class TestSessionPreviewImage(BaseTest):
    """会话列表消息透出-图片消息"""

    def setup(self):
        self.userA = self.users("userA")
        self.userB = self.users("userB")

    def test_image_message_preview_in_list(self):
        """
        步骤:
        1. userB向共同群组发送一张图片
        2. userA在消息列表页验证该群会话显示[图片]透出
        """
        # userB发送图片到共同群组
        self.userB.send_image_from_album("grp.popoqa93")
        time.sleep(2)

        # userB返回消息列表
        self.userB.aw.press_back()
        time.sleep(1)

        # userA在消息列表验证透出（图片消息通常显示"[图片]"）
        pos = self.userA.aw.find_text_by_ocr("图片", timeout=10)
        assert pos, "userA消息列表未看到图片消息透出"

    def teardown(self):
        pass
