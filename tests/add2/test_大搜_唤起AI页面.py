"""
测试用例: 大搜 - 唤起AI页面 (R24)
R24: 点击搜索页右上角AI icon，跳转到AI助手页面
"""
from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal, Search


class TestInvokeAIPage(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    def test_invoke_ai_page(self):
        """R24: 点击搜索页右上角AI icon，验证跳转到AI助手页面"""
        self.userA.click_image(MESSAGE_TAB_SEARCH, region=Normal.HALF_UP)
        self.userA.click_image(SEARCH_AI, region=Search.SEARCH_TAB)
        self.userA.aw.find_image(WORKHUB_TEXT, region=Normal.HALF_UP)

    def teardown(self):
        pass
