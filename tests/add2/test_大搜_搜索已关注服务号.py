"""
测试用例: 大搜 - 搜索已关注服务号 (R12)
R12: 搜索已关注服务号，点击跳转到服务号资料页
"""
from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal, Search


class TestSearchFollowedService(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    def test_search_followed_service_account(self):
        """R12: 搜索已关注服务号，验证能搜到并有服务号标签"""
        self.userA.search(tab="全部", text="阿鱼", isclose=False)
        self.userA.image_exists(SEARCH_RESULT_AYU, region=Normal.HALF_UP)
        self.userA.image_exists(ICON_FUWUHAO, region=Normal.HALF_UP)
        self.userA.click_image(SEARCH_CANCEL, region=Normal.HALF_UP)

    def teardown(self):
        pass
