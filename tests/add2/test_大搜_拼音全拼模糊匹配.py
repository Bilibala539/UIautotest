"""
测试用例: 大搜 - 拼音全拼模糊匹配 (R20-全拼)
R20: 输入全拼"beijingxingzheng"，全部tab联系人分组能匹配到北京行政服务号
"""
from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal


class TestPinyinFullMatch(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    def test_pinyin_full_match(self):
        """R20: 全拼搜索，联系人分组匹配到对应服务号"""
        self.userA.search(tab="全部", text="beijingxingzheng", isclose=False)
        found_lxr = self.userA.aw.find_text_by_ocr("联系人", timeout=5,
                                                     region=Normal.HALF_UP)
        assert found_lxr is not None, "全拼'beijingxingzheng'搜索结果中未出现联系人分组"
        found_empty = self.userA.aw.find_text_by_ocr("暂无搜索结果", timeout=3)
        assert found_empty is None, "全拼'beijingxingzheng'应匹配到结果，不应为空"
        self.userA.click_image(SEARCH_CANCEL, region=Normal.HALF_UP)

    def teardown(self):
        pass
