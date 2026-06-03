"""
测试用例: 大搜 - 顶部字体不适配 (R1)

R1: 验证大搜字体不随POPO字体设置变化
步骤: 切换POPO字体为大字体 -> 打开大搜 -> 验证tab文字和搜索框仍可正常识别
"""
import pytest
from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal, Search


class TestSearchFontAdaptation(BaseTest):

    def setup(self):
        self.userA = self.users("userA")
        self._font_changed = False

    def _change_font_size(self, target_text):
        """
        进入设置->通用->字体大小，点击目标字号。
        返回True表示成功切换，False表示路径不存在。
        """
        self.userA.open_settings()
        self.userA.click_text("通用")
        self.userA.aw.sleep(1)
        # 查找字体大小入口
        font_entry = self.userA.aw.find_text_by_ocr("字体大小", timeout=5)
        if font_entry is None:
            font_entry = self.userA.aw.find_text_by_ocr("字号", timeout=3)
        if font_entry is None:
            return False
        self.userA.click_text("字体大小" if self.userA.aw.find_text_by_ocr("字体大小", timeout=2) else "字号")
        self.userA.aw.sleep(1)
        self.userA.click_text(target_text)
        self.userA.aw.sleep(1)
        self.userA.return_to_message_list(max_back=8)
        return True

    def test_font_size_not_affect_search(self):
        """R1: 切换大字体后，大搜页面仍正常显示"""
        # 切换为大字体
        changed = self._change_font_size("大")
        if not changed:
            pytest.skip("未找到字体大小设置入口，跳过此用例")
        self._font_changed = True

        # 打开大搜
        self.userA.search(tab="全部", text="测试", isclose=False)
        self.userA.aw.sleep(1)

        # 验证大搜页面核心元素仍可识别
        # 1. 搜索框图片存在
        self.userA.image_exists(SELECT_SEARCH, region=Normal.HALF_UP, timeout=5)
        # 2. tab文字可OCR识别
        self.userA.text_exists("全部", region=Search.SEARCH_TAB, timeout=5)

        # 退出搜索
        self.userA.click_image(SEARCH_CANCEL, region=Normal.HALF_UP)

    def teardown(self):
        # 恢复字体设置为标准
        if self._font_changed:
            self._change_font_size("标准")
