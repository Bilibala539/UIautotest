"""
测试用例: 大搜 - 搜索结果数量控制 (R19)
R19: 全部tab输入关键词，联系人分组混排结果最多展示3个
"""
from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal


class TestSearchResultCount(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    def test_result_count_limit(self):
        """R19: 联系人分组混排结果最多展示3个"""
        self.userA.search(tab="全部", text="测试", isclose=False)
        self.userA.image_exists(SEARCH_ALL_LXR, region=Normal.HALF_UP)
        self.userA.click_image(SEARCH_CANCEL, region=Normal.HALF_UP)

    def teardown(self):
        pass
