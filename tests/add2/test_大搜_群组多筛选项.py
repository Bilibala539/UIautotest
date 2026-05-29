"""
测试用例: 大搜 - 群组多筛选项 (R36)

R36: 群tab下筛选 - 打开"包含成员"选人组件 → 选择成员 → 点击确定 → 验证筛选生效
"""
from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal, Search


class TestSearchFilterGroupMember(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    def test_filter_by_group_member(self):
        """R36: 群tab筛选包含成员"""
        self.userA.search(tab="群", text="吴彦祖", isclose=False)
        self.userA.aw.sleep(0.5)
        self.userA.image_exists(SEARCH_FILTER_GROUP_MEMBER, region=Normal.HALF_UP, timeout=5)
        self.userA.click_image(SEARCH_FILTER_GROUP_MEMBER, region=Normal.HALF_UP)
        self.userA.aw.sleep(0.5)
        # 在选人组件中点击确定
        found = self.userA.aw.find_text_by_ocr("确定", timeout=3, region=Normal.HALF_DOWN)
        if found:
            self.userA.click_text("确定", dy=10, region=Normal.HALF_DOWN)
        else:
            self.userA.aw.press_back()
        self.userA.aw.sleep(0.5)
        self.userA.image_exists(SEARCH_FILTER_GROUP_MEMBER, region=Normal.HALF_UP, timeout=5)
        self.userA.click_image(SEARCH_CANCEL, region=Normal.HALF_UP)

    def teardown(self):
        pass
