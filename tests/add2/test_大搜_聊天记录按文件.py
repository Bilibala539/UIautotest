"""
测试用例: 大搜 - 聊天记录消息被删除后仍可搜索到 (R31)

R31 对应 xlsx R30: 消息已被删除，服务端搜索仍会下载到本地，进行显示
"""
import random

from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal, Search

RECIPIENT = "grp.popoqa93"
RECIPIENT_EMAIL = "grp.popoqa93@corp.netease.com"


class TestSearchDeletedMessageStillShows(BaseTest):

    def setup(self):
        self.userA = self.users("userA")
        # 造数：CLI 发一条随机内容消息
        self.msg_content = f"删除仍显示测试{random.randint(10000, 99999)}"
        self.userA.cli.send_message_p2p_cli(
            receiver=RECIPIENT_EMAIL,
            message=self.msg_content,
        )
        # UI 进入聊天页，本地删除该消息
        # UI 进入聊天页：直接从消息列表点击会话
        self.userA.click_text(RECIPIENT)
        self.userA.aw.sleep(1)
        self.userA.image_exists(CHAT_PLUS_BUTTON, region=Normal.HALF_DOWN, timeout=8)
        # CLI 消息刚发，在最底部附近，找3次
        found = None
        for _ in range(3):
            found = self.userA.aw.find_text_by_ocr(self.msg_content, timeout=2)
            if found:
                break
            self.userA.aw.swipe_up(distance=300)
            self.userA.aw.sleep(0.5)
        assert found is not None, f"setup: 未在聊天页找到消息 '{self.msg_content}'"
        self.userA.aw.long_press_text(self.msg_content, duration=1.5)
        self.userA.click_text("删除", region=Normal.HALF_DOWN)
        # 确认删除弹窗
        self.userA.click_text("删除", region=Normal.CENTER_POP)
        self.userA.aw.sleep(1)
        self.userA.return_to_message_list()

    def test_deleted_message_still_searchable(self):
        """R31: 消息本地删除后，服务端搜索仍能找到并下载显示"""
        self.userA.search(tab="消息", text=self.msg_content, isclose=False)
        self.userA.aw.sleep(2)
        # 验证：服务端搜索仍能返回该消息
        found = self.userA.aw.find_text_by_ocr(self.msg_content, timeout=10,
                                                region=Search.RESULT_LIST)
        assert found is not None,             f"R31: 消息已本地删除，但服务端搜索未能返回该消息 '{self.msg_content}'"
        # 点击搜索结果，验证能进入聊天页并看到消息（服务端下载到本地显示）
        self.userA.click_text(self.msg_content, region=Search.RESULT_LIST)
        self.userA.aw.sleep(2)
        # 验证进入聊天页
        in_chat = self.userA.aw.find_image(CHAT_PLUS_BUTTON, timeout=5,
                                            region=Normal.HALF_DOWN)
        if in_chat:
            # 进入聊天页后验证消息可见（服务端重新下载到本地）
            msg_visible = self.userA.aw.find_text_by_ocr(
                self.msg_content, timeout=5)
            assert msg_visible is not None,                 "R31: 点击搜索结果进入聊天页后，消息未重新加载显示"
        self.userA.return_to_message_list()

    def teardown(self):
        pass
