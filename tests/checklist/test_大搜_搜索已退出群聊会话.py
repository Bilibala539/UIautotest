"""
测试用例: 大搜 - 搜索已退出群聊会话消息 (R10)

R10: 消息tab搜索后左滑筛选条 → 勾选"匹配范围" → "包含已退出会话"
"""
from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal, Search


class TestSearchExitedGroupMessage(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    def test_search_exited_group_message(self):
        """R10: 消息tab筛选'包含已退出会话'"""
        self.userA.search(tab="消息", text="测试", isclose=False)
        self.userA.aw.sleep(0.5)
        # 左滑筛选条露出"匹配范围"
        self.userA.aw.swipe(420, 190, 80, 190, duration=0.4)
        self.userA.click_image(SEARCH_FILTER_MSG_RANGE)
        # 验证并点击"包含已退出会话"选项
        self.userA.text_exists("包含已退出会话", timeout=5)
        # 返回消息列表
        self.userA.click_image(SEARCH_CANCEL, region=Normal.HALF_UP)

    def teardown(self):
        pass
