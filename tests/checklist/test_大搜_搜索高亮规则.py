"""
测试用例: 大搜 - 搜索高亮规则 (R22)
R22: 搜索结果中关键词应蓝色高亮显示
"""
from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal


class TestSearchHighlight(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    def test_keyword_highlight_rule(self):
        """R22: 搜索结果中关键词高亮（验证蓝色高亮图片出现）"""
        self.userA.search(tab="全部", text="王英", isclose=False)
        self.userA.image_exists(SEARCH_WANGYING_BLUE, region=Normal.HALF_UP)
        self.userA.click_image(SEARCH_CANCEL, region=Normal.HALF_UP)

    def teardown(self):
        pass
