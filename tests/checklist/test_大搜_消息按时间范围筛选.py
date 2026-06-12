"""
测试用例: 大搜 - 消息按时间范围筛选 (R28)

R28: 消息tab下筛选时间范围 - 打开"全部时间"下拉 → 选择"近7天" → 验证筛选生效
"""
from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal, Search


class TestSearchFilterByTime(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    def test_filter_by_recent_7_days(self):
        """R28: 消息tab筛选近7天消息"""
        self.userA.search(tab="消息", text="测试", isclose=False)
        self.userA.aw.sleep(0.2)
        self.userA.click_image(SEARCH_FILTER_MSG_TIME, region=Normal.HALF_UP)
        self.userA.aw.sleep(0.2)
        self.userA.click_text("近7天", dy=10)
        self.userA.click_image(ADDLINK_OK_BUTTON, region=Normal.DIALOG_TOP)
        self.userA.aw.sleep(0.2)
        self.userA.image_exists(SEARCH_FILTER_MSG_TIME_7BLUE, region=Normal.HALF_UP, timeout=5)
        self.userA.click_image(SEARCH_CANCEL, region=Normal.HALF_UP)

    def teardown(self):
        pass
