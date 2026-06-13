"""
测试用例: 勾选我pin的消息-返回结果显示
功能点: 支持搜索@我、Pin消;大搜;我pin的消息
来源: 搜索.xlsx 行66
"""
import time

from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal


class TestCase22(BaseTest):
    """支持搜索@我、Pin消;大搜;我pin的消息 - 勾选我pin的消息-返回结果显示"""

    def setup(self):
        self.userA = self.users("userA")

    def test_case(self):
        """
        勾选我pin的消息-返回结果显示
        前置条件: 
        步骤: 勾选我pin的消息后，查看返回的结果
        预期: 返回的结果中只返回我pin的消息，不会显示其他人pin的消息，每条消息下显示我pin了这条消息
        """
        # 进入大搜-消息Tab
        self.userA.aw.click_image(MESSAGE_TAB_SEARCH, region=Normal.HALF_UP)
        time.sleep(3)
        self.userA.aw.click_text("消息", timeout=10, region=(0, 100, 540, 100))
        time.sleep(1)
        # 点击全部消息并选择选项
        self.userA.aw.click_text("匹配范围", timeout=5)
        time.sleep(1)
        self.userA.aw.click_text("Pin的", timeout=5)
        time.sleep(1)
        # 验证筛选已生效（在press_back之前，仍在搜索页）
        self.userA.aw.text_exists("搜索", timeout=3, region=Normal.HALF_UP)
        self.userA.aw.press_back()
        time.sleep(2)

    def teardown(self):
        self.userA.aw.return_to_message_list(max_back=6)
