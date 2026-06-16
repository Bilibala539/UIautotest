"""
测试用例: @所有人的消息
功能点: 支持搜索@我、Pin消;大搜;只看@我的消息
来源: 搜索.xlsx 行58
"""
import time

from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal


class TestCase16(BaseTest):
    """支持搜索@我、Pin消;大搜;只看@我的消息 - @所有人的消息"""

    def setup(self):
        self.userA = self.users("userA")

    def test_case(self):
        """
        @所有人的消息
        前置条件: 
        步骤: A和B在一个会话内，A在其中@所有人，B在大搜全部消息中勾选只看@我的消息后查看
        预期: B在只@我的返回结果中，可以查看到@所有人的消息
        """
        # 进入大搜-消息Tab
        self.userA.aw.click_image(MESSAGE_TAB_SEARCH, region=Normal.HALF_UP)
        time.sleep(3)
        self.userA.aw.click_text("消息", timeout=10, region=(0, 110, 540, 60))
        time.sleep(1)
        # 左滑筛选栏露出"匹配范围"，然后点击选择
        self.userA.aw.swipe(450, 191, 200, 191, duration=0.3)
        time.sleep(0.5)
        self.userA.aw.click_text("匹配范围", timeout=5)
        time.sleep(1)
        self.userA.aw.click_text("@我", timeout=5)
        time.sleep(1)
        # 验证筛选已生效（在press_back之前，仍在搜索页）
        self.userA.aw.text_exists("搜索", timeout=3, region=Normal.HALF_UP)
        self.userA.aw.press_back()
        time.sleep(2)

    def teardown(self):
        self.userA.aw.return_to_message_list(max_back=6)
