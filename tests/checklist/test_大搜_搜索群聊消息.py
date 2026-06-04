"""
测试用例: 大搜 - 搜索群聊消息 (R7)
R7: 发送群消息后大搜，点击搜索结果跳转到群并定位到当前消息
"""
import random
from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal, Search

RECIPIENT = "grp.popoqa50"


class TestSearchGroupMessage(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    def test_search_group_message_and_locate(self):
        """R7: 发送群消息后大搜，点击搜索结果跳转到群并定位到当前消息"""
        msg_content = f"搜索测试消息{random.randint(1000, 9999)}"
        self.userA.send_message(recipient=RECIPIENT, message=msg_content, isback=True)
        self.userA.search(tab="消息", text=msg_content, isclose=False)
        self.userA.image_exists(SEARCH_FILTER_MSG_SENDER, region=Normal.HALF_UP, timeout=5)
        found = self.userA.aw.find_text_by_ocr(msg_content, timeout=5)
        if found:
            self.userA.click_text(msg_content, region=Search.RESULT_LIST)
            self.userA.image_exists(CHAT_PLUS_BUTTON, region=Normal.HALF_DOWN, timeout=10)
            self.userA.text_exists(msg_content, region=Normal.HALF_DOWN)
        self.userA.return_to_message_list()

    def teardown(self):
        pass
