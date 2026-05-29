"""
测试用例: 大搜 - 群组tab无关键词不输入不搜索结果为空 (R34)
R34: 唤起大搜切换到消息tab，不输入关键词，验证大搜结果返回为空
"""
from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal


class TestGroupTabNoKeyword(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    def test_switch_to_message_tab_without_keyword(self):
        """R34: 唤起大搜切换到消息tab，不输入关键词，验证大搜结果返回为空"""
        self.userA.click_image(MESSAGE_TAB_SEARCH, region=Normal.HALF_UP)
        on_page = self.userA.aw.find_text_by_ocr("搜索", timeout=5)
        assert on_page is not None, "搜索页未打开（未找到搜索占位文字）"
        self.userA.click_image(SEARCH_TAB4_NO, region=Normal.HALF_UP)
        self.userA.image_exists(SEARCH_TAB4, region=Normal.HALF_UP)
        no_results = self.userA.aw.find_text_by_ocr("暂无搜索结果", timeout=3)
        if no_results is None:
            hint = self.userA.aw.find_text_by_ocr("关键词", timeout=3)
            assert hint is not None or no_results is not None, \
                "消息tab无关键词时应显示空态提示"
        self.userA.click_image(SEARCH_CANCEL, region=Normal.HALF_UP)

    def teardown(self):
        pass
