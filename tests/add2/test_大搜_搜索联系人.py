"""
测试用例: 大搜 - 搜索联系人 (R6)
R6: 通过真名/拼音搜索联系人，点击进入P2P会话
"""
import pytest
from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal, Search


class TestSearchContact(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    @pytest.mark.parametrize("keyword", [
        pytest.param("王英", id="R6_真名搜索"),
        pytest.param("wangying43", id="R6_拼音搜索"),
    ])
    def test_search_contact_and_open_chat(self, keyword):
        """R6: 联系人tab搜索联系人并点击，验证打开P2P会话"""
        self.userA.search(tab="联系人", text=keyword, isclose=False)
        result = self.userA.aw.find_text_by_ocr("王英", timeout=5, region=Search.RESULT_LIST)
        assert result is not None, f"搜索'{keyword}'未在联系人tab找到王英"
        self.userA.click_text("王英", region=Search.RESULT_LIST)
        self.userA.image_exists(CHAT_PLUS_BUTTON, region=Normal.HALF_DOWN)
        self.userA.return_to_message_list()

    def teardown(self):
        pass
