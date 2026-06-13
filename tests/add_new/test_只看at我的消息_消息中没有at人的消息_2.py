"""
测试用例: 消息中没有@人的消息
功能点: 支持搜索@我、Pin消;消息历史;只看@我的消息
来源: 搜索.xlsx 行82
"""
import time

from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal


class TestCase34(BaseTest):
    """支持搜索@我、Pin消;消息历史;只看@我的消息 - 消息中没有@人的消息"""

    def setup(self):
        self.userA = self.users("userA")

    def test_case(self):
        """
        消息中没有@人的消息
        前置条件: 
        步骤: A和B在一个会话内，A发送了一条普通文本消息，B在消息历史匹配范围中勾选只看@我的消息后查看
        预期: B在只@我的返回结果中，不会返回这条消息
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
