"""
测试用例: 大搜 - 日程搜索 (R18)

R18: 搜索页切到日程tab → 搜索已有日程 → 验证结果出现
"""
from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal, Search


class TestSearchSchedule(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    def test_search_schedule(self):
        """R18: 日程tab搜索已有日程可查到"""
        self.userA.click_image(MESSAGE_TAB_SEARCH, region=Normal.HALF_UP)
        self.userA.aw.sleep(0.5)
        # 切到日程tab
        self.userA.click_text("日程", dy=10)
        self.userA.aw.sleep(0.5)
        # 验证日程搜索页就绪
        assert self.userA.aw.find_text_by_ocr("输入关键词查找日程", timeout=3) is not None, \
            "R18: 日程搜索页未就绪（未找到占位文字）"
        assert self.userA.aw.find_text_by_ocr("参与人", timeout=3) is not None, \
            "R18: 日程搜索页缺'参与人'筛选项"
        # 输入关键词搜索
        self.userA.click_image(SELECT_SEARCH, dx=10)
        self.userA.input_text("会议")
        self.userA.aw.sleep(1)
        # 验证搜索结果
        assert self.userA.aw.find_text_by_ocr("已加载全部", timeout=8) is not None, \
            "R18: 日程搜索结果未加载（未找到'已加载全部'）"
        # 返回消息列表
        self.userA.click_image(SEARCH_CANCEL, region=Normal.HALF_UP)

    def teardown(self):
        pass
