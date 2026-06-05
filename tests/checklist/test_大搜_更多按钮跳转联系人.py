"""
测试用例: 大搜 - 更多按钮跳转联系人tab (R21)
R21: 全部tab联系人分组下点击"更多"，跳转到联系人tab展示所有匹配结果
"""
from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal, Search


class TestMoreButtonNavigation(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    def test_more_button_jump_to_contacts_tab(self):
        """R21: 全部tab联系人分组下点击'更多'，跳转到联系人tab"""
        self.userA.search(tab="全部", text="测试", isclose=False)
        self.userA.image_exists(SEARCH_ALL_LXR, region=Normal.HALF_UP)
        found = self.userA.aw.find_text_by_ocr("更多", timeout=3, region=Normal.HALF_UP)
        if found:
            self.userA.click_text("更多", region=Search.RESULT_LIST)
            self.userA.image_exists(SEARCH_TAB2, region=Normal.HALF_UP)
        self.userA.click_image(SEARCH_CANCEL, region=Normal.HALF_UP)

    def teardown(self):
        pass
