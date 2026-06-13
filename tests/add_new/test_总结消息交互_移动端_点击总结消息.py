"""
测试用例: 点击总结消息
功能点: 会话AI;总结消息;总结消息交互（移动端）
来源: 搜索.xlsx 行96
"""
import time

from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal


class TestCase41(BaseTest):
    """会话AI;总结消息;总结消息交互（移动端） - 点击总结消息"""

    def setup(self):
        self.userA = self.users("userA")

    def test_case(self):
        """
        点击总结消息
        前置条件: 
        步骤: 点击总结消息后，查看表现
        预期: 弹起半屏，默认选中要点回顾，文本插入在输入框中(补充图片1)
        """
        # 进入聊天页面
        self.userA.send_message(recipient="grp.popoqa50", message="AI测试", isback=False)
        time.sleep(1)
        # 打开AI助手并点击总结消息
        self.userA.aw.click_text("AI", timeout=5, region=Normal.HALF_UP)
        time.sleep(2)
        self.userA.aw.click_text("总结消息", timeout=5)
        time.sleep(2)
        # 验证弹起半屏
        self.userA.aw.text_exists("要点回顾", timeout=5)

    def teardown(self):
        self.userA.aw.return_to_message_list(max_back=6)
