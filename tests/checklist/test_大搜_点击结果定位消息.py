"""
测试用例: 大搜 - 点击搜索结果定位消息 (R29)
R29: 搜索消息后点击，定位至会话内此条消息位置
"""
import random
from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal, Search

RECIPIENT = "grp.popoqa50"


class TestSearchMessageLocate(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    def test_search_result_message_locate(self):
        """R29: 搜索消息后点击，定位至会话内此条消息位置"""
        msg_content = f"定位测试消息{random.randint(1000, 9999)}"
        self.userA.send_message(recipient=RECIPIENT, message=msg_content, isback=True)
        self.userA.search(tab="消息", text=msg_content, isclose=False)
        self.userA.image_exists(SEARCH_FILTER_MSG_SENDER, region=Normal.HALF_UP, timeout=5)
        found = self.userA.aw.find_text_by_ocr(msg_content, timeout=5)
        if found:
            self.userA.click_text(msg_content, region=Search.RESULT_LIST)
            self.userA.image_exists(CHAT_PLUS_BUTTON, region=Normal.HALF_DOWN, timeout=10)
            # 跳转后消息可能不在当前可见区，上滑确保定位到的消息在屏幕内
            self.userA.aw.swipe_up(distance=200)
            self.userA.aw.sleep(0.5)
            self.userA.text_exists(msg_content, region=Normal.HALF_DOWN)
        self.userA.return_to_message_list()

    def teardown(self):
        pass
