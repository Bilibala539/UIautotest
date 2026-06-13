"""
测试用例: 独立大搜
功能点: 支持搜索@我、Pin消;大搜
来源: 搜索.xlsx 行74
"""
import time

from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal


class TestCase28(BaseTest):
    """支持搜索@我、Pin消;大搜 - 独立大搜"""

    def setup(self):
        self.userA = self.users("userA")

    def test_case(self):
        """
        独立大搜
        前置条件: 
        步骤: 在独立大搜中勾选匹配范围中的选项，查看是否返回对应的结果
        预期: 独立大搜中勾选匹配范围中的选项，可以返回对应的结果
        """
        # 进入大搜-消息Tab
        self.userA.aw.click_image(MESSAGE_TAB_SEARCH, region=Normal.HALF_UP)
        time.sleep(1)
        self.userA.aw.image_exists(SEARCH_EMPTY, timeout=5)
        self.userA.aw.click_text("消息", timeout=5, region=Normal.HALF_UP)
        time.sleep(1)
        # 点击匹配范围查看选项
        self.userA.aw.click_text("匹配范围", timeout=5)
        time.sleep(1)
        self.userA.aw.text_exists("只看@我的消息", timeout=5)
        self.userA.aw.press_back()
        time.sleep(1)
        # 验证
        self.userA.aw.text_exists("匹配范围", timeout=3, region=Normal.HALF_UP)

    def teardown(self):
        self.userA.aw.return_to_message_list(max_back=6)
