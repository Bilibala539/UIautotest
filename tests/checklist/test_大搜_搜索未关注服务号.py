"""
测试用例: 大搜 - 搜索未关注服务号 (R11)
R11: 搜索未关注服务号，点击弹出资料卡片
"""
from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal, Search


class TestSearchUnfollowedService(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    def test_search_unfollowed_service_account(self):
        """R11: 搜索未关注服务号，点击弹出服务号资料卡"""
        self.userA.search(tab="全部", text="广州行政助手", isclose=False)
        self.userA.image_exists(SEARCH_RESULT_GZXZZS, region=Normal.HALF_UP)
        self.userA.click_image(SEARCH_RESULT_GZXZZS, region=Normal.HALF_UP)
        self.userA.text_exists("广州行政助手", timeout=5)
        self.userA.aw.press_back()
        self.userA.click_image(SEARCH_CANCEL, region=Normal.HALF_UP)

    def teardown(self):
        pass
