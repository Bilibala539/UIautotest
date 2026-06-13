"""
测试用例: 待办事项
功能点: 会话AI;总结消息;总结消息效果
来源: 搜索.xlsx 行104
"""
import time

from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal


class TestCase48(BaseTest):
    """会话AI;总结消息;总结消息效果 - 待办事项"""

    def setup(self):
        self.userA = self.users("userA")

    def test_case(self):
        """
        待办事项
        前置条件: 
        步骤: 点击总结消息中的待办事项，查看返回内容的格式
        预期: 返回如下格式的总结
        """
        # 进入聊天页面
        self.userA.send_message(recipient="grp.popoqa50", message="AI测试", isback=False)
        time.sleep(1)
        # 打开AI助手并点击总结消息
        self.userA.aw.click_text("AI", timeout=5, region=(0, 35, 540, 115))
        time.sleep(2)
        self.userA.aw.click_text("总结消息", timeout=5)
        time.sleep(2)
        self.userA.aw.click_text("待办事项", timeout=5)
        time.sleep(1)
        self.userA.aw.text_exists("待办事项", timeout=3)

    def teardown(self):
        self.userA.aw.return_to_message_list(max_back=6)
