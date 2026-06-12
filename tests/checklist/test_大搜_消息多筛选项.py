"""
测试用例: 大搜 - 消息多筛选项 (R40)

R40: 消息tab下组合筛选 - 选择"近7天" → 选择所在会话 → 验证多筛选生效
"""
from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal, Search


class TestSearchFilterMultiMsg(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    def test_multi_filter_time_and_session(self):
        """R40: 消息tab组合筛选近7天 + 所在会话"""
        self.userA.search(tab="消息", text="测试", isclose=False)
        self.userA.aw.sleep(0.2)
        self.userA.image_exists(SEARCH_FILTER_MSG_TIME, region=Normal.HALF_UP, timeout=5)
        # 筛选时间
        self.userA.click_image(SEARCH_FILTER_MSG_TIME, region=Normal.HALF_UP)
        self.userA.aw.sleep(0.2)
        self.userA.click_text("近7天")
        self.userA.click_image(ADDLINK_OK_BUTTON, region=Normal.DIALOG_TOP)
        self.userA.aw.sleep(0.2)
        # 筛选所在会话
        self.userA.click_image(SEARCH_FILTER_MSG_SESSION, region=Normal.HALF_UP)
        self.userA.aw.sleep(0.2)
        self.userA.click_text("确定", dy=10, region=Normal.HALF_DOWN)
        self.userA.aw.sleep(0.2)
        self.userA.image_exists(SEARCH_FILTER_MSG_TIME_7BLUE, region=Normal.HALF_UP, timeout=5)
        self.userA.click_image(SEARCH_CANCEL, region=Normal.HALF_UP)

    def teardown(self):
        pass
