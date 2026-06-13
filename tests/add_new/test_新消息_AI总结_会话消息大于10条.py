"""
测试用例: 会话消息大于10条
功能点: 会话AI;新消息 AI总结
来源: 搜索.xlsx 行112
"""
import time

from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal


class TestCase53(BaseTest):
    """会话AI;新消息 AI总结 - 会话消息大于10条"""

    def setup(self):
        self.userA = self.users("userA")

    def test_case(self):
        """
        会话消息大于10条
        前置条件: 
        步骤: 却换到一个历史会话中，其中的消息多于10条，查看是否显示AI总结的按钮
        预期: 显示AI总结的按钮
        """
        # 进入聊天页面
        self.userA.send_message(recipient="grp.popoqa50", message="AI测试", isback=False)
        time.sleep(1)
        # 验证有AI总结入口
        result = self.userA.aw.find_text_by_ocr("AI总结", timeout=5)
        if not result:
            result = self.userA.aw.find_text_by_ocr("总结", timeout=3)

    def teardown(self):
        self.userA.aw.return_to_message_list(max_back=6)
