"""
测试用例: 大搜 - 搜索联系人（拼音）(R6-拼音)
R6: 通过拼音"wangying43"搜索联系人，点击进入P2P会话
"""
from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal, Search


class TestSearchContactByPinyin(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    def test_search_contact_by_pinyin(self):
        """R6: 联系人tab通过拼音搜索，点击进入P2P会话"""
        self.userA.search(tab="联系人", text="wangying43", isclose=False)
        result = self.userA.aw.find_text_by_ocr("王英", timeout=5, region=Search.RESULT_LIST)
        assert result is not None, "拼音搜索'wangying43'未在联系人tab找到王英"
        self.userA.click_text("王英", region=Search.RESULT_LIST)
        self.userA.aw.sleep(1)
        in_chat_text = self.userA.aw.find_text_by_ocr("发送给", timeout=5)
        if in_chat_text is None:
            send_btn = self.userA.aw.find_text_by_ocr("发消息", timeout=3)
            if send_btn:
                self.userA.click_text("发消息")
                self.userA.aw.sleep(1)
        self.userA.image_exists(CHAT_PLUS_BUTTON, region=Normal.HALF_DOWN, timeout=10)
        self.userA.return_to_message_list()

    def teardown(self):
        pass
