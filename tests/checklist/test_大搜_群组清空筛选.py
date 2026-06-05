"""
测试用例: 大搜 - 群组清空筛选 (R37)

R37: 群tab下清空筛选 - 选择成员筛选 → 重新打开选人组件 → 清空选中 → 确定 → 验证结果为空
"""
from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal, Search


class TestSearchFilterGroupClear(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    def test_clear_group_member_filter(self):
        """R37: 群tab清空包含成员筛选"""
        self.userA.search(tab="群", text="测试", isclose=False)
        self.userA.aw.sleep(0.2)
        # 打开包含成员选人组件
        self.userA.click_image(SEARCH_FILTER_GROUP_MEMBER, region=Normal.HALF_UP)
        self.userA.aw.sleep(0.2)
        # 点击确定（不做实际选择，仅打开后关闭）
        self.userA.click_text("确定", dy=10, region=Normal.HALF_DOWN)
        self.userA.aw.sleep(0.2)
        # 重新打开选人组件，选人，清空
        self.userA.click_image(SEARCH_FILTER_GROUP_MEMBER, region=Normal.HALF_UP)
        self.userA.click_image(SELECT_CONTACTR_TAB, region=Normal.HALF_UP)
        self.userA.click_image(SELECT_CIRCLE)
        self.userA.click_image(SELECT_OK_BLUE, region=Normal.HALF_DOWN)
        self.userA.image_exists(SEARCH_FILTER_GROUP_MEMBER_BLUE, region=Normal.HALF_UP)
        self.userA.aw.sleep(0.2)
        self.userA.click_image(SEARCH_FILTER_DELETE, dy=10, region=Normal.HALF_UP)
        # 验证清空后回到空态
        self.userA.image_exists(SEARCH_FILTER_GROUP_MEMBER, region=Normal.HALF_UP)

    def teardown(self):
        pass
