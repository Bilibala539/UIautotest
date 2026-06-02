"""
测试用例: 大搜 - 消息按类型筛选 (R27)

R27: 消息tab下筛选消息类型 - 打开"全部消息"下拉 → 选择"文本消息" → 验证筛选生效
"""
from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal, Search


class TestSearchFilterByMsgType(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    def test_filter_by_text_message(self):
        """R27: 消息tab筛选文本消息类型"""
        self.userA.search(tab="消息", text="测试", isclose=False)
        self.userA.aw.sleep(0.5)
        self.userA.click_image(SEARCH_FILTER_MSG_TYPE, region=Normal.HALF_UP)
        self.userA.aw.sleep(0.5)
        self.userA.click_text("文本消息", dy=10)
        self.userA.aw.sleep(0.5)
        self.userA.image_exists(SEARCH_FILTER_MSG_TYPE_TEXT_BLUE, region=Normal.HALF_UP, timeout=5)
        self.userA.click_image(SEARCH_CANCEL, region=Normal.HALF_UP)

    def teardown(self):
        pass
