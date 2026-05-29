"""
测试用例: 大搜 - 群组tab切换筛选 (R38)

R38: 群tab下无关键词无筛选 → 验证空态 → 加筛选（默认排序→最近更新）→ 验证有结果
"""
from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal, Search


class TestSearchFilterGroupTabSwitch(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    def test_group_tab_filter_switch(self):
        """R38: 群tab无关键词时加筛选验证结果变化"""
        # 进入搜索页，切到群tab
        self.userA.click_image(MESSAGE_TAB_SEARCH, region=Normal.HALF_UP)
        self.userA.aw.sleep(0.5)
        self.userA.click_image(SEARCH_TAB3_NO, region=Normal.HALF_UP)
        self.userA.image_exists(SEARCH_TAB3, region=Normal.HALF_UP)
        # 无关键词无筛选 → 空态
        self.userA.image_exists(SEARCH_EMPTY)
        # 打开默认排序下拉，选"最近更新"
        self.userA.click_image(SEARCH_FILTER_GROUP_SORT, region=Normal.HALF_UP)
        self.userA.aw.sleep(0.5)
        self.userA.click_text("最近更新", dy=10)
        self.userA.aw.sleep(0.5)
        # 验证筛选条出现
        self.userA.text_exists("最近更新", region=Search.RESULT_LIST, timeout=5)
        self.userA.click_image(SEARCH_CANCEL, region=Normal.HALF_UP)

    def teardown(self):
        pass
