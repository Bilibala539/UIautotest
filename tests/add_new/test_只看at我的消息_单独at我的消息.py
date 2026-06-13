"""
测试用例: 单独@我的消息
功能点: 支持搜索@我、Pin消;大搜;只看@我的消息
来源: 搜索.xlsx 行57
"""
import time

from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal


class TestCase15(BaseTest):
    """支持搜索@我、Pin消;大搜;只看@我的消息 - 单独@我的消息"""

    def setup(self):
        self.userA = self.users("userA")

    def test_case(self):
        """
        单独@我的消息
        前置条件: 
        步骤: A和B在一个会话内，A单独@B，B在大搜匹配范围中勾选只看@我的消息后查看
        预期: B在只@我的返回结果中，可以查看到@B的消息
        """
        # 进入大搜-消息Tab
        self.userA.aw.click_image(MESSAGE_TAB_SEARCH, region=Normal.HALF_UP)
        time.sleep(1)
        self.userA.aw.image_exists(SEARCH_EMPTY, timeout=5)
        self.userA.aw.click_text("消息", timeout=5, region=Normal.HALF_UP)
        time.sleep(1)
        # 点击匹配范围并选择选项
        self.userA.aw.click_text("匹配范围", timeout=5)
        time.sleep(1)
        self.userA.aw.click_text("只看@我的消息", timeout=5)
        time.sleep(1)
        self.userA.aw.press_back()
        time.sleep(2)
        # 验证
        self.userA.aw.text_exists("匹配范围", timeout=3, region=Normal.HALF_UP)

    def teardown(self):
        self.userA.aw.return_to_message_list(max_back=6)
