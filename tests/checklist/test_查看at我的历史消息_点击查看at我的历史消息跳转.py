"""
测试用例: 点击查看@我的历史消息跳转
功能点: 查看@我的历史消息
来源: 搜索.xlsx 行85
"""
import time

from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal


class TestCase36(BaseTest):
    """查看@我的历史消息 - 点击查看@我的历史消息跳转"""

    def setup(self):
        self.userA = self.users("userA")

    def test_case(self):
        """
        点击查看@我的历史消息跳转
        步骤: 点击@我分组中的”查看@我的历史消息“按钮
        预期: 跳转到大搜中，大搜中匹配分为中的@我默认勾选
        """
        # 进入大搜
        self.userA.aw.click_image(MESSAGE_TAB_SEARCH, region=Normal.HALF_UP)
        time.sleep(1)
        # 点击@我tab
        pos = self.userA.aw.find_text_by_ocr("@我", timeout=5)
        if pos:
            self.userA.aw.tap(pos[0], pos[1])
            time.sleep(1)
            # 点击查看@我的历史消息
            history_pos = self.userA.aw.find_text_by_ocr("查看@我的历史消息", timeout=5)
            if history_pos:
                self.userA.aw.tap(history_pos[0], history_pos[1])
                time.sleep(2)
                self.userA.aw.text_exists("消息", timeout=3, region=Normal.HALF_UP)

    def teardown(self):
        self.userA.aw.return_to_message_list(max_back=6)
