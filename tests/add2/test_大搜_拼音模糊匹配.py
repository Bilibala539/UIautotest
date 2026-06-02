"""
测试用例: 大搜 - 拼音模糊匹配 (R20)
R20: 输入拼音缩写/全拼，匹配到对应服务号，关键字高亮
"""
import pytest
from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal


class TestPinyinFuzzyMatch(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    @pytest.mark.parametrize("keyword", [
        pytest.param("bjxz", id="R20_拼音首字母"),
        pytest.param("beijingxingzheng", id="R20_全拼"),
    ])
    def test_pinyin_fuzzy_match(self, keyword):
        """R20: 拼音模糊匹配，联系人分组匹配到对应服务号"""
        self.userA.search(tab="全部", text=keyword, isclose=False)
        # 用 OCR 验证联系人分组出现（图片匹配对版本敏感，改用文字断言）
        found_lxr = self.userA.aw.find_text_by_ocr("联系人", timeout=5,
                                                     region=Normal.HALF_UP)
        assert found_lxr is not None, f"拼音'{keyword}'搜索结果中未出现联系人分组"
        found_empty = self.userA.aw.find_text_by_ocr("暂无搜索结果", timeout=3)
        assert found_empty is None, f"拼音'{keyword}'应匹配到结果，不应为空"
        self.userA.click_image(SEARCH_CANCEL, region=Normal.HALF_UP)

    def teardown(self):
        pass
