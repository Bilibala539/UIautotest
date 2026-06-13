"""
测试用例: 只看@我的消息-无关键词消息
功能点: 支持搜索@我、Pin消;消息历史;只看@我的消息
来源: 搜索.xlsx 行83
"""
import time

from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal


class TestCase35(BaseTest):
    """支持搜索@我、Pin消;消息历史;只看@我的消息 - 只看@我的消息-无关键词消息"""

    def setup(self):
        self.userA = self.users("userA")

    def test_case(self):
        """
        只看@我的消息-无关键词消息
        前置条件: 
        步骤: 大搜中不输入关键词，只勾选只看@我的消息
        预期: 勾选只看@我的消息后，会直接返回结果
        """
        # 进入群设置-搜索聊天内容
        self.userA.aw._enter_group_settings("测试测试")
        time.sleep(1)
        self.userA.aw.click_text("搜索聊天内容", timeout=5)
        time.sleep(2)
        # 点击匹配范围并选择
        self.userA.aw.click_text("匹配范围", timeout=5)
        time.sleep(1)
        self.userA.aw.click_text("只看@我的消息", timeout=5)
        time.sleep(1)
        self.userA.aw.press_back()
        time.sleep(2)
        # 验证
        self.userA.aw.text_exists("匹配范围", timeout=3, region=Normal.HALF_UP)

    def teardown(self):
        self.userA.aw.return_to_message_list(max_back=8)
