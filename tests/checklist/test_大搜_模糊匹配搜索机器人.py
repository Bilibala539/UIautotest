"""
测试用例: 大搜 - 模糊匹配搜索机器人 (R16)
R16: 模糊匹配搜索机器人账号，验证能搜到
"""
from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal


class TestSearchBot(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    def test_search_bot_by_fuzzy_name(self):
        """R16: 模糊匹配搜索机器人，验证能搜到机器人账号"""
        self.userA.search(tab="全部", text="助手", isclose=False)
        self.userA.image_exists(SEARCH_ALL_LXR, region=Normal.HALF_UP)
        found_empty = self.userA.aw.find_text_by_ocr("暂无搜索结果", timeout=3)
        assert found_empty is None, "搜索'助手'应有搜索结果，不应为空"
        self.userA.click_image(SEARCH_CANCEL, region=Normal.HALF_UP)

    def teardown(self):
        pass
