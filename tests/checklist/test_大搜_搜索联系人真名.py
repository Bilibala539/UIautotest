"""
测试用例: 大搜 - 搜索联系人（真名）(R6-真名)
R6: 通过真名"王英"搜索联系人，点击进入P2P会话
"""
from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal, Search


class TestSearchContactByName(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    def test_search_contact_by_name(self):
        """R6: 联系人tab通过真名搜索，点击进入P2P会话"""
        self.userA.search(tab="联系人", text="王英", isclose=False)
        result = self.userA.aw.find_text_by_ocr("王英", timeout=5, region=Search.RESULT_LIST)
        assert result is not None, "真名搜索'王英'未在联系人tab找到结果"
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
