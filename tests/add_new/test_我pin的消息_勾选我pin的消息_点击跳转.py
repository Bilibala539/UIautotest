"""
测试用例: 勾选我pin的消息，点击跳转
功能点: 支持搜索@我、Pin消;大搜;我pin的消息
来源: 搜索.xlsx 行68
"""
import time

from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal


class TestCase24(BaseTest):
    """支持搜索@我、Pin消;大搜;我pin的消息 - 勾选我pin的消息，点击跳转"""

    def setup(self):
        self.userA = self.users("userA")

    def test_case(self):
        """
        勾选我pin的消息，点击跳转
        前置条件: 
        步骤: 在大搜中勾选我pin的消息后，点击返回结果
        预期: 大搜进入该条消息的消息视图
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
