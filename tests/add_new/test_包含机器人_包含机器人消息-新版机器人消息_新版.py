"""
测试用例: 包含机器人消息-新版机器人消息
功能点: 支持搜索@我、Pin消;消息历史;包含机器人
来源: 搜索.xlsx 行76
"""
import time

from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal


class TestCase29(BaseTest):
    """支持搜索@我、Pin消;消息历史;包含机器人 - 包含机器人消息-新版机器人消息"""

    def setup(self):
        self.userA = self.users("userA")

    def test_case(self):
        """
        包含机器人消息-新版机器人消息
        前置条件: 
        步骤: 勾选包含机器人消息后，查看新版机器人的消息是否可以搜索到
        预期: 勾选包含机器人消息后，可以查看到新版机器人的消息和其他类型的消息
        """
        # 进入群设置-搜索聊天内容
        self.userA.aw._enter_group_settings("测试测试")
        time.sleep(1)
        self.userA.aw.click_text("搜索聊天内容", timeout=5)
        time.sleep(2)
        # 点击匹配范围并选择
        self.userA.aw.click_text("匹配范围", timeout=5)
        time.sleep(1)
        self.userA.aw.click_text("@我", timeout=5)
        time.sleep(1)
        self.userA.aw.press_back()
        time.sleep(2)
        # 验证
        self.userA.aw.text_exists("匹配范围", timeout=3, region=Normal.HALF_UP)

    def teardown(self):
        self.userA.aw.return_to_message_list(max_back=8)
