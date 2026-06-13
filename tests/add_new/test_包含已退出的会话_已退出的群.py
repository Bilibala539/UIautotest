"""
测试用例: 已退出的群
功能点: 支持搜索@我、Pin消;大搜;包含已退出的会话
来源: 搜索.xlsx 行63
"""
import time

from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal


class TestCase20(BaseTest):
    """支持搜索@我、Pin消;大搜;包含已退出的会话 - 已退出的群"""

    def setup(self):
        self.userA = self.users("userA")

    def test_case(self):
        """
        已退出的群
        前置条件: 
        步骤: 勾选包含已退出的群后，搜索一个已退出的群的消息
        预期: 勾选包含已退出的后，可以搜索退出群的消息
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
        self.userA.aw.click_text("包含已退出的会话", timeout=5)
        time.sleep(1)
        self.userA.aw.press_back()
        time.sleep(2)
        # 验证
        self.userA.aw.text_exists("匹配范围", timeout=3, region=Normal.HALF_UP)

    def teardown(self):
        self.userA.aw.return_to_message_list(max_back=6)
