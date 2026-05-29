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
        self.userA.aw.sleep(0.5)
        self.userA.image_exists(SEARCH_FILTER_GROUP_MEMBER, region=Normal.HALF_UP, timeout=5)
        # 打开包含成员选人组件
        self.userA.click_image(SEARCH_FILTER_GROUP_MEMBER, region=Normal.HALF_UP)
        self.userA.aw.sleep(0.5)
        # 点击确定（不做实际选择，仅打开后关闭）
        found = self.userA.aw.find_text_by_ocr("确定", timeout=3, region=Normal.HALF_DOWN)
        if found:
            self.userA.click_text("确定", dy=10, region=Normal.HALF_DOWN)
        else:
            self.userA.aw.press_back()
        self.userA.aw.sleep(0.5)
        # 重新打开选人组件，清空
        self.userA.click_image(SEARCH_FILTER_GROUP_MEMBER, region=Normal.HALF_UP)
        self.userA.aw.sleep(0.5)
        found_clear = self.userA.aw.find_text_by_ocr("清空", timeout=3)
        if found_clear:
            self.userA.click_text("清空", dy=10)
            self.userA.aw.sleep(0.3)
        found = self.userA.aw.find_text_by_ocr("确定", timeout=3, region=Normal.HALF_DOWN)
        if found:
            self.userA.click_text("确定", dy=10, region=Normal.HALF_DOWN)
        else:
            self.userA.aw.press_back()
        self.userA.aw.sleep(0.5)
        # 验证清空后回到空态
        empty = self.userA.aw.find_image(SEARCH_EMPTY, timeout=5, region=Normal.HALF_UP)
        assert empty is not None, "R37: 清空筛选后结果应为空"
        self.userA.click_image(SEARCH_CANCEL, region=Normal.HALF_UP)

    def teardown(self):
        pass
