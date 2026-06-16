"""
测试用例: 已解散的群
功能点: 支持搜索@我、Pin消;大搜;包含已退出的会话
来源: 搜索.xlsx 行64
"""
import time

from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal


class TestCase21(BaseTest):
    """支持搜索@我、Pin消;大搜;包含已退出的会话 - 已解散的群"""

    def setup(self):
        self.userA = self.users("userA")

    def test_case(self):
        """
        已解散的群
        前置条件: 
        步骤: 勾选包含已退出的群后，搜索一个已的群的消息
        预期: 勾选包含已退出的后，可以搜索退出群的消息
        """
        # 进入大搜-消息Tab
        self.userA.aw.click_image(MESSAGE_TAB_SEARCH, region=Normal.HALF_UP)
        time.sleep(1)
        if not self.userA.aw.find_text_by_ocr("取消", timeout=2):
            self.userA.aw.swipe(270, 40, 270, 10, duration=0.2)
            time.sleep(0.5)
            self.userA.aw.click_image(MESSAGE_TAB_SEARCH, region=Normal.HALF_UP)
            time.sleep(1)
        self.userA.aw.click_text("消息", timeout=10, region=(0, 110, 540, 60))
        time.sleep(1)
        # 左滑筛选栏露出"匹配范围"，然后点击选择
        self.userA.aw.swipe(450, 191, 200, 191, duration=0.3)
        time.sleep(0.5)
        self.userA.aw.click_text("匹配范围", timeout=5)
        time.sleep(1)
        self.userA.aw.click_text("包含已退出会话", timeout=5)
        time.sleep(1)
        # 验证筛选已生效（在press_back之前，仍在搜索页）
        self.userA.aw.text_exists("搜索", timeout=3, region=Normal.HALF_UP)
        self.userA.aw.press_back()
        time.sleep(2)

    def teardown(self):
        self.userA.aw.return_to_message_list(max_back=6)
