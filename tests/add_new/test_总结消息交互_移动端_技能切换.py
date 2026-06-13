"""
测试用例: 技能切换
功能点: 会话AI;总结消息;总结消息交互（移动端）
来源: 搜索.xlsx 行97
"""
import time

from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal


class TestCase42(BaseTest):
    """会话AI;总结消息;总结消息交互（移动端） - 技能切换"""

    def setup(self):
        self.userA = self.users("userA")

    def test_case(self):
        """
        技能切换
        前置条件: 
        步骤: 点击总结消息后，逐一切换其中的技能
        预期: 点击切换后，输入框中技能文本切换为对应的技能需求
        """
        # 进入聊天页面
        self.userA.send_message(recipient="grp.popoqa50", message="AI测试", isback=False)
        time.sleep(1)
        # 打开AI助手并点击总结消息
        self.userA.aw.click_text("AI", timeout=5, region=(0, 35, 540, 115))
        time.sleep(2)
        self.userA.aw.click_text("总结消息", timeout=5)
        time.sleep(2)
        # 切换技能
        self.userA.aw.click_text("问题清单", timeout=5)
        time.sleep(1)
        self.userA.aw.text_exists("问题清单", timeout=3)

    def teardown(self):
        self.userA.aw.return_to_message_list(max_back=6)
