"""
测试用例: 大搜 - 拼音缩写模糊匹配 (R20-缩写)
R20: 输入拼音缩写"bjxz"，全部tab联系人分组能匹配到北京行政服务号
"""
from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal


class TestPinyinAbbrevMatch(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    def test_pinyin_abbrev_match(self):
        """R20: 拼音首字母缩写搜索，联系人分组匹配到对应服务号"""
        self.userA.search(tab="全部", text="bjxz", isclose=False)
        found_lxr = self.userA.aw.find_text_by_ocr("联系人", timeout=5,
                                                     region=Normal.HALF_UP)
        assert found_lxr is not None, "拼音缩写'bjxz'搜索结果中未出现联系人分组"
        found_empty = self.userA.aw.find_text_by_ocr("暂无搜索结果", timeout=3)
        assert found_empty is None, "拼音缩写'bjxz'应匹配到结果，不应为空"
        self.userA.click_image(SEARCH_CANCEL, region=Normal.HALF_UP)

    def teardown(self):
        pass
